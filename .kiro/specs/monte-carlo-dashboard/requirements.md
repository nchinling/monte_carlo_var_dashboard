# Requirements Document

## Introduction

This feature delivers an interactive Streamlit dashboard built on top of the existing `monte_carlo.py` script. The dashboard lets a user configure and run a Monte Carlo simulation for a chosen stock ticker using Geometric Brownian Motion (GBM). The user supplies a ticker symbol, a historical date range, the number of simulations, and a Value at Risk (VaR) percentile. The dashboard downloads historical closing prices from Yahoo Finance, derives daily-return statistics (drift and volatility), simulates future price paths, computes the VaR threshold at the chosen percentile, and visualizes the simulated paths along with the VaR threshold. The goal is to replace the current command-line, hard-coded workflow with a configurable, self-serve web interface.

## Glossary

- **Dashboard**: The Streamlit web application that provides the user interface and orchestrates data retrieval, simulation, and visualization.
- **Data_Service**: The component responsible for downloading historical closing prices from Yahoo Finance via the yfinance library.
- **Simulation_Engine**: The component that computes return statistics and runs the Monte Carlo GBM simulation to produce future price paths.
- **Risk_Calculator**: The component that computes the worst-case price and Value at Risk from the simulated final prices.
- **Visualizer**: The component that renders the simulated price paths and the VaR threshold line as a chart in the Dashboard.
- **Ticker_Symbol**: A string identifier for a publicly traded security (for example, "MU") used to query Yahoo Finance.
- **Date_Range**: A start date and end date bounding the historical period from which returns are derived.
- **Historical_Prices**: The series of adjusted closing prices retrieved for the Ticker_Symbol over the Date_Range.
- **Daily_Returns**: The day-over-day percentage change of the Historical_Prices.
- **Drift**: The mean of the Daily_Returns, denoted mu, representing the average daily return.
- **Volatility**: The standard deviation of the Daily_Returns, denoted sigma, representing daily risk.
- **Simulation_Count**: The number of independent price paths to simulate.
- **Horizon**: The number of future trading days to simulate for each path (default 30).
- **Last_Price**: The most recent closing price in the Historical_Prices, used as the starting point for all simulated paths.
- **Price_Paths**: The grid of simulated future prices with dimensions Horizon by Simulation_Count.
- **Final_Prices**: The simulated prices on the last day of the Horizon across all paths.
- **VaR_Percentile**: The percentile used to identify the worst-case outcome threshold (for example, 5 for the worst 5% of outcomes).
- **Worst_Case_Price**: The price at the VaR_Percentile of the Final_Prices distribution.
- **Value_at_Risk**: The difference between the Last_Price and the Worst_Case_Price, expressed per share (denoted VaR).

## Requirements

### Requirement 1: Enter a Ticker Symbol

**User Story:** As a user, I want to enter a ticker symbol, so that I can run the simulation for the security of my choice.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a text input control for the Ticker_Symbol.
2. WHEN the user submits an empty Ticker_Symbol, THEN THE Dashboard SHALL display a message requesting a Ticker_Symbol and SHALL NOT run the simulation.
3. WHEN the user submits a Ticker_Symbol, THE Dashboard SHALL normalize the Ticker_Symbol by removing leading and trailing whitespace and converting characters to uppercase before querying the Data_Service.

### Requirement 2: Select a Historical Date Range

**User Story:** As a user, I want to select a start date and an end date, so that I can control the historical period used to estimate returns.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a date input control for the Date_Range start date.
2. THE Dashboard SHALL provide a date input control for the Date_Range end date.
3. WHEN the user submits a Date_Range where the start date is on or after the end date, THEN THE Dashboard SHALL display a validation message and SHALL NOT run the simulation.
4. THE Dashboard SHALL restrict the selectable end date to be on or before the current date.
5. IF the selected Date_Range yields fewer than 2 Historical_Prices data points, THEN THE Dashboard SHALL display a message indicating insufficient data and SHALL NOT run the simulation.

### Requirement 3: Specify the Number of Simulations

**User Story:** As a user, I want to specify the number of simulations, so that I can balance statistical detail against run time.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a numeric input control for the Simulation_Count.
2. THE Dashboard SHALL provide a default Simulation_Count of 1000.
3. THE Dashboard SHALL restrict the Simulation_Count to a minimum of 1 and a maximum of 10000.
4. IF the user submits a Simulation_Count outside the range of 1 to 10000, THEN THE Dashboard SHALL display a validation message and SHALL NOT run the simulation.
5. THE Dashboard SHALL accept only integer values for the Simulation_Count.

### Requirement 4: Specify the VaR Percentile

