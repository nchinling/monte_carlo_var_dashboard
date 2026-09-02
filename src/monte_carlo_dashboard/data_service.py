"""Data_Service: download historical closing prices from Yahoo Finance.

Isolates network I/O behind a small interface so the Dashboard can wrap it in a
try/except and distinguish the "no data" case (an empty result) from a download
error (a propagated exception).

Mirrors the retrieval logic from the original ``monte_carlo.py`` script:

    yf.download(ticker, start=..., end=..., auto_adjust=True)['Close'].squeeze()
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf


def fetch_prices(ticker: str, start_date: date, end_date: date) -> pd.Series:
    """Download adjusted closing prices for ``ticker`` over the date range.

    Downloads from Yahoo Finance for ``[start_date, end_date)`` and returns a
    1-D :class:`pandas.Series` of closing prices, matching the original script's
    ``yf.download(...)['Close'].squeeze()`` logic. (Req 5.1, 5.2)

    Returns an empty Series when no data is found for the requested ticker and
    date range so the Dashboard can report the "no data" case. (Req 5.3)

    Download errors are not swallowed; they propagate to the caller so the
    Dashboard can report a download failure distinctly. (Req 5.4)
    """
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True,
    )["Close"].squeeze()

    # squeeze() returns a scalar when the frame has a single row; coerce any
    # non-Series result back into a 1-D Series so the contract is stable.
    if not isinstance(data, pd.Series):
        data = pd.Series(data)

    return data
