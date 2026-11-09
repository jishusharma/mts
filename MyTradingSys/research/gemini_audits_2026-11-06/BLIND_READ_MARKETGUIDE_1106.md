# Blind Read Audit: `scripts/dev/market_guide.py` (`order_flow_state_lines`) (2026-11-06)

- **Card**: `gemini-blind-read-of-scripts-dev-market-` (SOURCED: `MyTradingSys/system/tasks/gemini-blind-read-of-scripts-dev-market-.json:203`)
- **Target**: `scripts/dev/market_guide.py` (`order_flow_state_lines` and supporting order-flow helper definitions, lines `219–387`, SOURCED: `scripts/dev/market_guide.py:219-387`)
- **Commit audited**: `c8c657cc6666` (`market_guide: order-flow state line per TF 1m/5m/15m (descriptive, no tested edge)`, SOURCED: `MyTradingSys/system/tasks/gemini-blind-read-of-scripts-dev-market-.json:210-212`)
- **Method**: Read `scripts/dev/market_guide.py:219-387` and cross-checked `MyTradingSys/research/orderflow_views_2026-10-14/study.py` and `RESULT.md` to verify that every constant, threshold, formula, and printed number in `order_flow_state_lines` and `order_flow_section` has an explicit `SOURCED` reference or an `OURS` label, and recomputed `order_flow_state` and `order_flow_state_lines` independently on synthetic and boundary inputs. No `VALIDATION` or `HOLDOUT` data was read; no source files were modified.

## 1. Independent Recomputation of `order_flow_state` & `order_flow_state_lines`

1. **Window length guard (`scripts/dev/market_guide.py:280-281, 323-325`)**:
   - Requires `len(bars) >= 2 * half` where `OF_HALF = {"1m": 15, "5m": 12, "15m": 16}` (`2 * half = 30, 24, 32` closed bars respectively; OURS verification).
   - When `len(bars) < 2 * half`, `order_flow_state_lines` prints:
     `"<tf>: n/a (<len> closed bars, need <2*h>) | descriptive only, no tested edge"` (`scripts/dev/market_guide.py:324`).
2. **Cumulative Volume Delta (`scripts/dev/market_guide.py:282-285`)**:
   - Per-bar delta = `tbv - (v - tbv) = 2 * tbv - v`, accumulated into `cvd`.
   - Split into prior half `pri = bars[-2*half:-half]`, `cp = cvd[-2*half:-half]` and recent half `rec = bars[-half:]`, `cr = cvd[-half:]` (`scripts/dev/market_guide.py:286, 296`).
3. **Price & CVD Swing Classification (`scripts/dev/market_guide.py:287-306`)**:
   - `ll = min(rec.l) < min(pri.l)`, `hh = max(rec.h) > max(pri.h)` (`:287-289`).
   - If `ll != hh`, `side = "low" if ll else "high"` (`:290-291`). If `ll == hh` (both true = outside half, or both false = inside half), tie-broken by the newer extreme index within `rec` (`i_lo >= i_hi -> "low"`, else `"high"`, `:292-295`).
   - Low side (`:297-301`): `price = "LL" if ll else "HL"`, `level = lo_r`, `cvd_sw = "LL" if min(cr) < min(cp) else "HL"`, mapped to:
     - `("LL", "HL") -> "bullish CVD divergence"`
     - `("LL", "LL") -> "CVD confirms the low"`
     - `("HL", "LL") -> "CVD lower low, price holds"`
     - `("HL", "HL") -> "higher low, CVD with it"`
   - High side (`:302-306`): `price = "HH" if hh else "LH"`, `level = hi_r`, `cvd_sw = "HH" if max(cr) > max(cp) else "LH"`, mapped to:
     - `("HH", "LH") -> "bearish CVD divergence"`
     - `("HH", "HH") -> "CVD confirms the high"`
     - `("LH", "HH") -> "CVD higher high, price holds"`
     - `("LH", "LH") -> "lower high, CVD with it"`
4. **OI 60-Minute Percentage Change (`scripts/dev/market_guide.py:262-276, 307-312`)**:
   - `oi_at(oi, t)` selects the latest `(ts, v)` in `[t - 600000, t]` (within 10 minutes at or before `t`, `:262-268`).
   - `oi_change_60m(oi, t)` computes `(b - a) / a * 100.0` where `a = oi_at(oi, t - 3600000)` and `b = oi_at(oi, t)` evaluated at `t = bars[-1]["ct"] + 1` (`:271-275, 307`).
   - Appends `", OI up (positions opening)"` if `oi_pct > 0`, or `", OI down (positions closing)"` if `oi_pct < 0` (`:308-312`).
5. **Formatted Output Line (`scripts/dev/market_guide.py:326-329`)**:
   - `"<tf> @<HH:MMZ>: price <LL|HL|HH|LH> <level:.1f> | Binance CVD <LL|HL|HH|LH> | OI 60m <+X.XX%|n/a> | <state> | descriptive only, no tested edge"`.

## 2. Per-Claim & Provenance Verification Table

