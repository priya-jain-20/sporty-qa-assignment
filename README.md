# Sports betting QA automation

Two automated checks for single-bet placement on the desktop app:

- **UI:** place a €10 Home bet and compare the receipt, slip, and balance (TC-01).
- **API:** reject a €100 stake after the balance has fallen below €100 (TC-03).

Tests assert the specification. A failure is a product gap.

## Setup

Python 3.9+ and Google Chrome (the UI test drives Chrome; Selenium Manager fetches the driver).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

From the repository root:

```bash
pytest                  # UI and API
pytest tests/ui         # browser journey only
pytest tests/api        # API rule only
pytest -m api           # same API test, selected by marker
```

The UI test opens a Chrome window. Hide it with:

```bash
HEADLESS=true pytest tests/ui
```

## Configuration

| Variable | Default | Used for |
| --- | --- | --- |
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | App and API host |
| `USER_ID` | `candidate-H7YdL80g5fVO` | `x-user-id` header and `?user-id=` |
| `HEADLESS` | `false` | Set `true` to hide the Chrome window |

Both tests reset the same user. Run them one at a time against that user; parallel workers will overwrite each other's balance.

## Layout

```text
config/config.py      base URL, user, stake, opening balance
api/client.py         HTTP client and endpoint paths
api/betting_req.py    request object and shared session
pages/                page objects; each page owns its XPath locators
utils/money.py        euro amounts to two decimal places
model/models.py       slip, receipt, and match values
tests/ui/conftest.py  Chrome and the balance reset for the browser test
tests/api/conftest.py API fixtures only; this suite does not open Chrome
```

Replace a locator in the page file that owns it, and paths in `api/client.py`, when the UI or API changes. Tests call page objects and the client; they do not contain selectors or URLs.

Why these two tests were automated, and what stays manual, is in [docs/strategy-and-recommendations.md](docs/strategy-and-recommendations.md).

## Reporting

`pytest-html` writes a single HTML report on every run. No extra install beyond the requirements file.

```bash
pytest
open reports/report.html
```

`reports/` is not committed. Generate it locally after a run.
