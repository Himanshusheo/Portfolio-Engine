"""
Scenario and stress testing for portfolio risk.

Applies market shocks to returns and evaluates portfolio impact.
Reflects risk-management and capital adequacy workflows.
"""

import numpy as np
import pandas as pd


def apply_shock(
    returns: pd.DataFrame,
    shock: np.ndarray,
    date: pd.Timestamp = None,
) -> pd.DataFrame:
    """
    Apply a one-period shock to returns at a given date.

    Shock is additive: shocked_return = original_return + shock_i for each asset.
    If date is None, applies to the last row.

    Args:
        returns: DataFrame of returns.
        shock: 1D array of return shocks per asset (e.g., -0.20 for -20% equity).
        date: Date to apply shock; defaults to last date.

    Returns:
        Copy of returns with shock applied at the specified date.
    """
    out = returns.copy()
    shock = np.asarray(shock).ravel()
    if len(shock) != returns.shape[1]:
        raise ValueError("Shock length must match number of assets")
    idx = date if date is not None else returns.index[-1]
    if idx not in returns.index:
        raise ValueError(f"Date {idx} not in returns index")
    loc = returns.index.get_loc(idx)
    out.iloc[loc] = out.iloc[loc].values + shock
    return out


def stress_test_portfolio(
    weights: np.ndarray,
    shock: np.ndarray,
) -> dict:
    """
    Evaluate portfolio impact under a one-period shock.

    Computes portfolio return under the shock and implied drawdown
    if the shock were applied in isolation.

    Args:
        weights: Portfolio weights (1D).
        shock: Asset-level return shocks (e.g., -0.20 for -20% equity drop).

    Returns:
        Dict with portfolio_return, portfolio_drawdown, shock_magnitude.
    """
    w = np.asarray(weights).ravel()
    s = np.asarray(shock).ravel()
    if len(w) != len(s):
        raise ValueError("Weights and shock must have same length")
    port_return = float(w @ s)
    # Drawdown from 1.0 if shock is applied: value = 1 + port_return, dd = -port_return if negative
    port_drawdown = max(0, -port_return) if port_return < 0 else 0.0
    return {
        "portfolio_return": port_return,
        "portfolio_drawdown": port_drawdown,
        "shock_magnitude": float(np.linalg.norm(s)),
    }


def equity_crash_scenario(
    n_assets: int,
    equity_idx: int,
    crash_pct: float = -0.20,
) -> np.ndarray:
    """
    Build a simple equity-crash shock vector.

    Args:
        n_assets: Number of assets.
        equity_idx: Index of equity asset(s) to shock; others set to 0.
        crash_pct: Return shock (e.g., -0.20 for -20%).

    Returns:
        Shock vector (1D array).
    """
    shock = np.zeros(n_assets)
    shock[equity_idx] = crash_pct
    return shock


def run_stress_test(
    returns: pd.DataFrame,
    weights: np.ndarray,
    shock: np.ndarray,
) -> dict:
    """
    Run stress test: apply shock to returns and compute portfolio metrics.

    Args:
        returns: Historical returns.
        weights: Portfolio weights.
        shock: Shock vector.

    Returns:
        Dict with stressed_returns, stress_result (from stress_test_portfolio),
        and baseline_return (last-period return before shock).
    """
    stress_result = stress_test_portfolio(weights, shock)
    baseline = returns.iloc[-1].values @ np.asarray(weights).ravel()
    shocked = apply_shock(returns, shock)
    shocked_return = shocked.iloc[-1].values @ np.asarray(weights).ravel()
    return {
        "baseline_return": float(baseline),
        "stressed_return": float(shocked_return),
        "stress_result": stress_result,
    }
