# RECALL ON TOM'S OWN DAX TRADES (card tom-dax-recall, H1 of PROBE_PLAN.md), 2026-10-11

**Answer.** On the 7 entries Tom shows on his own DAX charts, the coded engine produced **0 signals** (WATCH or
SETUP_FORMING), with the fee term as coded and with DAX fees. Signal recall = **0 / 7**. On 4 entries the engine did have a
same-side candidate within 0.15 % of his entry, but with 1-2 proofs (3 needed); on the other 3 (his spike-top shorts)
it had no same-side candidate near his price at all. By the stop rule in PROBE_PLAN section 4 (recall < 3 for reasons that
are not data limits): **STOP backtests of the current encoding; fix the encoding first.** The DAX backtest stays built
and runs once the encoding changes (it then tests the fix on Tom's home market).

## 1. The trades (read from video frames, not transcripts)
Date = Windows taskbar clock or chart header in the frame; levels = order labels on the chart. Frames: F:/MTS/data/tom_videos/frames.
| id | video | date, local time | side | entry | stop | target | what Tom says the setup is (transcript) |
|---|---|---|---|---|---|---|---|
| T1 | n7ZSkjb7JXs | 2025-12-22 ~07:25 CET, pre-market | short x3 | 24481 | (moved to 24485) | 24422 | no liquidity at the top, pre-market |
| T2 | k0zm5NYn0IQ | 2026-01-08 08:35 CET | short x1 | 25343 | n/s | n/s | counter trade at highs, no liquidity above |
| T3 | ujedEcmvBMk | 2026-05-12 ~10:00 CEST | short x2 | 24229 | 24257 | 24111 | short at pre-market highs, weekly-profile bias |
| T3b | ujedEcmvBMk | 2026-05-12 ~12:00 CEST | short x1 (re-entry after stop) | 24216 | 24236 | 24111 | re-entry at low volume after the stop flush |
| T4 | UOBgXV20yCM | 2026-05-18 ~10:00 CEST | long x1 | 23887 | 23857 | 23962 | Monday gap, P profile, pullback buy signal |
| T5 | T6hDJcHrVBM | 2026-05-19 open spike | short x3 | 24690 | 24753 | 24184 (TP2) | rocket at the open, P-shape exhaustion, inside bar, above an old-high ledge |
| T6 | zQTbdEweG3c | 2026-06-02 ~10:00 CEST | short x1 | 25344 | n/s | n/s | counter-trend at the spike top, liquidity gap + POC target |

Extraction check (operator question 2026-10-11): the T3 transcript says the stop is at "18,258"; the chart says 24257.
Prices, dates and times in the transcripts are not reliable; the frames are. Tom's stops are 20-63 points (0.08-0.26 %).

## 2. Engine at those moments (SnapAt every minute, entry-30 .. entry+5; rules declared in tom_dax_recall.py)
FDAX prices are shifted to the cash-index CFD by the fair-value basis (r 2 %). Declared run:
| id | entry found (UTC) | class | nearest same-side candidate (zone, price, proof) | verdict as coded / DAX-fee |
|---|---|---|---|---|
| T1 | not touched +-60 min | NOT_IN_DATA | - | - |
| T2 | not touched +-60 min | NOT_IN_DATA | - | - |
| T3 | 07:55 | MISS-PROOF | vwap_band_+1 24192.6, proof 2, gross RR 5.09, net RR 0.70 | WAIT_RR / WAIT_PROOF |
| T3b | 09:41 | MISS-PROOF | 4h_vah 24149.7, proof 1 | WAIT_RR / WAIT_PROOF |
| T4 | 07:48 | MISS-PROOF | vwap_band_+2 23824.4, proof 2, gross RR 2.99 | WAIT_RR / WAIT_PROOF |
| T5 | 07:56 | MISS-RULE | none | - |
| T6 | not touched +-60 min | NOT_IN_DATA | - | - |
Post-hoc sensitivity (labelled; added after the declared run because the Dec/Jan futures-CFD offset was ~200 points
against 100-120 in theory, while May/Jun matched theory; anchor = the CFD session extreme within +-90 min):
T1 MISS-PROOF (vwap 24297, proof 2); T2, T5, T6 MISS-RULE; T3, T3b, T4 MISS-RULE because the +-90 min extreme lands on
other bars (cruder anchor). Union over both runs: 0 signals; 4 near-zone candidates with proof <= 2; 3 entries with no candidate.
Candidate types the engine offered around these instants: ct_long/ct_short 47 each, scalp 27, tc_long 7.

## 3. What this says
1. **Two blockers in series, both encoding, not market:** (a) the verdict's net_rr uses the BTC perp fee term (cost = 2 x 0.0005 x entry, src/main/java/datafeed/ExecutionMathConstants.java:17,28), so a
   DAX-sized stop always fails WAIT_RR (T3: gross 5.09 -> net 0.70); (b) the proofs Tom reads at these moments
   (profile shape P/b, exhaustion at a spike, inside bar, weak-high ledge, "no liquidity above") are not proofs in the engine,
   so proof stays at 1-2. Order-flow proofs cannot fire on CFD data, which may cost 1 proof: a data limit, flagged.
2. **His most typical trade is not a candidate type at all:** 3 of 7 (T2, T5, T6) are fades of an opening/morning spike
   top; the engine's zones (VWAP bands, 4h VAH, swing levels) did not sit at his price. Gap context (T4 Monday gap) is now
   specified in conditions/gap_rules.md (27 rules) but not coded.
3. Management is part of the trade: T3 -> stopped -> T3b re-entry; T1/T5 partials with the rest running (PROBE_PLAN M arms).
4. Fees: Tom's 0.1 % stops work on FDAX (about 0.1 point per round turn) and cannot work on BTC perps at 0.05 % per side:
   the DIAG_BTC finding (stops inside the noise, fees ~2.8 R) is a transfer problem on top of the encoding problem.

## 4. Next (cards)
- tom-encode-spike-fade: code the spike-top fade (T2/T5/T6) from his words + these frames as a candidate type with its
  own proofs (profile shape, inside bar, ledge), each sourced; replay on these 7 instants first (recall >= 4/7 to pass).
- tom-verdict-fee-per-market: net_rr fee term per instrument (FDAX vs Deribit), so a DAX test is not judged with BTC fees.
- Then tom-dax-backtest full run (built, waiting), then tom-probe-prereg.
Data: dax_archive holds Dec 2025-Jun 2026 windows now; the full 2024-10..2026-10 download continues in the background.
