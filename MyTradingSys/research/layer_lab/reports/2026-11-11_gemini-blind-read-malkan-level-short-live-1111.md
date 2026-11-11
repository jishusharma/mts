CONSISTENT: 6 | CONTRADICTION: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `malkan_level_short_live.py` against its Module Docstring

- **Card**: `gemini-blind-read-malkan-level-short-live-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-malkan-level-short-live-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/backtest/layers/rsi/malkan_level_short_live.py` (implementation and module docstring)
  - `MyTradingSys/backtest/layers/rsi/test_malkan_level_short_live.py` (unit tests verifying docstring clauses)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-malkan-level-short-live-1111.md` (this report)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `malkan_level_short_live.py` or `test_malkan_level_short_live.py`.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
  - No orders, no exchange calls, no auto_trader imports.
- **Verdict**: All 6 required docstring clauses are CONSISTENT across module docstring, implementation, and unit tests (6 CONSISTENT, 0 CONTRADICTION, 0 NOT_IN_DATA).

---

## 1. Docstring Clauses vs Implementation and Tests

| # | Clause Description | Docstring Ref (`malkan_level_short_live.py`) | Implementation Ref (`malkan_level_short_live.py`) | Test Evidence (`test_malkan_level_short_live.py`) | Status |
|---|---|---|---|---|---|
| 1 | `events()` covers the newest closed 4h bar only | L12: `"events(bars4h, bars1d, bars1w) -> runner events for the newest CLOSED 4h bar only (\"t\" = its open ms)."` | L94-103: `i = len(b4) - 1`; `sig = [s for s in M.signals(_with_fill_bar(b4), d, w, **kw) if s["i"] == i]`; `return [{"t": b4[i]["t"], ...}]` | L30-32: `for e in L.events(B4[:k], B1D, B1W, **kw): assert e["t"] == B4[k - 1]["t"], "events() must report the newest closed bar only"` | CONSISTENT |
| 2 | One synthetic fill bar appended after the newest bar | L13-15: `"...so one synthetic fill bar is appended after the newest bar (open = high = close of the newest bar, low far under the prior open): the trigger layers read data up to the trigger bar's close only... so the synthetic bar decides nothing but the fill..."` | L76-79: `def _with_fill_bar(b4): last = b4[-1]; return b4 + [{"t": last["t"] + STEP_4H, "o": last["c"], "h": last["c"], "l": min(last["o"], last["c"]) * 0.5, "c": last["c"]}]`; called in L95, L98 | L43-57: `test_batch_signals_equal_incremental_feed_no_repaint()` verifies `_with_fill_bar` causes parity between batch and incremental alert detection | CONSISTENT |
| 3 | Event has `collection_only` and `shadow_side` "short" but NO `side` | L19: `"Event shape: collection_only + shadow_side \"short\", NO \"side\" (the auto_trader cannot map it, same pattern as wlow_bounce)."` | L101-103: `return [{"t": b4[i]["t"], "event": EVENT, "shadow_side": "short", "collection_only": True, "entry_ref": b4[i]["o"], "stop": s["stop"], "target_r": M.TARGET_R, "max_bars": M.MAX_BARS, "full_stack": bool(full)}]` | L62-63: `assert e["event"] == "MALKAN_LEVEL_SHORT_DIV3_10" and e["shadow_side"] == "short" and e["collection_only"] is True`; `assert "side" not in e` | CONSISTENT |
| 4 | Five journal row kinds (`signal`, `outcome`, `no_fill`, `unresolved`, `kill`) | L20: `"Journal (jsonl, append-only, runtime_data/ is git-ignored): rows kind signal | outcome | no_fill | unresolved | kill."` | L188: `new.append({"kind": "outcome", ...})`; L190: `new.append({"kind": "no_fill", ...})`; L192: `new.append({"kind": "unresolved", ...})`; L198: `new.append({"kind": "kill", ...})`; L204: `new.append({"kind": "signal", ...})` | L132: `assert [r["kind"] for r in _rows(jp)] == ["signal"]`; L135: `out = [r for r in _rows(jp) if r["kind"] == "outcome" ...]` ; L164: `assert any(r["kind"] == "kill" for r in _rows(jp))` | CONSISTENT |
| 5 | Kill rule: after `KILL_TRADES` closed paper trades with net R <= 0 -> verdict `KILL`, alerts stop | L21: `"Kill rule (FORWARD_PREREG.md, operator-set, OURS): after KILL_TRADES closed paper trades net R <= 0 -> verdict KILL, alerts stop."` | L39: `KILL_TRADES = 30`; L144-147: `nets = [r["net_r"] for r in rows if r.get("kind") == "outcome" and r.get("status") == "closed"]`; `verdict = "RUNNING" if n < KILL_TRADES else ("KILL" if total <= 0 else "PAST_30")`; L196-200: `if k["verdict"] == "KILL": ... return []` | L150-156: `test_kill_rule_30_closed_trades_net_r_le_zero()`; L158-165: `test_step_stops_alerting_after_the_kill(tmp_path)` | CONSISTENT |
| 6 | No order, exchange call, or `auto_trader` import anywhere | L3: `"Pure decision code for the runner: NO order, NO exchange call, NO auto_trader path."` | L23-28: imports only stdlib (`json`, `math`, `sys`, `pathlib.Path`) and pure math sibling `MyTradingSys.backtest.layers.rsi.malkan_level_short as M`; 0 exchange/order/network imports | L2: `"Fixtures: the three 2026 BTC csv files of test_malkan_level_short.py (closed bars only). No network, no order, no exchange."`; L174: `assert "side" not in e and "layer_rules" not in e` | CONSISTENT |

---

## 2. Test Execution Verification

Command:
```bash
python -m pytest MyTradingSys/backtest/layers/rsi/test_malkan_level_short_live.py
```
Result:
`13 passed in 29.63s` (SOURCED: pytest output on live worktree).
All test assertions covering the 6 clauses pass cleanly.
