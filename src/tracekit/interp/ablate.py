"""
Directional ablation: remove a direction from the residual stream and measure
whether the behavior it steers can still occur.

Why this exists
---------------
`steer.py` established SUFFICIENCY: adding alpha * v to the residual stream at
one layer drives the derail rate monotonically from 0% to 86%. Sufficiency
shows the direction is a lever. It does not show the model USES that direction
when nothing is intervening -- an amplified correlate of the behavior would
produce the same sweep.

NECESSITY is the complement: project the direction out of the residual stream,
generate normally, and ask whether the behavior survives. If derails collapse,
the direction is load-bearing. If they persist, the behavior has redundant
encoding and the direction is one input rather than the pathway. Both outcomes
are reportable results; the ambiguous case is handled by the random control.

Method
------
At each target layer, the hook replaces the layer's output hidden states with

    h <- h - (h . v_hat) v_hat

which is the component of h orthogonal to v_hat. Nothing is deleted: the tensor
keeps its shape and every other direction is untouched. After the operation
h . v_hat == 0 exactly, so downstream layers read zero signal along v_hat.

Ablation is applied at EVERY layer by default, following Arditi et al. The
direction is extracted at one layer but removed throughout, so the model never
represents it anywhere in its residual stream. Applying it from partway up
leaves earlier layers free to write the component, and applying it at a single
layer lets every later layer rewrite it.

Controls
--------
Three arms are generated in one run:

  - `none`   : no hook. Reproduces the alpha=0 baseline and confirms the
               serving setup is unchanged.
  - `target` : ablate the difference-of-means direction.
  - `random` : ablate a random unit direction at the same layers, same seed
               discipline. Removing ANY direction perturbs the model, so
               without this arm a drop in derails cannot be separated from
               generic damage.

Both directions are unit norm, but the magnitude actually removed is |h . v_hat|,
which is larger for a direction aligned with the residual stream than for a
random one. That asymmetry is inherent to the comparison, so the runner logs
the mean removed magnitude per arm rather than leaving it implicit.

Reproducibility
---------------
The eval split is recomputed with the same seed and fraction used by the alpha
sweep, so the 50 items generated here are the same 50 the sweep ran on and are
disjoint from the items that built the vector. Decoding is greedy.

--swap-split exchanges the two halves, fitting the direction on what was the
eval set and evaluating on what was the fitting set. At vector_fraction 0.5
that is the second fold of a 2-fold cross-validation, and reproducing the
effect there is what shows the result does not depend on which items happened
to define the direction.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import numpy as np
import torch
import torch.nn as nn

from tracekit.interp.config import HarvestConfig
from tracekit.interp.data import ProbeExample, build_probe_examples
from tracekit.interp.steer import (
    SteeringVector,
    build_steering_vector,
    report_residual_norms,
    split_items,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ARM_NONE = "none"
ARM_TARGET = "target"
ARM_RANDOM = "random"


# ---------------------------------------------------------------------------
# Direction construction
# ---------------------------------------------------------------------------


def random_unit_direction(dim: int, seed: int) -> np.ndarray:
    """
    Draw a random unit vector, isotropically, for the control arm.

    Gaussian coordinates then normalize: this is uniform on the unit sphere,
    unlike sampling coordinates uniformly in a box (which concentrates mass
    toward the corners and would bias the control).
    """
    if dim <= 0:
        raise ValueError(f"dim must be positive, got {dim}")
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim)
    norm = float(np.linalg.norm(v))
    if norm == 0.0 or not np.isfinite(norm):  # pragma: no cover - probability zero
        raise ValueError(f"Degenerate random direction (norm={norm}).")
    return (v / norm).astype(np.float32)


def resolve_ablation_layers(
    n_layers: int,
    start_layer: int = 0,
    single_layer: bool = False,
) -> list[int]:
    """
    Layers to ablate at. Default is every layer, following Arditi et al.

    Global ablation means the model never represents the direction anywhere in
    its residual stream, so there is no layer at which it can be rewritten and
    no cutoff to justify. Restricting the range is available for comparison
    arms but is not the main configuration: starting partway up leaves earlier
    layers free to write the component, and a single layer lets every later
    layer rewrite it.
    """
    if not 0 <= start_layer < n_layers:
        raise ValueError(f"start_layer {start_layer} out of range for {n_layers}-layer model")
    return [start_layer] if single_layer else list(range(start_layer, n_layers))


# ---------------------------------------------------------------------------
# Ablation hook
# ---------------------------------------------------------------------------


class AblationHook:
    """
    Context manager that projects a direction out of the residual stream at
    every registered layer while active.

    Mirrors SteeringHook's dtype/device caching and tuple-unwrapping, but
    registers on many layers and subtracts a projection rather than adding a
    scaled vector.

    The dot product and subtraction are computed in float32 even when the model
    runs in bf16. A bf16 dot product over 8192 terms accumulates enough error
    that the residual component along v_hat is not reliably zeroed, which is the
    one property the intervention depends on.

    Set `enabled=False` for an exact-identity pass; the hook returns the output
    object untouched, adding no numeric noise to the control arm.
    """

    def __init__(
        self,
        layers: nn.ModuleList,
        layer_indices: list[int],
        vector: np.ndarray,
        enabled: bool = True,
    ) -> None:
        if not layer_indices:
            raise ValueError("layer_indices must be non-empty")
        n_layers = len(layers)
        bad = [i for i in layer_indices if not (0 <= i < n_layers)]
        if bad:
            raise ValueError(f"layer indices out of range for {n_layers}-layer model: {bad}")
        if vector.ndim != 1:
            raise ValueError(f"vector must be 1-D, got shape {vector.shape}")

        self._layers = layers
        self._layer_indices = list(layer_indices)
        self._vector_np = vector.astype(np.float32)
        self._enabled = bool(enabled)
        self._handles: list[torch.utils.hooks.RemovableHandle] = []
        self._vector_cache: torch.Tensor | None = None
        self._removed_magnitudes: list[float] = []

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def reset_stats(self) -> None:
        self._removed_magnitudes = []

    @property
    def mean_removed_magnitude(self) -> float:
        """Mean |h . v_hat| over every position seen since the last reset."""
        if not self._removed_magnitudes:
            return float("nan")
        return float(np.mean(self._removed_magnitudes))

    def _hook(self, module: nn.Module, inputs: tuple, output):
        if not self._enabled:
            return output
        hidden = output[0] if isinstance(output, tuple) else output
        if not torch.is_tensor(hidden):
            raise TypeError(
                f"AblationHook expected tensor (or tuple with tensor first), got {type(hidden)}."
            )
        if self._vector_cache is None or self._vector_cache.device != hidden.device:
            self._vector_cache = torch.from_numpy(self._vector_np).to(
                dtype=torch.float32, device=hidden.device
            )
        if self._vector_cache.shape[0] != hidden.shape[-1]:
            raise ValueError(
                f"Ablation vector dim {self._vector_cache.shape[0]} != hidden dim "
                f"{hidden.shape[-1]} -- vector was built from a different model/layer width."
            )

        orig_dtype = hidden.dtype
        h32 = hidden.to(torch.float32)
        coeff = h32 @ self._vector_cache  # [batch, seq] -- signed overlap with v_hat
        ablated = h32 - coeff.unsqueeze(-1) * self._vector_cache
        self._removed_magnitudes.append(float(coeff.abs().mean().item()))
        ablated = ablated.to(orig_dtype)

        if isinstance(output, tuple):
            return (ablated,) + output[1:]
        return ablated

    def __enter__(self) -> AblationHook:
        for idx in self._layer_indices:
            self._handles.append(self._layers[idx].register_forward_hook(self._hook))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles = []

    @property
    def layer_indices(self) -> list[int]:
        return list(self._layer_indices)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AblationArm:
    """One generation condition: a name, a direction, and whether to intervene."""

    name: str
    vector: np.ndarray
    enabled: bool


def _generate_one(model, tokenizer, prompt_text: str, max_new_tokens: int) -> tuple[str, str, int]:
    """Greedy generation for a single prompt. Returns (completion, finish_reason, n_new)."""
    input_ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt_text}],
        add_generation_prompt=True,
        return_tensors="pt",
    )
    if not torch.is_tensor(input_ids):  # newer transformers returns BatchEncoding
        input_ids = input_ids["input_ids"]
    input_ids = input_ids.to(model.device)
    with torch.no_grad():
        gen = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
        )
    seq = gen.sequences[0]
    n_new = int(seq.shape[0] - input_ids.shape[1])
    completion = tokenizer.decode(seq[input_ids.shape[1] :], skip_special_tokens=True)
    return completion, ("length" if n_new >= max_new_tokens else "stop"), n_new


def run_ablation_arms(
    model,
    tokenizer,
    arms: list[AblationArm],
    layer_indices: list[int],
    eval_examples: list[ProbeExample],
    output_path: Path,
    start_layer: int,
    max_new_tokens: int = 500,
    swap_split: bool = False,
) -> None:
    """
    Generate every eval prompt under every arm and append JSONL records.

    Each arm gets its own hook registration so the control arm runs with no
    hook attached at all, rather than with a disabled hook still in the call
    path. That keeps `none` an exact reproduction of unmodified generation.
    """
    layers = model.model.layers
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as out_f:
        for arm in arms:
            logger.info("arm=%s: generating on %d prompts", arm.name, len(eval_examples))
            hook: AblationHook | None = None
            if arm.enabled:
                hook = AblationHook(layers, layer_indices, arm.vector, enabled=True)
                hook.__enter__()
            try:
                for i, ex in enumerate(eval_examples, start=1):
                    completion, finish_reason, n_new = _generate_one(
                        model, tokenizer, ex.prompt_text, max_new_tokens
                    )
                    out_f.write(
                        json.dumps(
                            {
                                "item_id": ex.item_id,
                                "category": ex.category,
                                "condition": ex.condition,
                                "responder_model": ex.responder_model,
                                "arm": arm.name,
                                "start_layer": start_layer,
                                "swap_split": swap_split,
                                "ablation_layers": [layer_indices[0], layer_indices[-1]],
                                "completion": completion,
                                "finish_reason": finish_reason,
                                "n_new_tokens": n_new,
                                "max_new_tokens": max_new_tokens,
                            }
                        )
                        + "\n"
                    )
                    if i % 10 == 0 or i == len(eval_examples):
                        logger.info("  arm=%s: %d/%d", arm.name, i, len(eval_examples))
            finally:
                if hook is not None:
                    logger.info(
                        "  arm=%s: mean |h . v_hat| removed = %.3f",
                        arm.name,
                        hook.mean_removed_magnitude,
                    )
                    hook.__exit__(None, None, None)
    logger.info("Ablation run complete -> %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--hardware-profile", choices=["local_dev", "rental_gpu"], required=True)
    parser.add_argument("--activations-path", required=True, type=Path)
    parser.add_argument("--labels-path", required=True, type=Path)
    parser.add_argument("--items-path", required=True, type=Path)
    parser.add_argument("--results-path", required=True, type=Path)
    parser.add_argument("--judgments-csv", required=True, type=Path)
    parser.add_argument(
        "--layer-index",
        required=True,
        type=int,
        help="Layer the direction is EXTRACTED from. Does not control where ablation "
        "is applied; see --ablation-start.",
    )
    parser.add_argument(
        "--ablation-start",
        type=int,
        default=0,
        help="First layer to ablate at, through the end of the stack. Default 0 "
        "(every layer), following Arditi et al. Raise it only as a comparison arm.",
    )
    parser.add_argument(
        "--single-layer",
        action="store_true",
        help="Ablate only at --ablation-start. Later layers can then rewrite the "
        "component; use only as a comparison arm.",
    )
    parser.add_argument("--positive-label", default="derail")
    parser.add_argument("--category", default="values_conflict_low")
    parser.add_argument("--condition", default="base", choices=["base", "steered"])
    parser.add_argument(
        "--responder-model", default="together:meta-llama/Llama-3.3-70B-Instruct-Turbo"
    )
    parser.add_argument(
        "--vector-fraction",
        type=float,
        default=0.5,
        help="Must match the alpha sweep so the eval items are identical.",
    )
    parser.add_argument(
        "--split-seed",
        type=int,
        default=0,
        help="Must match the alpha sweep so the eval items are identical.",
    )
    parser.add_argument(
        "--swap-split",
        action="store_true",
        help="Fit the direction on what was the eval half and evaluate on what was "
        "the fitting half. With --vector-fraction 0.5 this is the second fold of a "
        "2-fold cross-validation.",
    )
    parser.add_argument(
        "--random-seed", type=int, default=1234, help="Seed for the random control direction."
    )
    parser.add_argument("--max-new-tokens", type=int, default=500)
    parser.add_argument(
        "--arms",
        nargs="+",
        default=[ARM_NONE, ARM_TARGET, ARM_RANDOM],
        choices=[ARM_NONE, ARM_TARGET, ARM_RANDOM],
    )
    parser.add_argument(
        "--output-path", default=Path("results/interp/ablation_runs.jsonl"), type=Path
    )
    args = parser.parse_args()

    activations = torch.load(args.activations_path, weights_only=False)
    labels: dict[str, str] = json.loads(args.labels_path.read_text())

    median_norm = report_residual_norms(activations, args.layer_index)
    logger.info("Median residual norm at layer %d: %.1f", args.layer_index, median_norm)

    vector_items, eval_items = split_items(
        sorted(activations),
        labels,
        args.positive_label,
        vector_fraction=args.vector_fraction,
        seed=args.split_seed,
    )
    if args.swap_split:
        vector_items, eval_items = eval_items, vector_items

    # The swap is load-bearing: a silently ignored flag would rerun fold one and
    # look like a successful replication. Assert the partition survived and log
    # both halves' leading item ids so the exchange is visible in the run log.
    overlap = set(vector_items) & set(eval_items)
    if overlap:
        raise ValueError(
            f"Split is not a partition: {len(overlap)} item(s) in both halves "
            f"(first few: {sorted(overlap)[:5]})."
        )
    n_pos_eval = sum(1 for i in eval_items if labels[i] == args.positive_label)
    logger.info(
        "Split: %d vector items, %d eval items (seed=%d, fraction=%.2f, swap=%s).",
        len(vector_items),
        len(eval_items),
        args.split_seed,
        args.vector_fraction,
        args.swap_split,
    )
    logger.info("  vector items begin: %s", vector_items[:5])
    logger.info("  eval   items begin: %s", eval_items[:5])
    logger.info("  eval positives: %d/%d", n_pos_eval, len(eval_items))

    sv: SteeringVector = build_steering_vector(
        activations, labels, args.layer_index, args.positive_label, vector_items
    )
    dim = sv.vector.shape[0]
    rand_vec = random_unit_direction(dim, seed=args.random_seed)
    cos = float(np.dot(sv.vector, rand_vec))
    logger.info("cos(target, random) = %+.4f (expected near 0 in %d dims)", cos, dim)

    examples = build_probe_examples(
        items_path=args.items_path,
        results_path=args.results_path,
        judgments_csv=args.judgments_csv,
        category=args.category,
        condition=args.condition,
        responder_model=args.responder_model,
    )
    eval_set = set(eval_items)
    eval_examples = [ex for ex in examples if ex.item_id in eval_set]
    if not eval_examples:
        raise ValueError("No eval examples matched the split; check items/results paths.")

    cfg = HarvestConfig(
        model_name=args.model_name,
        hardware_profile=args.hardware_profile,
        category=args.category,
        condition=args.condition,
        responder_model=args.responder_model,
    )
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name,
        torch_dtype=cfg.torch_dtype,
        attn_implementation=cfg.attn_implementation,
        device_map=cfg.device_map,
    )
    model.eval()

    layer_indices = resolve_ablation_layers(
        len(model.model.layers),
        start_layer=args.ablation_start,
        single_layer=args.single_layer,
    )
    logger.info(
        "Ablating at layers %d-%d (%d layers).",
        layer_indices[0],
        layer_indices[-1],
        len(layer_indices),
    )

    arm_specs = {
        ARM_NONE: AblationArm(ARM_NONE, sv.vector, enabled=False),
        ARM_TARGET: AblationArm(ARM_TARGET, sv.vector, enabled=True),
        ARM_RANDOM: AblationArm(ARM_RANDOM, rand_vec, enabled=True),
    }
    arms = [arm_specs[name] for name in args.arms]

    run_ablation_arms(
        model,
        tokenizer,
        arms,
        layer_indices,
        eval_examples,
        args.output_path,
        start_layer=args.ablation_start,
        max_new_tokens=args.max_new_tokens,
        swap_split=args.swap_split,
    )


if __name__ == "__main__":
    main()
