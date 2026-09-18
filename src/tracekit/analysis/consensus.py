"""Single definition of the consensus label used for every rate in the study.

Why this module exists
----------------------
The consensus rule was originally implemented twice: once in the main judging
pipeline (exclude the responder's own judgment, break ties lexicographically)
and once, implicitly, in the intervention analyses (count all six judges, drop
items with no majority). The two implementations disagreed, which showed up as
denominators below the item count in the steering and ablation tables while the
main study reported denominators of exactly 100.

One definition, one implementation, called from every analysis path. Any change
to the rule happens here and propagates everywhere, which is the only way to
keep the paper's rates mutually comparable.

The rule
--------
1. Drop judgments that errored or carry no classification.
2. Exclude the responding model's judgment of its own output. Self-judgment is
   excluded so that self-preference remains measurable rather than absorbed
   into the ground truth.
3. Take the most frequent remaining label.
4. Break ties by lexicographic order of the label string.

Step 4 is deterministic rather than principled: with five judges and three or
more labels a 2-2-1 split has no majority, and an arbitrary but reproducible
choice is preferable to dropping the item, which would make denominators depend
on judge disagreement.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

__all__ = [
    "ConsensusResult",
    "consensus_label",
    "normalize_model_id",
]

_NON_FILENAME_CHARS = re.compile(r"[:/]")


def normalize_model_id(model_id: str) -> str:
    """Return the filename-safe form of a provider-qualified model id.

    Judgment files are named after the judge with ``:`` and ``/`` replaced by
    ``_`` (``together:meta-llama/Llama-3.3-70B-Instruct-Turbo`` becomes
    ``together_meta-llama_Llama-3.3-70B-Instruct-Turbo``). Responder ids are
    carried in the raw form. Comparing the two requires normalizing both, or
    the responder is silently never excluded and the consensus quietly reverts
    to counting all six judges.
    """
    return _NON_FILENAME_CHARS.sub("_", model_id.strip())


@dataclass(frozen=True)
class ConsensusResult:
    """Outcome of applying the consensus rule to one response.

    Attributes:
        label: The winning label.
        count: Votes the winning label received.
        n_judges: Judges whose votes were counted, after exclusions.
        tie: True when at least two labels shared the top count and the winner
            was chosen lexicographically. Reported so analyses can quantify how
            often the deterministic tie-break was load-bearing.
        excluded: The judge excluded as the responder, or None.
    """

    label: str
    count: int
    n_judges: int
    tie: bool
    excluded: str | None


def consensus_label(
    votes: Mapping[str, str | None],
    responder: str | None = None,
    *,
    strict: bool = True,
) -> ConsensusResult | None:
    """Apply the study's consensus rule to one response's judgments.

    Args:
        votes: Mapping of judge id to the label that judge assigned. Entries
            whose value is None or empty are treated as missing and dropped,
            which is how errored judgments are represented upstream.
        responder: Id of the model that produced the response, in either raw or
            filename-normalized form. Its judgment is excluded. Pass None when
            the responder is not among the judges, as for a pseudo-responder
            such as an ablation arm, in which case nothing is excluded.
        strict: When True, raise if no votes remain. When False, return None.

    Returns:
        A ConsensusResult, or None when no votes remain and strict is False.

    Raises:
        ValueError: If no usable votes remain and strict is True.

    Note:
        The responder is excluded by id, not by output. An intervention run
        whose generations come from Llama must pass Llama's id even though the
        pseudo-responder is named something else, or Llama ends up judging its
        own output and the rate is no longer leave-one-out.
    """
    excluded: str | None = None
    counted: dict[str, str] = {}

    normalized_responder = normalize_model_id(responder) if responder else None
    for judge, label in votes.items():
        if label is None or not str(label).strip():
            continue
        if normalized_responder and normalize_model_id(judge) == normalized_responder:
            excluded = judge
            continue
        counted[judge] = str(label)

    if not counted:
        if strict:
            raise ValueError(
                f"No usable judgments remain (responder={responder!r}, " f"votes={dict(votes)!r})."
            )
        return None

    tally = Counter(counted.values())
    top_count = max(tally.values())
    winners = sorted(label for label, n in tally.items() if n == top_count)

    return ConsensusResult(
        label=winners[0],
        count=top_count,
        n_judges=len(counted),
        tie=len(winners) > 1,
        excluded=excluded,
    )
