# PRE-REGISTRATION: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest), frozen 2026-10-11 before any DAX outcome was computed

Why: PROBE_PLAN.md H5. Tom trades FDAX; coded Tom on BTC shows gross R below a random-entry null. If the same code
has no edge on Tom's own market either, the loss is in our encoding (H1-H4), not in the transfer to BTC.

## Frozen inputs
- Rules: Java engine at the fast-track HEAD of the run (archive mode, `-Dmts.symbol=GER40`), verdict.py and tom_bt.py
  unchanged. No parameter is tuned for DAX. The commit hash goes into the report header.
- Data: Dukascopy DEUIDXEUR 1m BID (cash-index CFD; volume = the feed's own unit, no aggressor split -> taker-buy = half,
  so CVD/delta proofs cannot fire). `MyTradingSys/backtest/dax_data.py`, archive `F:/MTS/data/dax_archive`.
- Snapshots: TomSnapshotGen every 15 min, 2024-11-04 .. 2026-10-09 (the first month of the fetch, from 2024-10-01, is warm-up
  for weekly profiles). A snapshot counts only if a 1m bar exists within the 2 minutes before asOf (market open); closed-market
  snapshots are dropped before any verdict (stale prices otherwise create phantom signals).
- Simulation: tom_bt.sim_limit_trade as is. Closed minutes are filled with flat bars at the last close and volume 0 FOR THE
  SIMULATOR ONLY, so a gap through the stop fills at the reopening bar's open (the sim already uses min/max(open, stop)).
  Holding across the close is allowed (the timeout counts bars, as on BTC); the report states how many trades did.
- Fees: FDAX round turn about EUR 2.5 per contract against EUR 25 per point = 0.1 point: profile `FEES_FDAX` in fees.py,
  0.000005 of price per side on every leg. Stress: + 1 point slippage on stop/timeout legs (`slip` = 1/price).
- Variants: the four of the 2026-10-06 BTC rerun (A, episode, watch_episode, p4_episode), one trade at a time.
- Verdict twice: as coded (Java net_rr carries the BTC perp fee term) and DAX-fee (net_rr := gross_rr). DAX-fee is primary
  for this market; as-coded is reported beside it.
- Null: tom_bt_report.random_entry_null (200 draws, same day, same side and distances), on DAX.

## Periods
- dev = 2024-11-04 .. 2026-04-10. holdout = 2026-04-11 .. 2026-10-09, read ONCE after the dev table is written.
  (The 7 recall instants of tom-dax-recall lie in Dec 2025 .. Jun 2026; recall reads no outcomes, so the holdout stays clean.)
- Pass bar (protocol): >= 100 filled trades in a period and net R 95 % CI lower bound > 0; else "no edge shown" or
  "insufficient N".

## Matched-proof BTC
Re-score the existing BTC rows (F:/MTS/data/tom_bt_2026-10-07 snapshots) with the order-flow proofs masked exactly as on DAX:
book_imbalance null (already), cvd_aligned false, delta_flip not detected, finished_auction not detected (its deltas need
aggressor data); proof_count recomputed as Java counts it minus the masked proofs. Same variants, same verdict pair.
BTC holdout 2026-06-26.. is burned (B147): report dev only for BTC.

## Branch after the run (PROBE_PLAN section 4)
DAX edge, BTC none -> transfer (S/F arms on BTC). No DAX edge -> discretionary edge (Q/M arms on DAX first) or encoding (if
recall was poor). Trial registry: one row per variant x market x verdict-kind; counts go into the DSR of tom-probe-prereg.

## Addendum 2026-10-13 (card tom-holdout-clean-split; original text above unchanged; dates only, no outcome read)
- Ledger dates are not verified trade dates (card rv-fix-tom-ledger-date-column: `date` is empty on all rows), so every recording, inferred and legacy date of every ledger group is treated as a possible trade day (`TOM_LEDGER_CANONICAL_GROUPS.csv` column `date_candidates_to_exclude`).
- Clean holdout: of the 156 archive days in 2026-04-11..2026-10-09, 26 are dropped (each candidate date inside the window +-1 trading day, Sunday session bars with their Monday); 130 remain. Lists: `HOLDOUT_CLEAN.json` (`dropped_days`, `remaining_holdout_days`). Rebuild: `python -I scripts/dev/tom_holdout_split.py`.
- Forward holdout: DAX bars from 2026-10-10 on, read once, only at >= 100 trades; before that no look at any outcome.
- Design/check split: not re-derived here. It is the session split already frozen in `TOM_LAYER_V2_SPEC.md` section 7: DESIGN = T1, T2, T2b, T3, T3b, T5, T6, T7 (sessions S1-S6); CHECK = T11, T12 (S7, S8; recall target 2 of 2 to pass, 1 of 2 inconclusive); T4 is family C (in neither set); T8 excluded. Copied into `HOLDOUT_CLEAN.json` under `split`.
- Dev window: the same candidate dates +-1 trading day leave dev too (10 days listed in `dev_dropped_days`, window 2024-11-04..2026-04-10), as spec section 7 requires for all 9 sessions.
- Every recall iteration on this ledger is a TRIAL_REGISTRY row (N2 iii).
