# Pre-registration template: backtest readiness (12 items)

Source: research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md section 6 (adopted 2026-10-12, card backtest-readiness-template).
Copy this file next to a layer's pre-registration (or HOME_FIT_AUDIT_<layer>.md) and fill every slot BEFORE any backtest run.
An item with no answer or no evidence line is `NOT_ANSWERED`; the run does not start. Missing data is `NOT_IN_DATA`, never 0.

## 0. Pre-build gate (items 0a-0g; decision q13, 2026-10-14: adopted, "be flexible"; 0g added 2026-10-30)

Answer all seven in writing before anything is built. A "no" stops the build unless the pre-registration states why it is waived.
Source: research/mts_flow_audit_2026-10-13/REPORT.md section 3.

- 0a Cost: smallest stop or target this idea uses? On BTC fees stay under 0.25 R only with a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry).
- 0b Gross: does a cheap fixed-horizon check on existing data show a raw move of at least 2x the round-trip cost?
- 0c Record: does the source have dated calls or trades we can score on BTC data? Score them first (B162 is the template). No record: hypothesis, never a core.
- 0d Data: does BTC history hold every input the source reads? A missing input is NOT_IN_DATA; nothing is built on it.
- 0e Power: trades in the dev window and the detectable edge; if larger than the claimed edge, write INCONCLUSIVE in advance or do not run (backtest/power_mde.py).
- 0f Kill: which result ends this source for good, and how many redesigns are allowed before it?
- 0g Operator intent (class C9, 2026-10-30): when the idea comes from the operator's own trading (his levels, his "first touch", his lower highs), does the encoding fire where HE would mark it? Check it on at least 3 of his dated chart notes or screenshots before any run; a definition he has not confirmed is labelled OURS and the result says so. Examples of misses: T087 "first touch" was one 1m touch, he means approach classes (near miss, wick through, close through then fail, accepted); coded KR-L10 cannot see his daily last lower high.

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

## 13. Context (d-context-retest-1104; gate step 3pc, `scripts/dev/prereg_context_lint.py`): the trader's rule is tested with its context or not at all.

Copy this block into the PRE_REG as a `## Context` section, one gate per line, or `none, because ...` (deciding "none" is allowed; forgetting is not):

- Regime: <higher-TF trend / regime gate, e.g. daily close vs SMA200 side; weekly and monthly RSI band (SOURCED Malkan)>
- Phase: <range / break / retest / trend, e.g. tf_break class R (reclaim) only>
- Session: <time-of-day gate, e.g. US cash session, or none, because the rule is daily>
- Entry: <signal bar, or retest: first pullback to the signal level within N bars>

The RESULT.md carries one `Regime mix:` line (bull / bear / range share of the window's weeks, or NOT_IN_DATA with the reason).
Reuse `backtest/research_kit.py` context tags (card context-harness-research-kit) rather than writing a new trend tag; CONTEXT_FILTER_REVIEW_2026-11-04.md lists the existing ones.

Answer: TODO
Evidence (file:line): TODO

## RESULT.md rows every backtest carries (card backtest-log-sanity-and-year-lines-1112; video K31xH GAP_TABLE S5, S6, S8)

- Log sanity (before any metric): the 5 latest trades with entry/exit bar, price and the matching 1m kline open/close; any mismatch stops the run. Helper: `backtest/trade_sanity.py` `log_sanity`.
- Per-year rows: n, mean, sum for each calendar year of entry, next to the pooled number (one bad year can hide in a pooled mean). Helper: `year_side_lines`.
- Long/short rows: n, mean, sum for the long side and the short side (descriptive only). Helper: `year_side_lines`.

