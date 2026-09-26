"""
app/utils.py
------------
Utility helpers used across route handlers.

Contains price formatting and rounding logic shared by the items routes.

NOTE: This module contains an intentional bug (B5) in the price rounding
helper. The arithmetic produces silently incorrect results for certain
decimal inputs due to a flawed rounding approach.
"""


def round_price(value: float) -> float:
    """Round a price to 2 decimal places for storage and display."""
    return round(value, 2)


def format_price_display(value: float) -> str:
    """Return a human-readable price string, e.g. '$19.99'."""
    return f"${round_price(value):.2f}"
