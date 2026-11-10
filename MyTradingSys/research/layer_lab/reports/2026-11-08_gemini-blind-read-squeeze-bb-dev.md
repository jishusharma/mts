MATCH: 16 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `squeeze.py` BB-dev quirk vs `FORMULAS.md` s31

- **Card**: `gemini-blind-read-of-squeeze-py-bb-dev-q`
- **Task**: Independent Gemini blind read of `MyTradingSys/backtest/layers/squeeze/squeeze.py` against `MyTradingSys/backtest/layers/FORMULAS.md` section 31: verify whether the code reproduces LazyBear's BB-dev quirk (`dev = multKC * stdev`) exactly and nothing else.
- **Scope In Read**:
  - `MyTradingSys/backtest/layers/squeeze/squeeze.py` (lines 1-51)
  - `MyTradingSys/backtest/layers/FORMULAS.md` (section 31, lines 692-699)
- **Scope Out Respected**: No edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Verification

In `FORMULAS.md` s31 (lines 694, 697), LazyBear's Pine script quirk is defined as:
- SOURCED script quirk: `dev = multKC * stdev(source, length)`, so Bollinger half-width is `BBhw = kc_mult * sd = 1.5 * sd` by default, not `2.0 * sd`. The `bb_mult` input is not used for the band.
- OURS variant: `textbook_bb=True` restores half-width `bb_mult * sd = 2.0 * sd`.
- Default parameter values: `bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, mom_len=20, textbook_bb=False`.
- Tie tolerance (OURS): 1e-9 relative tolerance for `BBhw == KChw` (neither ON nor OFF).
- Both bands center on the same SMA(close, n), so `lower_BB > lower_KC` and `upper_BB < upper_KC` is strictly `BBhw < KChw` (squeeze ON), `BBhw > KChw` (squeeze OFF).

Audit of `squeeze.py`:
1. Line 24 sets: `dev_mult = bb_mult if textbook_bb else kc_mult`.
2. When `textbook_bb=False` (default, line 16), `dev_mult` evaluates strictly to `kc_mult` (`1.5` default), exactly ignoring `bb_mult` (`2.0` default) and setting `bb_hw = kc_mult * sd`.
3. When `textbook_bb=True`, `dev_mult` evaluates strictly to `bb_mult` (`2.0` default), restoring the textbook definition.
4. No other alterations to the formula or extraneous logic exist in `squeeze.py`.

---

## 2. Itemized Clause Audit: `squeeze.py` vs `FORMULAS.md` s31

