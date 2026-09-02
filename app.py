"""Streamlit entrypoint for the Monte Carlo Dashboard.

Run with:

    streamlit run app.py

This module owns only user interaction: it renders the input widgets,
collects the current values, and exposes the "Run Simulation" button. The
run pipeline (validation, data retrieval, simulation, risk, and chart) is
wired in a subsequent step; this file is structured so that logic can be
added inside the ``if run_clicked:`` block below.
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import streamlit as st

# The package lives under ``src/`` so that computation stays isolated from the
# Streamlit entrypoint. Add ``src`` to ``sys.path`` so ``streamlit run app.py``
# can import it regardless of the current working directory.
_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from monte_carlo_dashboard.validation import (  # noqa: E402
    MAX_SIMULATION_COUNT,
    MAX_VAR_PERCENTILE,
    MIN_SIMULATION_COUNT,
    MIN_VAR_PERCENTILE,
    has_sufficient_data,
    normalize_ticker,
    validate_inputs,
)
from monte_carlo_dashboard.data_service import fetch_prices  # noqa: E402
from monte_carlo_dashboard.simulation import (  # noqa: E402
    compute_return_stats,
    run_simulation,
)
from monte_carlo_dashboard.risk import compute_risk  # noqa: E402
from monte_carlo_dashboard.visualization import build_figure  # noqa: E402

# Number of future trading days to simulate; matches the SimulationResult
# grid contract (price_paths has shape (HORIZON, simulation_count)).
HORIZON = 30


def collect_inputs() -> dict:
    """Render the input widgets and return the current input values.

    Returns a dict with the raw ticker, start/end dates, simulation count,
    and VaR percentile. The values are returned un-normalized and
    un-validated; normalization and validation happen when the run button is
    clicked (wired in a later step).
    """
    today = date.today()

    # Requirement 1.1 / 1.2: ticker text input defaulting to "MU".
    ticker = st.text_input("Ticker Symbol", value="MU")

    # Requirement 2.1 / 2.2 / 2.4: start and end date inputs, with the end
    # date capped at today so a future end date cannot be selected.
    default_start = today - timedelta(days=365)
    start_date = st.date_input("Start date", value=default_start, max_value=today)
    end_date = st.date_input("End date", value=today, max_value=today)

    # Requirement 3.1 / 3.2 / 3.3 / 3.5: integer simulation count, default
    # 1000, bounded to [1, 10000] with an integer step.
    simulation_count = st.number_input(
        "Number of simulations",
        min_value=MIN_SIMULATION_COUNT,
        max_value=MAX_SIMULATION_COUNT,
        value=1000,
        step=1,
    )

    # Requirement 4.1 / 4.2 / 4.3: VaR percentile, default 5, bounded to
    # [1, 99].
    var_percentile = st.number_input(
        "VaR percentile",
        min_value=MIN_VAR_PERCENTILE,
        max_value=MAX_VAR_PERCENTILE,
        value=5,
    )

    return {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "simulation_count": int(simulation_count),
        "var_percentile": var_percentile,
    }


def main() -> None:
    """Render the dashboard: title, input widgets, and the run button."""
    st.title("Monte Carlo Simulation Dashboard")
    st.write(
        "Configure a Geometric Brownian Motion simulation for a stock ticker, "
        "then run it to estimate downside risk (Value at Risk)."
    )

    inputs = collect_inputs()

    # Requirement 10.1: an explicit control that triggers a simulation run
    # using the current input values.
    run_clicked = st.button("Run Simulation")

    if run_clicked:
        # Requirement 1.3: normalize the ticker (trim + uppercase) before
        # anything else so validation and retrieval use the clean symbol.
        ticker = normalize_ticker(inputs["ticker"])

        # Requirement 2.3 / 10.1: validate all inputs up front. If anything is
        # wrong, surface every problem and stop without running a simulation.
        validation = validate_inputs(
            ticker=ticker,
            start_date=inputs["start_date"],
            end_date=inputs["end_date"],
            simulation_count=inputs["simulation_count"],
            var_percentile=inputs["var_percentile"],
            today=date.today(),
        )
        if not validation.is_valid:
            for message in validation.errors:
                st.error(message)
            return

        # Requirement 5.4: retrieval can fail (network / yfinance error). Wrap
        # it so a download error is reported clearly and the pipeline stops
        # without running the simulation.
        try:
            prices = fetch_prices(
                ticker,
                inputs["start_date"],
                inputs["end_date"],
            )
        except Exception as exc:  # noqa: BLE001 - report any download failure
            st.error(f"Failed to download price data for {ticker}: {exc}")
            return

        # Requirement 5.3: an empty series means no data for this ticker/range.
        if prices.empty:
            st.warning(f"No data found for {ticker}")
            return

        # Requirement 2.5: need at least 2 price points to derive returns.
        if not has_sufficient_data(prices):
            st.warning(
                f"Insufficient historical data for {ticker}: at least 2 price "
                "points are required to run a simulation. Try widening the "
                "date range."
            )
            return

        # Requirement 10.2: run the compute pipeline inside a spinner so the
        # user sees progress while the simulation runs.
        with st.spinner("Running Monte Carlo simulation..."):
            last_price = float(prices.iloc[-1])
            stats = compute_return_stats(prices)
            simulation = run_simulation(
                last_price=last_price,
                stats=stats,
                simulation_count=inputs["simulation_count"],
                horizon=HORIZON,
            )
            risk = compute_risk(
                last_price,
                simulation.final_prices,
                inputs["var_percentile"],
            )
            fig = build_figure(
                simulation.price_paths,
                risk.worst_case_price,
                ticker,
                inputs["simulation_count"],
                HORIZON,
            )

        # Requirement 10.3: display statistics, risk metrics, and the chart
        # together after a successful run.
        st.subheader("Results")

        # Requirement 6.4: display drift and volatility.
        stat_col, risk_col = st.columns(2)
        with stat_col:
            st.metric("Drift (daily mean return)", f"{stats.drift:.4%}")
            st.metric("Volatility (daily std dev)", f"{stats.volatility:.4%}")
        # Requirement 8.3: display last price, worst-case price, and VaR.
        with risk_col:
            st.metric("Last price", f"${risk.last_price:,.2f}")
            st.metric(
                f"Worst-case price (P{inputs['var_percentile']})",
                f"${risk.worst_case_price:,.2f}",
            )
            st.metric("Value at Risk", f"${risk.value_at_risk:,.2f}")

        # Requirement 9.1: render the simulated price paths and VaR line.
        st.pyplot(fig)


if __name__ == "__main__":
    main()
