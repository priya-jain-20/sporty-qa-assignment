"""TC-03: Reject a stake above the remaining balance."""

import copy
import json
from decimal import Decimal

import pytest

from api.betting_req import BettingReq
from api.client import Endpoints
from config.config import BASE_URL, CURRENCY, INITIAL_BALANCE, USER_ID
from utils.money import eur

# €30 is a valid stake. €100 is the maximum stake and, after that €30 bet,
# is above the remaining balance. The API must reject it.
SETUP_STAKE = Decimal("30.00")
OVER_BALANCE_STAKE = Decimal("100.00")
MAX_STAKE = Decimal("100.00")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-user-id": USER_ID,
}
PARAMS = {
    "matchId": "",
    "selection": "HOME",
    "stake": SETUP_STAKE,
}


def execute_request(params, headers, method="GET", path=Endpoints.BALANCE):
    betting_req = BettingReq(
        params=params,
        headers=headers,
        method=method,
        path=path,
        base_url=BASE_URL,
    )
    return betting_req.status_code, betting_req.response_body


def _error_text(body) -> str:
    if isinstance(body, dict):
        return " ".join(str(body.get(key, "")) for key in ("error", "message"))
    return json.dumps(body)


@pytest.mark.api
@pytest.mark.critical
def test_stake_above_balance_is_rejected_and_balance_stays_unchanged():
    """Chosen because the API is the control that still applies when the UI is bypassed.

    A client can post a stake the user cannot afford. The balance must stay
    unchanged and must not go negative.
    """
    headers = copy.deepcopy(HEADERS)
    try:
        status, reset_payload = execute_request({}, headers, method="POST", path=Endpoints.RESET_BALANCE)
        assert status == 200, reset_payload
        assert eur(reset_payload["balance"]) == INITIAL_BALANCE, "Reset response balance"
        assert reset_payload.get("currency") == CURRENCY, "Reset response currency"

        status, opening = execute_request({}, headers, method="GET", path=Endpoints.BALANCE)
        assert status == 200, opening
        opening_balance = eur(opening["balance"])
        assert opening.get("currency") == CURRENCY, "Persisted currency after reset"
        assert opening_balance > SETUP_STAKE, "Opening balance must cover the setup bet"

        status, matches = execute_request({}, headers, method="GET", path=Endpoints.MATCHES)
        assert status == 200, matches
        assert matches, "Match catalog is empty"

        params = copy.deepcopy(PARAMS)
        params["matchId"] = matches[0]["id"]
        params["stake"] = SETUP_STAKE
        status, placed = execute_request(params, headers, method="POST", path=Endpoints.PLACE_BET)
        assert status == 200, placed

        status, after_setup = execute_request({}, headers, method="GET", path=Endpoints.BALANCE)
        assert status == 200, after_setup
        remaining = eur(after_setup["balance"])
        assert remaining == eur(opening_balance - SETUP_STAKE), "Balance after the €30 setup bet"
        assert remaining < OVER_BALANCE_STAKE <= MAX_STAKE

        params = copy.deepcopy(PARAMS)
        params["matchId"] = matches[0]["id"]
        params["stake"] = OVER_BALANCE_STAKE
        status, rejected = execute_request(params, headers, method="POST", path=Endpoints.PLACE_BET)
        assert status == 422, rejected
        assert "insufficient" in _error_text(rejected).lower(), rejected

        status, final = execute_request({}, headers, method="GET", path=Endpoints.BALANCE)
        assert status == 200, final
        final_balance = eur(final["balance"])
        assert final_balance == remaining, "Balance must be unchanged after rejection"
        assert final_balance > 0, "Balance must not become negative"
    finally:
        execute_request({}, copy.deepcopy(HEADERS), method="POST", path=Endpoints.RESET_BALANCE)
