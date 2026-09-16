"""
Compare derail labels between the main study (hosted API, no truncation) and
the ablation control arm (local weights, 500-token budget) on the same items.

Purpose: settle by inspection whether the token budget changed what judges
called a derail, rather than arguing it from the definition.

Writes a readable side-by-side of every item where the two disagree.

Usage:
    python scripts/compare_derail_labels.py
    python scripts/compare_derail_labels.py --all   # dump every eval item
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
from pathlib import Path

RESPONDER = "together:meta-llama/Llama-3.3-70B-Instruct-Turbo"
CATEGORY = "values_conflict_low"
MAIN_RESULTS = Path(
    "results/steerability_v2_together_meta-llama_Llama-3.3-70B-Instruct-Turbo.jsonl"
)
ABL_RUNS = Path("results/interp/ablation_runs.jsonl")
ABL_JUDGMENTS = "results/interp/ablation_judgments/judge_*_on_ablated_none.jsonl"
AGG = Path("results/judgments/aggregated_judgments.csv")
OUT = Path("results/interp/derail_label_comparison.txt")


def main_study_labels() -> dict[str, str]:
    """consensus_loo per item for Llama, values-conflict, base condition."""
    import csv

    out: dict[str, str] = {}
    with AGG.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (
                row["responder_model"] == RESPONDER
                and row["category"] == CATEGORY
                and row["condition"] == "base"
            ):
                out[row["item_id"]] = row["consensus_loo"]
    return out


def ablation_labels() -> dict[str, str]:
    """Majority label across the six judges for the no-intervention arm."""
    votes: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for path in glob.glob(ABL_JUDGMENTS):
        judge = os.path.basename(path)
        for line in open(path, encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("classification"):
                votes[rec["item_id"]][judge] = rec["classification"]
    labels: dict[str, str] = {}
    for item, v in votes.items():
        counts = collections.Counter(v.values()).most_common()
        if len(counts) > 1 and counts[0][1] == counts[1][1]:
            labels[item] = "TIE"
        else:
            labels[item] = counts[0][0]
    return labels


def main_study_text() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in open(MAIN_RESULTS, encoding="utf-8"):
        rec = json.loads(line)
        if (rec.get("extra") or {}).get("category") != CATEGORY:
            continue
        out[rec["item_id"]] = (rec.get("raw_completions") or [""])[0]
    return out


def ablation_text() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for line in open(ABL_RUNS, encoding="utf-8"):
        rec = json.loads(line)
        if rec["arm"] == "none":
            out[rec["item_id"]] = (rec["completion"], rec["finish_reason"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--all", action="store_true", help="Dump every eval item, not just disagreements."
    )
    args = ap.parse_args()

    main_lab, abl_lab = main_study_labels(), ablation_labels()
    main_txt, abl_txt = main_study_text(), ablation_text()

    shared = sorted(set(abl_lab) & set(main_lab))
    print(f"Eval items with labels on both sides: {len(shared)}")

    m_derail = [i for i in shared if main_lab[i] == "derail"]
    a_derail = [i for i in shared if abl_lab[i] == "derail"]
    print(f"  main study : {len(m_derail)} derail")
    print(f"  ablation   : {len(a_derail)} derail")

    only_main = [i for i in shared if main_lab[i] == "derail" and abl_lab[i] != "derail"]
    only_abl = [i for i in shared if abl_lab[i] == "derail" and main_lab[i] != "derail"]
    print(f"  derail in main only     : {len(only_main)}  {only_main}")
    print(f"  derail in ablation only : {len(only_abl)}  {only_abl}")
    print(f"  agree on label          : {sum(1 for i in shared if main_lab[i] == abl_lab[i])}")

    to_dump = shared if args.all else (only_main + only_abl)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for item in to_dump:
            a_text, a_finish = abl_txt.get(item, ("", ""))
            f.write("=" * 78 + "\n")
            f.write(f"{item}   main={main_lab[item]}   ablation={abl_lab[item]}\n")
            f.write("=" * 78 + "\n\n")
            f.write(f"--- MAIN STUDY (hosted API, no truncation) ---\n{main_txt.get(item, '')}\n\n")
            f.write(f"--- ABLATION CONTROL (local, 500 cap, finish={a_finish}) ---\n{a_text}\n\n\n")
    print(f"\nWrote {len(to_dump)} item(s) to {OUT}")


if __name__ == "__main__":
    main()
