# Pre-registration template: backtest readiness (12 items)

Source: research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md section 6 (adopted 2026-10-12, card backtest-readiness-template).
Copy this file next to a layer's pre-registration (or HOME_FIT_AUDIT_<layer>.md) and fill every slot BEFORE any backtest run.
An item with no answer or no evidence line is `NOT_ANSWERED`; the run does not start. Missing data is `NOT_IN_DATA`, never 0.

## 0. Pre-build gate (items 0a-0f; decision q13, 2026-10-14: adopted, "be flexible")

Answer all six in writing before anything is built. A "no" stops the build unless the pre-registration states why it is waived.
Source: research/mts_flow_audit_2026-10-13/REPORT.md section 3.

- 0a Cost: smallest stop or target this idea uses? On BTC fees stay under 0.25 R only with a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry).
- 0b Gross: does a cheap fixed-horizon check on existing data show a raw move of at least 2x the round-trip cost?
- 0c Record: does the source have dated calls or trades we can score on BTC data? Score them first (B162 is the template). No record: hypothesis, never a core.
- 0d Data: does BTC history hold every input the source reads? A missing input is NOT_IN_DATA; nothing is built on it.
- 0e Power: trades in the dev window and the detectable edge; if larger than the claimed edge, write INCONCLUSIVE in advance or do not run (backtest/power_mde.py).
- 0f Kill: which result ends this source for good, and how many redesigns are allowed before it?

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Answer: TODO
Evidence (file:line): TODO

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Answer: TODO
Evidence (file:line): TODO

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Answer: TODO
Evidence (file:line): TODO

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Answer: TODO
Evidence (file:line): TODO

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Answer: TODO
Evidence (file:line): TODO

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Answer: TODO
Evidence (file:line): TODO

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Answer: TODO
Evidence (file:line): TODO

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Answer: TODO
Evidence (file:line): TODO

## 9. Null like-for-like: same session window, same order type, same fill rules.

Answer: TODO
Evidence (file:line): TODO

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Answer: TODO
Evidence (file:line): TODO

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Answer: TODO
Evidence (file:line): TODO

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Answer: TODO
Evidence (file:line): TODO
