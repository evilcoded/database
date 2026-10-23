# V103 scoped user-reported preview evidence

Adds an immutable private evidence store and an explicit CLI for manual app-preview reports. The public installer contains no user's account IDs, amounts or quantities. Values are supplied locally by CLI arguments. The CLI requires one unique registered manual account matching institution, pricing plan and currency; ambiguous accounts are refused.

A reported amount, explicit commission, total debit and asset quantity are retained with source USER_REPORTED_APP_PREVIEW, a deterministic content identity and local record timestamp. The actual quote timestamp is unknown and stays null. No expiry, current-execution-quote validation, zero spread or zero total cost is inferred. The implied debit per unit is arithmetic on reported values, not a verified execution price or provider price comparison. Repeated identical reports retain the original record instead of creating a new supposed quote time.

Runtime attaches reports only by exact account/instrument/currency/side and identifies exact vs differing research notional. A report at one notional does not establish a fee at another notional. The evidence does not replace documentary cost projections, budget fits, fee models, learned allocations, availability declarations or canonical recommendations. No orders, ledger entries or ML training mutations are performed. Existing UI and filter persistence remain unchanged.

Validation: seven tests for immutability/repetition, integrity, exact scope, amount mismatch, unknown costs and invalid amounts; unique-account CLI check; prior budget/route/filter tests; installer repeat/divergence preflight checks. Local runtime account matching still requires validation on the user's installation.
