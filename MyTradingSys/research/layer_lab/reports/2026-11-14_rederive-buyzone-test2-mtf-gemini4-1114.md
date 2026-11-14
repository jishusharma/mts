# Blind Re-derivation Report: buyzone_test2_mtf_2026-11-14

- **Verdict:** FAIL (strict count/number match; substantively confirms `KILL`)
- **Script:** `MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test2-mtf/rederive.py`
- **Deliverable:** `MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test2-mtf/REDERIVE.md`

## Findings

1. **Verdict (MATCH):** Independent re-derivation (`rederive.py`) gives `KILL` for `PRIMARY` both sides (`VAL` 12bp mean R = `-0.0730`, 95% CI `[-0.2777, +0.1458]`, placebo percentile `56.8%`), matching `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` (`KILL`, `-0.075`, CI `-0.269..+0.145`, placebo `55`).
2. **Trade counts and headline mean R (MISMATCH):**
   - `PRIMARY` VAL both: recomputed `n=90`, mean12 `-0.0730` vs stated `n=91`, `-0.075` (`RESULT.md:7`, `RESULT_tables.md:14`).
   - `PRIMARY` DEV both: recomputed `n=122`, mean12 `+0.2066` vs stated `n=130`, `+0.230` (`RESULT.md:7`, `RESULT_tables.md:13`).
   - `PRIMARY` VAL long: recomputed `n=31`, mean12 `-0.4268` vs stated `n=32`, `-0.413` (`RESULT.md:12`, `RESULT_tables.md:40`).
   - `PRIMARY` VAL short: recomputed `n=59` (MATCH), mean12 `+0.1129` vs stated `+0.109` (`RESULT.md:13`, `RESULT_tables.md:58`).
3. **Top coin in VAL (MATCH):** `BTC` with sum `+3.8120` (recomputed) vs `BTC` with sum `+3.81` (`RESULT_tables.md:75`). Removing `BTC` gives `n=83`, mean12 `-0.1251` (recomputed) vs `n=84`, `-0.126` (`RESULT_tables.md:33`).

## Verification Commands

- `python MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test2-mtf/rederive.py`
- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test2-mtf/REDERIVE.md`
