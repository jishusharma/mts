# RECALL_DAX_V2 - recall and fire rate of the frozen family A fade encoding (card tom-v2-recall-fire-rate, 2026-10-13, JIS-NUC)

**Verdict: DESIGN FAIL. No proof count in 1..4 keeps recall at 4 of 5 (best: 2 of 5 at k = 1). The chain stops here:
CHECK (T11, T12) was NOT read, the DAX dev backtest does not start, the holdout stays sealed, no BTC run.**

Encoding: `SpikeFadeDetector` PRICE arm exactly as shipped by card tom-encode-spike-fade (no parameter touched).
Rules: spec sections 7 and 14, plus the declared choices in the `tom_dax_recall.py` docstring (V2 section). No trade
outcome, P&L or holdout day was computed. Data: Dukascopy GER40 1m archive, Berlin window 07:00-17:35.

## 1. What was built first: the longer series
The blocker from the encode card (a snapshot's 1m series is 1440 bars, the detector needs 21 sessions) is closed two ways:
- Engine: `MarketDataSnapshot.fetchHistoricalSnapshot` hands the fade call a 40-calendar-day 1m series, only with
  `-Dmts.spikeFade=true` (new `SetupCandidatesBuilder.build(..., fadeKlines1m)` overload; flag off = `null` = unchanged).
  `SpikeFadeFlagOffGoldenTest` (flag-off output equals the pre-change goldens on BTC and GER40) still passes.
- Replay: `dax_engine.py fade` runs the same detector at every window minute with the same trailing series.
  Parity checked on 3 fires (2025-12-22, 2026-01-08, 2026-05-19): zone, stop, proof count and `stop_n5` identical between
  the harness row and a flag-on `dax_engine.py snap` snapshot.

## 2. DESIGN recall (sessions S1-S5; S6 = ES, not replayable)
Unit = session (spec 7); a session is hit if any of its groups is hit. Hit = a fade_short at a window minute whose
zone price is within one stop-width of his basis-adjusted entry, emitted before price has fallen one stop-width below it.
Random = 1000 draws of the same number of random same-session instants (per group, same dates, seed 20261013), each
carrying the running session high; share = draws with recall >= the observed one.
| k (proof count >= k) | Sessions hit | Which | Groups hit | Random share >= observed | Random mean |
|---|---|---|---|---|---|
| 0 (idea only, reference, not in the spec's 1..4) | 4 of 5 | S1, S2, S4, S5 | T1, T2, T2b, T5, T6 | 0.003 | 1.36 |
| 1 | **2 of 5** | S2, S5 | T2, T2b, T6 | 0.157 | 0.78 |
| 2 | 1 of 5 | S2 | T2 | 0.406 | 0.41 |
| 3 | 0 of 5 | - | - | 1.0 | 0.04 |
| 4 | 0 of 5 | - | - | 1.0 | 0 |
k* = largest k in 1..4 with recall >= 4 of 5 = **none**, so the spec 14 test fails before the random comparison matters.

Per group (basis-adjusted entry from `TOM_TRADE_LEDGER.csv`, declared anchor BASIS_R 0.02; width = ledger stop, 20 = A-S2 where no
stop is seen; times UTC):
| Group | Date | His entry (futures) | Adjusted | Width | Window high | Fire minutes | First fire | Zone range of fires | Reading |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2025-12-22 | 24481 | 24363.0 | 20 | 24358.4 | 13 | 08:17 | 24347.8-24358.4 | hit at k=0 only (fires have 0-1 proof) |
| T2 | 2026-01-08 | 25318 | 25219.5 | 20 | 25221.3 | 77 | 08:09 | 25162.3-25221.3 | hit up to k=2 |
| T2b | 2026-01-08 | 25341 | 25242.4 | 22 | 25221.3 | 77 | 08:09 | 25162.3-25221.3 | hit up to k=1 |
| T3 | 2026-05-12 | 24229 | 24178.6 | 36 | 24213.0 | **0** | - | - | no fire at any k: price never above the prior day's high 24368 (A-C2 fails) |
| T3b | 2026-05-12 | 24216 | 24165.6 | 20 | 24213.0 | **0** | - | - | same day, same reason |
| T5 | 2026-05-19 | 24690 | 24648.1 | 63 | 24696.0 | 456 | 07:09 | 24462.5-24696.0 | hit at k=0 only (max 2 proofs, 1 minute at k=2) |
| T6 | 2026-06-02 | 25344 | 25320.4 | 20 | 25363.5 | 30 | 07:54 | 25308.5-25363.5 | hit up to k=1 |
| T6 | 2026-06-08 | 25344 | 25328.7 | 20 | 24742.2 | 0 | - | - | window high 586 points under his level (date wrong) |
Two things drive the fail, both visible in the table and neither fixed here (the encoding is frozen):
1. Few proofs fire where he traded. T1 and T5 fire only at 0-2 proofs, and 3 or more proofs fire on 42 of 360 dev days and 4 on none. P5 and A-S1 are mutually exclusive (spec 16), so the PRICE arm can reach 3 proofs, not 4.
2. T3/T3b (the 2026-05-12 re-entry day, and the second video of the same trade) is outside the A-C2 range form.
   The spec already says a PRICE pass is a pass of the weaker rule; here even the weaker idea condition excludes a ledger trade.

## 3. Iterations (each one is a TRIAL_REGISTRY row)
| # | Rule | Result |
|---|---|---|
| 1 | Fall clock from the session open (the literal reading of "before price has moved one stop-width below his entry") | 0 of 5 at every k, **by construction**: all five DESIGN sessions open more than one stop-width under his entry, so even a candidate at his exact entry price would be a miss. File: `design_result_iter1_literal.json`. A measure that cannot return a hit is not a recall test. |
| 2 | Fall clock starts when price first trades within one stop-width of his entry; the fall is a later bar at or below entry minus width (a detector emitting at his own entry price now scores a hit; unit test) | the table above |
Iteration 2 changes the definition of "fell", not the encoding, and was fixed before the per-group result was read. It is
still a second look at the same five sessions; the DSR count includes both rows.

## 4. Fire rate (dev: 2024-11-04..2026-04-10, 360 Berlin session days after the 10 dropped days)
First-attempt = first fire of the day with proof count >= k (re-entry is another card). Spec 14: no target, only the cap
(2 fills per day) and the random-instant comparison. Power note for a later dev run (spec 14): at k = 1 the
dev period offers 163 first attempts (0.45 per session day) before any fill rule, so 100 fills is not ruled out by the fire rate.
| Proof count | First-attempt days | Per session day | Candidate minutes per day | `stop_n5` median | Share below 0.88 N5 |
|---|---|---|---|---|---|
| k >= 0 | 167 | 0.464 | 110.7 | 1.465 | 0.233 |
| k >= 1 | 163 | 0.453 | 83.0 | 1.433 | 0.239 |
| k >= 2 | 132 | 0.367 | 26.3 | 1.410 | 0.258 |
| k >= 3 | 42 | 0.117 | 1.3 | 1.149 | 0.190 |
| k >= 4 | 0 | 0 | 0 | - | - |
At impulse_rank >= 0.8 the per-day rate is 0.333 / 0.325 / 0.228 / 0.067 / 0 for k = 0..4; at >= 0.9: 0.261 / 0.250 / 0.186 / 0.058 / 0
(spec 13, reported, not chosen). Stop rule of the first attempt: A-S1 125 days, A-S2 42 days. The stop-width census says
24 % of first attempts at k >= 1 sit below Tom's narrowest stop (0.88 N5): the zone is not mostly drawn narrower than his,
which was the spec 11 warning sign.
Read next to recall: a candidate on 45 % of ordinary days with 2 of 5 recall at k = 1 and 0.78 mean random recall is not
yet distinguishable from a clock (share 0.157 against the 0.05 bar).

## 5. CHECK and what stays closed
CHECK (T11, T12) is read once after k* is frozen; there is no k*, so it was **not read** (`tom_v2_recall.py check`
refuses to run without a k*). The DAX holdout (2026-04-11 on) was read only as 20-session lookback context and on the
ledger sessions that spec 7 already excludes; no fire, rate or outcome was computed on any other holdout day.

## 6. What this does and does not say
- Does: the PRICE arm as frozen reaches only 2 of 5 DESIGN sessions once at least one proof is required, and 3+ proofs
  fire on 12 % of dev days and on one of his design sessions (T2/T2b, 5 minutes, none a hit).
- Does not: this is 5 sessions, all EXPOSED, dates inferred, basis the declared theory anchor (observed futures-CFD offset in
  Dec/Jan was ~200 against theory 100-120, which T1/T2 hits are sensitive to). A fail on five sessions says the encoding is
  not demonstrated, not that Tom's idea is wrong.
- Decision for Jis, not taken here: k = 0 (idea only, no proof required) reaches 4 of 5 with random share 0.003. That is
  outside the spec's counts 1..4 and contradicts Tom's "you have proof" (zQTbdEweG3c:28-32), so using it is a spec
  amendment and a new trial row, not a reading of this result. Other options: add the PROFILE arm (cards 3 and 4), or
  stop the Tom v2 DAX chain.

Files: `design_result.json` (every number above, group detail, census), `design_result_iter1_literal.json`;
code `MyTradingSys/backtest/tom_v2_recall.py`, `tom_dax_recall.py` (V2 section), `dax_engine.py fade`;
tests `MyTradingSys/backtest/test_tom_v2_recall.py` (9, fail before the functions exist), `SpikeFadeTest` (+2),
`SpikeFadeFlagOffGoldenTest` (unchanged, passes). Fires (not committed): `F:/MTS/data/tom_v2_recall/design_fires.jsonl`.
