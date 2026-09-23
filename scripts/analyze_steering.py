#!/usr/bin/env python3
"""Regenerate the steering-sweep rates under the study's consensus rule.

Replaces the rates in ``results/interp/steering_rates.csv`` and
``results/interp/steering_rates_per_item.csv``. The earlier versions counted all
six judges and dropped items with no majority, which produced denominators below
the item count and made the sweep incomparable with the main study.

The steered conditions are renamed pseudo-responders, so the leave-one-out
exclusion in the judging pipeline does not fire on its own. The generating model
must be passed explicitly with --responder or the generating model ends up
judging its own output.

Usage:
    python scripts/analyze_steering.py \
        --judgments-dir results/interp/judgments \
        --responder together:meta-llama/Llama-3.3-70B-Instruct-Turbo \
        --rates-output results/interp/steering_rates.csv \
        --per-item-output results/interp/steering_rates_per_item.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

from scipy.stats import binomtest

from tracekit.analysis.consensus import consensus_label

LOGGER = logging.getLogger("analyze_steering")

POSITIVE_LABEL = "derail"
JUDGMENT_FILENAME = re.compile(
    r"^judge_(?P<judge>.+)_on_steered_L(?P<layer>\d+)_alpha(?P<alpha>[+-]?\d+(?:\.\d+)?)\.jsonl$"
)


def load_votes(
    judgments_dir: Path,
) -> tuple[dict[float, dict[str, dict[str, str]]], set[int]]:
    """Collect per-alpha, per-item judge votes and the layers encountered."""
    votes: dict[float, dict[str, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    layers: set[int] = set()

    for path in sorted(judgments_dir.glob("judge_*_on_steered_L*_alpha*.jsonl")):
        if path.name.endswith(".errors.jsonl"):
            continue
        match = JUDGMENT_FILENAME.match(path.name)
        if not match:
            LOGGER.warning("Skipping unrecognized filename: %s", path.name)
            continue
        judge = match.group("judge")
        alpha = float(match.group("alpha"))
        layers.add(int(match.group("layer")))
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("error"):
                    continue
                votes[alpha][record["item_id"]][judge] = record.get("classification")

    if not votes:
        raise ValueError(f"No steering judgments found in {judgments_dir}")
    return votes, layers


def analyze(
    judgments_dir: Path,
    responder: str,
    rates_output: Path | None,
    per_item_output: Path | None,
) -> int:
    votes, layers = load_votes(judgments_dir)
    if len(layers) > 1:
        raise ValueError(
            f"Judgments span multiple layers {sorted(layers)}; pooling them would "
            "mix interventions."
        )

    labels_by_alpha = {}
    per_item_rows, counts = [], {}
    for alpha in sorted(votes):
        positives = ties = 0
        for item_id, item_votes in sorted(votes[alpha].items()):
            consensus = consensus_label(item_votes, responder=responder)
            positives += consensus.label == POSITIVE_LABEL
            ties += consensus.tie
            per_item_rows.append(
                {
                    "alpha": alpha,
                    "item_id": item_id,
                    "consensus": consensus.label,
                    "n_judges": consensus.n_judges,
                    "tie": int(consensus.tie),
                }
            )
        counts[alpha] = (positives, len(votes[alpha]), ties)
        labels_by_alpha[alpha] = {
            row["item_id"]: row["consensus"] for row in per_item_rows if row["alpha"] == alpha
        }

    totals = {total for _, total, _ in counts.values()}
    if len(totals) != 1:
        raise ValueError(
            f"Conditions disagree on item count ({counts}); rates would not be "
            "comparable across the sweep."
        )

    if 0.0 not in counts:
        raise ValueError("No alpha=0 control condition found; cannot test against it.")
    control_positives, control_total, _ = counts[0.0]

    rates_rows = []
    print(f"{'alpha':>8} {'derail':>9} {'rate':>7} {'p vs 0':>12} {'ties':>5}")
    for alpha in sorted(counts):
        positives, total, ties = counts[alpha]
        if alpha == 0.0:
            p_text, p_value = "---", ""
        else:
            # Paired: the same items run under every alpha, so the test uses
            # only the items whose label changed against the control.
            control = labels_by_alpha[0.0]
            here = labels_by_alpha[alpha]
            shared = control.keys() & here.keys()
            gained = sum(here[i] == POSITIVE_LABEL and control[i] != POSITIVE_LABEL for i in shared)
            lost = sum(here[i] != POSITIVE_LABEL and control[i] == POSITIVE_LABEL for i in shared)
            if gained + lost:
                p_value = binomtest(gained, gained + lost, 0.5).pvalue
                p_text = f"{p_value:.3g}"
                p_value = f"{p_value:.6g}"
            else:
                p_text, p_value = "n/a", ""
        print(
            f"{alpha:>+8.0f} {positives:>4}/{total:<4} {positives / total * 100:6.0f}% "
            f"{p_text:>12} {ties:>5}"
        )
        rates_rows.append(
            {
                "alpha": alpha,
                "layer": sorted(layers)[0],
                "derail_count": positives,
                "total": total,
                "rate": f"{positives / total:.4f}",
                "p_vs_control_mcnemar": p_value,
                "ties": ties,
            }
        )

    for path, rows in ((rates_output, rates_rows), (per_item_output, per_item_rows)):
        if not path:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judgments-dir", type=Path, required=True)
    parser.add_argument(
        "--responder",
        required=True,
        help="Model that generated the steered responses; excluded from consensus.",
    )
    parser.add_argument("--rates-output", type=Path, default=None)
    parser.add_argument("--per-item-output", type=Path, default=None)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    return analyze(args.judgments_dir, args.responder, args.rates_output, args.per_item_output)


if __name__ == "__main__":
    sys.exit(main())
