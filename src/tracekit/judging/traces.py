"""Extraction of a responder's reasoning from its saved output.

Reasoning-model backends prepend the model's reasoning to its answer inside a
``<thinking>...</thinking>`` block (see tracekit.models and the matching
stripping logic in tracekit.judging.judge_output). For DeepSeek-R1 that block
is the model's visible chain of thought, which is what the reasoning-trace
rubric classifies.

Only the reasoning is passed to judges, not the answer after it. The question
is what the reasoning contains; the answer is already labeled by the main
suppression rubric, and showing it would let the judges' reading of the answer
leak into their reading of the reasoning.
"""

from __future__ import annotations

import re

__all__ = ["MissingReasoningError", "extract_reasoning"]

_THINKING_BLOCK = re.compile(r"<thinking>(.*?)</thinking>", re.DOTALL | re.IGNORECASE)


class MissingReasoningError(ValueError):
    """The saved output has no usable reasoning block."""


def extract_reasoning(response: str) -> str:
    """Return the text of the first reasoning block in a saved response.

    Args:
        response: A responder's full saved output, reasoning then answer.

    Returns:
        The reasoning text with surrounding whitespace removed.

    Raises:
        MissingReasoningError: If the response has no ``<thinking>`` block, or
            the block is empty. Raised rather than returning an empty string,
            because judging an empty trace would silently record every such
            item as "concern-absent" and inflate that count.
    """
    match = _THINKING_BLOCK.search(response)
    if match is None:
        raise MissingReasoningError("No <thinking>...</thinking> block in response.")
    reasoning = match.group(1).strip()
    if not reasoning:
        raise MissingReasoningError("The <thinking> block is empty.")
    return reasoning
