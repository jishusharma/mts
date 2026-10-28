# REVIEW_O2: E2 Krown S8 4h post-mortem and the edge program next step (Opus, O2, 2026-10-28)

**E2-AS-FROZEN: yes. Verdict: (a) — park the BTC 4h+ trading-edge program on the R1 §5 STOP list; do not spend VALIDATION (c); hold R7 (72 months to power).**

Question (OPUS_RUNS.md O2): was E2 run as frozen, and what is the edge program's next step: (a) R1 §5 STOP list, (b) one new pre-registered test powered on entry days, or (c) spend VALIDATION anyway?

Scope honored: no outcome column beyond the already-shipped DEV RESULT.md was read, no bar ≥ 2024-07-01 loaded (the recount drops it at load and the test plants one and asserts refusal), VALIDATION/HOLDOUT never touched. All labels SOURCED (file:line) or OURS.

## 1. Independent reproduction of C0 (`recount_o2.py`, not `e2_run.py`)

`recount_o2.py` re-derives the frozen trade model from PRE_REG s2 items 6-8 (not from `e2_run.py`) and runs it on public Binance USD-M 4h klines for BTC/ETH/SOL 2020-01-01..2024-06-30, fetched into a gitignored cache; any bar ≥ 2024-07-01 00:00Z is dropped at load and asserted absent before any computation. The S8 event rule is the repo's own `krown_events.setup_s8` (imported, unchanged).

Reproduced, within 1 % on every number (full list on `recount_o2.py --check`):

| quantity | E2 RESULT.md | O2 recount | Δ |
|---|---|---|---|
| freeze bar: events / days | 807 / 539 | **807 / 539** | 0 |
| C0 n | 420 | 420 | 0 |
| C0 entry days | 332 | 332 | 0 |
| mean net R | +0.1312 | +0.1312 | 0 |
| SE | 0.0760 | 0.0760 | 0 |
| t | +1.73 | +1.725 | <1 % |
| mean gross R | +0.1527 | +0.1527 | 0 |
| 4 × mean fee R | 0.0861 | 0.0861 | 0 |
| busy / floor skips | 386 / 0 | 386 / 0 | 0 |
| verdict | INCONCLUSIVE | INCONCLUSIVE | — |

No mismatches. The single 4×-fee vs fee column I flagged early was my own reference bug (I had stored the *4×* value in the `fee` slot; RESULT.md quotes mean fee 0.0215 and 4×fee 0.0861 — both reproduced).

## 2. E2 checked against PRE_REG s2, item by item

- **Fees** — `backtest/fees.py:27-28` taker 0.0005 / maker 0.0002 (SOURCED, confirmed against source); slippage 0.0002 OURS (`sim_desk SLIP_DEFAULT`). `e2_run.py:29` uses exactly these. Frozen. ✓
- **Stop floor 0.56 %** (4 × 14 bp) — `e2_run.py FLOOR=0.0056`; RESULT 0 of 420 under floor. Frozen. ✓
- **Bracket** — target 2R, stop = far side of last 10 bars incl. signal, 100-bar time stop, stop wins same-bar, market entry next open (taker+slip), target limit maker: `e2_run.py TARGET_R/STOP_BARS/HOLD_BARS=2.0/10/100` + `run_trade`. Frozen. ✓
- **Busy rule** — one position per symbol, signals during a position skipped and counted: `simulate_symbol` `free_from` gate. 386 busy. Frozen; this is what cut 539 signal-days to 332 entry-days. ✓
- **Freeze bar** — 807 events / 539 days ±1 % checked *before any outcome* (else BLOCKED.md): `e2_run.py` main gates at the counts before simulation; RESULT reports 807/539 pass. O2 recount reproduces 807/539. Frozen and honored. ✓
- **Seed / bootstrap** — 2,000 day-block resamples, seed 20261028, FORMULAS 18.7: `e2_run.py RESAMPLES,SEED`. Frozen. ✓
- **No sealed bar** — the `counts_only.load` loader drops `t ≥ CUT_MS` and asserts; O2's independent `guard()` raises on any survivor and `test_recount_o2.py` plants a 2024-07-01 bar and asserts the refusal. Frozen and honored. ✓
- **9-cell structure, verdict only on C0** — `e2_run.py` builds C0 + C1-C8; `verdict()` fires on C0 only; strata carry no word and cannot rescue C0. Frozen. ✓

**E2-AS-FROZEN: yes** — the run honored the frozen spec on every parameter above, and my independent recount reproduces both the 807/539 gate and the C0 block.

