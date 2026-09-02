# Implementation Plan: Monte Carlo Dashboard

## Overview

This plan converts the modular Streamlit dashboard design into incremental Python coding tasks. Work starts by scaffolding the `src/monte_carlo_dashboard` package and its dataclass contracts, then implements each pure computational module (validation, simulation, risk) with property-based Hypothesis tests placed next to the code they verify. The Data_Service and Visualizer follow, then everything is wired into the `app.py` Streamlit Dashboard. Each step builds on the previous one so there is no orphaned code, and the final steps integrate the full pipeline behind the run button.

The implementation language is Python (as specified in the design). Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/); external data retrieval and Streamlit wiring are covered by mock-based unit, integration, and smoke tests.

## Tasks

- [x] 1. Set up project structure, dependencies, and shared data models
  - [x] 1.1 Scaffold the package, dependencies, and data models
    - Create the `src/monte_carlo_dashboard/` package with `__init__.py` and the `tests/` folder
    - Create `requirements.txt` with streamlit, yfinance, numpy, pandas, matplotlib, hypothesis, pytest
    - Implement `models.py` with frozen dataclasses `SimulationInputs`, `ReturnStats`, `SimulationResult`, `RiskResult`, and `ValidationResult`
    - _Requirements: 1.1, 6.4, 7.2, 8.3_

- [x] 2. Implement input validation (Dashboard support)
  - [x] 2.1 Implement `validation.py` functions
    - Implement `normalize_ticker` to trim whitespace and uppercase
    - Implement `validate_inputs` to check ticker non-empty, start < end, end <= today, simulation_count in 1..10000, var_percentile in 1..99, aggregating all failures into `ValidationResult.errors`
    - Implement `has_sufficient_data` to require at least 2 price points
    - _Requirements: 1.3, 2.3, 2.4, 2.5, 3.3, 3.4, 4.3, 4.4_

  - [ ]* 2.2 Write property test for ticker normalization
    - **Property 1: Ticker normalization is stripped, uppercased, and idempotent**
    - **Validates: Requirements 1.4**

  - [ ]* 2.3 Write property test for date-range validity boundary
    - **Property 2: Date-range validity boundary**
    - **Validates: Requirements 2.3, 2.4**

  - [ ]* 2.4 Write property test for sufficient-data predicate
    - **Property 3: Sufficient-data predicate matches series length**
    - **Validates: Requirements 2.5**

  - [ ]* 2.5 Write property test for simulation-count range validity
    - **Property 4: Simulation-count range validity**
    - **Validates: Requirements 3.3, 3.4**

  - [ ]* 2.6 Write property test for VaR-percentile range validity
    - **Property 5: VaR-percentile range validity**
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 2.7 Write unit test for non-integer simulation count rejection
    - Assert a non-integer simulation count is rejected as an edge case
    - _Requirements: 3.5_

- [x] 3. Implement the Simulation_Engine
  - [x] 3.1 Implement `compute_return_stats` in `simulation.py`
    - Compute daily returns via `pct_change().dropna()`, drift as the mean, volatility as the standard deviation, returning a `ReturnStats`
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 3.2 Write property test for daily returns definition and length
    - **Property 6: Daily returns definition and length**
    - **Validates: Requirements 6.1**

  - [ ]* 3.3 Write property test for return statistics
    - **Property 7: Return statistics match mean and standard deviation**
    - **Validates: Requirements 6.2, 6.3**

  - [x] 3.4 Implement `run_simulation` in `simulation.py`
    - Set every path's first value to `last_price`, build a `(horizon, simulation_count)` grid, apply the GBM recurrence `price[t] = price[t-1] * exp((mu - 0.5*sigma^2) + sigma*Z)`, set `final_prices = price_paths[-1]`, and accept an injectable `numpy.random.Generator`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 3.5 Write property test for path starting price
    - **Property 8: Every simulated path starts at the last price**
    - **Validates: Requirements 7.1**

  - [ ]* 3.6 Write property test for simulation shape and final-price invariant
    - **Property 9: Simulation shape and final-price invariant**
    - **Validates: Requirements 7.2, 7.3, 7.5**

  - [ ]* 3.7 Write property test for the GBM recurrence
    - **Property 10: GBM recurrence holds at every step**
    - **Validates: Requirements 7.4**

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement the Risk_Calculator
  - [x] 5.1 Implement `risk.py` functions
    - Implement `compute_worst_case_price` using `np.percentile`, `compute_value_at_risk` as `last_price - worst_case_price`, and `compute_risk` returning a `RiskResult`
    - _Requirements: 8.1, 8.2_

  - [ ]* 5.2 Write property test for worst-case price
    - **Property 11: Worst-case price equals the percentile and is monotonic**
    - **Validates: Requirements 8.1**

  - [ ]* 5.3 Write property test for Value at Risk
    - **Property 12: Value at Risk is the last price minus the worst-case price**
    - **Validates: Requirements 8.2**

