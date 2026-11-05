# RESULT: Kurisko Quad Rotation DEV event study - NOT RUN, 0 frozen cells (2026-11-05)

Card `kurisko-dev-event-study`. `python run_dev.py` exit 2: `REFUSED: PRE_REG freezes 0 cells: nothing may be run`.
The PRE_REG (commit 86288e03) froze 0 of 8 candidate cells (all BLOCK at `prereg_gate.py`, see `BLOCKED.md`), so no
cell may be run: no forward return, MFE/MAE, placebo or Holm was computed; DEV outcome not read; VALIDATION and HOLDOUT not read.
Run receipt: `run_receipt.json` (status REFUSED; PRE_REG sha, kurisko module sha, seed none). One run per PRE_REG: this one is spent.

Regime mix: not computed (0 frozen cells, no outcome read); DEV window 2022-01..2024-06 BTCUSDT, bull/bear/range split not measured here; no regime-conditioned claim is made.

## Verdict arms
| cell | n | verdict | reason |
|---|---|---|---|
| 1m:stoch:long | 912 | BLOCKED | fee 2.10 R > 0.30 R ceiling; not frozen, not run |
| 1m:stoch:short | 912 | BLOCKED | fee 2.35 R; not frozen, not run |
| 1m:rsi:long | 18 | BLOCKED | 18 event-days, MDE 0.84 SD; not frozen, not run |
| 1m:rsi:short | 14 | BLOCKED | 14 event-days; not frozen, not run |
| 5m:stoch:long | 678 | BLOCKED | fee 0.60 R > 0.30 R ceiling; not frozen, not run |
| 5m:stoch:short | 742 | BLOCKED | fee 0.79 R; not frozen, not run |
| 5m:rsi:long | 3 | BLOCKED | 3 event-days; not frozen, not run |
| 5m:rsi:short | 4 | BLOCKED | 4 event-days; not frozen, not run |

n = event-days from PRE_REG s4 (counts only). No cell is NO EDGE: no outcome was read, so none can FAIL.

## Decisions (OURS)
- The card asks for PASS / FAIL / INSUFFICIENT-N per frozen cell; the PRE_REG froze none. Reported as a contradiction, not re-cut: no cell was added or unblocked, each candidate keeps the PRE_REG BLOCK.
- The later 15m/1h maker-entry PRE_REG (`research/layer_lab/kurisko_quad_1103/PRE_REG.md`) also froze 0 of 24 cells, so no Kurisko cell anywhere is runnable.
- No VALIDATION card (nothing passed). Routes named in PRE_REG s7 (15m/1h, minimum-stop filter, maker entry, tick stop) each need a new PRE_REG and gate.

Kill scope: FAIL/INCONCLUSIVE: stop; this BLOCK (count-only, no outcome read) covers only Quad Rotation on BTCUSDT 1m and 5m with bands (9,3),(14,3),(40,4),(60,10) D-line, the pattern-low stop and a 14 bp taker round trip; 15m and 1h, a minimum-stop filter, a maker entry or a tick stop are untested and need their own PRE_REG and gate.

Reproduce: `python run_dev.py` (exit 2); tests `python -m pytest test_run_dev.py` (8 pass; failed at collection before run_dev.py existed).
