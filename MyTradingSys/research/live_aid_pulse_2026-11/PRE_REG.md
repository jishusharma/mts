# PRE-REGISTRATION: Live Aid pulse SETUP FORMING vs matched null, BTCUSDT 1m, fee-net (frozen 2026-11-10)

Card `live-aid-pulse-backtest-1109` (operator ask 2026-11-09: measure the Live Aid Home "pulse" so the coaching is measured). Builder session, JIS-NB worktree.
The commit that adds this file precedes the commit that adds any result; `git log` is the proof. Status: EXPLORATORY TRIAL, DEV only. Nothing here adopts a rule or changes `pulse.js`.
Only counts of setups (no price outcome) from one week (2023-03-01..2023-03-08) were looked at before freezing; one run of the primary cell; no parameter is changed after the first outcome is read.
Labels: SOURCED = file:line in this repo. OURS = our judgement. Every DECISION (OURS) was taken because the repo had no answer; the most conservative reading was chosen.

## 1. Question and the rule under test
Does the pulse "SETUP FORMING" flag (`MyTradingSys/tools/live_aid/pulse.js` `setup()`, l.67-90: price within 0.15 % of a named level on either side, the 1h-4h lean (`g.hi`) pointing away from the level, and at least one RSI/WaveTrend/CVD divergence on 1m-15m agreeing) precede a move in the flagged direction that beats a matched random-time null, fee-net, over the next 15/30/60 min, by session?
The rule is the live code, ported line for line to python (`pulse_port.py`), parity-tested against `pulse.js` and `level_registry.js` through node on fixtures (`test_pulse_parity.py`). Every pulse threshold stays as in the file: `P` = OURS (pulse.js l.12), `WT_HOT` 53 = SOURCED (LazyBear). Thresholds are NOT tuned here; a measured change is a separate card.
Fold wording in the card title ("2m/7m/10m"): the pulse folds 2m, 7m and 10m candles from 1m on UTC-day buckets (pulse.js l.4-5, `foldK`). It is the timeframe grid, not a train/test fold. DECISION (OURS): read that way; no train/test folding, the whole DEV window is one out-of-sample read of fixed rules.

## 2. Data, window, split
| Item | Value | Label |
|---|---|---|
| Tape | Binance USD-M BTCUSDT perpetual 1m klines with taker-buy volume, `F:/MTS/data/tom_raw/klines` (the repo research tape, as `research/gross_effect_screen_2026-10-15/PRE_REG.md` s.2) | SOURCED |
| Difference from the page | the page reads spot/fapi candles live; the card says spot 1m. Spot 1m for the DEV years is not on disk; the perp tape is the proxy. CVD is perp taker flow, not spot | DECISION (OURS) |
| Window | DEV only: decision times 2022-02-01 00:00Z to 2024-06-30 22:00Z (881 UTC days; January 2022 is warm-up for 1000 x 1m and 150 x 4h candles) | DECISION (OURS) |
| Not read | VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07 onward): the loader opens only files named up to `BTCUSDT-1m-2024-06` and asserts every bar is before 2024-07-01 (`study.py load_1m`) | SOURCED (repo split, `backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md`) |
| The card's "90 days" | not used: 90 recent days are 2026 candles, which is HOLDOUT. A 30-month DEV read gives the power the card asks for | DECISION (OURS) |