| # | Feature / Clause | `FORMULAS.md` s31 Clause (SOURCED/OURS) | `squeeze.py` Implementation | Verdict |
|---:|---|---|---|---|
| 1 | Module purpose & context columns | Context columns only; defaults SOURCED from LazyBear's public Pine script (s31:695) | Returns `(squeeze_on, squeeze_off, momentum)` aligned lists, no orders/signals (`squeeze.py:17`) | MATCH |
| 2 | Function signature & defaults | `bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, mom_len=20` (s31:695) | `def squeeze_momentum(high, low, close, bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, mom_len=20, textbook_bb=False)` (`squeeze.py:15-16`) | MATCH |
| 3 | Length mismatch check | Required input validation across high, low, close arrays | `if not (len(high) == len(low) == n): raise ValueError(...)` (`squeeze.py:22-23`) | MATCH |
| 4 | BB dev multiplier selection | LazyBear quirk: `dev = multKC * stdev` by default; `textbook_bb=True` uses `bb_mult` (s31:694, 697) | `dev_mult = bb_mult if textbook_bb else kc_mult` (`squeeze.py:24`) | MATCH |
| 5 | True Range (TR) formula | `TR_0 = H_0 - L_0`, `TR_i = max(H_i - L_i, abs(H_i - C_{i-1}), abs(L_i - C_{i-1}))` (s31:697) | `tr = [high[i] - low[i] if i == 0 else max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) for i in range(n)]` (`squeeze.py:25-26`) | MATCH |
| 6 | KC mid / Linear regression source (`src`) | `src_i = C_i - ((HH_i + LL_i)/2 + SMA(C, n)_i)/2` (s31:697) | `hh = max(high[i - kc_len + 1:i + 1])`; `ll = min(low[i - kc_len + 1:i + 1])`; `src[i] = close[i] - ((hh + ll) / 2.0 + _sma(close, i, kc_len)) / 2.0` (`squeeze.py:29-31`) | MATCH |
| 7 | Alignment / warmup None padding | Flags first defined at bar `n-1` (or `max(bb_len, kc_len) - 1`), None before (s31:697) | `on = [None] * n`, `off = [None] * n`, computed only when `i >= max(bb_len, kc_len) - 1` (`squeeze.py:32-36`) | MATCH |
| 8 | BB basis SMA | `basis = SMA(close, n)` (s31:697) | `m = _sma(close, i, bb_len)` with `_sma(a, i, n) = sum(a[i-n+1:i+1]) / n` (`squeeze.py:11-12, 37`) | MATCH |
| 9 | BB population standard deviation | `POPULATION stdev (section 22)`: divisor `N` (s31:697) | `sd = math.sqrt(sum((c - m) ** 2 for c in close[i - bb_len + 1:i + 1]) / bb_len)` (`squeeze.py:38`) | MATCH |
| 10 | BB half-width computation | `BBhw = kc_mult * sd` (quirk) or `bb_mult * sd` (`textbook_bb=True`) (s31:694, 697) | `bb_hw = dev_mult * sd` (`squeeze.py:39`) | MATCH |
| 11 | KC half-width computation | `KChw = 1.5 * rangema` = `kc_mult * SMA(TR, n)` (s31:697) | `kc_hw = kc_mult * _sma(tr, i, kc_len)` (`squeeze.py:40`) | MATCH |
| 12 | Relative tie tolerance (OURS) | Relative tolerance 1e-9: ties within `1e-9 relative count as equal` (s31:697) | `tol = 1e-9 * max(1.0, abs(bb_hw), abs(kc_hw))` (`squeeze.py:41`) | MATCH |
| 13 | Squeeze ON condition | `BBhw < KChw`: squeeze ON (strict) (s31:697) | `on[i] = bb_hw < kc_hw - tol` (`squeeze.py:42`) | MATCH |
| 14 | Squeeze OFF condition | `BBhw > KChw`: squeeze OFF (strict) (s31:697) | `off[i] = bb_hw > kc_hw + tol` (`squeeze.py:43`) | MATCH |
| 15 | Momentum warmup alignment | First defined: `flags at bar n-1, momentum at bar 2n-2` (s31:697) | Computed only when `i >= kc_len + mom_len - 2`, otherwise None (`squeeze.py:44`) | MATCH |
| 16 | Momentum linear regression formula | Endpoint value of least-squares line on last `mom_len` values of `src`: `mean(y) + slope * (n-1 - (n-1)/2)` with `slope = sum((x - xm)*y) / sum((x - xm)^2)` (s31:697) | `xm = (mom_len - 1) / 2.0`, `sxx = sum((k - xm) ** 2 ...)`, `ym = sum(y)/mom_len`, `slope = sum((k - xm)*y[k] ...) / sxx`, `mom[i] = ym + slope * (mom_len - 1 - xm)` (`squeeze.py:46-50`) | MATCH |

---

## 3. Quirk-Specific Invariance Analysis

1. **LazyBear Script Line**:
   In LazyBear's Pine Script:
   ```pinescript
   multKC = input(1.5, title="KC MultFactor")
   mult = input(2.0, title="BB MultFactor")
   ...
   basis = sma(source, length)
   dev = multKC * stdev(source, length)
   ```
   Notice that `dev` (which builds the Bollinger Bands) multiplies by `multKC` (1.5) instead of `mult` (2.0).

2. **In `squeeze.py`**:
   ```python
   dev_mult = bb_mult if textbook_bb else kc_mult
   ...
   bb_hw = dev_mult * sd
   kc_hw = kc_mult * _sma(tr, i, kc_len)
   ```
   - When called with default arguments (`textbook_bb=False`), `dev_mult` is `kc_mult` (1.5). Thus `bb_hw = 1.5 * sd`.
   - `bb_mult` is ignored unless `textbook_bb=True`.
   - When called with `textbook_bb=True`, `dev_mult` is `bb_mult` (2.0). Thus `bb_hw = 2.0 * sd`.

3. **Conclusion**:
   `squeeze.py` reproduces LazyBear's BB-dev quirk (`dev = multKC * stdev`) exactly, preserves the textbook alternative cleanly behind `textbook_bb=True`, and introduces no extraneous logic or deviations.
