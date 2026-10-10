# Strategy and recommendations

## Why these two tests

**TC-01, UI, place a valid bet.** This is the only journey where the customer chooses an outcome, sees a payout, and receives a receipt. The slip and the receipt are not on the API. A reversed match, a payout that is not stake × odds, or a balance taken more than once is a dispute about money. Automating it locks the critical path and catches UI-only mistakes on every run.

**TC-03, API, stake above the remaining balance.** The test posts a valid €30 bet, then posts €100. That second stake is still inside the €100 maximum and is above whatever balance remains, so the API must return 422 and leave the balance unchanged. On the specified opening balance the remainder is €95.50. The bet slip can be skipped with a direct `POST /api/place-bet`. This check is a single request with a clear expected balance, and it does not need a browser, so it belongs on every change.

Other cases in the test plan are real, but they are either timing-sensitive, blocked on an open product question, or they do not move money. These two cover the customer journey and the server-side financial control.

## Left as manual

**Double-click and the in-progress 409 (TC-02).** The placing window is a short, random delay, and a retry after a lost response is called out in the plan as a clarification rather than a guaranteed rule. An automated race against that window will flake. Exercise it manually, watching the button and the balance, until the API exposes a way to hold the in-progress lock.

**Stake boundaries at €1.00 and €1.01 (TC-04).** The business rules and the minimum-stake message say €1.00. One validation row says €1.01. Automating the boundary now would record a contradiction as a defect. Confirm the limit with the product owner, then add the boundary cases.

**Filters, the error modal, and stake keystrokes (TC-05 UI, date and odds filters, Rebet / Close / X).** These need a person to judge copy, focus, and what the stake field accepts. They do not debit the balance. A short manual pass is enough while the two money tests are still red. The API half of stake precision, and the 401 / 400 / 405 matrix (TC-06), should be the next automated tests once this pair is in place. They are request contracts, not manual explorations.

## If this grows

1. **Split CI.** Run `pytest -m api` on every push. It needs no Chrome and finishes in seconds. Run the UI test headless on the main branch and before release. Give each worker its own `USER_ID`. The current user is shared, and a second run resets the balance under the first.

2. **Close the spec gaps before adding cases.** The reset response says €125.50 while `GET /api/balance` stays at another figure, and the OpenAPI text allows those to differ. Place-bet responses have come back as USD with a negative balance. The receipt omits the selection and does not use stake × odds. Agree the persisted reset balance, EUR as the only currency, the payout formula, and a selection field on the receipt. Then the automated asserts stop depending on interpretation.

3. **Add a contract layer, not more browser journeys.** Generate checks from the OpenAPI document for 401 (missing `x-user-id`), 400 (malformed or non-object JSON), 405, and 409. Keep one browser test for the receipt. Further UI cases, such as filters, can wait until the money rules fail the build on their own.
