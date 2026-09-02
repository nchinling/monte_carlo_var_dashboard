import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# 1. Fetch Historical Data
ticker = 'MU'
print(f"Downloading data for {ticker}...")
# We use the last couple of years to establish the stock's "behavior"
# auto_adjust=True is the modern yfinance default; squeeze() forces a 1-D Series
# so mu/sigma below are scalars rather than length-1 pandas Series.
data = yf.download(ticker, start='2024-08-31', end='2026-08-31',
                   auto_adjust=True)['Close'].squeeze()
print(f"Ticker Name: {ticker}\n{data}")

# 2. Calculate daily returns and statistics
# pct_change() calculates the daily percentage gain/loss
returns = data.pct_change().dropna()
print(f"{ticker} % returns\n{returns}")

mu = returns.mean()  # Average daily return (Drift)
sigma = returns.std() # Daily volatility (Risk)
print(f"Average returns: {mu} %")
print(f"Daily volatility: {sigma}")

# 3. Monte Carlo Setup
simulations = 1000 # Number of alternate realities we want to simulate
days = 30          # Time horizon (e.g., predicting the next 30 trading days)
last_price = data.iloc[-1].item() # The most recent closing price

# 4. Run the Simulation
# Generate a grid of random numbers (shocks) for every day in every simulation
random_shocks = np.random.normal(0, 1, (days, simulations))

# Create an empty grid to hold our future prices
price_paths = np.zeros((days, simulations))
price_paths[0] = last_price

# Loop through each day and apply the GBM formula
for t in range(1, days):
    # S_t = S_{t-1} * e^((mu - 0.5 * sigma^2) + sigma * random_shock)
    step_returns = np.exp((mu - 0.5 * sigma**2) + sigma * random_shocks[t])
    price_paths[t] = price_paths[t-1] * step_returns

# 5. Calculate Market Risk (Value at Risk - VaR)
# Look at the final prices on day 30 across all 1,000 simulations
final_prices = price_paths[-1]

# Find the 5th percentile (the threshold for the worst 5% of outcomes)
worst_case_price = np.percentile(final_prices, 5)
var_95 = last_price - worst_case_price

print("-" * 30)
print(f"Current Price: ${last_price:.2f}")
print(f"5% Worst-Case Price in 30 days: ${worst_case_price:.2f}")
print(f"Value at Risk (VaR) per share: ${var_95:.2f}")
print("-" * 30)

# 6. Visualize the Alternate Realities
plt.figure(figsize=(10,6))
plt.plot(price_paths, color='blue', alpha=0.05) # alpha makes lines semi-transparent
plt.title(f"Monte Carlo Simulation: {ticker} (1000 paths, 30 days)")
plt.xlabel("Days in the Future")
plt.ylabel("Stock Price ($)")
plt.axhline(y=worst_case_price, color='red', linestyle='--', linewidth=2, label='95% Confidence Threshold (VaR)')
plt.legend()
plt.show()