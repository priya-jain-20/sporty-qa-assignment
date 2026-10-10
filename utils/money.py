"""EUR amounts use two decimal places, half away from zero.

The slip formats money with two fraction digits. Expected payout is
stake × odds, rounded to cents with that same rule.
"""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
_CENTS = Decimal("0.01")


def eur(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


def parse_amount(text: str) -> Decimal:
    """Read the first amount from labels such as ``Balance: €125.50`` or ``Odds: 2.45``."""
    match = _NUMBER.search(text.replace(",", "").replace("€", ""))
    if match is None:
        raise ValueError(f"No amount found in {text!r}")
    return eur(match.group(0))


def potential_payout(stake: Decimal, odds: Decimal) -> Decimal:
    return eur(stake * odds)
