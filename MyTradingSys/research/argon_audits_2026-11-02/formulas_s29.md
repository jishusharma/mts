SAME=14 DIFF=0 NOT_IN_DATA=0

# Argon Independent Re-derivation and Code Audit: `FORMULAS.md` Section 29 (Tom VP Return-to-Value Count)

- **Card:** `argon-rederive-formulas-s29-1102`
- **Spec:** `MyTradingSys/backtest/layers/FORMULAS.md:666-683` (referencing Sections `12` at `FORMULAS.md:331-348`, `18.1` at `FORMULAS.md:422-437`, `18.6` at `FORMULAS.md:482-484`, and `18.7` at `FORMULAS.md:486-490`; pre-registration `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:1-46`)
- **Code under audit:** `MyTradingSys/backtest/vp_return_to_value.py:1-381` (and delegated helpers in `MyTradingSys/backtest/vp_pivot_probe.py:28-127,262-267`)
- **Provenance labels:**
  - `SOURCED`:
    - Return-to-value 70/30 frequency claim: `"But unfortunately that is only the case about 30% of the time and the other 70% he will try and strive to run back here."` (`extracts/processed/tom/extract_BB3c8visnkI.md:38`, cited at `MyTradingSys/backtest/layers/FORMULAS.md:668` and `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:8`).
    - Value area 70% volume fraction: `"within this zone here the market has traded 70% of the total liquidity for this week."` (`extracts/processed/tom/extract_BB3c8visnkI.md:28`; `"70% of the trades"` `1utSjHs_Mq8:19` at `MyTradingSys/backtest/layers/FORMULAS.md:427`; `VA_PCT = 0.70` at `MyTradingSys/backtest/vp_pivot_probe.py:29`).
    - Naked-POC revisit threshold $0.3\%$ ($0.003$): `"private static final double REVISIT_THRESHOLD_PCT = 0.003; // 0.3%"` (`src/main/java/datafeed/NakedPocTracker.java:26`, cited at `MyTradingSys/backtest/layers/FORMULAS.md:676` and `MyTradingSys/backtest/vp_return_to_value.py:28`).
  - `OURS` (including pre-registered measurement choices tagged `NO-SOURCE` in `FORMULAS.md:671-678`): UTC-day completeness (`288` 5m bars in $D$ and $D-1$), profile bin width `w = 10.0` USD (`MyTradingSys/backtest/layers/FORMULAS.md:422,671`), first close outside `[VAL, VAH]` event rule (`FORMULAS.md:672`), POC touch return rule and last-bar censoring (`FORMULAS.md:673`), back-inside-value rule (`FORMULAS.md:674`), Part B consecutive acceptance window $N \in \{3, 6, 12\}$ against value-area edge (`FORMULAS.md:675`), daily placebo shift cycle `(-3, -2, -1, -0.5, 0.5, 1, 2, 3)` by `(day_index mod 8)` times causal 1h `ATR14` at `00:00 UTC` (`FORMULAS.md:677`), day-block bootstrap (`2000` resamples, seed `20261009`), underpowered threshold `n < 100`, DEV window `2022-01-01..2024-06-30` (`FORMULAS.md:678`), post-hoc censoring filter `CENS_MIN_LEFT = 12` (`FORMULAS.md:682`), and near-band placebo restriction `|d| <= 1.0` (`MyTradingSys/backtest/vp_return_to_value.py:184-195,234-235`).

---

## Step 1: Independent Hand Derivation of Worked Examples from `FORMULAS.md` Text Alone