| # | Item / Printed Number / Threshold (`scripts/dev/market_guide.py`) | Code Location (`file:line`) | Stated Source or `OURS` Label (`file:line`) | Independent Verification | Status |
|---|---|---|---|---|---|
| 1 | Section header disclaimer: `"descriptive only, no tested edge: orderflow_views_2026-10-14 RESULT.md"` | `scripts/dev/market_guide.py:380` | `SOURCED` to `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md` (`:219, 318, 324, 327, 380`) | Every line returned by `order_flow_state_lines` and the section header explicitly carries `"descriptive only, no tested edge"`. | MATCH |
| 2 | Half-window lengths `OF_HALF["1m"] = 15` (15m half / 30m window) and `OF_HALF["5m"] = 12` (1h half / 2h window) | `scripts/dev/market_guide.py:223` | `SOURCED from MyTradingSys/research/orderflow_views_2026-10-14/study.py:12 (OURS there, not a trader's)` (`scripts/dev/market_guide.py:221`) | Verified in `MyTradingSys/research/orderflow_views_2026-10-14/study.py:12` (`H = {"1m": 15, "5m": 12}` with `# OURS`). | MATCH |
| 3 | Half-window length `OF_HALF["15m"] = 16` (4h halves / 8h total window) | `scripts/dev/market_guide.py:223` | `# H 15m=16 (4h halves): OURS, continues the x4 window step.` (`scripts/dev/market_guide.py:222`) | Explicitly labeled `OURS` in `scripts/dev/market_guide.py:222` (`15m * 16 = 240 min = 4h` half-window, x4 of 5m's `12 * 5m = 60 min`). | MATCH |
| 4 | Minimum closed bars threshold `2 * h` (`30` for 1m, `24` for 5m, `32` for 15m) printed in `n/a` fallback | `scripts/dev/market_guide.py:280, 324` | Derived directly from two half-windows `2 * OF_HALF[tf]` (`scripts/dev/market_guide.py:220-223, 279-280`) | Two contiguous half-windows (`pri = bars[-2*half:-half]`, `rec = bars[-half:]`) require `2 * half` bars. | MATCH |
| 5 | `OI_WINDOW_MS = 3600000` (60-minute OI change window) printed as `OI 60m` | `scripts/dev/market_guide.py:225, 271-275, 327` | `OI change window 60 min: same study (OI split)` (`scripts/dev/market_guide.py:222`, referencing `orderflow_views_2026-10-14/study.py`) | Verified in `MyTradingSys/research/orderflow_views_2026-10-14/study.py`: 60m OI change split (`t - 3600000` to `t`). | MATCH |
| 6 | `oi_at` staleness tolerance `600000` ms (`10 min` lookup window: `t - 600000 <= ts <= t`) | `scripts/dev/market_guide.py:262-268` | Docstring `:263` states `"within 10 min"` (2x the 5m `openInterestHist` period at `:373`), matching `orderflow_views_2026-10-14/study.py` | Prevents matching stale OI readings >10m before `t` or look-ahead readings `> t`. | MATCH |
| 7 | Per-bar CVD delta formula `2 * b["tbv"] - b["v"]` from Binance `fapi` col 9 (`takerBuyBaseAssetVolume`) | `scripts/dev/market_guide.py:230, 237, 284` | `# Swing = recent half-window vs the half before it, bar-close CVD (study.py definition a/d, no context filter)` (`scripts/dev/market_guide.py:220`) | Standard identity: `buy_vol - sell_vol = tbv - (v - tbv) = 2*tbv - v`; matches `study.py`. | MATCH |
| 8 | Printed price level `_f(s["level"], 1)` and OI percentage `"%+.2f%%" % s["oi_pct"]` | `scripts/dev/market_guide.py:298, 303, 328-329` | Direct data values (`lo_r` / `hi_r` of `rec` half-window and 60m OI % change `(b - a) / a * 100.0`, `:275, 287-288`) | Recomputed: `level` is exact recent-half min low (`side=="low"`) or max high (`side=="high"`), formatted to 1 decimal place; `oi_pct` formatted to signed 2 decimals or `"n/a"`. | MATCH |
| 9 | Printed `00:00Z VWAP (1m hlc3)` in `order_flow_section` (`vwap_00z`) | `scripts/dev/market_guide.py:333-341, 383-385` | Labeled `"our 00:00Z VWAP (1m hlc3)"` (`:383`) with explicit note on chart-relative CVD/VWAP anchoring | Uses closed 1m bars in `[day0, now_ms)` (`b["t"] >= day0 and b["ct"] < now_ms`), volume-weighted `(h+l+c)/3`. Causal (no unclosed bar leak). | MATCH |
| 10 | Closed-bar causal guard in `fapi_kline_bars` (`int(r[6]) >= now_ms -> continue`) and `resample` (complete UTC buckets only) | `scripts/dev/market_guide.py:234, 254` | Docstrings `:230, 245, 318` (`closed bars`) | `r[6]` is Binance `closeTime`; skipping `closeTime >= now_ms` and requiring all `n = ms // 60000` 1m bars per 5m/15m bucket prevents partial/in-flight bar leakage. | MATCH |

## 3. Defects List

None (`0` defects found; all 10 claims, constants, thresholds, and provenance labels match).

VERDICT: MATCH

