#!/usr/bin/env python3
"""Count how often the lexicographic tie-break decided a consensus label.

The consensus rule takes the most frequent label among the five peer judges
and breaks ties by lexicographic order, so a 2-2-1 split is resolved rather
than dropped. That choice is deterministic but arbitrary, so the paper
reports how often it was load-bearing, and whether any tie falls on a label
a headline claim counts.

Usage:
    python scripts/count_consensus_ties.py \\
        --aggregated results/judgments/aggregated_judgments.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from tracekit.analysis.consensus import consensus_label

CORE = ("values_conflict_low", "reasoning_values_elicit", "reasoning_values_suppress")
RESISTANCE = ("refusal-override", "comply-with-explicit-challenge")
ID_COLUMNS = {"item_id", "category", "responder_model", "condition"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--aggregated", type=Path, required=True)
    args = parser.parse_args(argv)

    agg = pd.read_csv(args.aggregated)
    judges = [c for c in agg.columns if ":" in c and c not in ID_COLUMNS]

    rows = []
    for record in agg.to_dict("records"):
        votes = {j: record[j] for j in judges if pd.notna(record[j])}
        result = consensus_label(votes, responder=record["responder_model"], strict=False)
        if result is None:
            continue
        if result.label != record["consensus_loo"]:
            raise SystemExit(
                f"Recomputed label {result.label!r} differs from consensus_loo "
                f"{record['consensus_loo']!r} for {record['item_id']} / "
                f"{record['responder_model']} / {record['condition']}; the CSV and "
                "the shared rule disagree."
            )
        rows.append(
            {**{k: record[k] for k in ID_COLUMNS}, "label": result.label, "tie": result.tie}
        )
    df = pd.DataFrame(rows)

    core = df[df.category.isin(CORE)]
    print(
        f"all categories: {df.tie.sum()} of {len(df)} labels decided "
        f"by tie-break ({df.tie.mean():.1%})"
    )
    print(f"core categories: {core.tie.sum()} of {len(core)} ({core.tie.mean():.1%})")

    headline = core[core.tie & core.label.isin(RESISTANCE) & (core.condition == "steered")]
    print(f"\nties on steered resistance labels (the 7.2 claim): {len(headline)}")
    if len(headline):
        print(headline[["item_id", "responder_model", "label"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