## 3. What is reproduced and what is NOT_IN_DATA
- Decision times: every 5 minutes (UTC multiples of 5 min). At decision time T only 1m bars with open < T are used; the forming 3m..4h candle is built from the 1m bars so far (the page's last row is the forming candle). Candles per timeframe as the live page holds them: 1000 x 1m (2m, 7m, 10m folded from those), 150 for 3m, 5m, 15m, 30m, 1h, 2h, 4h (`live_aid.html` l.1567). OURS: 5-minute cadence (cost bound).
- Price px = close of the last closed 1m bar.
- Named levels (computed only from bars before T): prior UTC day high/low/close (PDH, PDL, PDC), today's open (DO), weekly open Monday 00:00Z (WO), prior week high/low (PWH, PWL), today's Asia (00-08Z) high/low after 08:00Z. Merged within 0.15 % and laddered by `level_registry.js` logic (ported, parity-tested). Subset of the page's ladder.
- NOT_IN_DATA (no bar-by-bar causal history on disk): analyst levels, VAL/POC/VAH playbook levels, MA strip levels (4h/1d/1w EMA/SMA), VWAP, the Home direction (`homeDir`, passed as null so only the 1h-4h lean can make "big picture" true). Day high/low are excluded on purpose (price making a new extreme is always "at" them). Each is a real difference from the page: the page flags more places and sometimes more setups; this is the measured subset.

## 4. Events, arms, null
- Signal = a decision time where `setup()` returns a setup. Direction = its side (SHORT = -1, LONG = +1). Cooldown (OURS): an eligible signal needs no eligible signal of the same side in the previous 60 min; applied once to the ledger before any outcome is read.
- Entry: open of the 1m bar at T + 1 min (one bar of latency, OURS, as `gross_effect_screen` d=1). Exit: open h minutes later, h in {15, 30, 60}. Gross return G = sgn x (p_out / p_in - 1). An encounter with either bar missing is dropped and counted.
- Cost C = taker in + taker out + slippage: 2 x `BINANCE_TAKER` (0.0005, `backtest/fees.py:27`, SOURCED) = 10 bp, plus 2 bp per side slippage (OURS, `PRE_REG_VOLUME_2026-10-09.md:28` convention) = **14 bp round trip**. Net = G - C. The 10 bp (fee only) net is also written to the JSON. No funding term (horizons <= 60 min; a settlement straddle is rare; stated, not modelled).
- **Null N2 (primary)**: all decision times where the same near-a-level condition holds and `setup()` returns nothing ("near level, not forming"). Its direction is random with the same LONG/SHORT mix as the signals of the scope, so its expected net is (1 - 2p) x mean pool return - C, computed exactly, not drawn. Controls everything except the pulse's lean and divergence.
- Null N1 (secondary): every 5-min decision time in the scope with the same side mix. N3 (secondary, isolates the divergence): near-level pool times with a lean (`g.hi` != 0) and no setup, side = sign of the lean (up lean = LONG), no divergence required.
- Sessions (UTC, OURS): Asia 00-08, Europe 08-13, US 13-21, Late 21-24. The per-session cells use the same null restricted to that session. Regime split (secondary): trailing 30-day close return > +10 % bull, < -10 % bear, else range.
- Statistics: day-clustered bootstrap (resample UTC days with replacement, 4000 draws, seed 7): mean net with 95 % CI, and difference signal minus null with 95 % CI, per horizon x session and per horizon x regime. Events overlap in time (5-min cadence, several levels), so the day cluster is the unit; n counts events and overstates independent samples.

## 5. Pass/fail rule (fixed now; primary cell = h = 30 min, all sessions, all regimes, vs N2)
- N_min = 200 signals. DECISION (OURS).
- **PASS_NET** iff n >= 200 and the 95 % CI of mean net lies wholly above 0 and the CI of (signal - N2) lies wholly above 0.
- **PASS_GROSS_ONLY** iff not PASS_NET and the CI of (signal - N2) in gross terms lies wholly above 0 (the read carries information, but not enough to pay the 14 bp cost).
- **INCONCLUSIVE** iff n < 200.
- **FAIL** otherwise: the pulse flag is a coin flip beyond what being near a level already is, fee-net. FAIL means stop: no coaching claim from the SETUP FORMING flag on BTC perp 1m-4h with these thresholds; a threshold tune needs its own PRE_REG and the VALIDATION read.
- Secondary cells (15 and 60 min, four sessions, three regimes, N1, N3) are printed, carry no verdict, and are counted in the Holm family below. A secondary cell that shows a positive CI is a lead for a PRE_REG, never a finding.

## 6. Gate output (count-only; pasted)
`python scripts/dev/verdicts.py check "live aid pulse setup forming level divergence lean backtest"`:
```
check 'live aid pulse setup forming level divergence lean backtest': no prior row matches (need 6 of ['aid', 'backt', 'diver', 'formi', 'lean', 'level', 'live', 'pulse', 'setup']). Safe to pre-register; append your row after RESULT.
```
`python scripts/dev/prereg_gate.py --n 1500 --sd 0.4035 --cost 0.14 --m auto --new-cells 13 --sd-source "...study.py:cmd_counts"` (units: percent of notional; sd = unconditional 30 min return sd over the DEV window, price only, no rule outcome; n = 1500 is a conservative floor from 521 raw setups in the one week counted (2023-03-01..08), about 125 weeks in the window; 13 new cells = 12 horizon x session cells + the primary):
```
n 1500 sd 0.4035 m 236 z_holm 3.704 MDE 0.047 R + cost 0.14 = 0.187 vs max plausible gross 0.3; n needed 131
PASS: may freeze
```
`MDE 0.047 %` = 4.7 bp at 80 % power for the pooled primary cell; a per-session cell has about a quarter of n and an MDE about twice that.

## Context
Regime: none as a gate, because the pulse is shown in every regime and the claim is not regime-specific; every result reports the bull / bear / range split (secondary cells) and the window mix.
Phase: none, because the 1h-4h lean inside the rule is the page's own phase read; no separate trend-phase filter is added.
Session: by session, gate = the four UTC buckets of section 4 reported separately next to the pooled cell; the verdict uses the pooled cell.
Entry: signal at a 5-min decision time, market entry at the open of the next 1m bar plus one bar of latency, taker in and out, exit by time at h = 15/30/60 min; no stop, no target.
Regime mix: window 2022-02-01..2024-06-30, 881 UTC days, trailing 30-day close return: bull 261 days (29.6 %), bear 185 (21.0 %), range 435 (49.4 %).

FROZEN_UTC: 2026-11-10T08:20:00Z
