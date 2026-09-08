# Monte Carlo Simulation Dashboard

A Streamlit dashboard for exploring simulated stock-price paths and estimating downside risk with Value at Risk (VaR).

The app downloads historical adjusted closing prices from Yahoo Finance, estimates daily return statistics, and uses a Geometric Brownian Motion (GBM) Monte Carlo simulation to project 30 future trading days.

## Features

- Enter a stock ticker, historical date range, and number of simulation paths.
- Configure the VaR percentile from 1 to 99, with a default of 5.
- Download historical adjusted closing prices through Yahoo Finance.
- Calculate daily drift and volatility from historical percentage returns.
- Generate up to 10,000 simulated price paths.
- Calculate the percentile-based worst-case price and Value at Risk.
- Display the simulated paths with a red VaR threshold line labeled with the selected percentile, such as `VaR Threshold (P5)`.
- Report invalid inputs, missing data, and download failures in the dashboard.

## Requirements

- Python 3.10 or newer recommended
- Internet access for Yahoo Finance data

Dependencies are listed in `requirements.txt`.

## Installation

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the dashboard

```powershell
python -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Using the app

1. Enter a ticker symbol, such as `MU`.
2. Select a historical start and end date. The end date cannot be in the future.
3. Choose the number of simulations from 1 to 10,000.
4. Choose the VaR percentile from 1 to 99.
5. Select **Run Simulation**.

The results show the historical drift, historical volatility, latest price, simulated percentile price, Value at Risk, and the chart of simulated paths.

## Methodology

1. Historical adjusted closing prices are downloaded from Yahoo Finance.
2. Daily percentage returns are calculated. Their mean is used as drift ($\\mu$), and their standard deviation is used as volatility ($\\sigma$).
3. Each simulated path uses the GBM recurrence:

   ```text
   S_t = S_(t-1) * exp((mu - 0.5 * sigma^2) + sigma * Z_t)
   ```

   where `Z_t` is a standard normal random shock.

4. The selected percentile of the simulated final prices is used as the worst-case price.
5. Value at Risk is calculated as:

   ```text
   VaR = latest price - worst-case price
   ```

The simulation horizon is currently fixed at 30 future trading days in `app.py`.

## Project structure

```text
.
├── app.py                         # Streamlit user interface and pipeline
├── monte_carlo.py                 # Original standalone example script
├── requirements.txt               # Python dependencies
├── src/
│   └── monte_carlo_dashboard/
│       ├── data_service.py        # Yahoo Finance data retrieval
│       ├── models.py               # Result dataclasses
│       ├── risk.py                 # VaR calculations
│       ├── simulation.py            # Return statistics and GBM simulation
│       ├── validation.py            # Input validation and ticker normalization
│       └── visualization.py         # Matplotlib chart construction
└── tests/                         # Test package
```

## Run tests

```powershell
python -m pytest -q
```

## Disclaimer

This dashboard is for educational and exploratory use only. Monte Carlo outputs depend on historical data and model assumptions; they are not forecasts, guarantees, or financial advice.
