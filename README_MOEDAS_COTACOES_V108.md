# V108 — Currency isolation and current reference valuation

The legacy adapter exposed every crypto holding's cost as `amount_eur`, including non-EUR positions. This release restricts that compatibility adapter to explicitly EUR holdings while preserving the multi-currency canonical runtime. The snapshot records the adapter's currency scope from the same DataFrame used by the EUR engine. Decision rules, weights, model files, financial transactions and canonical account balances are not changed by installation.

The dashboard and snapshot-history readers require the new holdings-scope contract as well as the existing EUR cash contract before displaying legacy EUR figures. Earlier snapshots remain on disk and are excluded from these views because their holdings scope is unproven; this does not retroactively certify or repair them. Newly generated, isolated snapshots restore the current EUR result; the 10-minute change requires two eligible snapshots. Historical journals and training data are not rewritten or reset.

The existing funded-currency CoinGecko collector now refreshes current reference captures during normal collection cycles, with a 600-second cache and the existing request, batch, funding and binding checks. It retains a separate latest view in the existing observation directory (`latest_valuation.json`). That JSON file is not read by the daily JSONL journal reader. The first valid daily research observation remains immutable; refreshing the same day's price creates no additional daily learning observation. BRAPI acquisition cadence and historical learning contracts are unchanged.

Accounts and the universal dashboard use the same current-reference selection. Prices require a provider observation time, an age of at most 1,800 seconds (the existing acquisition validity window), a non-future capture and an unchanged binding digest. Missing or stale prices remain unavailable. This window does not assert real-time or executable prices, exchange-session verification, or validated recommendations. New ledger holdings additionally require a quote no earlier than their latest verified BUY/SELL, matched by instrument, account and currency. The ledger is read and verified; no position is created or duplicated.

Account details explain unavailable reference prices instead of reporting a P/L from an old quote. Partial coverage remains partial; unpriced holdings are not assigned zero value. Existing account controls, manual registration and persisted filters are retained.

## Installation

Wait for the active cycle to complete, stop only the Porquinho server, verify and run the pinned installer, then restart the existing launcher and hard-refresh the browser. The installer checks all known source hashes before any replacement, refuses divergent or missing bases and symlinks, backs up changed source files and is safe to repeat. It does not start services, place orders, write balances, modify model files or rewrite snapshots.

## Validation

Synthetic tests: `PYTHONPATH=/path/to/application python test_currency_valuation_v108.py`; `node test_currency_ui_v108.js /path/to/application`. Tests cover mixed-currency holdings with identical symbols, legacy snapshot rejection, current quote refresh without daily journal changes, cache integrity, exact account/currency boundaries, provider times and pre-purchase quote rejection. Existing acquisition, funded-currency, BRAPI and intraday tests also pass (97 applicable tests). A pre-existing scheduler-fragment fixture is excluded because it omits the existing `_a24_input_bridge` dependency; source-only fixtures requiring private opening-state files are not run.

Installation and idempotence are tested against synthetic application roots, including divergent-source preservation and unchanged financial/model sentinel files. User data, account IDs, transaction records and credentials are not included in this package.