**User Story:** As a user, I want to specify the percentile used for the worst-case threshold, so that I can measure risk at my chosen confidence level.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a numeric input control for the VaR_Percentile.
2. THE Dashboard SHALL provide a default VaR_Percentile of 5.
3. THE Dashboard SHALL restrict the VaR_Percentile to a minimum of 1 and a maximum of 99.
4. IF the user submits a VaR_Percentile outside the range of 1 to 99, THEN THE Dashboard SHALL display a validation message and SHALL NOT run the simulation.

### Requirement 5: Retrieve Historical Price Data

**User Story:** As a user, I want the dashboard to retrieve historical prices for my ticker and date range, so that the simulation reflects the security's recent behavior.

#### Acceptance Criteria

1. WHEN the user runs the simulation with a valid Ticker_Symbol and Date_Range, THE Data_Service SHALL download Historical_Prices of adjusted closing prices from Yahoo Finance for the Ticker_Symbol over the Date_Range.
2. THE Data_Service SHALL return the Historical_Prices as a one-dimensional series of closing prices.
3. IF the Data_Service returns no Historical_Prices for the requested Ticker_Symbol and Date_Range, THEN THE Dashboard SHALL display a message indicating that no data was found and SHALL NOT run the simulation.
4. IF the Data_Service raises an error while downloading Historical_Prices, THEN THE Dashboard SHALL display an error message describing the failure and SHALL NOT run the simulation.

### Requirement 6: Compute Return Statistics

**User Story:** As a user, I want the dashboard to compute the drift and volatility from historical returns, so that the simulation is parameterized by the security's observed behavior.

#### Acceptance Criteria

1. WHEN Historical_Prices are available, THE Simulation_Engine SHALL compute Daily_Returns as the day-over-day percentage change of the Historical_Prices, excluding undefined values.
2. THE Simulation_Engine SHALL compute the Drift as the mean of the Daily_Returns.
3. THE Simulation_Engine SHALL compute the Volatility as the standard deviation of the Daily_Returns.
4. THE Dashboard SHALL display the computed Drift and Volatility to the user.

### Requirement 7: Run the Monte Carlo Simulation

**User Story:** As a user, I want the dashboard to simulate future price paths using Geometric Brownian Motion, so that I can see a range of possible future outcomes.

#### Acceptance Criteria

1. WHEN the user runs the simulation, THE Simulation_Engine SHALL set the starting value of every Price_Path to the Last_Price.
2. THE Simulation_Engine SHALL generate Price_Paths over a Horizon of 30 trading days.
3. THE Simulation_Engine SHALL produce a number of Price_Paths equal to the Simulation_Count.
4. THE Simulation_Engine SHALL compute each subsequent daily price using the Geometric Brownian Motion formula, where the next price equals the prior price multiplied by the exponential of the quantity (Drift minus one half times Volatility squared) plus (Volatility times a standard normal random shock).
5. THE Simulation_Engine SHALL identify the Final_Prices as the simulated prices on the last day of the Horizon across all Price_Paths.

### Requirement 8: Compute Value at Risk

**User Story:** As a user, I want the dashboard to compute the worst-case price and Value at Risk at my chosen percentile, so that I can quantify downside risk per share.

#### Acceptance Criteria

1. WHEN the Final_Prices are available, THE Risk_Calculator SHALL compute the Worst_Case_Price as the value at the VaR_Percentile of the Final_Prices distribution.
2. THE Risk_Calculator SHALL compute the Value_at_Risk as the Last_Price minus the Worst_Case_Price.
3. THE Dashboard SHALL display the Last_Price, the Worst_Case_Price, and the Value_at_Risk per share.

### Requirement 9: Visualize the Simulation

**User Story:** As a user, I want to see a chart of the simulated price paths and the VaR threshold, so that I can visually interpret the range of outcomes and the downside boundary.

#### Acceptance Criteria

1. WHEN the simulation completes, THE Visualizer SHALL render a chart of all simulated Price_Paths over the Horizon within the Dashboard.
2. THE Visualizer SHALL render a horizontal threshold line at the Worst_Case_Price labeled as the VaR confidence threshold.
3. THE Visualizer SHALL label the chart with a title that includes the Ticker_Symbol, the Simulation_Count, and the Horizon.
4. THE Visualizer SHALL label the horizontal axis as future trading days and the vertical axis as stock price.

### Requirement 10: Trigger and Report Simulation Runs

**User Story:** As a user, I want an explicit control to run the simulation and clear feedback while it runs, so that I know when results reflect my current inputs.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a control that triggers a simulation run using the current input values.
2. WHILE a simulation run is in progress, THE Dashboard SHALL display a progress indicator.
3. WHEN a simulation run completes, THE Dashboard SHALL display the computed statistics, risk metrics, and visualization together.
