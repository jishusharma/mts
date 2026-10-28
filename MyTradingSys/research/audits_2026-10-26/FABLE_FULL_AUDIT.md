# FABLE FULL AUDIT — 2026-10-26

Auditor: Fable full-audit session (branch `jis-nuc/fable-audit`, worktree
`mts-jis-nuc-fable-audit`). Trunk baseline for this audit = this worktree's HEAD.
Green ref **576ea9438**. CI-incident red **d39c665a4**, handled by revert **09c0fcc3b**
(re-lands b6ae603af / 576ea9438).

Method: expected numbers were re-derived from `backtest/fees.py` constants,
`backtest/layers/FORMULAS.md` §18.5, and my own test runs — never read off the code
under audit. Research-only ship; no test gate was required. Where a doc was a
point-in-time snapshot, the verdict is marked "as of write time".

## Verdict table

### Group 1 — stand-up brief (`research/sim_standing_2026-10-26.md`, bfe807df8)

| # | item | claim | independent re-check | verdict | proof |
|---|------|-------|----------------------|---------|-------|
| 1.1 | ETH data gate | ETH 1m data not yet fetched; only BTC on `F:/MTS/data/tom_raw/klines` | counted on-disk: **89** `BTCUSDT-1m-*`, **0** `ETHUSDT-1m-*` | MATCH | my `ls` run; `studies/_bars.py:18` ROOT, `:40` SYMBOL_PARAM |
| 1.2 | 3 lane raws missing | `sim_ideas_raw/{argon,astra,fable}.md` all absent | as of write time (trunk ec00608e) all 3 absent; **since** `astra.md` landed (69f7df712, now an ancestor of this HEAD); `argon.md` + `fable.md` still absent | MATCH (write time; drift logged as F3) | `git merge-base --is-ancestor 69f7df712 HEAD` → yes; `ls research/sim_ideas_raw/` → astra.md only |
| 1.3 | FABLE_TESTED_PAGE_CONTRACT.md missing | card 5ea6032bf closed but the file never landed | `git ls-tree -r HEAD` → no `FABLE_TESTED_PAGE_CONTRACT.md` anywhere; the card's `result` still names it; a redo task exists on HEAD (commit 6ce0c39e6) | MATCH | `research/design_cards_2026-10-26/` (absent); `system/desk_queue/20261026-154448-redo-…-page-cont.json` |
| 1.4 | layer-review parked | layer-review-after-simulator is PARKED | verified against task / desk-queue state on trunk ec00608e at write time | MATCH (write time) | `research/sim_standing_2026-10-26.md` (bfe807df8) |

### Group 2 — per-ship review tables (`research/reviews_2026-10-26/`)

**simv2_accuracy_review.md (7da17db62)**

| # | claim | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 2.1 | page win-rate is net>0 but the ledger cell is gross>0 (flagged gap) | `desk.numbers` win-rate = `(net>0).mean()` at `desk.py:95`; `ladder_run.cell` win-rate = `(gross>0).mean()` at `ladder_run.py:185`; page renders only the net-based figure | MATCH | `sim_desk/desk.py:95`; `levels_confluence_2026-10-14/ladder_run.py:185` |
| 2.2 | slippage default 2 bps (0.02%), OURS, merged into the taker leg only | `SLIP_DEFAULT=0.02` (percent) at `_bars.py:23` ("ours"); merged taker at `:176` (`taker=(taker_pct+slip_pct)/100`) and replayed at `:207`; `levels.py:169` consumes `slip_pct`; T06 `costs.csv:203-205` documents the 3 rows | MATCH | `sim_desk/studies/_bars.py:23,176,207`; `dsa_backtest_audit_…/scripts/T06/costs.csv:203-205` |
| 2.3 | MC band = 1000 fixed-seed shuffles, seed 7; luck line `sd·√(2 ln N)/√n` | `desk.py:107` `monte_carlo(shuffles=1000, seed=7)`; two identical calls → identical output (my run: deterministic True); luck line numeric: `desk.luck(1.0,60,1000)=0.4798526` == `√(2 ln 1000)/√60 = 0.479853` | MATCH | `sim_desk/desk.py:99-121`; my re-derive run |

**sim_ux_review.md (604619a1)** — 5/5 HOLDS; 6 STALE published pages flagged as
non-defect.

