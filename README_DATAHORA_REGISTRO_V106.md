# V106 explicit execution timestamp in the existing investment form

Reuses the existing form, payload builder, review/confirmation endpoints and financial writers. No alternative trade flow, data store or authority is introduced. Only the existing experience JavaScript file is replaced.

The native datetime-local input is changed to a plain text ISO 8601 timestamp with explicit UTC offset (or Z). This avoids browser-localized date input badInput while making timezone interpretation explicit. Dates, times and offsets are checked before the same prior payload validator runs. Naive timestamps, invalid calendar dates, impossible clocks, offsets exceeding 14 hours and unknown-offset -00:00 are rejected. The entered text is retained while the payload is normalized to UTC. No current time is prefilled and no bank or browser timezone is silently assumed.

Direct opening of the existing form now starts with a disabled, empty instrument prompt rather than automatically selecting the first asset. The earlier exact-instrument handoff from the position router still selects that exact identifier after opening. Quantity, price, gross, commission and execution evidence are not autofilled or modified.

Validation: explicit UTC/Lisbon/Brazil offset examples, leap/invalid dates and offsets, payload conversion/restoration, native input replacement, empty instrument selection, zero-fee and precision validation, prior exact-ID handoff/filter tests, installer preflight/repetition/divergence. No live trade was recorded by testing or installation. Successful review and financial commit must be verified separately in the existing application.