**Root finding (why it came back INCONCLUSIVE):** the pre-registration *powered* the test on **signal days (539)** but its verdict statistic is **entry days (332)** after the busy rule. The 807/539 freeze bar is a *counts* gate; it does not power the *entry-day* statistic that `verdict()` actually tests. So E2 was structurally under-powered: in the 2020-01..2024-06 window it could only ever reach 332 entry days, i.e. INCONCLUSIVE was the expected outcome before the run. This is weak point 2 of `opus_run_design_2026-10-28/R6_LIVE_READ.md`, now confirmed by the result. (The C4 long-only t +2.86 is a *stratum* and, per PRE_REG, cannot rescue C0.)

## 3. Next step: verdict (a), with sources

- **The kill line does not fire on this result.** `PRE_REG.md:50/81` kill sentence is scoped to **FAIL** ("PASS_DEV fails with days ≥ 439 -> … STOP"). FAIL is only reachable at entry days ≥ 439. E2 is INCONCLUSIVE at 332 < 439 (PRE_REG s2 "INCONCLUSIVE iff entry days < 439, never FAIL"), so the R1 §5 STOP list is *not* triggered by a FAIL. (a) below is therefore a *reversible park on the absence of power*, not a FAIL verdict.
- **(c) spend VALIDATION anyway — rejected, quantified.** VALIDATION = 2024-07-01..2025-06-30 = 365 days. At E2's entry-day rate 332/1,643 = **0.20 entry day per day** (OURS, from RESULT.md) that is ≈ **73 entry days**, far under 439. Spending the program's one clean OOS read would guarantee another structurally under-powered INCONCLUSIVE and consume the only one-shot read (`krown-s8-4h-validation-read` is one_read; PRE_REG s2 item 11). Wasted.
- **(b) one new pre-registered test powered on entry days — rejected now.** A test powered on entry days needs 439 entry days = 439/0.20 ≈ **2,195 days ≈ 72 months** of *new* data (DEV is exhausted and has been read; R1's rule: nothing mined on DEV is confirmed on DEV). It also **pays m from the ledger** — R1 §2 bills DEV-mined results at m = 281 (z 3.75) or the 3,018-cell count (z 4.31), not R6's m = 65 — so n_needed is *above* 439 entry days, i.e. **longer than 72 months** (and `prereg_gate.py --m auto`'s ledger fix, `fable-run2-regate-fixes-1to8`, is still open, so R6's m=65 was computed by the unfixed gate — weak point 1 of R6_LIVE_READ). Economically a 72-month+ forward test is not a "next step"; it is R7 held.
- **(a) park on the R1 §5 STOP list — chosen.** "pause; delete nothing": reversible, no data destroyed, no mainnet/private move forced. It halts the unpowered 4h+ BTC trading-edge work (the last powered family of R1 E1) and preserves the frozen R7 design. This is the safe default: do not burn the one-shot VALIDATION (c) or commit a 72-month (b) read on a program that is not testable on any available or one-shot window. **Condition to reopen (the single number):** a data window ≥ ~439 entry days, or a cheaper/shorter-stop rule that lifts the entry-day rate above ~0.21/day. Log `DECISION (OURS): verdict (a), park on R1 §5; do not spend VALIDATION; hold R7; reopen at ≥ 439 entry days (≈ 72 months) or entry-day rate > 0.21/day.`

## 4. R7 forward test: **HOLD** (design stays; forward trading not started now)

At 0.20 entry days/day, a powered forward read (439 entry days, m = 65) is **≈ 72 months**; paying the ledger m-bill (≥ 281) makes it longer still. R7's DEV anchor (E2) is INCONCLUSIVE, not a PASS the forward test would extend. R7's own handover (`fable-run7-forward-test` note) already says "Run only if REVIEW_O2.md says R7 = run." It does not: **HOLD** the frozen R7 design on trunk, do not start the forward testnet trade now; revisit when a ≥ 72-month window or a higher entry-day rate exists. Log `DECISION (OURS): R7 = hold (72 months to a powered forward read); no new raw card (verdict ≠ b).`

## 5. Must-fixes (for the record; do not reopen while parked)

1. **M1 (root cause, design):** power was set on signal days; the verdict statistic is entry days. Any re-activation must power on entry days (0.20/day here) → 439 entry days ≈ 72 months.
2. **M2 (resource):** the one-shot VALIDATION window (365 days → ~73 entry days) is under-powered and must not be spent while parked; spending it now guarantees another INCONCLUSIVE and burns the clean OOS read.
3. **M3 (multiple comparisons):** a fresh pre-reg pays m ≥ the ledger (R1 §2: m = 281 → z 3.75; 3,018 → z 4.31), raising n_needed above 439 entry days; `prereg_gate.py --m auto`'s ledger fix (`fable-run2-regate-fixes-1to8`) is still open, so R6's m = 65 came from the unfixed gate.

Stamp applied (verdict a): the line `REVIEWED: Opus_O2 2026-10-28 a` is added on its own line to the `note` of `krown-s8-4h-validation-read` and `fable-run7-forward-test`.
