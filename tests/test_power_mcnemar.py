"""Tests for the McNemar power calculation behind the paper's power figures."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "power_mcnemar", Path(__file__).resolve().parents[1] / "scripts" / "power_mcnemar.py"
)
power = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(power)


def test_min_discordant_at_paper_alpha() -> None:
    assert power.min_discordant(0.001) == 11


def test_min_discordant_at_conventional_alpha() -> None:
    assert power.min_discordant(0.05) == 6


@pytest.mark.parametrize(("n", "expected"), [(20, 0.0171), (50, 0.9211), (100, 1.0)])
def test_power_matches_reported_figures(n: int, expected: float) -> None:
    assert power.mcnemar_power(n, 0.30, 0.001) == pytest.approx(expected, abs=1e-4)


def test_rare_event_figure() -> None:
    assert power.chance_of_one_instance(100, 0.02) == pytest.approx(0.867, abs=1e-3)


def test_power_increases_with_sample_size() -> None:
    values = [power.mcnemar_power(n, 0.30, 0.001) for n in (20, 30, 50, 100)]
    assert values == sorted(values)


@pytest.mark.parametrize("alpha", [0.0, 1.0, -0.1])
def test_invalid_alpha_rejected(alpha: float) -> None:
    with pytest.raises(ValueError):
        power.min_discordant(alpha)
