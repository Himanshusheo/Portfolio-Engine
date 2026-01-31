"""
Portfolio optimization: mean-variance and risk parity.

Mean-variance finds weights that maximize the Sharpe ratio (or equivalently,
minimize risk for a given return). Risk parity equalizes each asset's
contribution to portfolio variance.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def mean_variance_weights(
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float = 0.0,
    allow_short: bool = False,
    bounds: tuple = None,
) -> np.ndarray:
    """
    Maximum-Sharpe-ratio weights using mean-variance optimization.

    Solves: max (w'mu - rf) / sqrt(w' cov w) s.t. sum(w)=1 and optional bounds.

    Args:
        mu: Expected returns (1D array).
        cov: Covariance matrix.
        rf: Risk-free rate (same units as mu).
        allow_short: If True, allow negative weights (ignores bounds).
        bounds: Optional sequence of (min, max) per asset for scipy.optimize.

    Returns:
        1D array of portfolio weights.
    """
    n = len(mu)
    mu_excess = np.asarray(mu).ravel() - rf

    def neg_sharpe(w):
        """Negative Sharpe ratio (we minimize)."""
        port_ret = w @ mu_excess
        port_var = w @ cov @ w
        if port_var <= 0:
            return 1e10
        return -(port_ret / np.sqrt(port_var))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    if allow_short:
        opt_bounds = None
    elif bounds is not None:
        opt_bounds = bounds
    else:
        opt_bounds = tuple((0, 1) for _ in range(n))
    x0 = np.ones(n) / n

    result = minimize(
        neg_sharpe,
        x0,
        method="SLSQP",
        bounds=opt_bounds,
        constraints=constraints,
    )
    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")
    return result.x


def risk_parity_weights(cov: np.ndarray, bounds: tuple = None) -> np.ndarray:
    """
    Risk parity weights: each asset contributes equally to portfolio variance.

    For variance, the risk contribution of asset i is w_i * (Sigma w)_i.
    We minimize the sum of squared deviations from equal contributions.

    Args:
        cov: Covariance matrix.
        bounds: Optional (min, max) per asset; default (1e-6, 1).

    Returns:
        1D array of portfolio weights.
    """
    n = cov.shape[0]

    def objective(w):
        w = np.asarray(w).ravel()
        sig = w @ cov @ w
        if sig <= 0:
            return 1e10
        total_vol = np.sqrt(sig)
        marginal_contrib = cov @ w
        risk_contrib = w * marginal_contrib
        target = total_vol / n
        return np.sum((risk_contrib - target) ** 2)

    x0 = np.ones(n) / n
    opt_bounds = bounds if bounds is not None else tuple((1e-6, 1) for _ in range(n))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=opt_bounds,
        constraints=constraints,
    )
    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")
    return result.x


def inverse_volatility_weights(cov: np.ndarray) -> np.ndarray:
    """
    Inverse-volatility weighting: w_i ∝ 1/σ_i.

    A simple heuristic that approximates risk parity when correlations
    are moderate. Weights sum to 1.

    Args:
        cov: Covariance matrix.

    Returns:
        1D array of portfolio weights.
    """
    vol = np.sqrt(np.diag(cov))
    inv_vol = 1.0 / np.maximum(vol, 1e-12)
    w = inv_vol / inv_vol.sum()
    return w


def optimize_from_returns(
    returns: pd.DataFrame,
    method: str = "mean_variance",
    rf: float = 0.0,
) -> pd.Series:
    """
    Compute optimal weights from a returns DataFrame.

    Args:
        returns: DataFrame of returns.
        method: One of "mean_variance" or "risk_parity".
        rf: Risk-free rate for mean-variance.

    Returns:
        Series of weights indexed by asset names.
    """
    mu = returns.mean().values
    cov = returns.cov().values

    if method == "mean_variance":
        w = mean_variance_weights(mu, cov, rf=rf)
    elif method == "risk_parity":
        w = risk_parity_weights(cov)
    else:
        raise ValueError(f"Unknown method: {method}")

    return pd.Series(w, index=returns.columns)
