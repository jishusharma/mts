# Live read of Fable run R6 (session local_db857283, started 09:13Z, read 2026-10-28 ~09:35Z)

Read from its tree `C:/Users/E-ngineers/IdeaProjects/mts-fable-run6-powered-prereg` (uncommitted; nothing on trunk yet). Read-only; the session was not messaged.

**Where it is:** about 375 messages in; PRE_REG.md, COUNTS.csv (45 rows), COUNTS.md, counts_only.py written; 3 cards drafted (`krown-s8-4h-e2-dev-run`, `krown-s8-4h-validation-read`, `carry-executability-memo-e3`); waiting on a Lab_Guy reviewer Agent for the card stamps; USAGE.md and LAYERS.md modified. Not shipped.

**Result it reached:** one family POWERED: Krown S8 (BBWP squeeze, then break) on 4h, BTC+ETH+SOL pooled over DEV_EXT 2020-21 + DEV 2022-24H1: 807 events on 539 UTC days vs 439 days needed (m 65, z 3.364, cost 0.025 R). Everything else is blocked: S5 229/435, pitchfork 476/763 (cost 0.093 R), Malkan 1d 20, 1w 5. DEV alone is not powered (274/444).

**What it did right:** sealed cut asserted at load and before compute; only OHLC columns loaded; gates run (`verdicts.py check`, `prereg_gate.py`) with outputs pasted; 9 cells with one verdict cell; freeze bar (807 +- 1 %) before any outcome; kill sentence parseable by `verdicts.py backfill`; DEV_EXT is real fetched klines, NOT_IN_DATA marked where missing.

**Two weak points (both go to Opus run O2 before any E2 run):**

| # | Point | Numbers (recomputed here, same formula as `prereg_gate.py`) | Why it matters |
|---|---|---|---|
| 1 | m choice decides the verdict | m 65: z 3.364, n 439 (R6). m 281 (R1 bill, `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:29`): z 3.748, n **523** of 539 = 3 % margin. m 3,018 (R1 cell count): n about 660 > 539 = **not powered** | `prereg_gate.py --m auto` ledger fix is still open (`fable-run2-regate-fixes-1to8`, fix 1); a Krown S5 desk row already read outcomes on DEV, so S8 is a sibling, not a clean new family |
| 2 | Power counted on signals, pass counted on entries | 539 signal days; pass needs entry days >= 439 after the one-position-per-symbol busy rule with a 100-bar (about 17 day) time stop | the busy rule drops signals; worst case cuts days well below 439, so a gate PASS may end INCONCLUSIVE after spending the run |

Smaller: sd 1.37 R is OURS from a Krown S5 CI (R1), not from S8; 4h-bar fills (stated as a lower bound); the same correlated BTC/ETH/SOL move on adjacent days is not one cluster (day-block bootstrap block length not stated).

DECISION (OURS): R6 is not interrupted; its pre-reg stands until O2 reviews it, and the E2 card should depend on O2's ACCEPT.
