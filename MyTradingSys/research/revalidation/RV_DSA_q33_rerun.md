VERDICT: SOUND

# RV-DSA Q33 matrix re-run (second eyes)

Date 2026-10-14 UTC. Host JIS-NUC.
Command matrix_q33.py Dumps/backtest/raw_1m_2022/klines F:/MTS/scratch/q33_20261014

## Result
cells 336
tested 186
underpowered 89
survivors 0
smallest q 0.620
events T1_cont 8689, T1_fade 8689, T2_cont 1491, T2b_fade 1275, T3_hold 19282, T3b_through 8427, T4_cont 1870

## Diff against committed
MATRIX_CELLS.csv committed SHA256 63A3EED04C362506F7924ECBE23CF28F90882D8A425B3404C7D4D2F8A865D573
scratch SHA256 identical True
MATRIX_SUMMARY.json byte-identical True

## Findings
None. Reproduction is exact.

## Not checked
RV04 steps 3-4 (spot-recompute, method items) not run; card asked steps 1-2 only.
