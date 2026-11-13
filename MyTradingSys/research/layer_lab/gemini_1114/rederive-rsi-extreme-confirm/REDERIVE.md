AGREE

Blind re-derivation of `MyTradingSys/research/rsi_extreme_confirm_2026-11-13` from `PRE_REG.md`, `cells.csv`, and `meta.json` confirms the headline verdict: **FAIL** (`0` of `384` pre-registered cells PASS, `0` ROBUST, with `177` of `384` pooled cells powered at `VAL_n >= 30`).

## 1. Pre-registered pass/fail rule (recorded before reading `RESULT.md`)

From `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md`:
- Family (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md:27-28`): `384` pooled-universe cells (`192` long: `T in {10, 15, 20, 25} x 4 buckets x 4 stops x 3 exits`; `192` short: `T in {75, 80, 85, 90} x 4 buckets x 4 stops x 3 exits`; `family=1` in `cells.csv`).
- Primary metric (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md:40`): `net R per trade = (direction * (exit/entry - 1) - 2 * taker - direction * funding) / (R / entry)`.
- Cell PASS (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md:46`): `VAL_n >= 30`, `VAL_mean_r > 0`, `VAL_lo > 0` (95% cluster-bootstrap CI lower bound), `VAL_plac_p <= 0.05`, `VAL_bh == 1` (BH-10% on VALIDATION over the `384` cells), and `DEV_mean_r > 0`.
- Cell ROBUST (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md:47`): `PASS` and `RECENT_n >= 30`, `RECENT_mean_r > 0`, `RECENT_lo > 0`.
- Verdict (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md:48-49`): `PASS` if any cell is PASS; `FAIL` if none and pooled cells are powered (`n >= 30`); `UNDERPOWERED` otherwise.

## 2. Independent arithmetic from `cells.csv` and `meta.json` (OURS)

Using `cells.csv` (`480` data rows = `384` `family=1` + `96` `family=0` pooled-bucket rows):
- Powered cells (`family=1`, `VAL_n >= 30`): `177 / 384`.
- Individual PASS gates on `family=1` (`384` cells):
  - `VAL_n >= 30`: `177`
  - `VAL_mean_r > 0`: `119` (`26` among `VAL_n >= 30`)
  - `VAL_lo > 0`: `0` (maximum `VAL_lo` among powered cells is `-0.090424`)
  - `VAL_plac_p <= 0.05`: `5`
  - `DEV_mean_r > 0`: `83` (`25` among `DEV_n >= 30`)
- BH-10% formula (`p_(k) <= (k / 384) * 0.10`, step-up):
  - When underpowered cells (`VAL_n < 30`) are gated to `p = 1.0` (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/run.py:205`): `0` cells significant on `VAL_p` (minimum powered `VAL_p = 0.077763 > 0.10/384`) and `0` on `DEV_p`.
  - When applied raw to all `384` `VAL_p` values without the `VAL_n >= 30` gate: `6` cells pass BH-10% (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/cells.csv:17`, `19`, `25`, `63`, `64`, `73` — 1-indexed CSV lines, `VAL_p` from `4.07e-5` to `1.28e-3`), all with `VAL_n = 2` (`VAL_lo = nan`), so `0` pass.
- Recomputed `PASS = 0 / 384`, `ROBUST = 0 / 384`. Verdict: **FAIL** (pooled cells are powered at `177 / 384`, and `0` cells PASS).
- Note on underlying trade-level data: raw kline/trade files are not committed in `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/`, so per-trade `net_r` from raw bars is not independently re-simulated here; all cell-level counts, means, BH, stop/T/BTC aggregations, and PASS/ROBUST verdicts are recomputed from `cells.csv` and `meta.json`.

## 3. Claim comparison against `RESULT.md`

| Claim | Claimed (`RESULT.md`, SOURCED) | Recomputed (`cells.csv` / `meta.json`, OURS) | Status | File:line |
|---|---|---|---|---|
| Headline verdict | `FAIL` | `FAIL` (`177/384` powered, `0` PASS) | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L3) |
| PASS / ROBUST counts | `0 of 384` PASS; `0` ROBUST | `0` of `384` PASS; `0` ROBUST | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L3) |
| BH 10% significant cells | `0 on VALIDATION, 0 on DEV` | `0` VAL / `0` DEV when `n<30` gated (`MyTradingSys/research/rsi_extreme_confirm_2026-11-13/run.py:205`); `6` underpowered (`VAL_n=2`) if raw `VAL_p` used | MATCH (gated) / MISMATCH (raw) | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L3) |
| Regime mix | DEV `57%/34%/9%`, VAL `62%/11%/27%`, RECENT `36%/54%/10%` | DEV `57%/34%/9%`, VAL `62%/11%/27%`, RECENT `36%/54%/10%` | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L4) |
| Powered & positive cell counts | `VAL n>=30: 177 of 384`; `VAL mean>0: 26`; `DEV n>=30 and mean>0: 25` | `VAL_n>=30`: `177`; `VAL_n>=30 & VAL_mean_r>0`: `26` (`119` across all `384`); `DEV_n>=30 & DEV_mean_r>0`: `25` | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L6) |
| Best DEV cell (`long, T=20, b=0, pct1, time24`) | `DEV_n=62, DEV_mean_r=0.284, VAL_n=29, VAL_mean_r=-0.061, RECENT_n=39, RECENT_mean_r=-0.486` | `DEV_n=62, DEV_mean_r=0.283828, VAL_n=29, VAL_mean_r=-0.0607, RECENT_n=39, RECENT_mean_r=-0.486159` | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L12) |
| Stop comparison (`long, low_pct1, tgt2r`) | `DEV=-0.008, VAL=0.228, RECENT=-0.156` | `DEV=-0.008, VAL=0.228, RECENT=-0.156` (mean over `T` on `bucket=-1`) | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L33) |
| Threshold `T=15` long pooled | `DEV_n=137.583, DEV_mean_r=-0.099, VAL_n=56.75, VAL_mean_r=0.18, RECENT_n=61.0, RECENT_mean_r=-0.115` | `DEV_n=137.583, DEV_mean_r=-0.099, VAL_n=56.75, VAL_mean_r=0.180, RECENT_n=61.0, RECENT_mean_r=-0.115` | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L55) |
| BTC alone (`long, T=15, atr100, time24`) | `DEV_btc_n=21, DEV=0.326, VAL_btc_n=3, VAL=0.946, RECENT_btc_n=5, RECENT=-0.781` | `DEV_btc_n=21, DEV=0.326, VAL_btc_n=3, VAL=0.946, RECENT_btc_n=5, RECENT=-0.781` | MATCH | [RESULT.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-extreme-confirm-gemini-1114/MyTradingSys/research/rsi_extreme_confirm_2026-11-13/RESULT.md#L67) |