| # | claim | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 2.4 | launcher / build / breakdown / MTS-Home commits all HOLD | full `sim_desk` suite (my run): **100 passed, 7 skipped** — covers `test_launcher.py`, `test_build2.py`, `test_conditions.py`, `test_desk.py` | MATCH | my pytest run |
| 2.5 | 6 STALE published pages are non-defect | stale published pages are snapshot artifacts, not defects; not independently re-derivable without re-running the desk publisher, and the review classifies them non-defect — concur | CANNOT-VERIFY (non-defect; no re-run) | `reviews_2026-10-26/sim_ux_review.md` |

**krown_study_review.md (40aa6008c)**

| # | claim | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 2.6 | Krown S4 (coil break) is correctly labelled OURS | `krown_params.json` coil/range entries labelled OURS; no Krown-extract rule backs S4 | MATCH | `backtest/layers/krown/params/krown_params.json` |
| 2.7 | Krown default run n 35, mean +0.278 R | matches `results/desk-krown-634f1a37.json` kpis and `TRIALS.md:280` | MATCH | `sim_desk/results/desk-krown-634f1a37.json`; `layer_lab/TRIALS.md:280` |
| 2.8 | planted-leak test has power and is fwd-index-lint clean | `test_krown.py:45-55` builds the mutated series with `np.concatenate` (no forward index); my re-run: **8 passed** | MATCH | `sim_desk/test_krown.py:44-68`; my pytest run |
| 2.9 | fee-net hand-check stated "fee 3.5818 R / net 1.96418 R" | hand math from `fees.py` constants: fee = `(0.0005·100 + 0.0002·104)/2 = 0.0354 R`, net = `1.9646 R`. The review's stated 3.5818 / 1.96418 are **off** (the test's own comment `test_krown.py:67  # 1.96418 R` carries the same off value). The test's asserted expression and its passing result are correct; only the prose numbers are wrong | MISMATCH (minor, prose only; HOLDS verdict stands) | `sim_desk/test_krown.py:58-68`; `backtest/fees.py:27-28`; my re-derive run → F1 |

### Group 3 — Fable per-layer review (`research/layer_review_2026-10-26/`)

| # | claim | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 3.1 | 13 families: FAILED 7 / NOT ENOUGH DATA 6 / 0 proven-promising | tally re-counts against `TRIALS.md`: wavetrend n 369 FAILED (`:273`), rsi n 2 NED (`:274`), krown n 35 NED (`:280`) — consistent | MATCH | `layer_lab/TRIALS.md:273,274,280` |
| 3.2 | fee-stop rule: stop ≥ 4× round-trip fee; taker floor 0.40% is consistent; maker floor 0.20% is labelled SOURCED | single-leg fees 0.0005/0.0002 (`fees.py:27-28`) → taker round-trip 0.10% → 4× = **0.40%** (matches the taker floor). The 0.20% maker floor does not fall out of 4× a maker round-trip (0.04% → 0.16%); it is labelled SOURCED from the gate study, so it is a source number, not an OURS derivation I can contradict | MATCH (taker re-derived; maker is source-labelled, not re-derived) | `backtest/fees.py:27-28`; `layer_review_2026-10-26/PER_LAYER_REVIEW.md:356` |
| 3.3 | K5 14 bp round-trip stop loses to fees (fee 2.1-2.3 R on 1m) | a 14 bp stop (< 200 bp maker floor, < 400 bp taker floor) cannot clear the fee-stop rule → consistent with the FAILED families' fee-net loss | MATCH | `PER_LAYER_REVIEW.md:115-117,358` |

### Group 4 — CI incident (d39c665a4 → 09c0fcc3b, green 576ea9438)

| # | claim | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 4.1 | revert restored the last-green bytes; no forward-fix of trunk | d39c665a4 touches exactly one file (`fable-sim-what-was-tested-page-contract.json`). `git rev-parse d39c665a4~1:<file>` = `4efbcdc2…` = `git rev-parse 09c0fcc3b:<file>` (byte-exact pre-red state); the at-red blob was `2daa278b…` (different) | MATCH | my `git rev-parse` run |
| 4.2 | "is the CI-REVERT doctor warning cleared?" | the audited incident d39c665a4 recovered to green in **~5 min (< 10-min CI_FIX_MIN)**, so it does NOT drive the current warning. The 72 h-window warning is driven by **3 other** slow red→green streaks: 4838ebdb 13.4 m, 5a4e0ef5 41.8 m, ad45837f 18.4 m | MATCH that the incident is not the driver; the warning itself is NOT cleared → F2 | `mts_doctor` CI-REVERT row (my run); the 3 streak commits |
| 4.3 | green ref 576ea9438 is valid | commit 576ea9438 exists on trunk | MATCH | `git log -1 576ea9438` |

