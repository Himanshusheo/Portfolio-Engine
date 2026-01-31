"""
Investment risk framework: end-to-end workflow example.

Demonstrates load → optimize → backtest → analytics → stress test.
"""

import numpy as np
import pandas as pd

from data_loader import load_and_prepare
from config import AllocationConfig
from strategy import get_strategy
from backtest import run_backtest, simulate_portfolio
from analytics import rolling_volatility
from scenario import stress_test_portfolio, equity_crash_scenario


def make_sample_data(n_days: int = 252 * 5, n_assets: int = 4) -> pd.DataFrame:
    """Generate synthetic price data."""
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", periods=n_days, freq="B")
    vol = np.array([0.12, 0.18, 0.22, 0.15])[:n_assets] / np.sqrt(252)
    mu = np.array([0.06, 0.08, 0.10, 0.05])[:n_assets] / 252
    returns = np.random.randn(n_days, n_assets) * vol + mu
    prices = 100 * np.cumprod(1 + returns)
    assets = [f"Asset_{i+1}" for i in range(n_assets)]
    return pd.DataFrame(prices, index=dates, columns=assets).reset_index()


def run_example():
    """Run full workflow: strategies, backtest, stress test."""
    # Sample data
    sample = make_sample_data()
    sample.to_csv("sample_prices.csv", index=False)
    returns = load_and_prepare("sample_prices.csv")
    print("Returns shape:", returns.shape, "\n")

    # Config
    cfg = AllocationConfig(
        risk_free_rate=0.0,
        rebalance_frequency="monthly",
        lookback_window=252,
        weight_bounds=(0.0, 1.0),
    )

    # Strategy comparison
    strategies = ["equal_weight", "mean_variance", "risk_parity"]
    results = {}

    for name in strategies:
        strategy_fn = get_strategy(name)
        bt = run_backtest(returns, strategy_fn, config=cfg)
        results[name] = bt
        print(f"--- {name} ---")
        print("Metrics:", bt["metrics"])
        print()

    # Rolling volatility for one strategy
    mv_values = results["mean_variance"]["values"]
    port_returns = mv_values.pct_change().dropna()
    roll_vol = rolling_volatility(port_returns, window=63, periods_per_year=252)
    print("Rolling volatility (63d, mean):", float(roll_vol.mean()), "\n")

    # Stress test: -20% equity shock on asset 0
    w_mv = results["mean_variance"]["weights_history"].iloc[-1].values
    shock = equity_crash_scenario(len(w_mv), equity_idx=0, crash_pct=-0.20)
    stress_result = stress_test_portfolio(w_mv, shock)
    print("Stress test (-20% on asset 0):")
    print("  Portfolio return under shock:", f"{stress_result['portfolio_return']:.2%}")
    print("  Portfolio drawdown:", f"{stress_result['portfolio_drawdown']:.2%}")

    return returns, results, stress_result


if __name__ == "__main__":
    run_example()
