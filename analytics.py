"""
Performance analytics for portfolio return series.

Metrics used in institutional reporting: annualized return/volatility,
Sharpe ratio, maximum drawdown, and rolling risk.
"""

import numpy as np
import pandas as pd


def annualized_return(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """
    Geometric mean return scaled to annual terms.

    (1 + total_return)^(periods_per_year / n) - 1.
    """
    n = len(returns)
    if n == 0:
        return 0.0
    total = (1 + returns).prod() - 1
    years = n / periods_per_year
    return float((1 + total) ** (1 / years) - 1) if years > 0 else 0.0


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """
    Annualized standard deviation of returns.

    std(returns) * sqrt(periods_per_year).
    """
    if len(returns) < 2:
        return 0.0
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Annualized Sharpe ratio: (mean_excess_return / std_return) * sqrt(periods).

    Excess return is return minus risk-free rate per period.
    """
    excess = returns - rf
    if len(excess) < 2:
        return 0.0
    std_excess = excess.std(ddof=1)
    if std_excess <= 0:
        return 0.0
    return float(excess.mean() / std_excess * np.sqrt(periods_per_year))


def max_drawdown(values: pd.Series) -> float:
    """
    Maximum drawdown: largest peak-to-trough decline as a fraction of peak.

    Drawdown at t = (running_max - value_t) / running_max.
    """
    peak = values.expanding().max()
    dd = (peak - values) / peak
    return float(dd.max())


def rolling_volatility(
    returns: pd.Series,
    window: int,
    periods_per_year: int = 252,
) -> pd.Series:
    """
    Rolling annualized volatility over a fixed window.

    Returns a series of annualized volatilities, NaN for the first window-1 points.
    """
    rolling_std = returns.rolling(window=window, min_periods=window).std(ddof=1)
    return rolling_std * np.sqrt(periods_per_year)


def performance_report(
    values: pd.Series,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> dict:
    """
    Standard performance report for a portfolio value series.

    Returns dict with annualized_return, annualized_volatility, sharpe_ratio,
    max_drawdown, total_return.
    """
    ret = values.pct_change().dropna()
    total_return = float(values.iloc[-1] / values.iloc[0] - 1)
    return {
        "total_return": total_return,
        "annualized_return": annualized_return(ret, periods_per_year),
        "annualized_volatility": annualized_volatility(ret, periods_per_year),
        "sharpe_ratio": sharpe_ratio(ret, rf, periods_per_year),
        "max_drawdown": max_drawdown(values),
    }
