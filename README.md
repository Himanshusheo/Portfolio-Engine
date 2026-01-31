# Portfolio Engine

A lightweight educational toolkit for portfolio optimization. Built for learning core concepts—covariance, mean-variance optimization, risk parity—without the overhead of a full library.

## Motivation

Portfolio optimization is a cornerstone of quantitative finance. This project distills the essentials into a minimal engine you can understand and extend. It demonstrates how returns drive risk estimates, how optimization chooses weights, and how backtests measure performance.

## Features

- **Data loading**: Load prices from CSV and compute returns
- **Risk models**: Covariance matrix and volatility
- **Optimization**:
  - Mean-variance (maximize Sharpe ratio)
  - Risk parity (equal risk contribution)
  - Inverse-volatility heuristic
- **Backtest**: Portfolio value simulation with fixed weights
- **Metrics**: Sharpe ratio, maximum drawdown, return summary

## Dependencies

- numpy
- pandas
- scipy

## How to Run

1. Install dependencies:

   ```bash
   pip install numpy pandas scipy
   ```

2. Run the example script (uses synthetic data):

   ```bash
   cd portfolio_engine
   python main.py
   ```

3. Use your own data: create a CSV with a date column and price columns per asset:

   ```csv
   date,SPY,AGG,GLD
   2020-01-02,100.0,110.0,120.0
   2020-01-03,101.5,110.2,119.8
   ...
   ```

   Then in Python:

   ```python
   from data_loader import load_and_prepare
   from optimizer import optimize_from_returns
   from backtest import simulate_portfolio, performance_summary

   returns = load_and_prepare("your_data.csv")
   weights = optimize_from_returns(returns, method="mean_variance")
   values = simulate_portfolio(returns, weights.values)
   print(performance_summary(values))
   ```

## Project Layout

```
portfolio_engine/
├── data_loader.py   # Load CSV, compute returns
├── risk_models.py   # Covariance, volatility
├── optimizer.py     # Mean-variance, risk parity
├── backtest.py      # Simulate portfolio, compute metrics
├── main.py          # End-to-end example
└── README.md
```
