"""
Load price data from CSV and compute returns.

This module handles reading price series and converting them to
period-over-period returns for use in portfolio analysis.
"""

import numpy as np
import pandas as pd


def read_prices(path: str, date_col: str = None) -> pd.DataFrame:
    """
    Load price data from a CSV file.

    Expects a CSV with a date column and one or more price columns.
    The date column is used as the index; remaining columns are treated as assets.

    Args:
        path: File path to the CSV.
        date_col: Name of the date column. If None, the first column is used.

    Returns:
        DataFrame with DatetimeIndex and asset price columns.
    """
    df = pd.read_csv(path)
    if date_col is None:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    return df.sort_index()


def prices_to_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price series to simple period-over-period returns.

    Return for period t is (price_t - price_{t-1}) / price_{t-1}.
    The first row will contain NaN and is dropped.

    Args:
        prices: DataFrame of prices (index = dates, columns = assets).

    Returns:
        DataFrame of returns.
    """
    returns = prices.pct_change().dropna()
    return returns


def load_and_prepare(path: str, date_col: str = None) -> pd.DataFrame:
    """
    Load prices from CSV and compute returns in one step.

    Args:
        path: Path to CSV file.
        date_col: Name of date column; uses first column if omitted.

    Returns:
        DataFrame of returns.
    """
    prices = read_prices(path, date_col)
    return prices_to_returns(prices)