1. **Prior-day Value Profile (`FORMULAS.md:671,680` & Section `18.1` Worked A at `FORMULAS.md:432-433`):**
   - Grid bin width $w = 1$ (`OURS` toy example; production `w = 10.0` USD `OURS` / `NO-SOURCE`, `FORMULAS.md:422,671`), value area target fraction $= 0.70$ (`SOURCED`, `extracts/processed/tom/extract_BB3c8visnkI.md:28`, `FORMULAS.md:427`).
   - Input bars $(l, h, v) = (0, 2, 6), (1, 3, 4), (1, 2, 10)$:
     - Bar $(0, 2, 6)$, span $2$: overlaps $\text{bin}_0=[0,1)$ by $1 \implies 6 \times \frac{1}{2} = 3.0$; overlaps $\text{bin}_1=[1,2)$ by $1 \implies 6 \times \frac{1}{2} = 3.0$.
     - Bar $(1, 3, 4)$, span $2$: overlaps $\text{bin}_1=[1,2)$ by $1 \implies 4 \times \frac{1}{2} = 2.0$; overlaps $\text{bin}_2=[2,3)$ by $1 \implies 4 \times \frac{1}{2} = 2.0$.
     - Bar $(1, 2, 10)$, span $1$: overlaps $\text{bin}_1=[1,2)$ by $1 \implies 10 \times \frac{1}{1} = 10.0$.
   - Bin volumes: $\text{vol} = [3.0, 15.0, 2.0]$ at bins $k \in \{0, 1, 2\}$ (`OURS`).
   - Total volume $= 3.0 + 15.0 + 2.0 = 20.0$; $70\%$ target $= 0.70 \times 20.0 = 14.0$ (`OURS`).
   - POC bin: $k_{\text{poc}} = 1$ ($\text{vol}[1] = 15.0$ is unique maximum) $\implies \text{poc\_price} = 1 \times 1 + \frac{1}{2} = 1.5$ (`OURS`).
   - Value area expansion: start $\text{lo} = \text{hi} = 1$, $\text{acc} = 15.0 \ge 14.0$ immediately (0 loop iterations) $\implies \text{val} = 1 \times 1 = 1.0$, $\text{vah} = (1 + 1) \times 1 = 2.0$ (`OURS`).
   - Matches `FORMULAS.md:680`: `POC 1.5, VAH 2.0, VAL 1.0`.

2. **Section 29.2 Day $D$ Event, Return, Back-Inside, Part B ($N \in \{3, 6, 12\}$), and Naked-POC (`FORMULAS.md:680`):**
   - Prior-day levels (`OURS` from Worked A): $\text{POC} = 1.5$, $\text{VAH} = 2.0$, $\text{VAL} = 1.0$.
   - Day $D$ bars $(h, l, c)$ for indices $0..5$ ($6$ bars total, `OURS`):
     - $0: (1.8, 1.2, 1.6)$
     - $1: (2.4, 1.7, 2.2)$
     - $2: (2.6, 2.1, 2.5)$
     - $3: (2.7, 2.3, 2.6)$
     - $4: (2.5, 1.4, 1.9)$
     - $5: (2.0, 1.8, 1.9)$
   - **Event (`FORMULAS.md:672,680`):** First bar with $c > 2.0$ or $c < 1.0$:
     - Bar $0$: $c[0] = 1.6 \in [1.0, 2.0]$ (inside).
     - Bar $1$: $c[1] = 2.2 > 2.0 \implies$ event at $e = 1$, $\text{side} = +1$, bars left after $e$ $= 6 - 1 - 1 = 4$ (bars $2, 3, 4, 5$, `OURS`).
   - **RETURN (`FORMULAS.md:673,680`):** Test later bars $j \in \{2, 3, 4, 5\}$ for $l[j] \le 1.5 \le h[j]$:
     - $j=2$: $[2.1, 2.6]$ ($2.1 > 1.5$, no); $j=3$: $[2.3, 2.7]$ ($2.3 > 1.5$, no); $j=4$: $[1.4, 2.5]$ ($1.4 \le 1.5 \le 2.5$, yes) $\implies \text{RETURN} = \text{True}$ (`OURS`).
   - **Back inside value (`FORMULAS.md:674,680`):** Later closes $c[2..5] = [2.5, 2.6, 1.9, 1.9]$; at $j=4$ (and $j=5$), $1.0 \le 1.9 \le 2.0 \implies \text{back\_inside} = \text{True}$ (`OURS`).
   - **Part B accepted away (`FORMULAS.md:675,680`):**
     - $N = 3$ (`OURS`): applicability requires $e + N - 1 = 1 + 2 = 3 \le 5$ ($\text{True}$). Closes of bars $1..3$ are $[2.2, 2.5, 2.6]$, all $> 2.0 \implies \text{accepted}_3 = \text{True}$. Bars strictly after index $3$ are $j \in \{4, 5\}$; bar $4$ has $1.4 \le 1.5 \le 2.5 \implies \text{returned}_3 = \text{True}$ (`OURS`).
     - $N = 6$ (`OURS`): applicability requires $e + 6 - 1 = 6 \le 5$ ($\text{False}$, not applicable).
     - $N = 12$ (`OURS`): applicability requires $e + 12 - 1 = 12 \le 5$ ($\text{False}$, not applicable).
   - **Naked-POC columns (`FORMULAS.md:676,680`):**
     - Exact touch over all bars $0..5$: bar $0$ ($1.2 \le 1.5 \le 1.8$) and bar $4$ ($1.4 \le 1.5 \le 2.5$) contain $1.5 \implies \text{exact} = \text{True}$ (`OURS`).
     - Near touch within $0.3\%$ (`SOURCED` threshold `0.003` from `src/main/java/datafeed/NakedPocTracker.java:26`): band $[1.5 \times 0.997, 1.5 \times 1.003] = [1.4955, 1.5045]$; bar $0$ and bar $4$ satisfy $l \le 1.5045$ and $h \ge 1.4955 \implies \text{near} = \text{True}$ (`OURS`).

