MATCH: 24 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `malkan_level_short_live.py` vs `FORWARD_PREREG.md`

- **Card**: `gemini-blind-read-of-malkan-level-short-`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-of-malkan-level-short-`)
- **Date**: 2026-11-10 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/research/malkan_level_shorts_2026-11-09/FORWARD_PREREG.md` (SOURCED/OURS spec)
  - `MyTradingSys/backtest/layers/rsi/malkan_level_short_live.py` (implementation)
  - `MyTradingSys/backtest/layers/rsi/malkan_level_short.py` (underlying imported signal / outcome library)
- **Scope Out Respected**:
  - No edits to read files.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
  - No orders, no trades, no exchange network calls.
- **Verdict**: No findings (all 24 clauses MATCH; 0 DIFF; 0 NOT_IN_DATA).

---

## 1. Clause-by-Clause Verification Table

| # | Spec Clause / Pinned Item | `FORWARD_PREREG.md` Ref | `malkan_level_short_live.py` Implementation & Evidence | Status |
|---|---|---|---|---|
| 1 | Symbol / Timeframe: BTCUSDT, closed 4h bars | L10: `BTCUSDT, closed 4h bars` | L12, L33, L61-73: `STEP_4H = 4 * 3600 * 1000`; `_closed(bars, step, t_close)`; runner registry key `malkan\|level_short\|4h` | MATCH |
| 2 | Arm layers: level + structure(div) + trigger | L11-12: `level + structure (divergence) + trigger` | L32: `ARM = {"layers": M.BASE \| {"structure"}, ...}`; `M.BASE = frozenset({"level", "trigger"})` | MATCH |
| 3 | Arm div_window: (3, 10) | L11: ``div_window` (3, 10)` | L32: `"div_window": (3, 10)` | MATCH |
| 4 | Arm price_mode: close | L11: ``price_mode` close` | L32: `"price_mode": "close"` | MATCH |
| 5 | Arm structure: div | L11: ``structure` div` | L32: `"structure": "div"` | MATCH |
| 6 | Not layers of this arm: WaveTrend and HTF | L13: `Not layers of this arm: WaveTrend and HTF` | L8, L32: `ARM` specifies only `M.BASE \| {"structure"}` (`level`, `trigger`, `structure`); excludes `wavetrend` and `htf` | MATCH |
| 7 | Full stack agreement logged as `full_stack` | L13, L30: `The 5-layer agreement at the same bar is logged as full_stack, never used as a gate` | L98-103, L205: `full = [s for s in M.signals(..., layers=M.FULL, structure="either", ...)]`; `e["full_stack"] = bool(full)` | MATCH |
| 8 | Fail closed on short daily history (< 30 closed dailies) | L13: `HTF history must still exist (>= 30 closed dailies...)` | L36, L67-73: `MIN_1D = 30`; returns `None` (and `events()` returns `[]`) if `len(d) < MIN_1D` | MATCH |
| 9 | Fail closed on short weekly history (< 20 closed weeklies) | L13: `HTF history must still exist (... >= 20 closed weeklies...)` | L37, L67-73: `MIN_1W = 20`; returns `None` (and `events()` returns `[]`) if `len(w) < MIN_1W` | MATCH |
| 10 | Fail closed on short 4h history (< 400 4h bars) | L13: `HTF history must still exist (... >= 400 4h bars, else no signal)` | L35, L67: `MIN_4H = M.LEVEL_LOOKBACK + 40` (360 + 40 = 400); returns `None` if `len(b4) < MIN_4H` | MATCH |
| 11 | Bar closure requirement: closed HTF bars only at trigger close | L10, L13: `closed 4h bars`; `closed dailies`; `closed weeklies` | L61-73: `_closed(bars, step, t_close)` filters `x["t"] + step <= tc` where `tc = b4[-1]["t"] + STEP_4H` | MATCH |
| 12 | Newest closed 4h bar only reported | L12, L30: `runner events for the newest CLOSED 4h bar only ("t" = its open ms)` | L94-101: `i = len(b4) - 1`; filters `[s for s in ... if s["i"] == i]`; returns event with `b4[i]["t"]` | MATCH |
| 13 | Entry: stop-sell under trigger bar's open within next 3 bars | L14: `a stop-sell under the trigger bar's open within the next 3 bars` | L16, L101: alert carries `"entry_ref": b4[i]["o"]`; L38: `NO_FILL_AFTER = 3`; `malkan_level_short.py:146-150`: checks `jj in range(i+1, min(i+4, len(b4)))` for `b4[jj]["l"] < ref` | MATCH |
| 14 | Stop: highest high of last 8 bars through fill bar +5 bps | L15: `highest high of the last 8 bars through the fill bar, +5 bps` | `malkan_level_short.py:107, 153`: `lo = i - WINDOW` (where `WINDOW = 8`); `stop = max(h[max(lo, 0):j + 1]) * 1.0005` | MATCH |
| 15 | Target: 2R | L16: `2R` | L102, L132: `"target_r": M.TARGET_R` (where `M.TARGET_R = 2.0`); `target = entry - 2.0 * risk` | MATCH |
| 16 | Time stop: 60 bars (close of bar 60) | L17: `60 bars (close of bar 60)` | L102, L133, L161, L167-176: `"max_bars": M.MAX_BARS` (where `M.MAX_BARS = 60`); exits at `k = min(j + max_bars, len(bars)) - 1` | MATCH |
| 17 | Stop priority: stop wins a bar that touches both stop and target | L17: `stop wins a bar that touches both` | `malkan_level_short.py:168-173`: `if bars[k]["h"] >= stop: return exit: stop` evaluated strictly before target check | MATCH |
| 18 | Fee: BINANCE_TAKER each side, charged in R | L18: ``fees.BINANCE_TAKER`, each side, charged in R` | L28, L130, L161-165: imports `M`; `fee_r = fee * 2 * entry / risk`; `net_r = gross_r - fee_r`; `M.FEE = BINANCE_TAKER` | MATCH |
| 19 | One trade at a time: trigger within 6 bars of filled signal skipped | L19: `a trigger within 6 bars of a filled signal is skipped` | `malkan_level_short.py:98, 100, 157`: `skip_to = i + 6`; if `i < skip_to: continue` | MATCH |
| 20 | Kill rule threshold: 30 closed paper trades | L24: `After 30 closed paper trades` | L39, L146: `KILL_TRADES = 30`; `if n < KILL_TRADES: RUNNING` | MATCH |
| 21 | Kill condition: sum of net R <= 0 | L24: `if the sum of net R <= 0 (equivalently the mean) the arm FAILS: verdict KILL` | L146: `verdict = "RUNNING" if n < KILL_TRADES else ("KILL" if total <= 0 else "PAST_30")` | MATCH |
| 22 | Kill action: live layer stops emitting alerts & journals kill row | L24: `verdict KILL, the live layer stops emitting alerts, one kill row is journaled` | L196-200: `if k["verdict"] == "KILL": ... new.append({"kind": "kill", ...}); _append(...); return []` | MATCH |
| 23 | Non-counting trades: no_fill and unresolved do not count towards 30 | L25: `no_fill and does not count. A trigger that left the history window unresolved ... does not count` | L144: `nets = [r["net_r"] for r in rows if r.get("kind") == "outcome" and r.get("status") == "closed"]` (filters only closed outcomes) | MATCH |
| 24 | Event shape: collection_only + shadow_side short, NO side key | L30: ``collection_only` + `shadow_side` "short", no `side`` | L101: `{"event": EVENT, "shadow_side": "short", "collection_only": True, ...}` - no `"side"` key present | MATCH |

---

## 2. Summary & Audit Verdict

- Checked Clauses: 24
- MATCH: 24
- DIFF: 0
- NOT_IN_DATA: 0
- Findings: No findings. All frozen parameters, layer constraints, HTF fail-closed boundaries, event shapes, resolution semantics, and kill-rule mechanisms in `malkan_level_short_live.py` strictly match `FORWARD_PREREG.md`.
