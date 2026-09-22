#!/usr/bin/env python3
"""Judge agreement on the steered suppression rubric, at three resolutions.

The five-way suppression kappa is low enough that a single number hides where
judges actually disagree. This script reports the ladder the paper uses:

    1. resistance vs compliance, the distinction the resistance claim uses
    2. which resistance mode, among responses judged as resistance
    3. which compliance mode, among responses judged as compliance
    4. the full five-way kappa, for reference

Levels 2 and 3 keep only the judgments that fall inside the level's label set.
A judge who called a resistance response "clean-suppression" is disagreeing
about resistance itself, which level 1 already measures; counting that vote
at level 2 would blur the two questions together. Fleiss' kappa needs a
constant rater count, so levels 2 and 3 report kappa over the items where
every judge's vote falls inside the set, and observed pairwise agreement over
every item.

Usage:
    python scripts/analyze_suppression_agreement.py \\
        --aggregated results/judgments/aggregated_judgments.csv \\
        --output results/analysis/suppression_agreement_full100.csv
"""

from __future__ import annotations

import argparse
import csv
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

CATEGORY = "reasoning_values_suppress"
RESISTANCE = ("refusal-override", "comply-with-explicit-challenge")
COMPLIANCE = ("clean-suppression", "partial-suppression", "values-smuggled")
ID_COLUMNS = {"item_id", "category", "responder_model", "condition"}


def kappa(matrix: list[list[str]]) -> float:
    """Fleiss' kappa for a subjects-by-raters matrix of labels."""
    if not matrix:
        return float("nan")
    table, _ = aggregate_raters(np.array(matrix))
    return float(fleiss_kappa(table))


def pairwise_agreement(votes_per_item: list[list[str]]) -> float:
    """Share of rater pairs that agree, pooled over items of any rater count."""
    agree = total = 0
    for votes in votes_per_item:
        for a, b in itertools.combinations(votes, 2):
            total += 1
            agree += a == b
    return agree / total if total else float("nan")


def subset_level(df: pd.DataFrame, judges: list[str], label_set: tuple[str, ...]) -> dict:
    """Agreement among judgments inside one label set, on items whose consensus is in it."""
    rows = df[df.consensus_loo.isin(label_set)]
    votes = [[r[j] for j in judges if r[j] in label_set] for r in rows.to_dict("records")]
    full = [v for v in votes if len(v) == len(judges)]
    unanimous = sum(1 for v in votes if v and len(set(v)) == 1)
    return {
        "items": len(votes),
        "kappa": kappa(full),
        "kappa_items": len(full),
        "observed_agreement": pairwise_agreement(votes),
        "unanimous": unanimous,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--aggregated", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    agg = pd.read_csv(args.aggregated)
    judges = [c for c in agg.columns if ":" in c and c not in ID_COLUMNS]
    steered = agg[(agg.category == CATEGORY) & (agg.condition == "steered")].dropna(subset=judges)

    raw = steered[judges].values.tolist()
    binary = [["resist" if v in RESISTANCE else "comply" for v in row] for row in raw]

    results = [
        (
            "resistance_vs_compliance",
            {"items": len(binary), "kappa": kappa(binary), "kappa_items": len(binary)},
        ),
        ("resistance_mode", subset_level(steered, judges, RESISTANCE)),
        ("compliance_mode", subset_level(steered, judges, COMPLIANCE)),
        ("five_way", {"items": len(raw), "kappa": kappa(raw), "kappa_items": len(raw)}),
    ]

    for name, r in results:
        extra = ""
        if "observed_agreement" in r:
            extra = (
                f", observed agreement {r['observed_agreement']:.3f} over {r['items']}, "
                f"{r['unanimous']} of {r['items']} unanimous"
            )
        print(f"{name:26s} kappa = {r['kappa']:.3f} over {r['kappa_items']} items{extra}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fields = ["level", "items", "kappa", "kappa_items", "observed_agreement", "unanimous"]
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for name, r in results:
                writer.writerow({"level": name, **{k: r.get(k, "") for k in fields[1:]}})
        print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
