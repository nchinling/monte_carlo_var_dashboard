"""Pure validation and normalization functions for the dashboard.

These functions are side-effect free so the Dashboard can call them before
running anything, and so the rules stay testable independent of Streamlit.
They map to the Dashboard (support) responsibilities in the design document.
"""

from __future__ import annotations

from datetime import date

from .models import ValidationResult

# Bounds for the configurable inputs (see requirements 3.3, 4.3).
MIN_SIMULATION_COUNT = 1
MAX_SIMULATION_COUNT = 10000
MIN_VAR_PERCENTILE = 1
MAX_VAR_PERCENTILE = 99

# Minimum number of historical price points needed to derive returns.
MIN_PRICE_POINTS = 2


def normalize_ticker(raw: str) -> str:
    """Trim leading/trailing whitespace and uppercase the ticker.

    Requirement 1.3: normalize the Ticker_Symbol by removing leading and
    trailing whitespace and converting characters to uppercase before
    querying the Data_Service.
    """
    return raw.strip().upper()


def validate_inputs(
    ticker: str,
    start_date: date,
    end_date: date,
    simulation_count: int,
    var_percentile: float,
    today: date,
) -> ValidationResult:
    """Validate all user inputs, aggregating every failure.

    Checks (all failures are collected into ``ValidationResult.errors`` so the
    user sees every problem at once):

    - ticker is non-empty after normalization (Req 1.3, 2.x context)
    - start date is strictly before end date (Req 2.3)
    - end date is on or before today (Req 2.4)
    - simulation_count in [1, 10000] (Req 3.3, 3.4)
    - var_percentile in [1, 99] (Req 4.3, 4.4)
    """
    errors: list[str] = []

    if normalize_ticker(ticker) == "":
        errors.append("Please enter a ticker symbol.")

    if not start_date < end_date:
        errors.append("Start date must be before the end date.")

    if end_date > today:
        errors.append("End date must be on or before today.")

    if not (MIN_SIMULATION_COUNT <= simulation_count <= MAX_SIMULATION_COUNT):
        errors.append(
            f"Number of simulations must be between {MIN_SIMULATION_COUNT} "
            f"and {MAX_SIMULATION_COUNT}."
        )

    if not (MIN_VAR_PERCENTILE <= var_percentile <= MAX_VAR_PERCENTILE):
        errors.append(
            f"VaR percentile must be between {MIN_VAR_PERCENTILE} "
            f"and {MAX_VAR_PERCENTILE}."
        )

    return ValidationResult(is_valid=not errors, errors=errors)


def has_sufficient_data(prices) -> bool:
    """Return True if there are at least 2 historical price points.

    Requirement 2.5: fewer than 2 Historical_Prices data points is
    insufficient to derive returns.
    """
    return len(prices) >= MIN_PRICE_POINTS
