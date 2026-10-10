"""HTTP client for the sports betting API.

Replace ``Endpoints`` and the request bodies in this module when the API changes.
Tests and page objects call these methods and do not build URLs themselves.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from api.betting_req import BettingReq
from utils.money import eur
from config.config import API_TIMEOUT_SECONDS, BASE_URL, USER_ID


class Endpoints:
    """Swap these paths if the service routes change."""

    MATCHES = "/api/matches"
    BALANCE = "/api/balance"
    PLACE_BET = "/api/place-bet"
    RESET_BALANCE = "/api/reset-balance"


class ApiError(AssertionError):
    """Raised when a call that the test requires does not succeed."""


class BettingApi:
    def __init__(
        self,
        base_url: str = BASE_URL,
        user_id: str = USER_ID,
        timeout: int = API_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.timeout = timeout

    def _headers(self, *, json_body: bool = False) -> dict[str, str]:
        headers = {
            "accept": "application/json",
            "x-user-id": self.user_id,
        }
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _send(self, method: str, path: str, params: dict | None = None) -> BettingReq:
        return BettingReq(
            params=params or {},
            headers=self._headers(json_body=method.upper() == "POST"),
            method=method,
            path=path,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def get_matches(self) -> list[dict[str, Any]]:
        betting_req = self._send("GET", Endpoints.MATCHES)
        if betting_req.status_code != 200 or not isinstance(betting_req.response_body, list):
            raise ApiError(
                f"GET {Endpoints.MATCHES} failed with {betting_req.status_code}: "
                f"{betting_req.response_body!r}"
            )
        return betting_req.response_body

    def get_balance(self) -> dict[str, Any]:
        betting_req = self._send("GET", Endpoints.BALANCE)
        if betting_req.status_code != 200 or not isinstance(betting_req.response_body, dict):
            raise ApiError(
                f"GET {Endpoints.BALANCE} failed with {betting_req.status_code}: "
                f"{betting_req.response_body!r}"
            )
        return betting_req.response_body

    def reset_balance(self) -> dict[str, Any]:
        betting_req = self._send("POST", Endpoints.RESET_BALANCE)
        if betting_req.status_code != 200 or not isinstance(betting_req.response_body, dict):
            raise ApiError(
                f"POST {Endpoints.RESET_BALANCE} failed with {betting_req.status_code}: "
                f"{betting_req.response_body!r}"
            )
        return betting_req.response_body

    def place_bet(self, match_id: str, selection: str, stake: Decimal) -> BettingReq:
        """POST one single bet. ``selection`` is HOME, DRAW, or AWAY.

        The request object is returned for both success and rejection so a test
        can assert 4xx contracts. Stake is sent as a two-decimal JSON number.
        """
        return self._send(
            "POST",
            Endpoints.PLACE_BET,
            params={"matchId": match_id, "selection": selection, "stake": eur(stake)},
        )
