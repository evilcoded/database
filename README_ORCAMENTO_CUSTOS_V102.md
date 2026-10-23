# V102 conditional reference budget fit

Adds a commission-aware research budget calculation to the existing route projection. It does not edit learned allocations, source forecasts, weights, models, histories, UI, orders or financial records. Original documentary fee projections are retained for audit.

Uses exact rational arithmetic and a bounded binary search on the documented common-base currency-quantum grid. A single common capital scale preserves all learned investment proportions. The original nominal cash reference is preserved. Each known percentage commission is independently rounded up according to the documented currency quantum. The selected research scale is maximal on that grid subject to invested reference capital plus documented commissions plus the preserved nominal cash reference fitting the original research budget.

This is not complete order sizing: executable instrument quantities, price/amount precision, current quotes, bank availability, personal tax applicability, spread and other unknown costs remain unresolved. Leg notionals may have sub-quantum fractions when preserving exact learned ratios; these are marked and represented as exact rational values. They must not be used as executable order amounts. The grid maximum is not a claim of optimal portfolio allocation. No risk/return re-ranking or automatic fee-inclusive quote interpretation is performed.

`complete_budget_feasibility_proven`, execution and recommendation authorization remain false; unknown-cost allowance and complete net advantage are not fabricated. Original over-budget variants remain visible; new conditional-fit counts are reported separately in the existing API summary.

Validation: nine budget tests, ten existing route tests, prior scenario and filter regression checks; installer preflight, repetition and divergence preservation. Uploaded research scenarios replayed using session-established account metadata: both EUR cases conditionally fit their known commissions; unknown BRL quote is refused. Runtime matching and newly updated scenarios still require local validation.
