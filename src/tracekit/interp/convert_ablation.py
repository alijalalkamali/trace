"""
Convert an ablation run into per-arm EvalResult files the judge pipeline can
consume.

Mirrors convert_sweep.py: each arm becomes its own pseudo-model result file,

    results/steerability_v2_ablated_{arm}.jsonl

with model_name "ablated:{arm}" and the generation in raw_completions[0] (the
BASE slot -- these are generations on base prompts; the intervention lives in
activation space, not in the prompt). raw_completions[1] is an empty
placeholder, and the arms are judged in the base condition only.

Arms must cover an identical item set. An ablation run whose arms disagree on
items is incomplete, and converting it silently would produce rate comparisons
across different denominators.

Usage:
    python -m tracekit.interp.convert_ablation \
        --ablation-path results/interp/ablation_runs.jsonl \
        --output-dir results/
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

from tracekit.io.dataset import EvalResult
from tracekit.io.jsonl import write_jsonl

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"item_id", "category", "arm", "completion", "finish_reason"}


def convert_ablation(ablation_path: Path, output_dir: Path) -> list[Path]:
    if not ablation_path.exists():
        raise FileNotFoundError(f"Ablation file not found: {ablation_path}")

    by_arm: dict[str, list[dict]] = defaultdict(list)
    with ablation_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{ablation_path}:{line_num}: invalid JSON: {e}") from e
            missing = REQUIRED_FIELDS - set(rec)
            if missing:
                raise ValueError(f"{ablation_path}:{line_num}: missing fields {sorted(missing)}")
            by_arm[rec["arm"]].append(rec)

    if not by_arm:
        raise ValueError(f"No records found in {ablation_path}")

    item_sets = {arm: {r["item_id"] for r in recs} for arm, recs in by_arm.items()}
    reference = next(iter(item_sets.values()))
    for arm, ids in item_sets.items():
        if len(ids) != len(by_arm[arm]):
            raise ValueError(f"Arm {arm!r}: duplicate item_ids present.")
        if ids != reference:
            raise ValueError(
                f"Arm {arm!r} covers a different item set than other arms "
                f"(symmetric difference: {sorted(ids ^ reference)[:5]}...). "
                f"Complete the run or drop the arm rather than converting silently."
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for arm, recs in sorted(by_arm.items()):
        model_name = f"ablated:{arm}"
        results = [
            EvalResult(
                item_id=r["item_id"],
                item_type="steerability",
                model_name=model_name,
                seed=None,
                raw_completions=[r["completion"], ""],
                finish_reasons=[r["finish_reason"], None],
                score=None,
                extra={
                    "category": r["category"],
                    "ablation_arm": arm,
                    "ablation_layers": r.get("ablation_layers"),
                    "extraction_layer": r.get("start_layer"),
                    "source_run": str(ablation_path),
                },
            )
            for r in sorted(recs, key=lambda r: r["item_id"])
        ]
        out_path = output_dir / f"steerability_v2_ablated_{arm}.jsonl"
        write_jsonl(out_path, results)
        n_len = sum(1 for r in recs if r["finish_reason"] == "length")
        logger.info(
            "%s: %d items -> %s (%d hit the token ceiling)",
            model_name,
            len(results),
            out_path,
            n_len,
        )
        written.append(out_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ablation-path", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    args = parser.parse_args()
    convert_ablation(args.ablation_path, args.output_dir)


if __name__ == "__main__":
    main()
