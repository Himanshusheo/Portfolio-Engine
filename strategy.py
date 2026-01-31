"""
Portfolio construction strategies.

Each strategy maps returns data to portfolio weights. Used by the
backtest engine to define how portfolios are built and rebalanced.
"""

import numpy as np
import pandas as pd

from optimizer import mean_variance_weights, risk_parity_weights
from config import AllocationConfig, DEFAULT_CONFIG


def equal_weight_strategy(
    returns: pd.DataFrame,
    config: AllocationConfig = None,
) -> np.ndarray:
    """
    Equal weight: w_i = 1/n for each asset.

    Simple baseline with no estimation risk.
    """
    n = returns.shape[1]
    return np.ones(n) / n


def mean_variance_strategy(
    returns: pd.DataFrame,
    config: AllocationConfig = None,
) -> np.ndarray:
    """
    Maximum Sharpe ratio weights from sample mean and covariance.

    Uses lookback_window periods for estimation when set.
    Falls back to equal weight if insufficient history.
    """
    cfg = config or DEFAULT_CONFIG
    r = returns
    if cfg.lookback_window is not None:
        r = returns.tail(cfg.lookback_window)
    n = r.shape[1]
    min_periods = n + 10
    if len(r) < min_periods:
        return np.ones(n) / n
    mu = r.mean().values
    cov = r.cov().values
    bounds = cfg.get_bounds(len(mu))
    return mean_variance_weights(
        mu, cov, rf=cfg.risk_free_rate, bounds=bounds
    )


def risk_parity_strategy(
    returns: pd.DataFrame,
    config: AllocationConfig = None,
) -> np.ndarray:
    """
    Risk parity: equal risk contribution per asset.

    Uses lookback_window periods when set.
    Falls back to equal weight if insufficient history.
    """
    cfg = config or DEFAULT_CONFIG
    r = returns
    if cfg.lookback_window is not None:
        r = returns.tail(cfg.lookback_window)
    n = r.shape[1]
    min_periods = n + 10
    if len(r) < min_periods:
        return np.ones(n) / n
    cov = r.cov().values
    bounds = cfg.get_bounds(cov.shape[0])
    return risk_parity_weights(cov, bounds=bounds)


def get_strategy(name: str):
    """Return strategy function by name."""
    strategies = {
        "equal_weight": equal_weight_strategy,
        "mean_variance": mean_variance_strategy,
        "risk_parity": risk_parity_strategy,
    }
    if name not in strategies:
        raise ValueError(f"Unknown strategy: {name}. Choose from {list(strategies)}")
    return strategies[name]
