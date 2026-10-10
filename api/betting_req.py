"""Sports-betting request, shaped like AdsReq.

Pass headers and params in. The request runs immediately unless execute_request is False.
GET sends params as the query string. POST sends params as the JSON body.
One session is reused so the connection stays open across calls.
Decimal amounts are written as JSON numbers with their exact digits.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal

import requests

from config.config import API_TIMEOUT_SECONDS, BASE_URL

_session = requests.Session()


def _json_body(payload: dict) -> str:
    """Encode ``payload`` so each Decimal is a JSON number, not a float or a string."""
    marker = uuid.uuid4().hex
    numbers: list[str] = []

    def default(value):
        if isinstance(value, Decimal):
            numbers.append(format(value, "f"))
            return f"{marker}{len(numbers) - 1}"
        raise TypeError(f"{type(value).__name__} is not JSON serializable")

    text = json.dumps(payload, default=default)
    for index, number in enumerate(numbers):
        text = text.replace(f'"{marker}{index}"', number)
    return text


class BettingReq:
    def __init__(
        self,
        params,
        headers,
        method="GET",
        path="/api/balance",
        base_url=BASE_URL,
        timeout=API_TIMEOUT_SECONDS,
        execute_request=True,
    ):
        self.params = params or {}
        self.headers = headers
        self.method = method.upper()
        self.path = path
        self.url = f"{base_url.rstrip('/')}{path}"
        self.timeout = timeout
        self.status_code = None
        self.response_headers = None
        self.response_body = None

        if execute_request:
            self.status_code, self.response_headers, self.response_body = self.execute_betting_request()

    def execute_betting_request(self):
        if self.method == "GET":
            response = _session.get(
                self.url,
                params=self.params,
                headers=self.headers,
                timeout=self.timeout,
            )
        elif self.method == "POST" and not self.params:
            response = _session.post(
                self.url,
                data="",
                headers=self.headers,
                timeout=self.timeout,
            )
        else:
            response = _session.request(
                self.method,
                self.url,
                data=_json_body(self.params),
                headers=self.headers,
                timeout=self.timeout,
            )
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return response.status_code, response.headers, body
