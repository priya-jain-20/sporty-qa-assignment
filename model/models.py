"""Values captured from the UI during TC-01. Amounts are decimal euros."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MatchSelection:
    match_id: str
    home_team: str
    away_team: str
    odds: Decimal

    @property
    def teams(self) -> str:
        return f"{self.home_team} vs {self.away_team}"


@dataclass(frozen=True)
class SlipState:
    teams: str
    selection: str
    odds: Decimal
    stake: Decimal
    potential_payout: Decimal


@dataclass(frozen=True)
class Receipt:
    bet_id: str
    match: str
    selection: str
    stake: Decimal
    odds: Decimal
    potential_payout: Decimal
    placed_at: str
