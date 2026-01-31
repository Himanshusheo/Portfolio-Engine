"""
Estimate covariance matrix and volatility from return data.

These are the building blocks for portfolio risk. Volatility is the
annualized standard deviation; the covariance matrix captures both
individual volatilities and correlations.
"""

import numpy as np
import pandas as pd


def sample_covariance(returns: pd.DataFrame) -> np.ndarray:
    """
    Compute the sample covariance matrix of returns.

    Uses the unbiased estimator (ddof=1). Useful for mean-variance
    optimization and risk parity.

    Args:
        returns: DataFrame of returns (rows = dates, columns = assets).

    Returns:
        Square covariance matrix as ndarray.
    """
    return np.cov(returns.values, rowvar=False, ddof=1)


def sample_covariance_frame(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Same as sample_covariance but returns a labeled DataFrame.
    """
    cov = sample_covariance(returns)
    assets = returns.columns.tolist()
    return pd.DataFrame(cov, index=assets, columns=assets)


def volatilities(returns: pd.DataFrame) -> np.ndarray:
    """
    Compute per-asset volatility (standard deviation of returns).

    Returns:
        1D array of volatilities, one per asset.
    """
    return np.std(returns.values, axis=0, ddof=1)


def annualized_volatility(returns: pd.DataFrame, periods_per_year: int = 252) -> np.ndarray:
    """
    Annualize volatility assuming the given number of periods per year.

    Daily data typically uses 252; monthly uses 12.

    Args:
        returns: DataFrame of returns.
        periods_per_year: Scaling factor for annualization.

    Returns:
        1D array of annualized volatilities.
    """
    vol = volatilities(returns)
    return vol * np.sqrt(periods_per_year)


def portfolio_volatility(weights: np.ndarray, cov: np.ndarray) -> float:
    """
    Compute the volatility of a portfolio given weights and covariance matrix.

    Volatility = sqrt(w' @ Sigma @ w).

    Args:
        weights: 1D array of portfolio weights.
        cov: Covariance matrix.

    Returns:
        Scalar volatility.
    """
    w = np.asarray(weights).ravel()
    return np.sqrt(w @ cov @ w)
