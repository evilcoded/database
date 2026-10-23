# V105 existing investment form validation

Updates only the existing manual-investment payload builder through the existing experience script. No alternate registration, API, model, ledger writer or financial record is introduced.

Zero and zero-like explicit fee values are valid. Empty fees are not silently converted into zero. Reads fields from the active modal first, reports each missing/invalid field by its displayed label, distinguishes browser number-input badInput from missing fields, accepts a single decimal comma when the browser exposes it, and rejects ambiguous thousand/decimal separators. Original decimal strings are retained in the payload rather than normalized through binary floating-point formatting.

The existing arithmetic tolerance is preserved: absolute max(0.01, gross*0.000001). Numeric finite checks prevent NaN/Infinity bypasses. The backend's strict Decimal review remains authoritative and unchanged. Quantity/price/total disagreements are explained with the calculated subtotal; no automatic price, quantity, fee or total correction is performed. Date and account context are checked before constructing the existing BUY review payload. No network request or write is performed by this payload builder.

The reported screenshot's quantity and unit price multiply to 499.7798014752, rather than 500.00. That mismatch is separate from the original generic mandatory-field message; the screenshot alone does not reveal which browser field was being read as empty or invalid.

Tests cover zero/00 fee, empty required fields including fee, browser-invalid input, the screenshot arithmetic discrepancy, decimal comma, ambiguous separators, negative fees, raw quantity precision, invalid date, prior exact-instrument handoff and filter persistence, plus installer preflight/repeat/divergence checks. Browser-local behavior still requires checking the new specific error on the user's machine.
