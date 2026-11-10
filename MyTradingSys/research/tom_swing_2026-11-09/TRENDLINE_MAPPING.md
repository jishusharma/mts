# Mapping Tom Swing Rules to Trendline Core & Contract v1

**Task Card:** `tom-swing-trendline-extract-1109`  
**Video ID:** `M7ompiwv5co` ("The Easiest Way to Start Trading (Swing Trading for Beginners)", Tom Vorwald EN, 2026-11-04)  
**Reference Implementations & Contracts:**
- `MyTradingSys/backtest/layers/trendlines/trendline_core.py`
- `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md` (v1 / v1.1)
- `MyTradingSys/research/trendlines_2026-10-17/AUDIT_2026-10-18.md`

---

## 1. Rule-by-Rule Contract Mapping

| # | Tom Swing Concept (`M7ompiwv5co`) | Status | Mapping to `trendline_core.py` / `TRENDLINE_CONTRACT.md` v1 | Gap / Specification Note |
|---|---|---|---|---|
| **1** | **Timeframe & Bar Close Basis:** Daily close evaluation ("wait for daily closing prices", holds several days to 1–2 weeks) | **COVERED** | `TRENDLINE_CONTRACT.md` F2 ("Time: UTC; bar stamped by open time; a bar exists to the detector only after its close") and F3 (`1d` detector instance). | Causal detector runs on closed bars only (`tf_resample.py`). |
| **2** | **Market Phases (Impulse vs Sideways Accumulation):** Two phases: range/consolidation and trend | **PARTIAL** | Contract L2/L7: L7 routes flat pairs (`abs(pb - pa) <= 0.25 * ATR_b`) to horizontal family; L2 handles directional trends. | `trendline_core.py` detects diagonal lines and isolates horizontal pairs, but does not explicitly label the macro market state as "range" vs "trend" in a unified phase classifier. |
| **3** | **Chart Geometry (Line Chart Closes vs Candlestick Wicks):** "Let's just take this line chart here" | **PARTIAL (BLOCKED BY GAP 1)** | Contract P5 specifies both `wick` (primary) and `close` (secondary, line chart) arms. | `trendline_core.py` implemented `price_arm="close"`, but Gap 1 in `AUDIT_2026-10-18.md` found `_penetration_ok` and `_advance` unconditionally test `low` / `high` wicks, killing 99.9% of close lines. |
| **4** | **Pivots & Swings (Swings 1/2/3 Anchor Formation):** Directional swings marking boundary | **COVERED** | Contract P1–P6: swing highs/lows confirmed causally after $k=3$ bars (`P3`), strict inequality (`P4`), lag shape (`P6`). | Arm A requires 2 swings + touch; Arm B requires 3 confirmed swings. |
| **5** | **Entry Trigger: Breakout with Impulse & Volume:** Break above boundary/line with expansion volume | **PARTIAL** | `trendline_core.py` tracks state transitions (`touched`, `broken`). Contract B1 emits `break` event. | Volume expansion confirmation (volume > baseline) is not integrated into `trendline_core.py` itself; requires upstream/downstream volume gate. |
| **6** | **Stop Loss Placement: Structural Floor Below Sideways Base:** Stop placed below the support level / last sideways phase | **MISSING** | `trendline_core.py` is an event detector (emits line coordinates, touch, break, retest), not an execution manager. Contract has no structural order placement logic. | Needs an execution model mapping the entry candle to the lowest swing low of the consolidation phase as the structural stop. |
| **7** | **Profit Target 1: Prior Liquidity / High-Volume Node (HVN):** Target set at previous consolidation / POC / HVN | **MISSING** | Trendline layer has no volume-profile or horizontal liquidity node target resolver. | Must interface with Volume Profile / Pit Levels layer (`vp_core` / `pit_levels`) to look up prior high-volume clusters. |
| **8** | **Profit Target 2: Measured Move (Distance Alpha):** Mirror impulse distance from consolidation base | **PARTIAL** | Handled mathematically via swing distance projection ($Target = Entry + (SwingHigh - SwingLow)$). | Formula exists in `backtest/layers/FORMULAS.md` §19, but is not emitted by `trendline_core.py`. |
| **9** | **Trade Management: Minimum R:R $\ge 1.5$:** | **MISSING** | Not in `trendline_core.py`. | Requires pre-trade trade validator: $(Target - Entry) / (Entry - Stop) \ge 1.5$. |

---

## 2. FIX-FIRST Gaps from AUDIT_2026-10-18 Blocking a Count

From `MyTradingSys/research/trendlines_2026-10-17/AUDIT_2026-10-18.md` §2, the following critical gaps directly block running a valid Tom swing count on BTC `4h` and `1d`:

1. **Gap 1 (HIGH) — `price_arm="close"` is dead by construction:**
   - *Audit finding:* `TRENDLINE_CONTRACT.md` P5 defines the close arm for line charts (Tom's exact stated method: "Let's just take this line chart here"). In `trendline_core.py:206-217`, `_penetration_ok` and `_advance` unconditionally test wicks (`bar["l"] < L - tol` and `bar["h"] > L + tol`) against the close-derived line, rejecting 10,523 pairs at 4h and 1,579 at 1d, leaving **1 line at 4h and 0 lines at 1d**.
   - *Blocker:* A pure line-chart close-based swing count cannot run until `_penetration_ok` uses `bar["c"]` for close-arm lines.
2. **Gap 2 (HIGH) — Pre-availability replay (`ib + 1 .. ib + k`) induces lookahead state transitions:**
   - *Audit finding:* A pivot $b$ at bar $ib$ is only causally confirmed at $t = ib + k$ ($k=3$). When a candidate line is formed, `trendline_core.py:199-200` replays bars $ib + 1 .. ib + k - 1$, causing lines to be born already "touched" or "eligible" prior to their causal birth.
   - *Blocker:* Distorts touch episode counts and breakout triggers on 4h and 1d bars.
3. **Gap 3 (HIGH) — `_broken_anchor` (E11) globally poisons anchor $ia$ across all lines:**
   - *Audit finding:* If an early steep inner trendline breaks, `trendline_core.py:177-178` permanently forbids anchor $ia$ from pairing with any subsequent higher low $ib2$, killing valid outer macro trendlines.
   - *Blocker:* Artificially depresses 4h and 1d swing counts over multi-year bull/bear runs.
4. **Gap 4 (MEDIUM) — Multi-touch inflation & uncounted retest/reclaim events:**
   - *Audit finding:* `count_only.py` counts 2nd, 3rd, and 4th touches on the same line repeatedly, while failing to count breakout and retest events.
   - *Blocker:* Violates Tom's rule of discrete swing entries (swings 1, 2, 3).
