# V111 — Continue research while budget/cash reconciliation is pending

The funded-currency projection previously disabled market research when aggregate active budget intent exceeded current canonical cash. After a manual purchase this could remove an entire currency's research requests while held-position valuation continued independently. That is a data-flow integration defect: market observation does not allocate capital.

When an otherwise valid context has only this budget/cash mismatch, this release restores research requests through the same observation adapters. It retains `ACTIVE_BUDGETS_EXCEED_CURRENT_CASH`, a null reconciled `investment_budget_amount`, the original budget/plan intents and the canonical cash. No budget is resized, apportioned, reserved or promoted to purchasing power. Other invalid account, plan, identity or authority contexts still block research. Class restrictions and explicit quote binding requirements are retained. The existing context fingerprint covers the additional research state. Contexts without this mismatch keep their previous shape and fingerprint behavior.

The cash-plan view carries the research state and explains pending capital reconciliation. It labels the amount as reconciled budget, leaving each plan's declared intent visible. The read-only diagnostic tool prints current research eligibility and request counts by account/currency alongside collector health and live positions. It does not run a market collection, cycle or training.

## Scope and remaining work

This restores research input; it does not complete final recommendations. The audited downstream comparison stages lack complete component sets and a finished final publication integration. Their existing return, risk, counterfactual, utility, cost, sizing and publication requirements remain unchanged. No research packet is marked validated by this release. Learned algorithms, model weights, historical sampling, horizons, recommendation frequency and execution permissions are not changed. Normal application cycles can resume the already-existing research work for the newly eligible context.

## Installation and optional restart

The installer preflights all five code files against known bases, refuses divergences/symlinks/missing old files, backs up changed files and is repeatable. No financial, budget, snapshot or model files are replaced. Without an option it leaves services running.

With `--reiniciar`, after installing it invokes the bundled checked restart tool. This identifies the current listener dynamically, verifies its working directory and local portfolio API, reads job status and refuses to signal a process with a running/queued/pending job or an uncertain identity. It rechecks the listener, sends SIGTERM only to the verified process, waits up to ten seconds and starts the existing launcher after the port is free. It does not force-kill processes or restart the Bridge. The job check is a pre-restart check, not an atomic lock against scheduler activity. Run after the normal cycle has completed.

After a completed post-update cycle, hard-refresh the browser and run the existing diagnostic tool. For a budget/cash mismatch, expected fields include `research_enabled: true`, `research_context_status: MARKET_RESEARCH_ONLY_CAPITAL_RECONCILIATION_PENDING`, an unchanged capital status and null reconciled investment budget. Forecast coverage is reported from actual output; it is not filled in by the UI.

## Validation

Synthetic regressions verify restoration of research across currencies, unchanged cash and plan intent, unchanged financial-capacity blocking in the action builder, retained class/source gates, failed identity/authority contexts, and acquisition through the existing daily observation journal. Restart tests verify that busy, ambiguous, changed or differently located listeners are not signalled. UI tests verify truthful research/capacity messaging and retained currency-filter/PnL behavior.

The old test expecting market research to disappear solely due to budget excess is superseded by these tests. A pre-existing scheduler-fragment fixture omits `_a24_input_bridge` and remains outside the applicable suite. The remaining 96 acquisition/funding/BRAPI/intraday checks pass, alongside the new tests. A local simulation against the supplied private audit confirms restored research requests with unchanged financial facts. Private audit data is not included in this package.
