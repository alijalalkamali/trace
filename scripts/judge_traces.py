#!/usr/bin/env python3
"""Judge DeepSeek-R1's steered reasoning traces with the reasoning-trace rubric.

DeepSeek-R1 is the only evaluated model whose saved output includes its
reasoning. On steered reasoning-suppression items it complies on every item,
so the question here is whether its reasoning still raises the values concern
the instruction told it to leave out. Each of the 100 traces is classified by
the five other models under REASONING_TRACE_RUBRIC.

Design choices, and why:
    - DeepSeek does not judge its own traces. Self-judgment is excluded from
      every consensus label in the study, and here it is excluded at the
      source rather than dropped afterward, so no call is spent on it.
    - Judges see the full response, reasoning and answer, since the finding
      is the gap between the two. Every response is first checked for a
      reasoning block, so none is judged without one.
    - The item context field is omitted by default. For these items it states
      the study's hypothesis that values reasoning leaks through suppression,
      which is close to the exact question being asked here, so showing it
      would prime the judges toward finding the concern. The main pipeline's
      control experiment measured that field's influence as largest on this
      category. Pass --include-item-context to reproduce the main pipeline's
      prompt instead.
    - Output files follow the main pipeline's schema and naming, so the same
      JSONL readers and the same resume logic apply.

Usage:
    python scripts/judge_traces.py \\
        --items-path data/steerability_items_v3.jsonl \\
        --results-path results/steerability_v2_deepseek_deepseek-reasoner.jsonl \\
        --output-dir results/traces/judgments
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from tracekit.analysis.consensus import normalize_model_id
from tracekit.io.dataset import EvalResult, SteerabilityItem
from tracekit.io.jsonl import read_jsonl, write_jsonl
from tracekit.judging.judge_prompt import build_judge_prompt
from tracekit.judging.reasoning_values_trace_rubric import REASONING_VALUES_TRACE_RUBRIC
from tracekit.judging.run_judges import (
    FatalJudgeError,
    JudgmentRecord,
    _call_judge_with_retry,
)
from tracekit.judging.traces import MissingReasoningError, extract_reasoning
from tracekit.models.loader import load_model

LOGGER = logging.getLogger("judge_traces")

RESPONDER = "deepseek:deepseek-reasoner"
SOURCE_CATEGORY = "reasoning_values_suppress"
TRACE_CATEGORY = "reasoning_values_suppress_trace"
CONDITION = "steered"
STEERED_INDEX = 1  # raw_completions = [base, steered]

DEFAULT_JUDGES = (
    "anthropic:claude-opus-4-7",
    "openai:gpt-5",
    "google:gemini-2.5-pro",
    "together:Qwen/Qwen3.7-Max",
    "together:meta-llama/Llama-3.3-70B-Instruct-Turbo",
)

CHECKPOINT_EVERY = 10


def load_traces(items_path: Path, results_path: Path) -> list[tuple[SteerabilityItem, str]]:
    """Pair each steered suppression item with DeepSeek's full response.

    Fails before any judge is called if a trace is missing, so a partial run
    never mixes judged and unjudgeable items.
    """
    items = {item.id: item for item in read_jsonl(items_path, SteerabilityItem)}
    pairs: list[tuple[SteerabilityItem, str]] = []
    missing: list[str] = []

    for result in read_jsonl(results_path, EvalResult):
        item = items.get(result.item_id)
        if item is None or item.category != SOURCE_CATEGORY:
            continue
        if len(result.raw_completions) <= STEERED_INDEX:
            missing.append(f"{result.item_id} (no steered completion)")
            continue
        response = result.raw_completions[STEERED_INDEX]
        try:
            extract_reasoning(response)  # presence check only
            pairs.append((item, response))
        except MissingReasoningError as exc:
            missing.append(f"{result.item_id} ({exc})")

    if missing:
        raise SystemExit(
            f"{len(missing)} trace(s) could not be extracted; resolve before judging:\n  "
            + "\n  ".join(missing)
        )
    if not pairs:
        raise SystemExit(f"No {SOURCE_CATEGORY} items found in {results_path}")
    return sorted(pairs, key=lambda pair: pair[0].id)


def judge_output_path(output_dir: Path, judge: str) -> Path:
    """Match the main pipeline's naming so the .gitignore rule applies."""
    return output_dir / f"judge_{normalize_model_id(judge)}_on_deepseek_traces.jsonl"


