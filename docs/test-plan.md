# Test Plan — Single Bet Placement

Six scenarios for one pre-match soccer bet. Priority follows money risk: a wrong balance, a duplicate debit, or a stake the user cannot afford comes before format and authentication checks.

| ID | Title | Priority |
| --- | --- | --- |
| TC-01 | Place a valid bet: balance, receipt, and slip consistency | Critical |
| TC-02 | Rapid double-click on Place Bet does not create duplicate bets | Critical |
| TC-03 | Stake above available balance is rejected and balance never goes negative | Critical |
| TC-04 | Stake boundary values (minimum and maximum) | High |
| TC-05 | Stake format and precision validation (UI and API) | High |
| TC-06 | API authentication and request validation | High |

## TC-01: Place a valid bet: balance, receipt, and slip consistency

**Priority:** Critical

**Risk rationale:** This is the core betting flow. If the balance is not deducted correctly, or if the receipt differs from what the user saw on the slip (payout, teams, odds), users are misled about money and the business could face financial discrepancies or customer disputes.

**Preconditions:** Balance reset to the initial value (€125.50) via `POST /api/reset-balance`.

**Steps:**

1. Open the app with the test user ID and note the header balance.
2. Select the Home (1) odds button on any upcoming match. Note the match, teams (home vs away), and odds.
3. Enter a stake of 10 in the bet slip.
4. Note the potential payout shown on the slip.
5. Click Place Bet and wait for the result.
6. Compare the receipt with the slip and check the header balance.
7. Refresh the page and check the balance again.

**Expected result:**

- Potential payout equals stake × selected odds, using the application's documented currency rounding rules.
- A success receipt appears showing Bet ID, match (home vs away in the same order as the match list), selection, stake, odds at placement, potential payout, and placement timestamp.
- Receipt values match the values shown on the slip before placement.
- Balance is reduced by the stake exactly once (€125.50 → €115.50) and remains €115.50 after refresh.
- Closing the receipt returns to the main flow with no active selection.

## TC-02: Rapid double-click on Place Bet does not create duplicate bets

**Priority:** Critical

**Risk rationale:** Users may double-click or retry when the connection is slow. Duplicate submissions could create unintended bets and deduct the stake more than once. The specification defines a 409 response when a bet is already in progress for the same user.

**Preconditions:** Balance reset to €125.50; a valid upcoming match and user ID are available.

**Steps:**

1. Select an outcome and enter a stake of 10.
2. Click Place Bet twice in quick succession, or attempt repeated submission while the first request is processing.
3. Observe the button state (Placing...) and the resulting receipt or error modal.
4. Refresh the page and check the balance.
5. API variant: send two concurrent `POST /api/place-bet` requests with the same user ID and request body while the first placement is in progress.

**Expected result:**

- The UI enters the loading state after the first submission and prevents accidental repeated submissions while the request is in progress.
- Only one bet is created for the single user action, and the balance drops by the stake once (€125.50 → €115.50).
- For concurrent API requests, a request received while another bet is in progress for the same user is rejected with 409, as specified.
- The final balance remains consistent after refresh.

## TC-03: Stake above available balance is rejected and balance never goes negative

**Priority:** Critical

**Risk rationale:** Accepting a bet the user cannot afford could create negative balances and unintended financial exposure. The specification requires balance validation at both the UI and API layers.

**Preconditions:** A valid user ID and match are available. Initial balance is €125.50.

**Steps:**

1. Reset the balance to €125.50 and verify it using `GET /api/balance`.
2. Place a valid €30 bet and verify that the balance becomes €95.50.
3. Select an outcome and enter a stake of 100, which is within the maximum stake limit but exceeds the available balance.
4. Attempt to place the bet through the UI.
5. Repeat the insufficient-balance check directly through `POST /api/place-bet` using the same user context and a stake of 100.
6. Check the balance in the UI and through `GET /api/balance`.

**Expected result:**

