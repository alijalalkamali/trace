#!/usr/bin/env python3
"""Compare the paper's difference-of-means direction with a ridge-regularized one.

Why this check exists
---------------------
A difference-of-means direction can bundle correlates of the behavior along
with the behavior itself. García-Ferrero et al. (2026) propose the Ridge Mean
Difference (RMD), which reweights the mean difference by the inverse of the
negative class's covariance so that directions of high within-class variance,
which carry correlates rather than the contrast, are discounted:

    delta   = mean_pos - mean_neg
    v_tilde = (Sigma_neg + lambda * I)^(-1) @ delta
    v_rmd   = v_tilde / ||v_tilde||

with Sigma_neg the covariance of the negative class and lambda = 1e-2 in their
experiments. Their activations are the last hidden state after the chat
template and generation token, which is the same generation-onset position
this study probes, so the two directions are computed from identical inputs.

Their weighted variant (WRMD) additionally needs a per-example confidence
score from several sampled answers and a set of neutral prompts. This study
has one consensus label per item and no neutral set, so RMD is the variant
that applies without inventing inputs the method requires.

What the script reports, per split
----------------------------------
    - cosine between the paper's direction and the ridge direction, both
      fitted on the same training items. High cosine means the paper's
      direction is not dominated by high-variance correlates.
    - how well each direction separates derail from non-derail on the test
      items, as an AUC over projections. This asks whether the ridge
      direction is a better readout, not only a different one.
    - the same comparison across a range of lambda, since the right lambda
      depends on the scale of the activations and theirs was tuned on a
      different model.

Computation
-----------
Sigma_neg is 8192 x 8192 but has rank at most n_neg - 1, around 28 per split.
The solve uses the Woodbury identity, which is exact and needs only an
n_neg x n_neg system:

    (X^T X / n + lambda I)^(-1) d = (1 / lambda) (d - X^T (n lambda I + X X^T)^(-1) X d)

with X the centered negative-class activations. No 8192 x 8192 matrix is
formed.

Usage:
    A=results/interp/activations/together_meta-llama_\
Llama-3.3-70B-Instruct-Turbo/values_conflict_low_base
    python scripts/compare_ridge_direction.py \
        --activations-path $A/activations.pt \
        --labels-path $A/labels.json \
        --layer-index 40 \
        --output results/interp/ridge_direction_comparison.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch

from tracekit.interp.steer import build_steering_vector, split_items

POSITIVE_LABEL = "derail"
PAPER_LAMBDA = 1e-2
LAMBDA_SWEEP = (1e-4, 1e-3, 1e-2, 1e-1, 1.0)


def layer_matrix(activations: dict, item_ids: list[str], layer_index: int) -> np.ndarray:
    """Stack one layer's activations for the given items as float64 rows."""
    rows = []
    for item_id in item_ids:
        per_layer = activations[item_id]
        vector = per_layer[layer_index] if layer_index in per_layer else per_layer[str(layer_index)]
        if isinstance(vector, torch.Tensor):
            vector = vector.detach().float().cpu().numpy()
        rows.append(np.asarray(vector, dtype=np.float64).ravel())
    return np.vstack(rows)


