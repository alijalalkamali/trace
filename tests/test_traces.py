"""Tests for the reasoning-trace rubric and reasoning extraction."""

from __future__ import annotations

import pytest

from tracekit.judging.judge_output import JudgeOutputError, parse_judge_output
from tracekit.judging.reasoning_values_trace_rubric import REASONING_VALUES_TRACE_RUBRIC as R
from tracekit.judging.rubrics import ALL_RUBRICS
from tracekit.judging.traces import MissingReasoningError, extract_reasoning


class TestTraceRubric:
    def test_category_name(self) -> None:
        assert R.category == "reasoning_values_suppress_trace"

    def test_not_registered_with_scored_rubrics(self) -> None:
        """Kept out of ALL_RUBRICS so the main pipeline can never route to it."""
        assert R.category not in ALL_RUBRICS

    def test_three_logical_cases(self) -> None:
        assert R.labels == (
            "concern-absent",
            "concern-set-aside",
            "concern-objected",
        )

    def test_every_label_has_a_description(self) -> None:
        assert set(R.label_descriptions) == set(R.labels)

    def test_core_rubrics_unchanged(self) -> None:
        """Adding the trace rubric must not alter any rubric the study scored."""
        suppress = ALL_RUBRICS["reasoning_values_suppress"]
        assert "concern-absent" not in suppress.labels
        assert len(suppress.labels) == 6

    def test_judge_output_validates_against_trace_labels(self) -> None:
        raw = (
            '{"classification": "concern-objected", "justification": "x", '
            '"cited_text": "y", "confidence": "high"}'
        )
        assert parse_judge_output(raw, R).classification == "concern-objected"

    def test_core_label_rejected_by_trace_rubric(self) -> None:
        raw = (
            '{"classification": "clean-suppression", "justification": "x", '
            '"cited_text": "y", "confidence": "high"}'
        )
        with pytest.raises(JudgeOutputError):
            parse_judge_output(raw, R)


class TestExtractReasoning:
    def test_returns_reasoning_without_the_answer(self) -> None:
        text = "<thinking>\nthe user asked me not to moralize\n</thinking>\nHere is the plan."
        assert extract_reasoning(text) == "the user asked me not to moralize"

    def test_tag_match_is_case_insensitive(self) -> None:
        assert extract_reasoning("<THINKING>a</THINKING> b") == "a"

    def test_multiline_reasoning_preserved(self) -> None:
        assert extract_reasoning("<thinking>a\nb\nc</thinking>") == "a\nb\nc"

    def test_only_first_block_returned(self) -> None:
        assert extract_reasoning("<thinking>a</thinking> x <thinking>b</thinking>") == "a"

    def test_missing_block_raises(self) -> None:
        with pytest.raises(MissingReasoningError, match="No <thinking>"):
            extract_reasoning("Just an answer.")

    def test_empty_block_raises(self) -> None:
        """An empty trace must not be judged as concern-absent."""
        with pytest.raises(MissingReasoningError, match="empty"):
            extract_reasoning("<thinking>   </thinking> answer")

    def test_unclosed_block_raises(self) -> None:
        with pytest.raises(MissingReasoningError):
            extract_reasoning("<thinking> never closed")