### Group 5 — cross-cut: do the docs contradict each other?

| # | check | re-check | verdict | proof |
|---|-------|----------|---------|-------|
| 5.1 | krown n 35 / +0.278 R | consistent across `TRIALS.md:280`, `results/desk-krown-634f1a37.json`, `krown_study_review.md` | MATCH | same 3 sources |
| 5.2 | wavetrend n 369 / −0.158 R; rsi n 2 / −1.036 R | consistent across `TRIALS.md:273-274` and `PER_LAYER_REVIEW` | MATCH | `TRIALS.md:273-274` |
| 5.3 | sim-dashboard-v1 "blocks on contract" | time-stale — the card is now done; a stale statement, not a contradiction | MATCH (stale, not conflicting) | `system/tasks/sim-dashboard-v1.json` (done, closed 2026-10-26T16:24:50Z) |
| 5.4 | any numeric conflict across the three review tables + the layer review | none found | MATCH | — |

## FINDINGS (cards proposed; ≤ 3)

**F1 — krown review + test comment carry an off fee-net prose number (doc only).**
What: `krown_study_review.md` states "fee 3.5818 R / net 1.96418 R" for the 100/98/104
hand-check; the correct values from `fees.py` are fee = **0.0354 R**, net = **1.9646 R**.
The test's own comment `test_krown.py:67  # 1.96418 R` repeats the off figure. The test's
asserted expression and passing result are correct.
Why it matters: a reader recomputing from FORMULAS §18.5 gets a different value and will
distrust the review; the test comment could mislead the next maintainer editing the
hand-check.
Suggested card id: `krown-review-feenet-prose`.

**F2 — CI-REVERT doctor warning is driven by 3 slow red→green streaks, not the audited incident.**
What: the mts_doctor CI-REVERT warning (72 h window) is driven by 4838ebdb (13.4 m),
5a4e0ef5 (41.8 m), ad45837f (18.4 m), each over the 10-min CI_FIX_MIN limit. The audited
d39c665a4 recovered in ~5 min (in-limit) and is not a driver.
Why it matters: anyone trying to "clear the CI-REVERT warning" from this audit will be
pointed at the wrong commit; the warning persists until the 3 streaks fall out of the
window or are addressed.
Suggested card id: `ci-revert-slow-streaks-review`.

**F3 — sim_ideas 3-lane merge is still incomplete (2 of 3 raws missing).**
What: `sim_ideas_raw/` now holds only `astra.md` (landed 69f7df712); `argon.md` +
`fable.md` remain absent, so the lane-3 merge is stuck at 1/3.
Why it matters: the stand-up brief's "lane-3 merge stuck" open item is only partially
resolved; the two outstanding raws are still blockers to the merge.
Suggested card id: `sim-ideas-3lane-merge`.

## Overall verdict

The shipped sim-desk work **HOLDS**. The three per-ship review tables are substantively
correct: simv2_accuracy's flagged win-rate net/gross gap, the 2 bps slippage, and the
fixed-seed MC band all re-derive and match; krown_study's S4-OURS labelling, default n 35
/ +0.278 R, and the powered planted-leak test all hold. The per-layer numbers are
internally consistent with `TRIALS.md`; the fee-stop taker floor 0.40 % re-derives as
4× a 0.10 % round-trip (the 0.20 % maker floor is source-labelled, not an OURS
derivation). The CI incident revert **09c0fcc3b** is a byte-exact last-green revert with
no forward-fix of trunk. One minor doc bug: the krown review's fee-net prose is off (F1).
The CI-REVERT doctor warning persists only because of 3 unrelated slow streaks (F2), not
the audited incident. The 3-lane merge is at 1/3 (F3). **No blocking defect found.**

Cards proposed (research-only; not filed, no test gate): 3 —
`krown-review-feenet-prose`, `ci-revert-slow-streaks-review`, `sim-ideas-3lane-merge`.
