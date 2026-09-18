#!/usr/bin/env python3
"""Reproduce the ablation results reported in the mechanism section.

For each split, the three arms (no hook, fitted direction ablated, random
direction ablated) are labeled with the study's consensus rule and compared
against the unablated arm.

Why McNemar rather than Fisher
------------------------------
Every item passes through all three arms, so the observations are paired.
Fisher's exact test compares two independent groups and discards the pairing,
which both loses power and answers a different question. McNemar uses only the
items whose label changed and asks whether the direction of change is one-sided,
which is the claim the necessity result makes.

Usage:
    python scripts/analyze_ablation.py \
        --fold RESULTS/interp/ablation_judgments:RESULTS/interp/ablation_runs.jsonl \
        --fold RESULTS/interp/ablation_judgments_fold2:RESULTS/interp/ablation_runs_fold2.jsonl \
        --responder together:meta-llama/Llama-3.3-70B-Instruct-Turbo \
        --output results/interp/ablation_rates.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from scipy.stats import binomtest

from tracekit.analysis.consensus import consensus_label

LOGGER = logging.getLogger("analyze_ablation")

ARMS = ("none", "target", "random")
POSITIVE_LABEL = "derail"
JUDGMENT_FILENAME = re.compile(r"^judge_(?P<judge>.+)_on_ablated_(?P<arm>[a-z]+)\.jsonl$")


@dataclass(frozen=True)
class ArmResult:
    """Labels and derail count for one arm of one split."""

    arm: str
    labels: dict[str, str]
    ties: int

    @property
    def positives(self) -> int:
        return sum(label == POSITIVE_LABEL for label in self.labels.values())

    @property
    def total(self) -> int:
        return len(self.labels)


def load_arm_labels(judgments_dir: Path, responder: str) -> dict[str, ArmResult]:
    """Label every item in every arm using the shared consensus rule.

    Error sidecars (``*.errors.jsonl``) are skipped: they record failed API
    calls, and the successful retry is already in the main file.
    """
    votes: dict[str, dict[str, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))

    for path in sorted(judgments_dir.glob("judge_*_on_ablated_*.jsonl")):
        if path.name.endswith(".errors.jsonl"):
            continue
        match = JUDGMENT_FILENAME.match(path.name)
        if not match:
            LOGGER.warning("Skipping unrecognized filename: %s", path.name)
            continue
        judge, arm = match.group("judge"), match.group("arm")
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("error"):
                    continue
                votes[arm][record["item_id"]][judge] = record.get("classification")

    results: dict[str, ArmResult] = {}
    for arm in ARMS:
        if arm not in votes:
            raise ValueError(f"No judgments found for arm {arm!r} in {judgments_dir}")
        labels, ties = {}, 0
        for item_id, item_votes in votes[arm].items():
            consensus = consensus_label(item_votes, responder=responder)
            labels[item_id] = consensus.label
            ties += consensus.tie
        results[arm] = ArmResult(arm=arm, labels=labels, ties=ties)

    sizes = {arm: results[arm].total for arm in ARMS}
    if len(set(sizes.values())) != 1:
        raise ValueError(
            f"Arms disagree on item count ({sizes}); comparing them would divide "
            "by different denominators."
        )
    return results


def count_identical_completions(runs_path: Path) -> dict[str, int]:
    """Count items whose intervened completion is byte-identical to the control.

    A random-direction arm that changes no text would be an inert intervention,
    and its null result would carry no information. This distinguishes "the
    hook did nothing" from "the hook changed the text but not the behavior".
    """
    digests: dict[str, dict[str, str]] = defaultdict(dict)
    with runs_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            digest = hashlib.sha256(record["completion"].encode("utf-8")).hexdigest()
            digests[record["arm"]][record["item_id"]] = digest

    identical = {}
    for arm in ("target", "random"):
        identical[arm] = sum(
            digests["none"].get(item) == digest for item, digest in digests.get(arm, {}).items()
        )
    return identical


def mcnemar(baseline: ArmResult, intervened: ArmResult) -> tuple[int, int, float | None]:
    """Return (suppressed, induced, exact p) for one paired comparison.

    ``suppressed`` counts items that derailed in the baseline arm and did not
    under the intervention; ``induced`` counts the reverse. Concordant items
    carry no information about the intervention and are excluded by design. The
    p-value is undefined when nothing changed, which is reported as None rather
    than as 1.0, since no discordant pairs is a stronger statement than a
    non-significant test.
    """
    shared = set(baseline.labels) & set(intervened.labels)
    suppressed = sum(
        baseline.labels[i] == POSITIVE_LABEL and intervened.labels[i] != POSITIVE_LABEL
        for i in shared
    )
    induced = sum(
        baseline.labels[i] != POSITIVE_LABEL and intervened.labels[i] == POSITIVE_LABEL
        for i in shared
    )
    if suppressed + induced == 0:
        return suppressed, induced, None
    p = binomtest(suppressed, suppressed + induced, 0.5).pvalue
    return suppressed, induced, p


def analyze(fold_specs: list[str], responder: str, output: Path | None) -> int:
    rows = []
    for index, spec in enumerate(fold_specs, start=1):
        judgments_dir, runs_path = (Path(part) for part in spec.split(":", 1))
        arms = load_arm_labels(judgments_dir, responder)
        identical = count_identical_completions(runs_path)

        print(f"\n== split {index} ({judgments_dir.name}) ==")
        for arm in ARMS:
            result = arms[arm]
            print(
                f"  {arm:7s} {result.positives:3d}/{result.total:<3d} "
                f"= {result.positives / result.total:.3f}  ties={result.ties}"
            )
        for arm in ("target", "random"):
            suppressed, induced, p = mcnemar(arms["none"], arms[arm])
            p_text = "n/a (no discordant pairs)" if p is None else f"{p:.3g}"
            print(
                f"  {arm} vs none: {suppressed} suppressed, {induced} induced, "
                f"p={p_text}; identical completions {identical[arm]}/"
                f"{arms[arm].total}"
            )
            rows.append(
                {
                    "split": index,
                    "arm": arm,
                    "baseline_positives": arms["none"].positives,
                    "arm_positives": arms[arm].positives,
                    "total": arms[arm].total,
                    "suppressed": suppressed,
                    "induced": induced,
                    "p_mcnemar": "" if p is None else f"{p:.6g}",
                    "identical_completions": identical[arm],
                    "ties_baseline": arms["none"].ties,
                    "ties_arm": arms[arm].ties,
                }
            )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fold",
        action="append",
        required=True,
        metavar="JUDGMENTS_DIR:RUNS_JSONL",
        help="One per split; repeat the flag for the second split.",
    )
    parser.add_argument(
        "--responder",
        required=True,
        help="Model that generated the arms; its own judgment is excluded.",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    return analyze(args.fold, args.responder, args.output)


if __name__ == "__main__":
    sys.exit(main())
