MATCH: 24 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `backtest/layers/vfi/vfi.py` vs `FORMULAS.md` Section 32 (`gemini-blind-read-of-vfi-py-vfi-engine-f`)

- **Card**: `gemini-blind-read-of-vfi-py-vfi-engine-f`
- **Reader / Provenance**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-of-vfi-py-vfi-engine-f`).
- **Scope In Read**:
  - `MyTradingSys/backtest/layers/vfi/vfi.py` (lines 1-53, SOURCED/OURS)
  - `MyTradingSys/backtest/layers/FORMULAS.md` (section 32, lines 700-716, SOURCED)
- **Scope Out Respected**: No source files edited; no live-tree edit, no push or sync ship, no `.secrets` or `.env` read.

---

## 1. Summary of Verification

Section 32 of `FORMULAS.md` specifies the Volume Flow Indicator (LazyBear / Katsanos) layer engine:
1. **Inputs & Default Parameters**: `length=130`, `coef=0.2`, `vcoef=2.5`, `stdev_len=30`, `smooth=3`, `smooth_kind="sma"`.
2. **Typical Price & Inter-bar Log Returns**:
   - `typ = (H + L + C) / 3`
   - `inter_i = ln(typ_i) - ln(typ_{i-1})` for $i \ge 1$.
3. **Cutoff & Population Standard Deviation**:
   - `vinter_i` = Population stdev (section 22, divisor $N$, not sample $N-1$) of `inter` over `stdev_len` window ending at $i$.
   - `cutoff_i = coef * vinter_i * C_i`.
4. **Volume Average & Volume Capping**:
   - `vave_i = SMA(volume, length)` over prior bars $i-\text{length} \dots i-1$ (previous bar's average, current bar excluded).
   - `vmax_i = vcoef * vave_i`.
   - `vc_i = min(V_i, vmax_i)`.
5. **Directional Flow & Volume Cutoff Check**:
   - `mf_i = typ_i - typ_{i-1}`.
   - `vcp_i = +vc_i` if $mf_i > cutoff_i$, `-vc_i` if $mf_i < -cutoff_i$, else $0.0$ (strict inequality; ties yield 0).
6. **VFI Raw Calculation & Warmup Window**:
   - `vfi_i = SUM(vcp, length)_i / vave_i`.
   - Full warmup convention: `vfi` is `None` until bar $\max(\text{stdev\_len}, \text{length}) + \text{length} - 1$.
7. **Smoothing Modes**:
   - If `smooth <= 1`, returns `(raw, list(raw))`.
   - If `smooth_kind == "sma"`, `SMA(raw, smooth)`.
   - If `smooth_kind == "ema"`, `EMA(raw, smooth)` with $\alpha = 2 / (\text{smooth} + 1)$, seeded by the first SMA.
   - Smoothed output is `None` until `smooth` raw VFI values exist.
8. **Worked Toy Hand Values (Section 32.2)**:
   - 9-bar toy ($N=9$, $\text{length}=3$, $\text{stdev\_len}=2$, $\text{smooth}=2$, $\text{coef}=0.2$, $\text{vcoef}=2.5$).
   - Exact numerical match across all intermediate values ($vcp$, $vave$, $vmax$, $vc$, cutoff) and final outputs ($vfi$, SMA, EMA).

---

## 2. Clause-by-Clause Audit Table

| # | Item / Clause | Formula / Requirement in `FORMULAS.md` s32 | Implementation in `vfi.py` | Verdict |
|---:|---|---|---|---|
| 1 | Function signature & defaults | `length 130, coef 0.2, vcoef 2.5, stdev length 30, smoothing length 3` (`FORMULAS.md:701`) | `def vfi(high, low, close, volume, length=130, coef=0.2, vcoef=2.5, smooth=3, stdev_len=30, smooth_kind="sma"):` (`vfi.py:8`) | MATCH |
| 2 | Input length validation | Input series length alignment check | `if not (len(high) == len(low) == len(volume) == n): raise ValueError(...)` (`vfi.py:13-14`) | MATCH |
| 3 | Smoothing kind validation | `smooth_kind` must be "sma" or "ema" (`FORMULAS.md:703`) | `if smooth_kind not in ("sma", "ema"): raise ValueError(...)` (`vfi.py:15-16`) | MATCH |
| 4 | Typical price formula | `typ = (H+L+C)/3` (`FORMULAS.md:703`) | `typ = [(high[i] + low[i] + close[i]) / 3.0 for i in range(n)]` (`vfi.py:17`) | MATCH |
| 5 | Typical price positivity check | Logarithm requires $typ > 0$ | `if any(t <= 0 for t in typ): raise ValueError("typical price must be positive (log)")` (`vfi.py:18-19`) | MATCH |
| 6 | Inter-bar log returns | `inter_i = ln(typ_i) - ln(typ_{i-1}) (i >= 1)` (`FORMULAS.md:703`) | `inter = [None] + [math.log(typ[i]) - math.log(typ[i - 1]) for i in range(1, n)]` (`vfi.py:20`) | MATCH |
| 7 | Loop start for vcp calculation | Requires at least $\max(\text{stdev\_len}, \text{length})$ bars for $inter$ window & prior volume | `for i in range(max(stdev_len, length), n):` (`vfi.py:22`) | MATCH |
| 8 | Population stdev of inter (`vinter`) | `vinter_i = POPULATION stdev (section 22) of inter over the last stdev_len values (first at i = stdev_len)` (`FORMULAS.md:703`) | `w = inter[i - stdev_len + 1:i + 1]`, `m = sum(w) / stdev_len`, `vinter = math.sqrt(sum((x - m) ** 2 for x in w) / stdev_len)` (`vfi.py:23-25`) | MATCH |
| 9 | Cutoff formula | `cutoff_i = coef * vinter_i * C_i` (`FORMULAS.md:703`) | `cutoff = coef * vinter * close[i]` (`vfi.py:26`) | MATCH |
| 10 | Volume average (`vave`) | `vave_i = SMA(volume, length) over bars i-length..i-1 (the PREVIOUS bar's average, current volume excluded; first at i = length)` (`FORMULAS.md:703`) | `vave = sum(volume[i - length:i]) / length` (`vfi.py:27`) | MATCH |
| 11 | Capped volume threshold (`vmax`) | `vmax_i = vcoef * vave_i` (`FORMULAS.md:703`) | `vcoef * vave` (`vfi.py:28`) | MATCH |
| 12 | Capped volume (`vc`) | `vc_i = min(V_i, vmax_i)` (`FORMULAS.md:703`) | `vc = min(volume[i], vcoef * vave)` (`vfi.py:28`) | MATCH |
| 13 | Price momentum / flow (`mf`) | `mf_i = typ_i - typ_{i-1}` (`FORMULAS.md:703`) | `mf = typ[i] - typ[i - 1]` (`vfi.py:29`) | MATCH |
| 14 | Directional volume assignment (`vcp`) | `vcp_i = +vc_i if mf_i > cutoff_i; -vc_i if mf_i < -cutoff_i; else 0 (strict; a tie is 0)` (`FORMULAS.md:703`) | `vcp[i] = vc if mf > cutoff else (-vc if mf < -cutoff else 0.0)` (`vfi.py:30`) | MATCH |
| 15 | Raw VFI warmup start index | `first at bar max(stdev_len, length) + length - 1` (`FORMULAS.md:704`) | `first = max(stdev_len, length) + length - 1` (`vfi.py:32`) | MATCH |
| 16 | Raw VFI none before warmup | `vfi is None until the sum window is fully real data` (`FORMULAS.md:704`) | `raw = [None] * n` for $i < \text{first}$ (`vfi.py:31-33`) | MATCH |
| 17 | Raw VFI numerator sum | `SUM(vcp, length)_i` over current bar and previous length-1 bars (`FORMULAS.md:703`) | `sum(vcp[i - length + 1:i + 1])` (`vfi.py:35`) | MATCH |
| 18 | Raw VFI division by vave | `vfi_i = SUM(vcp, length)_i / vave_i` (`FORMULAS.md:703`) | `... / vave if vave else None` (`vfi.py:35`) | MATCH |
| 19 | Smooth bypass when smooth <= 1 | `smooth <= 1 returns vfi itself` (`FORMULAS.md:703`) | `if smooth <= 1: return raw, list(raw)` (`vfi.py:36-37`) | MATCH |
| 20 | Smoothed warmup requirement | `Smoothed is None until smooth vfi values exist` (`FORMULAS.md:704`) | `if len(w) < smooth or any(x is None for x in w): prev = None; continue` (`vfi.py:42-44`) | MATCH |
| 21 | SMA smoothing implementation | `Smoothed output = SMA(vfi, smooth)` (`FORMULAS.md:703`) | `if smooth_kind == "sma" or prev is None: prev_sma = sum(w) / smooth; sm[i] = prev_sma; prev = prev_sma` (`vfi.py:45-48`) | MATCH |
| 22 | EMA smoothing seeding | `smooth_kind="ema" gives EMA(vfi, smooth), alpha = 2/(smooth+1), SMA-seeded (section 4)` (`FORMULAS.md:703`) | Initialized by `prev_sma = sum(w) / smooth` on the first window where `prev is None` (`vfi.py:45-48`) | MATCH |
| 23 | EMA smoothing recursion & alpha | `alpha = 2/(smooth+1)` (`FORMULAS.md:703`) | `a = 2.0 / (smooth + 1)`, `prev = a * raw[i] + (1 - a) * prev`, `sm[i] = prev` (`vfi.py:50-52`) | MATCH |
| 24 | Return tuple | `-> (vfi_raw, vfi_smoothed), lists aligned to the input` (`FORMULAS.md:703`, `vfi.py:9`) | `return raw, sm` (`vfi.py:53`) | MATCH |

---

## 3. Worked Toy Hand-Value Verification (Section 32.2)

Input series from `FORMULAS.md:707`:
- $C = [100, 102, 101, 105, 105, 104, 110, 108, 108.25]$ ($n=9$, bars 0-8)
- $H = C + 1$, $L = C - 1 \implies typ = C$
- $V = [10, 20, 30, 20, 40, 10, 100, 30, 50]$
- Parameters: $\text{stdev\_len} = 2, \text{length} = 3, \text{smooth} = 2, \text{coef} = 0.2, \text{vcoef} = 2.5$.

### Bar-by-Bar Breakdown:
- **Bar 3**: $mf = +4$; $inter_2 = \ln(101/102) \approx -0.009852$, $inter_3 = \ln(105/101) \approx 0.038840$; population stdev $vinter \approx 0.024346$; $cutoff = 0.2 \times 0.024346 \times 105 \approx 0.5113$; $mf > cutoff \implies vcp = +vc = +20$. (MATCH)
- **Bar 4**: $mf = 0$; tie against positive cutoff $\implies vcp = 0$. (MATCH)
- **Bar 5**: $mf = -1$; $inter_5 = \ln(104/105) \approx -0.009569$, $inter_4 = 0$; $vinter \approx 0.004785$; $cutoff \approx 0.0995$; $mf < -cutoff \implies vcp = -10$. (MATCH)
- **Bar 6**: $mf = +6$; $inter_6 = \ln(110/104) \approx 0.056089$; $vinter \approx 0.032830$; $cutoff \approx 0.7222$; $vave = 70/3 \approx 23.3333 \implies vmax = 175/3 \approx 58.3333$; $V=100 > vmax \implies vc = 175/3$; $mf > cutoff \implies vcp = +175/3 \approx 58.3333$. (MATCH)
- **Bar 7**: $mf = -2$; $inter_7 = \ln(108/110) \approx -0.018349$; $vinter \approx 0.037220$; $cutoff \approx 0.8040$; $mf < -cutoff \implies vcp = -30$. (MATCH)
- **Bar 8**: $mf = +0.25$; $inter_8 = \ln(108.25/108) \approx 0.002312$; $vinter \approx 0.010331$; $cutoff = 0.2 \times 0.010331 \times 108.25 \approx 0.2237$; $0.25 > 0.2237 \implies vcp = +50$. (MATCH)

### Raw VFI Output ($first = \max(2,3) + 3 - 1 = 5$):
- Bars 0-4: `None` (MATCH)
- Bar 5: $\sum vcp = 20 + 0 - 10 = 10$; $vave = 30 \implies 10 / 30 = 1/3 \approx 0.333333$ (MATCH)
- Bar 6: $\sum vcp = 0 - 10 + 175/3 = 145/3$; $vave = 70/3 \implies (145/3)/(70/3) = 29/14 \approx 2.071429$ (MATCH)
- Bar 7: $\sum vcp = -10 + 175/3 - 30 = 55/3$; $vave = 50 \implies (55/3)/50 = 11/30 \approx 0.366667$ (MATCH)
- Bar 8: $\sum vcp = 175/3 - 30 + 50 = 235/3$; $vave = 140/3 \implies (235/3)/(140/3) = 47/28 \approx 1.678571$ (MATCH)

### Smoothed Output ($\text{smooth}=2$, first at bar 6):
- **SMA**:
  - Bars 0-5: `None` (MATCH)
  - Bar 6: $(1/3 + 29/14) / 2 = 101/84 \approx 1.202381$ (MATCH)
  - Bar 7: $(29/14 + 11/30) / 2 = 128/105 \approx 1.219048$ (MATCH)
  - Bar 8: $(11/30 + 47/28) / 2 = 859/840 \approx 1.022619$ (MATCH)
- **EMA** ($\alpha = 2/3$, seed at bar 6 = $101/84$):
  - Bars 0-5: `None` (MATCH)
  - Bar 6: $101/84 \approx 1.202381$ (MATCH)
  - Bar 7: $(2/3)(11/30) + (1/3)(101/84) = 271/420 \approx 0.645238$ (MATCH)
  - Bar 8: $(2/3)(47/28) + (1/3)(271/420) = 1681/1260 \approx 1.334127$ (MATCH)

---

## 4. Verification Check Commands & Outcomes

1. `python -m unittest MyTradingSys/backtest/layers/vfi/test_vfi.py`:
   - Ran 5 tests: `test_raw`, `test_smoothed_sma`, `test_smoothed_ema`, `test_no_smoothing_returns_raw`, `test_bad_input`.
   - Result: All 5 passed in 0.000s (`OK`).
2. Sourced TV Verification reference in `FORMULAS.md:716`:
   - `VERIFIED-TV 2026-11-07, login C: TradingView "Volume Flow Indicator [LazyBear]" (VFI_LB 130 0.2 2.5 5), BYBIT:BTCUSDT.P 1D, raw vfi matches on 4/4 bars within the one-decimal display (2026-10-04 0.6 vs +0.641, 2026-10-08 -0.7 vs -0.736, 2026-10-09 1.4 vs +1.436, 2026-11-06 8.5 vs +8.518).`
