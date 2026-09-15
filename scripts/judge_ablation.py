"""
Judge the directional-ablation run: every judge x every arm.

Wraps tracekit.judging.run_judges unchanged, exactly as judge_steering_sweep.py
does. Each arm is a pseudo-responder file produced by
tracekit.interp.convert_ablation, judged in the BASE condition only -- the
ablation generations answer base prompts and the intervention lives in
activation space, so the base rubric is the right comparison (derail rate per
arm vs. the no-intervention control).

Total calls: 6 judges x 3 arms x 50 items = 900 judgments.

Resumable exactly like the main pipeline: rerun after any quota abort and only
missing or failed judgments are re-attempted.

Usage:
    python scripts/judge_ablation.py \
        --results-dir results \
        --items-path data/steerability_items_v3.jsonl \
        --output-dir results/interp/ablation_judgments
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from tracekit.judging.run_judges import FatalJudgeError, run_judge_on_responder

JUDGES = (
    "anthropic:claude-opus-4-7",
    "deepseek:deepseek-reasoner",
    "google:gemini-2.5-pro",
    "openai:gpt-5",
    "together:Qwen/Qwen3.7-Max",
    "together:meta-llama/Llama-3.3-70B-Instruct-Turbo",
)

ARM_FILE_RE = re.compile(r"steerability_v2_ablated_([A-Za-z0-9_.+-]+)\.jsonl")


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--items-path", type=Path, default=Path("data/steerability_items_v3.jsonl"))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results/interp/ablation_judgments")
    )
    parser.add_argument(
        "--judges",
        nargs="*",
        default=list(JUDGES),
        help="Subset of judges to run (default: all six).",
    )
    args = parser.parse_args()

    arm_files = sorted(args.results_dir.glob("steerability_v2_ablated_*.jsonl"))
    if not arm_files:
        raise SystemExit(
            f"No ablation arm files found under {args.results_dir} -- run "
            f"tracekit.interp.convert_ablation first."
        )
    print(f"{len(arm_files)} arm file(s), {len(args.judges)} judge(s).")

    aborted: list[tuple[str, str]] = []
    for judge in args.judges:
        for arm_path in arm_files:
            m = ARM_FILE_RE.fullmatch(arm_path.name)
            if not m:
                raise SystemExit(f"Unparseable arm filename: {arm_path.name}")
            responder = f"ablated:{m.group(1)}"
            out_path = args.output_dir / f"judge_{_slug(judge)}_on_{_slug(responder)}.jsonl"
            try:
                run_judge_on_responder(
                    judge_model_name=judge,
                    responder_model_name=responder,
                    items_path=args.items_path,
                    responder_results_path=arm_path,
                    output_path=out_path,
                    conditions=("base",),
                    error_log_path=out_path.with_suffix(".errors.jsonl"),
                )
            except FatalJudgeError:
                aborted.append((judge, responder))
                # Fatal for this judge across ALL arms (quota/auth) -- skip its
                # remaining arms; rerun the script later to resume.
                print(f"Skipping remaining arms for judge {judge}.")
                break

    if aborted:
        print("\nAborted sections (rerun this script to resume):")
        for j, r in aborted:
            print(f"  {j} on {r}")
    else:
        print("\nAll judge x arm sections complete.")


if __name__ == "__main__":
    main()
