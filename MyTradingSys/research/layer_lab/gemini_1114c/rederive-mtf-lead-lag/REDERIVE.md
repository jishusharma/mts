PASS — Blind re-derivation of `MyTradingSys/research/mtf_lead_lag_2026-11-09` from `PRE_REG.md`, `RESULT_dev.json`, and `RESULT_val.json` matches every headline verdict, sample count (`n`/`events`), hit rate, and 3-day fee-net forward return reported in `REPORT.md` (note: `RESULT.md` does not exist in the study folder; `REPORT.md` is the study report).

## Method (Blind Re-derivation)

1. Read `MyTradingSys/research/mtf_lead_lag_2026-11-09/PRE_REG.md:27` (SOURCED: `"no usable early-flip rule from RSI/WT states alone"` when the VALIDATION kill line fails) and parsed `RESULT_dev.json` and `RESULT_val.json` using `MyTradingSys/research/layer_lab/gemini_1114c/rederive-mtf-lead-lag/recompute.py` before opening `REPORT.md`.
2. Recomputed the two kill-line gates in VALIDATION (`RESULT_val.json`):
   - **Hit-rate gate** (`>= base_rate + 10 pp`, where `base_rate_1d_flip_7d = 0.227` / `22.7%` at `MyTradingSys/research/mtf_lead_lag_2026-11-09/RESULT_val.json:232`, SOURCED):
     - R1: `0.387 - 0.227 = +16.0 pp` (OURS; passes `>= 10 pp`)
     - R2: `0.350 - 0.227 = +12.3 pp` (OURS; passes `>= 10 pp`)
     - R3: `0.410 - 0.227 = +18.3 pp` (OURS; passes `>= 10 pp`)
   - **3-day fee-net forward return gate** (`> 2 SE` above `baseline_fwd.3d.mean_pct = -0.100%`, `se_pct = 0.091%`, `n = 2080` at `MyTradingSys/research/mtf_lead_lag_2026-11-09/RESULT_val.json:239-243`, SOURCED):
     - R1 (`mean = -0.003%`, `se = 0.210%`, `n = 394`): diff `+0.097%`, `z = +0.46` using rule SE or `+0.42` using combined SE (OURS; fails `> 2 SE`)
     - R2 (`mean = +0.071%`, `se = 0.174%`, `n = 598`): diff `+0.171%`, `z = +0.98` using rule SE or `+0.87` using combined SE (OURS; fails `> 2 SE`)
     - R3 (`mean = +0.165%`, `se = 0.206%`, `n = 440`): diff `+0.265%`, `z = +1.29` using rule SE or `+1.18` using combined SE (OURS; fails `> 2 SE`)
3. Because none of R1, R2, R3 pass both VALIDATION gates, the pre-registered verdict is **no usable early-flip rule from RSI/WT states alone** (OURS).

## Claim Table

| Claim | Recomputed (OURS) | Stated (SOURCED) | Source `file:line` | Status |
|---|---|---|---|---|
| Headline kill-line verdict | All 3 rules pass VAL hit-rate gate (`>= +10 pp`), all 3 fail 3d return `> 2 SE` gate (max `z = +1.29` rule SE / `+1.18` combined SE); no usable early-flip rule from RSI/WT states alone | `"no usable early-flip trigger from RSI/WT states alone; R3 is a valid anticipation filter."` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:33` | MATCH |
| R1 VAL (events, hit rate, 3d fee-net mean & SE) | `events=395`, `hit=38.7%` (`+16.0 pp` vs `22.7%`), `3d n=394`, `mean=-0.003%` (`-0.00%`), `SE=0.210%` | `VAL events=395`, `VAL hit=38.7 %`, `VAL base=22.7 %`, `VAL fee-net 3d (SE)=-0.00 % (0.21)`, `baseline 3d=-0.10 %` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:29` | MATCH |
| R2 VAL (events, hit rate, 3d fee-net mean & SE) | `events=600`, `hit=35.0%` (`+12.3 pp` vs `22.7%`), `3d n=598`, `mean=+0.071%` (`+0.07%`), `SE=0.174%` | `VAL events=600`, `VAL hit=35.0 %`, `VAL base=22.7 %`, `VAL fee-net 3d (SE)=+0.07 % (0.17)`, `baseline 3d=-0.10 %` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:30` | MATCH |
| R3 VAL (events, hit rate, 3d fee-net mean, SE, z) | `events=442`, `hit=41.0%` (`+18.3 pp` vs `22.7%`), `3d n=440`, `mean=+0.165%` (`+0.17%`), `SE=0.206%` (`0.21`), `z=+1.18` (combined) / `+1.29` (rule) | `VAL events=442`, `VAL hit=41.0 %`, `VAL base=22.7 %`, `VAL fee-net 3d (SE)=+0.17 % (0.21)`, `"about 1.2 standard errors"` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:3,31,33` | MATCH |
| R3 DEV (events, hit rate, 3d & 7d fee-net mean) | `events=655`, `hit=39.4%`, `3d mean=+0.430%`, `7d mean=+0.815%` (`+0.82%`) | `DEV events=655`, `DEV hit=39.4 %`, `R3 +0.43 % at 3d, +0.82 % at 7d` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:31,35` | MATCH |
| RSI `1d <- 4h` lead (DEV & VAL n, median, IQR) | DEV `n=122`, `16.0 h (4.0-36.0)`; VAL `n=78`, `12.0 h (8.0-32.0)` | `DEV n=122`, `16 h (4-36)`, `VAL n=78`, `12 h (8-32)` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:17` | MATCH |
| WT `1d <- 4h` lead (DEV & VAL n, median, IQR) | DEV `n=227`, `32.0 h (20.0-48.0)`; VAL `n=142`, `36.0 h (20.0-52.0)` | `DEV n=227`, `32 h (20-48)`, `VAL n=142`, `36 h (20-52)` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:19` | MATCH |
| Weekly leads (`RSI 1w <- 1d`, `WT 1w <- 1d`) | RSI DEV `n=14, 144.0 h, 64.3%`, VAL `n=11, 96.0 h, 45.5%`; WT DEV `n=30, 72.0 h, 46.7%`, VAL `n=19, 96.0 h, 42.1%` | RSI `14 | 144 h, only 64 % | 11 | 96 h, 45 %`; WT `30 | 72 h, 47 % | 19 | 96 h, 42 %` | `MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md:20-21` | MATCH |