- [x] 6. Implement the Visualizer
  - [x] 6.1 Implement `build_figure` in `visualization.py`
    - Plot all price paths semi-transparently, add a red dashed horizontal line at `worst_case_price` labeled as the VaR confidence threshold, set a title including ticker/simulation_count/horizon, and label the axes "Days in the Future" and "Stock Price ($)"; return the `Figure`
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ]* 6.2 Write property test for the chart title
    - **Property 13: Chart title contains ticker, simulation count, and horizon**
    - **Validates: Requirements 9.3**

  - [ ]* 6.3 Write unit tests for visualization details
    - Assert the path-line count equals simulation count plus one threshold line, the VaR line sits at the worst-case price with the expected label, and the axis labels are correct
    - _Requirements: 9.1, 9.2, 9.4_

- [x] 7. Implement the Data_Service
  - [x] 7.1 Implement `fetch_prices` in `data_service.py`
    - Call `yfinance.download(ticker, start, end, auto_adjust=True)['Close'].squeeze()`, return a 1-D Series (empty when no data), and let download errors propagate to the caller
    - _Requirements: 5.1, 5.2_

  - [ ]* 7.2 Write mock-based unit/integration tests for `fetch_prices`
    - Assert `yfinance.download` is called with the given ticker and date range, a 1-D Series is returned from a mocked multi-column frame, and an empty result is returned when no data exists
    - _Requirements: 5.1, 5.2_

- [x] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement and wire the Dashboard (`app.py`)
  - [x] 9.1 Build the Streamlit widgets and input collection
    - Add ticker `text_input` (default "MU"), start/end `date_input` (end capped at today), simulation-count `number_input` (default 1000, min 1, max 10000, integer step), percentile `number_input` (default 5, min 1, max 99), and the "Run Simulation" button
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.5, 4.1, 4.2, 4.3, 10.1_

  - [x] 9.2 Wire the run pipeline and result display
    - On button click: normalize the ticker, run `validate_inputs`, fetch prices inside a try/except, check `has_sufficient_data`, run `compute_return_stats` -> `run_simulation` -> `compute_risk` -> `build_figure` inside `st.spinner`, and display drift, volatility, last price, worst-case price, VaR, and the chart together; show the correct message for empty ticker, invalid inputs, no-data, insufficient-data, and download-error cases without running the simulation
    - _Requirements: 1.3, 2.3, 2.5, 5.3, 5.4, 6.4, 8.3, 9.1, 10.1, 10.2, 10.3_

  - [ ]* 9.3 Write smoke tests for the Dashboard widgets and spinner
    - Assert the app defines the ticker input, start/end date inputs, simulation-count input, percentile input, and run button, and that the pipeline is wrapped in `st.spinner`
    - _Requirements: 1.1, 2.1, 2.2, 3.1, 4.1, 10.1, 10.2_

  - [ ]* 9.4 Write mock-based integration tests for the end-to-end flow
    - With mocked data, assert a successful run displays statistics, risk metrics, and the chart together, and that a raised download error is caught and reported without running the simulation
    - _Requirements: 5.4, 10.3_

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate the 13 universal correctness properties from the design using Hypothesis (minimum 100 iterations each)
- Unit, integration, and smoke tests cover UI wiring, rendering details, and Yahoo Finance retrieval

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "3.1", "5.1", "6.1", "7.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.3", "5.2", "5.3", "6.2", "6.3", "7.2"] },
    { "id": 3, "tasks": ["3.4"] },
    { "id": 4, "tasks": ["3.5", "3.6", "3.7"] },
    { "id": 5, "tasks": ["9.1"] },
    { "id": 6, "tasks": ["9.2"] },
    { "id": 7, "tasks": ["9.3", "9.4"] }
  ]
}
```
