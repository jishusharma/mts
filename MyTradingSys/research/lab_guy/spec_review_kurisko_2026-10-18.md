# Non-Claude Spec Review: Kurisko Quad Rotation (`kurisko-quad-rotation-module` & `kurisko-dev-event-study`)

- **Reviewer**: Gemini 4 Argon (`gemini-4-argon`, low effort, Google AI Pro pool, blind-first from `KURISKO_SPEC.md` s3/s5/s6, `FORMULAS.md` s13/s20, `wavetrend_2026-10-17/PRE_REG.md`, `gross_effect_screen_2026-10-15/PRE_REG.md` lines 25-40)
- **Date**: 2026-10-18
- **Desk task**: `20261018-042506-non-claude-spec-review-kurisko-module-an`
- **Tokens**: in-session (single pass alongside backlog refinement)

## 1. `kurisko-quad-rotation-module` (C2)

- **E2 Definition vs Sources**: `KURISKO_SPEC.md:73` (R8, SOURCED) states Kurisko plots the D line (`"here I'm using the D line. And the D line is the signal line"`) and gives `(9,3), (14,3), (40,4), (60,10)` (`KURISKO_SPEC.md:72-73`). The card's step 2 writes `"fast line = raw %K; full (k,d,s) line = SMA_s(raw %K); %D unused in v0"`, which drops the `3`/`4` smoothing of `(9,3)`, `(14,3)`, `(40,4)` and contradicts both the card's own goal (`stochastic (9,3),(14,3),(40,4),(60,10,10)`) and `KURISKO_SPEC.md:73` (`plotted line = D = SMA_d(K_n)`).
- **E4 Fixture Independence**: With `D_i = SMA_d(raw %K_k)` for the first three bands (`(9,3),(14,3),(40,4)`) and `SMA_10(raw %K_60)` (or `SMA_10(SMA_10(raw %K_60))` for full `(60,10,10)`), every fixture expected value is uniquely determined from closed-bar OHLC without importing `stoch_core.py` (`HH_k == LL_k -> NaN`, first uptick `D9[t] > D9[t-1]` after all four `< 20` on `s..t-1`, one event per episode until any band `>= 20`).
- **E1 / E3 Look-Ahead**: All rolling extrema `HH_k, LL_k` and `SMA_d` use closed bars `t-k+1..t` only; `episode_start_t` is causal (`s <= t`); the planted future-spike mutant test catches `t+1` leaks.
- **Verdict**: `FIX: step 2 in kurisko-quad-rotation-module.json must compute the plotted line as D = SMA_d(raw %K_k) for (9,3), (14,3), (40,4) and SMA_10(raw %K_60) (or full SMA_10(SMA_10(raw %K_60)) for (60,10,10)) per KURISKO_SPEC.md:73 (R8: 'here I'm using the D line'), never unsmoothed raw %K with d=3,4 unused.`

## 2. `kurisko-dev-event-study` (C2)

- **E4 Goal vs Tests/Done_When**: `done_when` and `test_run_dev.py` verify the one-run receipt guard, PRE_REG cell-list and data-SHA pins, the `< 2024-07-01` loader cutoff, and the `FORMULAS.md` s13 net-R hand fixture (`gross_effect_screen_2026-10-15/PRE_REG.md:28-34`).
- **E5 / E7 Pre-Registration & Selection**: Pass bars (`PASS` / `FAIL` / `INSUFFICIENT-N` below the frozen event-day floor), Holm family count `m`, cost (14 bps RT), funding rule (frozen in `PRE_REG.md`), and random-clock placebo seed are locked in `PRE_REG.md` before `kurisko-dev-event-study` runs; `INSUFFICIENT-N` is explicitly separated from `NO EDGE`.
- **E1 / E6 Data & Realism**: Guard refuses missing/mismatched data SHAs, bars `>= 2024-07-01`, or a second run receipt; 14 bps RT cost (`fees.py:27` 5+5 bps taker + 2+2 bps slip OURS) and the stop-distance fee floor (`KURISKO_SPEC.md:76,86`) are enforced before outcome reads.
- **Verdict**: `ACCEPT`
