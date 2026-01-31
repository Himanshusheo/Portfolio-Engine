"""
Backtest engine: periodic rebalancing, value and weight tracking.

Rebalances at configured frequency using a strategy function. Tracks
portfolio value and weight history over time.
"""

import numpy as np
import pandas as pd

from analytics import performance_report
from config import AllocationConfig, DEFAULT_CONFIG


def _rebalance_dates(returns: pd.DataFrame, frequency: str) -> pd.DatetimeIndex:
    """Dates on which to rebalance (first date of each period)."""
    idx = returns.index
    if frequency == "daily":
        return idx
    periods = pd.Series(idx)
    if frequency == "monthly":
        periods = periods.dt.to_period("M")
    elif frequency == "quarterly":
        periods = periods.dt.to_period("Q")
    else:
        return idx
    first_positions = periods.drop_duplicates(keep="first").index
    return idx[first_positions]


def run_backtest(
    returns: pd.DataFrame,
    strategy_func,
    config: AllocationConfig = None,
) -> dict:
    """
    Run backtest with periodic rebalancing.

    Args:
        returns: DataFrame of returns (rows=dates, columns=assets).
        strategy_func: Function(returns_df, config) -> weights array.
        config: Allocation config; uses default if None.

    Returns:
        Dict with keys: values, weights_history, metrics.
        - values: Series of portfolio values (starts at 1).
        - weights_history: DataFrame of weights at each rebalance date.
        - metrics: Dict from analytics.performance_report.
    """
    cfg = config or DEFAULT_CONFIG
    rebal_dates = _rebalance_dates(returns, cfg.rebalance_frequency)
    assets = returns.columns.tolist()
    n = len(assets)

    values = pd.Series(index=returns.index, dtype=float)
    values.iloc[0] = 1.0

    weights_history = []
    current_weights = None

    for i in range(1, len(returns)):
        date = returns.index[i]
        hist = returns.iloc[: i + 1]

        # Rebalance at configured dates
        if date in rebal_dates:
            lookback = hist
            if cfg.lookback_window is not None:
                lookback = hist.tail(cfg.lookback_window)
            current_weights = strategy_func(lookback, cfg)
            current_weights = np.asarray(current_weights).ravel()
            weights_history.append((date, current_weights.copy()))

        if current_weights is None:
            current_weights = np.ones(n) / n
            weights_history.append((date, current_weights.copy()))

        # Portfolio return this period
        ret_t = returns.iloc[i].values @ current_weights
        values.iloc[i] = values.iloc[i - 1] * (1 + ret_t)

    weights_df = pd.DataFrame(
        {a: [w[i] for _, w in weights_history] for i, a in enumerate(assets)},
        index=[d for d, _ in weights_history],
    )

    metrics = performance_report(
        values,
        rf=cfg.risk_free_rate,
        periods_per_year=cfg.periods_per_year,
    )

    return {
        "values": values,
        "weights_history": weights_df,
        "metrics": metrics,
    }


def simulate_portfolio(
    returns: pd.DataFrame,
    weights: np.ndarray,
) -> pd.Series:
    """
    Simulate portfolio value with fixed weights (no rebalancing).

    For simple one-shot backtests when rebalancing is not needed.
    """
    w = np.asarray(weights).ravel()
    port_returns = returns.values @ w
    cum = np.cumprod(1.0 + port_returns)
    return pd.Series(cum, index=returns.index)
