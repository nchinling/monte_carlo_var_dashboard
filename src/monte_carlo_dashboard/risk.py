"""Risk_Calculator: compute the worst-case price and Value at Risk.

Pure, side-effect-free functions that operate on the simulated final prices.
They mirror the VaR logic from the original ``monte_carlo.py`` script:

    worst_case_price = np.percentile(final_prices, 5)
    var_95 = last_price - worst_case_price
"""

from __future__ import annotations

import numpy as np

from .models import RiskResult


def compute_worst_case_price(final_prices, var_percentile: float) -> float:
    """Return the price at ``var_percentile`` of the final-price distribution.

    Uses ``np.percentile`` over the simulated final prices, matching the
    original script's ``np.percentile(final_prices, 5)`` logic. (Req 8.1)
    """
    return float(np.percentile(final_prices, var_percentile))


def compute_value_at_risk(last_price: float, worst_case_price: float) -> float:
    """Return the Value at Risk as ``last_price - worst_case_price``. (Req 8.2)"""
    return float(last_price) - float(worst_case_price)


def compute_risk(last_price: float, final_prices, var_percentile: float) -> RiskResult:
    """Convenience wrapper returning a :class:`RiskResult`.

    Computes the worst-case price at ``var_percentile`` and the Value at Risk,
    then packages the last price, worst-case price, and VaR together.
    """
    worst_case_price = compute_worst_case_price(final_prices, var_percentile)
    value_at_risk = compute_value_at_risk(last_price, worst_case_price)
    return RiskResult(
        last_price=float(last_price),
        worst_case_price=worst_case_price,
        value_at_risk=value_at_risk,
    )