3. **Section 29.2 Placebo Shift and Outcome (`FORMULAS.md:677,680`):**
   - `PLACEBO_D` $= (-3, -2, -1, -0.5, 0.5, 1, 2, 3)$ (`OURS` / `NO-SOURCE`, `FORMULAS.md:483,677`).
   - For day index $3$ and $R_{\text{ref}} = 2$ (`OURS`):
     - $d = \text{PLACEBO\_D}[3 \bmod 8] = \text{PLACEBO\_D}[3] = -0.5$ (`OURS`).
     - $\text{shift} = d \times R_{\text{ref}} = -0.5 \times 2 = -1.0$ (`OURS`).
     - Shifted levels: $\text{POC}' = 1.5 - 1.0 = 0.5$, $\text{VAH}' = 2.0 - 1.0 = 1.0$, $\text{VAL}' = 1.0 - 1.0 = 0.0$ (`OURS`).
   - Event on Day $D$ against shifted band: bar $0$ has $c[0] = 1.6 > 1.0 = \text{VAH}' \implies e = 0$, $\text{side} = +1$ (`OURS`).
   - Outcome on later bars $j \in \{1, 2, 3, 4, 5\}$: lows are $[1.7, 2.1, 2.3, 1.4, 1.8]$; minimum later low is $1.4 > 0.5 = \text{POC}'$, so no later bar has $l \le 0.5 \le h \implies \text{RUN-AWAY}$ (`returned = False`, `OURS`).

4. **Section 29.2 Shares and Difference (`FORMULAS.md:678,680`):**
   - Three days with real events $[1, 1, 1]$ and real returns $[1, 1, 0]$ (`OURS`):
     - $\text{share}_{\text{real}} = \frac{1 + 1 + 0}{1 + 1 + 1} = \frac{2}{3} \approx 0.6667$ (`OURS`).
   - Placebo events $[1, 1, 1]$ and placebo returns $[0, 1, 0]$ (`OURS`):
     - $\text{share}_{\text{placebo}} = \frac{0 + 1 + 0}{1 + 1 + 1} = \frac{1}{3} \approx 0.3333$ (`OURS`).
   - Difference (real minus placebo):
     - $\text{diff} = \frac{2}{3} - \frac{1}{3} = \frac{1}{3} \approx 0.3333$ (`OURS`).

---

## Step 2 & 3: Formula-by-Formula Comparison (`FORMULAS.md` Section 29 vs `vp_return_to_value.py`)

