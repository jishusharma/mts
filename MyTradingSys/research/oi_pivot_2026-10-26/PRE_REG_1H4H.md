# PRE_REG: OI pivot candidates at 1h/4h, long DEV (card oi-pivot-1h-4h-long-oi-followup)

Frozen 2026-11-05 BEFORE any outcome was computed (the OI archive was downloaded, nothing was scored). Status: DESCRIPTIVE, no edge claim, no trading rule.
Follow-up of PRE_REG.md D3. Every number is OURS unless marked SOURCED. DEV only: bar open < 2024-07-01 (repo DEV cut, SOURCED layer_lab/LAB_BLOCKED_2026-10-17.md:17).

## Reused unchanged from PRE_REG.md
- D2 OI lag (5m stamp T usable by a bar closing at >= T + 5 min), candidates C1-C4, location rule, outcome (k = 1.0 ATR, H = 24 bars, HIT/MISS/AMBIGUOUS/TIMEOUT/CENSORED, AMBIGUOUS counted as MISS), side-matched baseline P_base from every bar, day-clustered ratio SE. Code: candidates.py, imported, not edited.

## DECISIONS (this follow-up)
| # | Parameter | Value | Label |
|---|---|---|---|
| E1 | Sample | BTCUSDT 2022-01-01..2024-06-30 UTC (912 days); no bar with open >= 2024-07-01 is read; rows without a full H inside DEV are CENSORED | window OURS, cut SOURCED |
| E2 | Bars | 1h and 4h aggregated from 1m klines F:/MTS/data/tom_raw/klines (UTC-aligned, incomplete bars dropped, candidates.aggregate) | OURS |
| E3 | OI | Binance public futures metrics 5m sum_open_interest, daily files cached under F:/MTS/data/oi_pivot_2026-10-26; OI read at the TF close with the D2 lag (candidates.oi_at) | source SOURCED (data.binance.vision), lag OURS |
| E4 | 4h-context lookback | 4 bars at both TFs (1h: 4 h; 4h: 16 h) set via candidates.TF_BARS_4H at run time | OURS |
| E5 | Warm-up | none before 2022-01-01 (klines start there); bars without ATR(14) or the 4-bar context are skipped (context NOT_IN_DATA rows dropped from cells) | OURS |
| E6 | Family | card text says "2 TF x 4 x 2 x 2 = 16"; the product is 32. DECISION (OURS): all 32 cells are run and counted (the honest family); the card's 16 is an arithmetic slip | OURS |
| E7 | Day cluster | UTC day of the event bar's open | OURS |

## Context
Added after the run, at the ship gate (prereg_context_lint); no gate below was used, none changes a number above.
- Regime: none, because this is a descriptive probability table over all of DEV; the regime split is reported as a mix line only.
- Phase: none, because candidates.py is frozen and carries no phase gate.
- Session: none, because all UTC hours are pooled (1h/4h bars, 24 h market).
- Entry: none, because no trade is taken; the outcome is a 1-ATR barrier race from the next bar's open.

## Gate lines (pasted, run in this tree before any outcome)
`python scripts/dev/verdicts.py check 'oi pivot reversal'`: `check 'oi pivot reversal': no prior row matches (need 2 of ['pivot', 'rever']). Safe to pre-register; append your row after RESULT.`
`python scripts/dev/prereg_gate.py --n 912 --sd 1.4 --sd-source scripts/dev/prereg_gate.py:7 --cost 0.0 --m auto --new-cells 16`:
`n 912 sd 1.4 m 233 z_holm 3.701 MDE 0.211 R + cost 0 = 0.211 vs max plausible gross 0.3; n needed 449` -> `PASS: may freeze`
`python scripts/dev/prereg_gate.py --n 912 --sd 1.4 --sd-source scripts/dev/prereg_gate.py:7 --cost 0.0 --m auto --new-cells 32`:
`n 912 sd 1.4 m 249 z_holm 3.718 MDE 0.211 R + cost 0 = 0.211 vs max plausible gross 0.3; n needed 452` -> `PASS: may freeze`
n = 912 is the maximum possible day clusters (every DEV day); a cell's own cluster count is smaller. The card's reference bar is n >= 401 (PRE_REG.md at m 89); at today's m the gate needs 452.
DECISION (OURS): frozen DESCRIPTIVE in advance. Each cell reports its day-cluster n against 401 (card) and 452 (gate today); a cell below the bar is underpowered by construction. No Holm verdict, no rule, no edge claim; the outcome is a probability of a 1-ATR reversal barrier, not R, so the gate is a sizing reference only.

## Output
pilot_1h4h_table.csv: one row per cell (tf, candidate, location, context): n_events, n_day_clusters, HIT, MISS, AMBIGUOUS, TIMEOUT, CENSORED, P, P_base, diff, SE_day, z = diff/SE_day, n_vs_401, n_vs_452. 32 rows in layer_lab/TRIALS.md would be one per cell; DECISION (OURS): one TRIALS row naming the 32-cell family, as the pilot did, plus one row per cell.

## Result (2026-11-05, after the freeze above)
Run: `python MyTradingSys/research/oi_pivot_2026-10-26/run_1h4h.py` (45 s). Table: pilot_1h4h_table.csv (32 rows). Bars 21888 (1h) and 5472 (4h) = every DEV hour; OI archive 912 of 912 days.
- Baseline P_base: 1h BOTTOM 0.4855 / TOP 0.4770; 4h BOTTOM 0.4845 / TOP 0.4821 (a 1-ATR barrier race is close to a coin flip, slightly below it).
- Candidate events 14421 over 28 non-empty cells; 4h delta_sign never fires (|delta|/volume >= 0.2 does not occur on 4h bars), so 4 cells are empty.
- n day clusters vs 401: 10 of 32 cells reach 401 (8 at 1h, plus 4h oi_flip AT_LEVEL WITH 523 and 4h pv_oi_div AT_LEVEL WITH 464); vs 452 (gate today): 10. Most-clustered cell: 1h oi_flip OTHER WITH, 836.
- TRIALS.md: 32 cell rows; each names the 32-cell family, so no separate family row was added (deviation from the Output line above, recorded here).
- In the 10 powered cells every |z| < 2 (range -1.88 .. +0.49); diff -0.031 .. +0.008: no candidate moves the reversal probability in a powered cell.
- Largest |z| overall: 4h vol_spike AT_LEVEL WITH diff -0.103 (P 0.380, z -3.85, 290 clusters, SHORT of 401): a 4h volume spike at the prior-day level fading the 4h move reverses LESS often than baseline (continuation lean). One cell of 32, underpowered, events not de-duplicated: a hypothesis for a later pre-registration, not a finding.
- 1h vol_spike OTHER AGAINST +0.050 (z +2.12, 364 clusters, SHORT).
Verdict: DESCRIPTIVE / NO EFFECT in powered cells. No rule, no edge claim; VALIDATION and HOLDOUT unread.