def already_judged(path: Path) -> list[JudgmentRecord]:
    """Successful prior records only, so failed rows are re-attempted."""
    if not path.exists():
        return []
    return [
        record
        for record in read_jsonl(path, JudgmentRecord)
        if record.classification.strip() and not record.error
    ]


def run_judge(
    judge_name: str,
    traces: list[tuple[SteerabilityItem, str]],
    output_dir: Path,
    include_item_context: bool,
) -> tuple[int, int]:
    """Judge every trace with one model. Returns (new_successes, new_errors)."""
    rubric = REASONING_VALUES_TRACE_RUBRIC
    path = judge_output_path(output_dir, judge_name)
    kept = already_judged(path)
    done = {record.item_id for record in kept}
    todo = [(item, response) for item, response in traces if item.id not in done]

    LOGGER.info("%s: %d of %d already judged", judge_name, len(done), len(traces))
    if not todo:
        return 0, 0

    judge = load_model(judge_name)
    new_records: list[JudgmentRecord] = []

    def persist() -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_jsonl(path, kept + new_records)

    for index, (item, response) in enumerate(todo, start=1):
        prompt = build_judge_prompt(
            rubric=rubric,
            item_base_prompt=item.base_prompt,
            item_steering_instruction=item.steering_instruction,
            response_to_judge=response,
            condition=CONDITION,
            expected_behavior_change=item.expected_behavior_change,
            include_expected_behavior_change=include_item_context,
        )
        record = JudgmentRecord(
            item_id=item.id,
            category=TRACE_CATEGORY,
            responder_model=RESPONDER,
            condition=CONDITION,
            judge_model=judge_name,
        )
        try:
            raw, parsed = _call_judge_with_retry(judge, prompt, rubric)
            record.raw_output = raw
            if parsed is None:
                record.error = "parse_failed_after_retries"
            else:
                record.classification = parsed["classification"]
                record.justification = parsed["justification"]
                record.cited_text = parsed["cited_text"]
                record.confidence = parsed["confidence"]
        except FatalJudgeError:
            persist()
            raise
        except Exception as exc:  # transient API failure: record and move on
            record.error = f"call_failed: {exc!r}"

        new_records.append(record)
        if index % CHECKPOINT_EVERY == 0 or index == len(todo):
            persist()
            LOGGER.info("%s: %d/%d", judge_name, index, len(todo))

    errors = sum(1 for record in new_records if record.error)
    return len(new_records) - errors, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--items-path", type=Path, required=True)
    parser.add_argument("--results-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--judges", nargs="+", default=list(DEFAULT_JUDGES))
    parser.add_argument(
        "--include-item-context",
        action="store_true",
        help="Show judges the item context field, as the main pipeline does.",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    judges = [j for j in args.judges if normalize_model_id(j) != normalize_model_id(RESPONDER)]
    if len(judges) != len(args.judges):
        LOGGER.warning("Dropped %s from judges: a model does not judge its own traces.", RESPONDER)

    traces = load_traces(args.items_path, args.results_path)
    LOGGER.info("Loaded %d steered traces from %s", len(traces), args.results_path.name)

    failed_judges = []
    for judge_name in judges:
        try:
            ok, errors = run_judge(judge_name, traces, args.output_dir, args.include_item_context)
            LOGGER.info("%s: %d new judgments, %d errors", judge_name, ok, errors)
        except FatalJudgeError as exc:
            LOGGER.error("%s aborted (progress saved): %s", judge_name, exc)
            failed_judges.append(judge_name)

    if failed_judges:
        LOGGER.error("Rerun to resume: %s", ", ".join(failed_judges))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