def unit(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if not np.isfinite(norm) or norm == 0.0:
        raise ValueError("Direction has zero or non-finite norm.")
    return vector / norm


def ridge_mean_difference(pos: np.ndarray, neg: np.ndarray, lam: float) -> np.ndarray:
    """RMD direction of García-Ferrero et al. (2026), eq. 2, via Woodbury.

    Args:
        pos: Positive-class activations, shape (n_pos, d).
        neg: Negative-class activations, shape (n_neg, d).
        lam: Ridge coefficient lambda > 0.

    Returns:
        Unit-norm direction of shape (d,).
    """
    if lam <= 0:
        raise ValueError(f"lambda must be positive, got {lam}")
    if pos.shape[1] != neg.shape[1]:
        raise ValueError("Positive and negative activations differ in width.")
    delta = pos.mean(axis=0) - neg.mean(axis=0)
    centered = neg - neg.mean(axis=0)
    n = centered.shape[0]
    # (C^T C / n + lam I)^-1 delta, with C the centered negatives.
    gram = centered @ centered.T + n * lam * np.eye(n)
    correction = centered.T @ np.linalg.solve(gram, centered @ delta)
    return unit((delta - correction) / lam)


def auc(scores: np.ndarray, is_positive: np.ndarray) -> float:
    """Rank-based AUC: chance a positive outscores a negative, ties counted half."""
    pos, neg = scores[is_positive], scores[~is_positive]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    diff = pos[:, None] - neg[None, :]
    return float(((diff > 0).sum() + 0.5 * (diff == 0).sum()) / diff.size)


def analyze_split(
    activations: dict,
    labels: dict[str, str],
    train_ids: list[str],
    test_ids: list[str],
    layer_index: int,
) -> list[dict]:
    """Compare MD and RMD for one split. Returns one row per lambda."""
    md = unit(
        np.asarray(
            build_steering_vector(
                activations, labels, layer_index, POSITIVE_LABEL, train_ids
            ).vector,
            dtype=np.float64,
        ).ravel()
    )

    train_pos = [i for i in train_ids if labels[i] == POSITIVE_LABEL]
    train_neg = [i for i in train_ids if labels[i] != POSITIVE_LABEL]
    pos = layer_matrix(activations, train_pos, layer_index)
    neg = layer_matrix(activations, train_neg, layer_index)

    # The reimplemented unweighted mean difference must equal the pipeline's
    # vector, or the comparison would be against a different baseline.
    md_check = unit(pos.mean(axis=0) - neg.mean(axis=0))
    agreement = float(md @ md_check)
    if agreement < 0.9999:
        raise SystemExit(
            f"Pipeline direction and reimplemented mean difference disagree "
            f"(cosine {agreement:.6f}); the baseline is not what the paper used."
        )

    test = layer_matrix(activations, test_ids, layer_index)
    test_is_pos = np.array([labels[i] == POSITIVE_LABEL for i in test_ids])
    md_auc = auc(test @ md, test_is_pos)

    rows = []
    for lam in LAMBDA_SWEEP:
        rmd = ridge_mean_difference(pos, neg, lam)
        rows.append(
            {
                "lambda": lam,
                "cos_md_rmd": float(md @ rmd),
                "test_auc_md": md_auc,
                "test_auc_rmd": auc(test @ rmd, test_is_pos),
                "n_train_pos": len(train_pos),
                "n_train_neg": len(train_neg),
                "n_test": len(test_ids),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--activations-path", type=Path, required=True)
    parser.add_argument("--labels-path", type=Path, required=True)
    parser.add_argument("--layer-index", type=int, default=40)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    activations = torch.load(args.activations_path, map_location="cpu", weights_only=False)
    labels = json.loads(args.labels_path.read_text(encoding="utf-8"))

    first, second = split_items(sorted(labels), labels, POSITIVE_LABEL)
    splits = {1: (first, second), 2: (second, first)}  # split 2 swaps the halves

    all_rows, rmd_by_split = [], {}
    for split, (train_ids, test_ids) in splits.items():
        for row in analyze_split(activations, labels, train_ids, test_ids, args.layer_index):
            all_rows.append({"split": split, **row})
        train_pos = [i for i in train_ids if labels[i] == POSITIVE_LABEL]
        train_neg = [i for i in train_ids if labels[i] != POSITIVE_LABEL]
        rmd_by_split[split] = ridge_mean_difference(
            layer_matrix(activations, train_pos, args.layer_index),
            layer_matrix(activations, train_neg, args.layer_index),
            PAPER_LAMBDA,
        )

    print(f"layer {args.layer_index}\n")
    print(
        f"{'split':>5} {'lambda':>8} {'cos(MD,RMD)':>12} {'test AUC MD':>12} {'test AUC RMD':>13}"
    )
    for r in all_rows:
        marker = "  <- paper's lambda" if r["lambda"] == PAPER_LAMBDA else ""
        print(
            f"{r['split']:>5} {r['lambda']:>8.0e} {r['cos_md_rmd']:>12.4f} "
            f"{r['test_auc_md']:>12.4f} {r['test_auc_rmd']:>13.4f}{marker}"
        )
    cross = float(rmd_by_split[1] @ rmd_by_split[2])
    print(
        f"\ncos(RMD split 1, RMD split 2) at lambda={PAPER_LAMBDA:g}: {cross:.4f} "
        "(the paper's difference-of-means directions: 0.82)"
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
