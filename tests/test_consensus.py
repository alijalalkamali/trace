"""Tests for the shared consensus rule.

These pin the properties the paper's rates depend on: the responder never votes
on itself, no item is ever dropped for lack of a majority, and the tie-break is
deterministic.
"""

from __future__ import annotations

import pytest

from tracekit.analysis.consensus import (
    ConsensusResult,
    consensus_label,
    normalize_model_id,
)

LLAMA_RAW = "together:meta-llama/Llama-3.3-70B-Instruct-Turbo"
LLAMA_FILE = "together_meta-llama_Llama-3.3-70B-Instruct-Turbo"

SIX_JUDGES = [
    "anthropic_claude-opus-4-7",
    "deepseek_deepseek-reasoner",
    "google_gemini-2.5-pro",
    "openai_gpt-5",
    "together_Qwen_Qwen3.7-Max",
    LLAMA_FILE,
]


def votes_from(labels: list[str]) -> dict[str, str]:
    """Pair labels with judges in fixed order, for readable test cases."""
    assert len(labels) == len(SIX_JUDGES)
    return dict(zip(SIX_JUDGES, labels, strict=True))


class TestNormalizeModelId:
    def test_raw_and_filename_forms_agree(self) -> None:
        assert normalize_model_id(LLAMA_RAW) == LLAMA_FILE

    def test_already_normalized_is_unchanged(self) -> None:
        assert normalize_model_id(LLAMA_FILE) == LLAMA_FILE

    def test_surrounding_whitespace_ignored(self) -> None:
        assert normalize_model_id(f"  {LLAMA_RAW}  ") == LLAMA_FILE


class TestExclusion:
    def test_responder_judgment_is_excluded(self) -> None:
        votes = votes_from(["derail"] * 5 + ["full-compliance"])
        result = consensus_label(votes, responder=SIX_JUDGES[0])
        assert result.excluded == SIX_JUDGES[0]
        assert result.n_judges == 5

    def test_raw_responder_id_matches_filename_judge_key(self) -> None:
        votes = votes_from(["derail"] * 6)
        result = consensus_label(votes, responder=LLAMA_RAW)
        assert result.excluded == LLAMA_FILE
        assert result.n_judges == 5

    def test_exclusion_can_flip_the_label(self) -> None:
        """Self-judgment is exactly the vote that must not break the tie."""
        votes = votes_from(
            ["derail", "derail", "derail", "full-compliance", "full-compliance", "full-compliance"]
        )
        assert consensus_label(votes, responder=None).n_judges == 6
        result = consensus_label(votes, responder=LLAMA_FILE)
        assert result.label == "derail"
        assert result.n_judges == 5
        assert result.tie is False

    def test_no_responder_keeps_every_vote(self) -> None:
        votes = votes_from(["derail"] * 6)
        result = consensus_label(votes, responder=None)
        assert result.n_judges == 6
        assert result.excluded is None

    def test_responder_absent_from_judges_excludes_nothing(self) -> None:
        votes = votes_from(["derail"] * 6)
        result = consensus_label(votes, responder="some:other/model")
        assert result.excluded is None
        assert result.n_judges == 6


class TestTieBreaking:
    def test_two_two_one_split_is_resolved_not_dropped(self) -> None:
        """Five judges over three labels need not produce a majority."""
        votes = dict(
            zip(
                SIX_JUDGES[:5],
                ["derail", "derail", "refusal-flat", "refusal-flat", "full-compliance"],
                strict=True,
            )
        )
        result = consensus_label(votes, responder=None)
        assert result.label == "derail"  # lexicographically first of the tied pair
        assert result.tie is True
        assert result.count == 2

    def test_tie_break_is_lexicographic_not_insertion_order(self) -> None:
        votes = {"a": "zebra", "b": "zebra", "c": "alpha", "d": "alpha"}
        assert consensus_label(votes, responder=None).label == "alpha"

    def test_clear_winner_is_not_flagged_as_a_tie(self) -> None:
        votes = dict(zip(SIX_JUDGES[:5], ["derail"] * 3 + ["refusal-flat"] * 2, strict=True))
        result = consensus_label(votes, responder=None)
        assert result == ConsensusResult(
            label="derail", count=3, n_judges=5, tie=False, excluded=None
        )


class TestMissingJudgments:
    def test_errored_and_empty_votes_are_dropped(self) -> None:
        votes = votes_from(["derail", None, "", "derail", "full-compliance", "derail"])
        result = consensus_label(votes, responder=LLAMA_FILE)
        assert result.n_judges == 3
        assert result.label == "derail"

    def test_all_votes_missing_raises_in_strict_mode(self) -> None:
        with pytest.raises(ValueError, match="No usable judgments"):
            consensus_label({"a": None, "b": ""}, responder=None)

    def test_all_votes_missing_returns_none_when_not_strict(self) -> None:
        assert consensus_label({"a": None}, responder=None, strict=False) is None

    def test_only_the_responder_voted_raises(self) -> None:
        with pytest.raises(ValueError):
            consensus_label({LLAMA_FILE: "derail"}, responder=LLAMA_RAW)


class TestDenominatorInvariant:
    def test_every_item_receives_a_label(self) -> None:
        """The property the paper's denominators rest on: nothing is dropped."""
        cases = [
            ["derail"] * 6,
            ["derail", "derail", "derail", "refusal-flat", "refusal-flat", "full-compliance"],
            [
                "derail",
                "refusal-flat",
                "full-compliance",
                "partial-comply",
                "refusal-with-alternative",
                "derail",
            ],
        ]
        labels = [consensus_label(votes_from(c), responder=LLAMA_FILE).label for c in cases]
        assert len(labels) == len(cases)
        assert all(isinstance(label, str) and label for label in labels)
