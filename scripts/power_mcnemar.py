#!/usr/bin/env python3
"""Exact power of McNemar's test for the sample sizes used in the study.

Reproduces the power figures in the Statistical Analysis section. The design
case is one model showing a behavior at 30% and another at 0%. Every item
where they differ then runs in one direction, so the test is significant once
the number of discordant items k satisfies 2 * 0.5**k <= alpha. With items
independent, k follows Binomial(n, 0.30), and power is P(k >= k_min).

Usage:
    python scripts/power_mcnemar.py
"""

from __future__ import annotations

import argparse
import sys

from scipy.stats import binom


def min_discordant(alpha: float) -> int:
    """Smallest one-directional discordant count significant at alpha."""
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    k = 1
    while 2 * 0.5**k > alpha:
        k += 1
    return k


def mcnemar_power(n_items: int, rate: float, alpha: float) -> float:
    """Power to detect `rate` vs 0 over `n_items` paired items at `alpha`."""
    if n_items < 1 or not 0.0 <= rate <= 1.0:
        raise ValueError("n_items must be positive and rate in [0, 1]")
    return float(binom.sf(min_discordant(alpha) - 1, n_items, rate))


def chance_of_one_instance(n_items: int, rate: float) -> float:
    """Probability of observing at least one instance of a rare behavior."""
    return 1.0 - (1.0 - rate) ** n_items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=0.001)
    parser.add_argument("--rate", type=float, default=0.30)
    args = parser.parse_args(argv)

    print(
        f"minimum one-directional discordant items at alpha={args.alpha}: "
        f"{min_discordant(args.alpha)}"
    )
    for n in (20, 50, 100):
        print(f"  n={n:3d}: power = {mcnemar_power(n, args.rate, args.alpha):.4f}")
    print(
        f"\nchance of at least one instance at a true rate of 2% over 100 items: "
        f"{chance_of_one_instance(100, 0.02):.3f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
