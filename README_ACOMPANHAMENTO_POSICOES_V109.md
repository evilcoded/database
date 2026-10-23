# V109 — Existing holding references after a manual purchase

V108 correctly rejected stale reference prices but missed two integration contracts. The manual trade path persists canonical BUY/SELL events using `event_type`/`asset_id`; the execution-time reader expected `transaction_type`. Also, current crypto reference refresh depended entirely on research-demand eligibility. An active investment budget above the remaining canonical cash disables those research requests, even when a purchased position still needs valuation.

This package reads BUY/SELL types through the existing canonical transaction translator, including conflict checks. Execution times remain sourced from the verified ledger head and prospective-cutover rules. No event is re-recorded or edited.

The same CoinGecko acquisition stage now combines eligible funded-research jobs with reference jobs for verified positive canonical holdings. It uses the existing instrument/account/currency context, registered account currency, unique explicit provider binding or existing reviewed reconciliation chain, and effective dates. Duplicate or changed contexts fail closed. No ticker, bank, asset availability, execution permission or currency conversion is inferred.

Holding reference jobs do not require available cash or an active investment budget. They do not change a budget or enable research that the existing planning rules blocked. Jobs share the existing transport, network/batch/time limits and latest-reference cache. A quote requested solely for a held position never creates a daily research journal observation. Jobs already eligible for funded research retain the existing immutable daily sampling rule. Cash, positions, models, allocation, sizing and recommendation rules are unchanged.

Collector health is recorded at `results/current_crypto_reference_acquisition_a24.json`: check time, job counts, capital-status counts, provider failure reason or refresh result, and existing false authority flags. It contains no credentials, account IDs or position data. Health write failures do not change acquisition behavior. BRAPI scheduling and source/learning semantics are unchanged.

The bundled `tools/diagnose_current_references_a24.py` reads that health file and the live local portfolio projection. It does not fetch market data, run cycles, train models or alter financial data. The diagnostic displays all returned holding contexts, rather than a special case for a bank or ticker.

## Install and validate

Finish any active cycle, stop the Porquinho server, run the hash-verified installer, and restart the existing launcher. Then run one normal cycle to completion. Inspect with:

```bash
"/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/.venv_recovery_20261021_014049/bin/python" -I -B \
"/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_current_references_a24.py"
```

A provider failure is reported rather than replaced with an assumed price. Successful valuation requires a fresh provider observation no earlier than the latest verified position-changing operation. Missing values stay unknown. Browser hard refresh retains the existing selected currency/account filter.

The installer requires the known V108 code bases, preflights every file, refuses divergent/missing bases and symlinks, backs up changes and is repeatable. It adds one read-only diagnostic tool and updates two application modules. It neither starts services nor runs acquisition itself.

Synthetic tests cover the actual persisted canonical event format, above-cash budgets, zero cash, funded/held job de-duplication, current refresh without extra daily learning, changed and ambiguous contexts, preserved ledger bytes, cache throttling and collection-to-valuation integration. V108 currency isolation/freshness tests and existing acquisition/funding/BRAPI/intraday regression tests remain applicable. User records and credentials are not included.
