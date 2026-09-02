"""Simulation_Engine: return statistics and Monte Carlo GBM simulation.

This module holds the pure, side-effect-free numerical core of the dashboard.
Functions accept plain values / pandas or NumPy inputs and return dataclasses
or NumPy arrays, with no Streamlit, network, or plotting dependencies.

`compute_return_stats` mirrors the return calculation in the original
``monte_carlo.py``:

    returns = data.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
"""

from __future__ import annotations

import numpy as np

from .models import ReturnStats, SimulationResult


def compute_return_stats(prices) -> ReturnStats:
    """Compute daily-return statistics from a series of historical prices.

    Daily returns are the day-over-day percentage change of ``prices`` with
    undefined values (the first, NaN entry) dropped. The drift is the mean of
    the daily returns and the volatility is their standard deviation.

    Args:
        prices: A 1-D pandas Series of historical closing prices.

    Returns:
        ReturnStats with ``drift`` (mu) and ``volatility`` (sigma).

    Validates: Requirements 6.1, 6.2, 6.3
    """
    daily_returns = prices.pct_change().dropna()
    drift = float(daily_returns.mean())
    volatility = float(daily_returns.std())
    return ReturnStats(drift=drift, volatility=volatility)


def run_simulation(
    last_price: float,
    stats: ReturnStats,
    simulation_count: int,
    horizon: int = 30,
    rng: np.random.Generator | None = None,
) -> SimulationResult:
    """Run a Geometric Brownian Motion (GBM) Monte Carlo simulation.

    Builds a ``(horizon, simulation_count)`` grid of simulated prices. Every
    path starts at ``last_price``, and each subsequent day is computed with the
    GBM recurrence, reproducing the loop in the original ``monte_carlo.py``::

        price_paths[t] = price_paths[t - 1] * np.exp(
            (mu - 0.5 * sigma**2) + sigma * Z
        )

    where ``mu`` is the drift, ``sigma`` is the volatility, and ``Z`` is a
    standard normal random shock.

    Args:
        last_price: The most recent closing price; the starting value of every
            simulated path.
        stats: ReturnStats providing ``drift`` (mu) and ``volatility`` (sigma).
        simulation_count: The number of independent price paths to simulate.
        horizon: The number of future trading days per path (default 30).
        rng: An optional injectable ``numpy.random.Generator`` for
            deterministic runs. Defaults to ``np.random.default_rng()``.

    Returns:
        SimulationResult with ``price_paths`` of shape
        ``(horizon, simulation_count)`` and ``final_prices`` equal to the last
        row of ``price_paths``.

    Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
    """
    if rng is None:
        rng = np.random.default_rng()

    mu = stats.drift
    sigma = stats.volatility

    # Generate a grid of standard normal shocks for every day in every path.
    random_shocks = rng.standard_normal((horizon, simulation_count))

    # Build the price grid; every path starts at last_price (Req 7.1, 7.2, 7.3).
    price_paths = np.zeros((horizon, simulation_count))
    price_paths[0] = last_price

    # Apply the GBM recurrence for each subsequent day (Req 7.4).
    for t in range(1, horizon):
        step_returns = np.exp((mu - 0.5 * sigma**2) + sigma * random_shocks[t])
        price_paths[t] = price_paths[t - 1] * step_returns

    # Final prices are the simulated prices on the last day (Req 7.5).
    final_prices = price_paths[-1]

    return SimulationResult(price_paths=price_paths, final_prices=final_prices)