| # | Formula / Rule | Status | Spec `file:line` | Code `file:line` | Boundary, Rounding & Provenance Notes |
|---|---|---|---|---|---|
| 1 | Complete UTC day filter: `288` 5m bars required in both $D$ and $D-1$ | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:670,682` | `MyTradingSys/backtest/vp_return_to_value.py:29,89-96` | `BARS_PER_DAY = 288` (`OURS`); loop starts at `start_ms // DAY_MS + 1` so $D-1$ is inside window; exact check `b - a != 288 or pb - pa != 288` increments `dropped["incomplete_day"]`. |
| 2 | Prior-day ($D-1$) volume profile (`poc_price`, `vah`, `val`) with bin $w=10.0$ USD and $70\%$ VA | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:671,680`; `MyTradingSys/backtest/layers/FORMULAS.md:422-437` | `MyTradingSys/backtest/vp_return_to_value.py:97-100`; `MyTradingSys/backtest/vp_pivot_probe.py:28-29,51-112` | `W_BIN = 10.0` (`OURS` / `NO-SOURCE`), `VA_PCT = 0.70` (`SOURCED`, `extracts/processed/tom/extract_BB3c8visnkI.md:28`). `seg.argmax()` (`vp_pivot_probe.py:96`) picks lowest bin on POC ties; `vl >= vh` (`vp_pivot_probe.py:80`) picks lower bin on VA ties; Worked A gives `(1.5, 2.0, 1.0)`. |
| 3 | Event detection: first 5m close of $D$ strictly outside `[VAL, VAH]`, `side` $\in \{+1,-1\}$, `bars_left` | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:672,680` | `MyTradingSys/backtest/vp_return_to_value.py:47-53,138-145` | `OURS`. Strict inequality `out = (c > vah) \| (c < val)` (`vp_return_to_value.py:47`); boundary closes `c == vah` or `c == val` do not fire; `e = int(np.argmax(out))` (`vp_return_to_value.py:51`); `bars_left = len(c) - 1 - e` (`vp_return_to_value.py:53`); Worked 29.2 gives `e = 1, side = 1, bars_left = 4`. |
| 4 | `NO-EVENT` day handling: counted in fire rate, excluded from return-share denominator | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:672` | `MyTradingSys/backtest/vp_return_to_value.py:48-50,138-140,224,229` | `OURS`. When `not out.any()`, `analyse_day` returns `event: None` (`vp_return_to_value.py:49`); `study` leaves `o["event"][i] = 0` (`vp_return_to_value.py:138-140`), so `den` in `share(R["ret"], R["event"], mask)` excludes no-event days while `fire_rate` (`vp_return_to_value.py:229`) averages `R["event"]` over all `nd` days. |
| 5 | Primary outcome `RETURN` vs `RUN-AWAY`: later bar $j > e$ touches prior POC (`l <= poc <= h`) | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:668,673,680` | `MyTradingSys/backtest/vp_return_to_value.py:39-40,54,141` | Tests `SOURCED` 70/30 claim (`extracts/processed/tom/extract_BB3c8visnkI.md:38`) via `OURS` rule `_touch(h[e + 1:], l[e + 1:], poc)`. Slice `e + 1:` is strictly after event bar; `_touch` (`vp_return_to_value.py:40`) uses inclusive `(l <= level) & (h >= level)`. Worked 29.2 gives `returned = True` at bar 4 (`1.4 <= 1.5 <= 2.5`). |
| 6 | Part A last-bar event censoring (`bars_left == 0` $\to$ `None`, counted as no-return) | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:673,682` | `MyTradingSys/backtest/vp_return_to_value.py:55-56,141,143` | `OURS`. If `bars_left == 0`, `analyse_day` sets `returned = None` (`vp_return_to_value.py:55-56`); `study` casts `bool(r["returned"])` to `False` (`0.0` in `o["ret"][i]`, `vp_return_to_value.py:141`) and sets `o["cens_a"][i] = 1` (`vp_return_to_value.py:143`). |
| 7 | Secondary outcome `back_inside`: later bar $j > e$ closes in `[VAL, VAH]` | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:674,680` | `MyTradingSys/backtest/vp_return_to_value.py:57-58,144,228` | `OURS`. Slice `cl = c[e + 1:]` (`vp_return_to_value.py:57`); inclusive boundary check `(cl >= val) & (cl <= vah)` (`vp_return_to_value.py:58`). Worked 29.2 gives `back_inside = True` (bar 4 close `1.9` in `[1.0, 2.0]`). |
| 8 | Part B applicability for $N \in \{3, 6, 12\}$: `e + N - 1 <= len(c) - 1` | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:675,680` | `MyTradingSys/backtest/vp_return_to_value.py:26,60-61,146-148` | `NS = (3, 6, 12)` (`OURS` / `NO-SOURCE`, `vp_return_to_value.py:26`); `applicable = e + n - 1 <= len(c) - 1` (`vp_return_to_value.py:61`, equivalent to `e + N - 1 <= 287` on a 288-bar day). Worked 29.2 (6 bars, `e = 1`) gives `True` for $N=3$ and `False` for $N=6, 12$. |
| 9 | Part B acceptance (`accepted_N`) and post-acceptance POC return (`returned_N`) | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:675,680,682` | `MyTradingSys/backtest/vp_return_to_value.py:64-69,149-151,237-242` | `OURS`. `seg = c[e:e + n]` (`vp_return_to_value.py:65`); strict edge check `np.all(seg > vah)` if `side == 1` else `np.all(seg < val)` (`vp_return_to_value.py:66`); outcome checks `h[e + n:], l[e + n:]` strictly after the $N$-th close (`vp_return_to_value.py:68`), returning `None` (censored, counted `0.0` via `bool(a["returned"])` at `vp_return_to_value.py:150`) when `len(h) <= e + n`. Worked 29.2 gives `accepted = True, returned = True` for $N=3$. |
| 10 | Naked-POC exact touch and $0.3\%$ near touch over all days (`_naked`) | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:676,680` | `MyTradingSys/backtest/vp_return_to_value.py:28,112-115,136-137,244-247` | Threshold `NAKED_PCT = 0.003` is `SOURCED` (`src/main/java/datafeed/NakedPocTracker.java:26`); daily evaluation is `OURS`. Exact: `_touch(h, l, poc)`; near: `np.any((l <= poc * (1 + NAKED_PCT)) & (h >= poc * (1 - NAKED_PCT)))` (`vp_return_to_value.py:115`), denominator `np.ones(nd)` over all complete days (`vp_return_to_value.py:245-246`). Worked 29.2 gives `(True, True)`. |
| 11 | Causal $R_{\text{ref}} = \text{ATR}_{14}$ of 1h bars closed at or before `00:00 UTC` of $D$ | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:677,682`; `MyTradingSys/backtest/layers/FORMULAS.md:331-348` | `MyTradingSys/backtest/vp_return_to_value.py:82,101-106`; `MyTradingSys/backtest/vp_pivot_probe.py:30,116-127` | `OURS`. Plain SMA of 14 1h True Ranges (`P.atr_sma`, `vp_pivot_probe.py:116-127`). `k = int(np.searchsorted(t1 + P.HOUR_MS, day_start, side="right")) - 1` (`vp_return_to_value.py:102`) selects the last 1h bar whose close `t1 + HOUR_MS <= day_start` (no look-ahead); non-finite ATR increments `dropped["no_atr"]` (`vp_return_to_value.py:104-106`). |
| 12 | Placebo band shift `shift_levels` by $d \cdot R_{\text{ref}}$ with `d = PLACEBO_D[idx % 8]` | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:677,680,682`; `MyTradingSys/backtest/layers/FORMULAS.md:482-484` | `MyTradingSys/backtest/vp_return_to_value.py:27,33-36,107,131-134`; `MyTradingSys/backtest/vp_pivot_probe.py:37` | `PLACEBO_D = (-3, -2, -1, -0.5, 0.5, 1, 2, 3)` (`OURS` / `NO-SOURCE`), `idx = d - start_ms // DAY_MS` (`vp_return_to_value.py:107`), `dv = float(PLACEBO_D[dy["idx"] % 8])` (`vp_return_to_value.py:131`), adds `d * r_ref` to `poc_price`, `vah`, `val` (`vp_return_to_value.py:35-36`). Worked 29.2 (`idx=3, r_ref=2`) gives `d = -0.5`, shifted `(0.5, 1.0, 0.0)`, `e = 0, side = 1, returned = False`. |
| 13 | Return share, paired real-minus-placebo difference, and day-block bootstrap 95% CI (`share`, `diff`) | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:678,680`; `MyTradingSys/backtest/layers/FORMULAS.md:486-490` | `MyTradingSys/backtest/vp_return_to_value.py:156-181`; `MyTradingSys/backtest/vp_pivot_probe.py:34-35,262-267` | `OURS`. `N_BOOT = 2000`, `BOOT_SEED = 20261009` (`vp_pivot_probe.py:34-35`); `share` computes `float(num.sum() / den.sum())` and `[nanpercentile(x, 2.5), nanpercentile(x, 97.5)]` (`vp_return_to_value.py:160-171`); `diff` reuses the single `idx = _idx(len(a))` draw for both streams (`vp_return_to_value.py:179-180`). Worked 29.2 gives `2/3 = 0.6667`, `1/3 = 0.3333`, `diff = 0.3333`. |
| 14 | Power gate (`underpowered`), mechanical `verdict`, DEV split guard, and post-hoc `censoring` / `near_band_primary` | `SAME` | `MyTradingSys/backtest/layers/FORMULAS.md:678,682` | `MyTradingSys/backtest/vp_return_to_value.py:24,184-213,234-235,264-281,362-366` | `OURS`. `underpowered(n)` flags `n < 100` (`vp_return_to_value.py:197-198`); `verdict(a)` tests `lo <= 0.70 <= hi` and `dl <= 0 <= dh` (`vp_return_to_value.py:268,275`); `DEV_START..DEV_END` enforced by `assert_dev_only` (`vp_return_to_value.py:364-366`); `censoring` restricts to `bars_left >= 12` (`CENS_MIN_LEFT = 12`, `vp_return_to_value.py:201-213`); `near_band_primary` filters `abs(dvals) <= 1.0` (`vp_return_to_value.py:184-195`). |

Noticed: none — every formula, boundary condition, tie-breaker, censoring rule, and worked example in `MyTradingSys/backtest/layers/FORMULAS.md:666-683` matches `MyTradingSys/backtest/vp_return_to_value.py:1-381` (`SAME=14 DIFF=0 NOT_IN_DATA=0`).
