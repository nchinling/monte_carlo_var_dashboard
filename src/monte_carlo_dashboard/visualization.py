"""Visualizer: build the matplotlib figure for the Monte Carlo simulation.

Renders all simulated price paths semi-transparently along with a horizontal
Value at Risk (VaR) threshold line at the worst-case price. The function
returns a ``matplotlib.figure.Figure`` so the Dashboard can render it with
``st.pyplot(fig)`` without relying on the global pyplot state or calling
``plt.show()``. This keeps the Visualizer free of Streamlit and interactive
backends, so it works cleanly under a non-interactive (Agg) backend.

Mirrors the plotting logic from the original ``monte_carlo.py``:
    plt.plot(price_paths, color='blue', alpha=0.05)
    plt.axhline(y=worst_case_price, color='red', linestyle='--', ...)
"""

from __future__ import annotations

from matplotlib.figure import Figure


def build_figure(
    price_paths,
    worst_case_price: float,
    ticker: str,
    simulation_count: int,
    horizon: int,
    var_percentile: float = 5,
) -> Figure:
    """Build the price-path chart with the VaR threshold line.

    Args:
        price_paths: Simulated price grid of shape ``(horizon, simulation_count)``.
        worst_case_price: Price at the VaR percentile; drawn as a horizontal line.
        ticker: Ticker symbol shown in the chart title.
        simulation_count: Number of simulated paths, shown in the title.
        horizon: Number of future trading days, shown in the title.
        var_percentile: Percentile used to calculate the VaR threshold, shown
            in the legend.

    Returns:
        A ``matplotlib.figure.Figure`` containing the plotted paths, the VaR
        threshold line, a descriptive title, and labeled axes.

    Requirements: 9.1, 9.2, 9.3, 9.4
    """
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    # Req 9.1: plot every simulated path semi-transparently.
    ax.plot(price_paths, color="blue", alpha=0.05)

    # Req 9.2: horizontal VaR threshold line at the worst-case price.
    ax.axhline(
        y=worst_case_price,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"VaR Threshold (P{var_percentile:g})",
    )

    # Req 9.3: title includes the ticker, simulation count, and horizon.
    ax.set_title(
        f"Monte Carlo Simulation: {ticker} "
        f"({simulation_count} paths, {horizon} days)"
    )

    # Req 9.4: axis labels for future trading days and stock price.
    ax.set_xlabel("Days in the Future")
    ax.set_ylabel("Stock Price ($)")

    ax.legend()

    return fig
