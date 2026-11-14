# CHECK NKN-03 (adversarial review, 2026-11-14)

**Verdict: the builder's UNDERPOWERED / no-edge result holds (numbers reproduce, no look-ahead found). Two non-blocking flags: verdict label order vs PRE_REG DEV gate, placebo is not day-conditioned.**

| # | Check | Result | Evidence |
|---|---|---|---|
| 0 | Context fidelity | OK | study.py implements each frozen item: MARKUP label (L369-373), trap (L293-298), 1h confirm (L299), skip (L300), HM (L317), VWAP-touch entry (L337-355), session-low stop + floor + 1h VWAP stop (L216-243), 20:00 exit, V1/V2 reads (L319-321), pivot at-level (L358). Index filter is a tag only, as the frozen design says (holds on 72.6% of P1 trades). CELLS has 15 rows, 5 primary = RESULT. One exit logic, no hidden cells. Controls need src/phase/side so cannot enter primary masks (L455-469). |
| 1 | Commit order | OK | afc7c80a8 (12:28, PRE_REG + study + tests) before 245c85e1b (12:35, RESULT/results.json/make_result.py). `git diff afc7c80a8 245c85e1b` touches no study/PRE_REG/test file. results.json code_sha256 = sha256 of current study.py (afc6938f...). |
| 2 | DEV/VAL by signal bar | OK | SPLIT_MS compare on sig_ms = day + open + 60 min (L400, L659). |
| 3 | Fees both legs | OK | fee_r = (bp/2e4)(E+X)/dist (L193). Hand trade BTC day 18920: E 66149.31, X 66397.59, dist 1799.3 (gross 0.1380) -> fee 6e-4 x 132546.9 / 1799.3 = 0.0442 R at 12 bp; my script gives 0.044199; 6 bp is half. |
| 4 | Look-ahead / independent recompute | OK | Own loop-based script (scratchpad indep.py: own Wilder RSI9, EMA3, WMA21, ATR, VWAP, stop, exit, no study code) on BTC and ETH, MARKUP, +2%: 7 of 7 trades match study.py on day, entry bar, entry price, exit price, gross R to 6 digits (BTC 2, ETH 5). HM uses epoch 1h bar floor(14:30)-1 (closed), 4h likewise, daily d-1, label for day d uses close d-1 (csv 2024-01-02 close_used 44179.55 = 2024-01-01 close). NKN_BUG=1 makes the look-ahead test fail (ran it). Small sample (7 trades), full coin set not recomputed. |
| 5 | Fill realism | OK (note) | Stop first, gap fills at open (L241), VWAP exit at 1h close. VWAP limit assumed filled on any touch (no queue/partial), a mild optimism; does not matter for a negative result. |
| 6 | Placebo like-for-like | FLAG (non-blocking) | Same coin, side, phase, entry clock, layer flags, exits, fees. But the pool is ALL MARKUP VAL coin-days, not scanner/trap/confirm-armed days, and enters at the open, not a VWAP touch (declared in PRE_REG). So p 0.82 compares a +2% mover day against ordinary days. Real mean -0.129 is below placebo mean -0.065 anyway. Also gi 33 for real k>=385 has no pool slot (falls back to coin pool), trivial. |
| 7 | Primary side/phase | OK | MARKUP long only; MARKDOWN short only in control C4; label known at prior close. |
| 8 | SOURCED/OURS | OK | Labels in PRE_REG match code constants (SCAN 2%/1%, TRAP 10, SKIP 4%, floor 0.5%/0.6 ATR, band 0.25, V1 50, V2 20). No grid. HM/ADX 20 wording consistent. |
| 9 | Universe/provenance | OK | 13 coins on 1m (>=10), BTC included; 20 coins 15m (C6), none excluded (checked results.json); 4h and daily as layer reads; weekly omitted with reason. |
| 10 | Verdict vs gates | FLAG (non-blocking) | All 5 primary n VAL < 100 (28/76/18/9/1) -> UNDERPOWERED is correct on n. But PRE_REG says a cell failing DEV gross >= 2 x fee "is FAIL", and all 5 fail it (dev_check all False; code at L739 gives n<100 precedence). Strictly the frozen text reads FAIL for all five. Either label means no edge; the report should state both. Recomputed from results.json: P4 net12 -0.0153, net6 +0.004, CI low -0.2472; P1 net12 -0.1289, day CI low -0.2399, placebo p 0.8216, BH q 1.0. All match RESULT. |
| 11 | Tests / lint / compile | OK | pytest 27 passed; prereg_context_lint 0 offenders; `python -W error -m py_compile` clean on study.py, test_study.py, make_result.py, fetch_1m.py. |
| 12 | RESULT text vs data | FLAG (trivial) | Funnel VAL: HM 30, VWAP touch 28 (RESULT L60 says 30 reach the touch, 28 enter; the summary line "30 reach the VWAP touch" should be 28). Rest matches. |

Cost of the flags: none changes a number or turns a PASS into anything; they affect wording only.
