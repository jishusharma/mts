# PRE_REG: causal pivot candidates, P(reversal) by TF (card oi-pivot-reversal-probability-by-tf)

Frozen 2026-10-26 BEFORE any outcome was computed. Status: DESCRIPTIVE pilot, no edge claim, no trading rule (see Gate).
Every number is OURS unless marked SOURCED. DEV only: bar open < 2024-07-01 (repo DEV cut, SOURCED layer_lab/LAB_BLOCKED_2026-10-17.md:17).

## DECISIONS (OURS)
- D1 Sample: the card says "30 days of OI that exist" = the recorder snapshots 2026-09-12..10-10, but those days are HOLDOUT. DEV-only wins: use Binance public futures metrics (5m sum_open_interest, free public data) for the LAST 30 DEV days, 2024-06-01..2024-06-30 UTC, with 1m klines from F:/MTS/data/tom_raw/klines. Warm-up days 2024-05-29..31 are read for indicators/levels only; no candidate is counted before 06-01. Outcome look-ahead is capped at 2024-06-30 23:59 (no bar with open >= 2024-07-01 is read); rows without a full horizon are CENSORED.
- D2 OI lag: a metrics row stamped T is used only by bars closing at or after T + 5 min (one extra 5m lag, conservative; the stamp semantic is not documented).
- D3 Long OI path for 1h/4h: the 5m metrics archive covers 2021-12..today, so 1h/4h reads aggregate it (OI at the TF close). Not run here; follow-up card filed (tasks.py new) with the 1h/4h grid. The 1h divergence event study showed no edge (_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md: t -0.65..+1.22), nothing restated.

## Bars and normaliser
5m and 15m bars aggregated from 1m (open first, high max, low min, close last, volume sum, taker_buy_volume sum). Bar i is known at its close. delta = 2*taker_buy - volume (SOURCED FORMULAS.md section on `delta = 2*tbv - v`). ATR = plain SMA of True Range over 14 bars ending at i (SOURCED FORMULAS.md section 12, length 14 OURS). L = 3 bars lookback (OURS).

## Candidates (evaluated at the close of bar i, using bars <= i only; each fires on onset only: true at i, false at i-1)
Each carries a side: BOTTOM (reversal up expected) or TOP.
- C1 oi_flip: OI slope s_i = OI_i - OI_(i-L); fires when sign(s_i) != sign(s_(i-1)), both non-zero. Side: against the L-bar price move (close_i < close_(i-L) -> BOTTOM, > -> TOP, equal -> no fire).
- C2 pv_oi_div: price up (close_i > close_(i-L)) and s_i < 0 -> TOP; price down and s_i > 0 -> BOTTOM.
- C3 delta_sign: bar delta_i opposes the L-bar price move and |delta_i| / volume_i >= 0.2 -> delta > 0 with price down = BOTTOM, delta < 0 with price up = TOP.
- C4 vol_spike: volume_i >= 2 x mean(volume_(i-20..i-1)); close_i < open_i -> BOTTOM, close_i > open_i -> TOP.

## Conditioning
- Location (levels known at the time): AT_LEVEL when, for BOTTOM, low_i <= prior completed UTC day low + 0.5 ATR_i; for TOP, high_i >= prior day high - 0.5 ATR_i. Else OTHER.
- Context: 4h return sign, close_i vs close_(i-48) on 5m (i-16 on 15m): WITH (BOTTOM and return < 0, TOP and return > 0: the candidate fades the prevailing 4h move) or AGAINST (otherwise).

## Outcome (reversal before continuation)
Entry E = open of bar i+1. A = ATR_i (frozen at the close). Reversal hit: price reaches E + k A (BOTTOM; E - k A for TOP) before E - k A (E + k A), k = 1.0, within H = 24 bars from bar i+1. Reported separately: HIT, MISS, TIMEOUT (neither within H), AMBIGUOUS (both barriers in one bar, counted as MISS in the headline P = lower bound), CENSORED (fewer than H bars before the DEV end). P = HIT / (HIT+MISS+AMBIGUOUS+TIMEOUT), CENSORED excluded.
Swing label (outcome annotation only): bar i is a 5-bar pivot (strict, ties are not pivots) known at i+2 (CYCLE_DESIGN.md five-bar rule, SOURCED); never used by a candidate.
Baseline: the same outcome from every bar (per TF and side), P_base. Report diff = P - P_base.
SE: day-clustered ratio estimator over UTC days, SE = sqrt(sum_d (h_d - P n_d)^2) / n (n_d events, h_d hits that day).

## Trial list (counted arms)
2 TF x 4 candidates x 2 locations x 2 contexts = 32 cells; one headline k=1.0, H=24, L=3, no tuning, no other variant run. Appended to layer_lab/TRIALS.md.

## Gate lines (pasted)
`python scripts/dev/verdicts.py check 'oi pivot reversal'`: `check 'oi pivot reversal': no prior row matches (need 2 of ['pivot', 'rever']). Safe to pre-register; append your row after RESULT.`
`python scripts/dev/prereg_gate.py --n 30 --sd 1.4 --sd-source scripts/dev/prereg_gate.py:7 --cost 0.0 --m auto --new-cells 32`:
`n 30 sd 1.4 m 89 z_holm 3.449 MDE 1.096 R + cost 0 = 1.096 vs max plausible gross 0.3; n needed 401` -> `BLOCK: do not freeze`.
DECISION (OURS): the BLOCK is for an R-edge claim. This pilot makes none: it is frozen as DESCRIPTIVE / INCONCLUSIVE in advance, produces no trade rule and no Holm verdict, and a 30-day DEV slice cannot support one (30 clusters, 89-cell family). Any edge claim needs the 1h/4h archive follow-up with n >= 401 clusters or a smaller family.
