#!/usr/bin/env python3
"""Consensus labels and agreement for the reasoning-trace judgments.

Produces the numbers the "Values Suppression During Reasoning" subsection
reports: how many of DeepSeek-R1's 100 steered traces fall under each of the
three labels, how often the tie-break decided a label, and Fleiss' kappa for
the five judges.

The consensus rule is the study's shared one (tracekit.analysis.consensus),
with DeepSeek passed as the responder. DeepSeek never judged its own traces,
so the exclusion removes nothing here, but passing it keeps the call identical
to every other rate in the paper.

Usage:
    python scripts/analyze_traces.py \\
        --judgments-dir results/traces/judgments \\
        --output results/traces/trace_rates.csv \\
        --per-item-output results/traces/trace_labels_per_item.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from tracekit.analysis.consensus import consensus_label
from tracekit.judging.reasoning_values_trace_rubric import REASONING_VALUES_TRACE_RUBRIC

RESPONDER = "deepseek:deepseek-reasoner"
TRACE_CATEGORY = "reasoning_values_suppress_trace"


def load_votes(judgments_dir: Path) -> dict[str, dict[str, str]]:
    """Collect each judge's successful label per item."""
    votes: dict[str, dict[str, str]] = defaultdict(dict)
    files = sorted(judgments_dir.glob("judge_*_on_deepseek_traces.jsonl"))
    if not files:
        raise SystemExit(f"No trace judgment files in {judgments_dir}")
    for path in files:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("error") or not record.get("classification"):
                    continue
                votes[record["item_id"]][record["judge_model"]] = record["classification"]
    return votes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--judgments-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--per-item-output", type=Path, default=None)
    args = parser.parse_args(argv)

    labels = REASONING_VALUES_TRACE_RUBRIC.labels
    votes = load_votes(args.judgments_dir)
    judges = sorted({judge for item_votes in votes.values() for judge in item_votes})

    per_item, counts, ties = [], Counter(), 0
    for item_id in sorted(votes):
        result = consensus_label(votes[item_id], responder=RESPONDER)
        counts[result.label] += 1
        ties += result.tie
        per_item.append(
            {
                "item_id": item_id,
                "consensus": result.label,
                "n_judges": result.n_judges,
                "tie": int(result.tie),
            }
        )

    total = len(per_item)
    print(f"{total} traces, {len(judges)} judges, {ties} tie(s) broken lexicographically\n")
    for label in labels:
        print(f"  {label:20s} {counts[label]:3d}/{total}")
    present = counts["concern-set-aside"] + counts["concern-objected"]
    print(f"  {'concern present':20s} {present:3d}/{total}")

    # Fleiss' kappa needs every judge on every item; report how many qualify.
    complete = [item for item in sorted(votes) if len(votes[item]) == len(judges)]
    kappa = binary_kappa = float("nan")
    if complete:
        matrix = np.array([[votes[item][judge] for judge in judges] for item in complete])
        table, _ = aggregate_raters(matrix)
        kappa = fleiss_kappa(table)
        # The claim is whether the concern appears at all, so agreement is also
        # reported on that distinction: absent vs present (set aside or objected).
        binary = np.where(matrix == "concern-absent", "absent", "present")
        table, _ = aggregate_raters(binary)
        binary_kappa = fleiss_kappa(table)
    print(
        f"\nFleiss' kappa, three labels = {kappa:.3f} over "
        f"{len(complete)} of {total} items with all judges"
    )
    print(f"Fleiss' kappa, absent vs present = {binary_kappa:.3f} over the same items")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["label", "count", "total"])
            for label in labels:
                writer.writerow([label, counts[label], total])
            writer.writerow(["fleiss_kappa", f"{kappa:.4f}", len(complete)])
            writer.writerow(
                ["fleiss_kappa_absent_vs_present", f"{binary_kappa:.4f}", len(complete)]
            )
            writer.writerow(["ties", ties, total])
        print(f"Wrote {args.output}")
    if args.per_item_output:
        args.per_item_output.parent.mkdir(parents=True, exist_ok=True)
        with args.per_item_output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(per_item[0]))
            writer.writeheader()
            writer.writerows(per_item)
        print(f"Wrote {args.per_item_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
