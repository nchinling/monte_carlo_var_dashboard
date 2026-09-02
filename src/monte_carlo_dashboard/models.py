"""Data models shared between the dashboard modules.

These small frozen dataclasses carry data between modules with explicit,
typed contracts instead of loose tuples or dicts. They map one-to-one to the
data-transfer objects described in the design document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np


@dataclass(frozen=True)
class SimulationInputs:
    """Validated, normalized user inputs for a simulation run."""

    ticker: str  # normalized (uppercase, trimmed)
    start_date: date
    end_date: date
    simulation_count: int  # 1..10000
    var_percentile: float  # 1..99
    horizon: int = 30  # trading days


@dataclass(frozen=True)
class ReturnStats:
    """Daily-return statistics derived from historical prices."""

    drift: float  # mu: mean of daily returns
    volatility: float  # sigma: std of daily returns


@dataclass(frozen=True)
class SimulationResult:
    """Result of a Monte Carlo GBM simulation."""

    price_paths: np.ndarray  # shape (horizon, simulation_count)
    final_prices: np.ndarray  # shape (simulation_count,) == price_paths[-1]


@dataclass(frozen=True)
class RiskResult:
    """Risk metrics computed from the simulated final prices."""

    last_price: float
    worst_case_price: float
    value_at_risk: float  # last_price - worst_case_price


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating user inputs before running a simulation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)  # human-readable messages
