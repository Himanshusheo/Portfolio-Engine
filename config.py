"""
Configuration parameters for portfolio allocation and backtesting.

These settings drive optimization constraints, rebalancing frequency,
and risk metric calculations.
"""

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class AllocationConfig:
    """
    Parameters for portfolio construction and backtesting.

    Attributes:
        risk_free_rate: Per-period risk-free rate (e.g., 0.02/252 for daily).
        rebalance_frequency: "daily" | "monthly" | "quarterly".
        lookback_window: Number of periods used for return/covariance estimation.
        weight_bounds: (min_weight, max_weight) applied to each asset.
    """

    risk_free_rate: float = 0.0
    rebalance_frequency: str = "monthly"
    lookback_window: Optional[int] = None
    weight_bounds: Tuple[float, float] = (0.0, 1.0)
    periods_per_year: int = 252

    def get_bounds(self, n_assets: int) -> Tuple[Tuple[float, float], ...]:
        """Return scipy-optimize style bounds for n assets."""
        lo, hi = self.weight_bounds
        return tuple((lo, hi) for _ in range(n_assets))


DEFAULT_CONFIG = AllocationConfig()