- The UI displays Insufficient balance and blocks placement.
- The API rejects the request with 422 and an appropriate insufficient-balance error.
- No additional bet is placed and the balance remains €95.50.
- The balance never becomes negative, and the UI and API report consistent values.

## TC-04: Stake boundary values (minimum and maximum)

**Priority:** High

**Risk rationale:** Stake limits are important financial controls. Off-by-one errors at the boundaries could allow invalid stakes or reject valid ones.

**Preconditions:** Balance reset to €125.50 before each independent test, as required.

**Steps:** Enter each stake below through the UI and verify the result. Repeat the relevant boundary checks through the API.

| Stake | Expected result |
| --- | --- |
| 0 | Rejected: Minimum stake is €1.00 |
| 0.99 | Rejected: Minimum stake is €1.00 |
| 1.00 | Accepted, subject to clarification of the minimum-stake discrepancy |
| 100.00 | Accepted |
| 100.01 | Rejected: Maximum stake is €100.00 |

**Expected result:**

- Based on the business rules and specified UI copy, stakes from €1.00 to €100.00 inclusive are valid, subject to sufficient balance.
- Stakes outside the permitted range are blocked by the UI and rejected by the API with 422.
- The balance changes only for successfully placed bets.

**Specification clarification:** The business rules state a minimum stake of €1.00, while one validation-table row states €1.01. This plan uses €1.00 based on the business rules and minimum-stake UI message. Confirm the intended boundary with the product owner before treating the discrepancy as a defect.

## TC-05: Stake format and precision validation (UI and API)

**Priority:** High

**Risk rationale:** Invalid precision and nonnumeric input can cause incorrect monetary calculations or inconsistent validation. The API must enforce the rules independently of UI validation.

**Preconditions:** Balance reset to €125.50; a valid user ID and match are available.

**Steps:**

1. In the UI, try entering `abc`, `1,5`, `10.555`, and an empty value in the stake field.
2. Observe what the input accepts and whether the potential payout is calculated correctly.
3. Through the API, submit requests with stake values `"abc"`, `10.555`, `null`, and a missing stake field.
4. Check the response and balance after each request.

**Expected result:**

- The UI accepts numeric input with a single decimal separator and at most two decimal places.
- The UI blocks placement when the stake is empty or invalid.
- The API rejects nonnumeric, over-precise, null, and missing stakes according to the specified validation contract. Semantic validation failures should return 422; malformed JSON should return 400.
- No invalid request creates a bet or changes the balance.
- Potential payout is calculated consistently from the accepted stake and selected odds.

## TC-06: API authentication and request validation

**Priority:** High

**Risk rationale:** The API is the enforcement point for user context, match validity, and selection validity. If it accepts unauthorized or invalid requests, clients could bypass UI validation and place unintended bets.

**Preconditions:** A valid user ID and a known valid match ID retrieved from `GET /api/matches`.

**Steps:**

1. Call `GET /api/balance` without the `x-user-id` header.
2. Call `POST /api/place-bet` with a valid user context but `selection: "WIN"`.
3. Call `POST /api/place-bet` with `matchId: "does-not-exist"`.
4. Send malformed JSON directly to `POST /api/place-bet`, using a raw request body.
5. Send a valid JSON array or string instead of a JSON object.
6. Call `PUT /api/place-bet`.

**Expected result:**

| Case | Expected status |
| --- | --- |
| Missing or invalid `x-user-id` | 401 Unauthorized |
| Invalid selection | 422 Unprocessable Entity |
| Unknown match ID | 422 Unprocessable Entity |
| Malformed JSON | 400 Bad Request |
| Valid JSON that is not an object | 400 Bad Request |
| Unsupported HTTP method | 405 Method Not Allowed |

- No rejected request should create a bet or deduct the user's balance.
- API responses should match the documented error contract. Record any differences as observed results and investigate whether they indicate an implementation defect or an undocumented behavior.
