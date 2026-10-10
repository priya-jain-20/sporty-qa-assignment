"""Runtime settings. Override with environment variables; do not hardcode them in tests."""

import os
from decimal import Decimal

BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app").rstrip("/")
USER_ID = os.getenv("USER_ID", "candidate-H7YdL80g5fVO")

# Business rules used by TC-01. The reset endpoint must restore this balance.
INITIAL_BALANCE = Decimal("125.50")
STAKE = Decimal("10.00")
CURRENCY = "EUR"

HEADLESS = os.getenv("HEADLESS", "false").lower() in {"1", "true", "yes"}
BROWSER = os.getenv("BROWSER", "chrome")
PAGE_TIMEOUT_SECONDS = int(os.getenv("PAGE_TIMEOUT_SECONDS", "20"))
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "20"))
# Place Bet holds an in-progress state for about 1–4 seconds before the API call.
PLACEMENT_TIMEOUT_SECONDS = int(os.getenv("PLACEMENT_TIMEOUT_SECONDS", "15"))
