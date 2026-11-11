MATCH: 6 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `rsi_ma_cross_live.py` against its Docstring and Tests

- **Card**: `gemini-blind-read-rsi-ma-cross-live-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-rsi-ma-cross-live-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/backtest/layers/rsi/rsi_ma_cross_live.py` (implementation and module docstring)
  - `MyTradingSys/backtest/layers/rsi/test_rsi_ma_cross_live.py` (unit tests verifying docstring clauses)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `rsi_ma_cross_live.py` and `test_rsi_ma_cross_live.py`.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
  - No orders, no exchange calls, no auto_trader imports.
- **Verdict**: All 6 required docstring clauses MATCH live implementation and test assertions (6 MATCH, 0 DIFF, 0 NOT_IN_DATA).

---

## 1. Clause Verification Table (6 Docstring Clauses)

| # | Clause Description | Docstring Ref (`rsi_ma_cross_live.py`) | Implementation Ref (`rsi_ma_cross_live.py`) | Test Evidence (`test_rsi_ma_cross_live.py`) | Status |
|---|---|---|---|---|---|
| 1 | Newest closed 4h bar only | L8: `"events(b4) -> runner events for the newest CLOSED 4h bar only (\"t\" = its open ms), both sides pooled (T06)."` | L67-72: `i = len(b4) - 1`; `for side in SIDES: if i in S.events_for(b4, side): ... out.append({\"t\": b4[i][\"t\"], ...})` | L22: `assert e[\"t\"] == B4[k - 1][\"t\"], \"events() must report the newest closed bar only\"` | MATCH |
| 2 | No side key (event has collection_only and shadow_side but no side) | L10: `"Event shape: collection_only + shadow_side, NO \"side\" (the auto_trader cannot map it)."` | L72: `out.append({\"t\": b4[i][\"t\"], \"event\": EVENT[side], \"shadow_side\": side, \"collection_only\": True, ...})` | L39: `assert \"side\" not in e and e[\"collection_only\"] is True and e[\"shadow_side\"] == side`; L117: `assert all(\"side\" not in e for e in incremental().values())` | MATCH |
| 3 | Five journal row kinds (`signal`, `outcome`, `no_fill`, `unresolved`, `kill`) | L12: `"Journal (jsonl, append-only, runtime_data/ is git-ignored): rows kind signal \| outcome \| no_fill \| unresolved \| kill."` | L163: `\"kind\": \"outcome\"`; L165: `\"kind\": \"no_fill\"`; L167: `\"kind\": \"unresolved\"`; L172: `\"kind\": \"kill\"`; L178: `\"kind\": \"signal\"` | L92: `assert [r[\"kind\"] for r in rows] == [\"signal\"]`; L97: `assert kinds == [\"signal\", \"outcome\"]`; L109: `assert any(json.loads(x)[\"kind\"] == \"kill\" for x in jp.read_text().splitlines())` | MATCH |
| 4 | Kill rule: after KILL_TRADES closed paper trades with net R <= 0 -> verdict KILL, alerts stop | L13: `"Kill rule (OURS, same as the Malkan forward): after KILL_TRADES closed paper trades net R <= 0 -> verdict KILL, alerts stop."` | L36: `KILL_TRADES = 30`; L114-117: `nets = [r[\"net_r\"] for r in rows if r.get(\"kind\") == \"outcome\" and r.get(\"status\") == \"closed\"]`; `verdict = \"RUNNING\" if n < KILL_TRADES else (\"KILL\" if total <= 0 else \"PAST_30\")`; L170-174: `if k[\"verdict\"] == \"KILL\": ... return []` | L102-111: `def test_kill_rule_after_30_losing_trades_stops_alerts(tmp_path): ... assert L.step(B4[:i + 1], str(jp)) == []` | MATCH |
| 5 | No order, exchange, or auto_trader import anywhere | L3: `"Pure decision code for the runner: NO order, NO exchange call, NO auto_trader path."` | L18-22: imports only standard library (`importlib.util`, `json`, `math`, `sys`, `pathlib.Path`); zero imports of `auto_trader`, `requests`, `urllib`, `ccxt`, `execution` | L114-116: `def test_no_order_or_auto_trader_path(): imports = ...; assert all(not any(b in x for b in (\"auto_trader\", \"requests\", \"urllib\", \"ccxt\", \"execution\")) for x in imports)` | MATCH |
| 6 | Parity: batch == one-bar feed | L8-9: `"RSI is causal, so the signal on bar i is the same on any history that ends at i (parity test: batch == one-bar-at-a-time feed)."` | L67-76: `events(b4)` computes trigger on `len(b4) - 1` slice via causal Wilder RSI14 + SMA14 logic in frozen study | L27-33: `def test_batch_equals_one_bar_feed(): ... assert {t for (t, s) in inc if s == side} == set(b)` | MATCH |

---

## 2. Test Execution Verification

Command:
```bash
python -m pytest MyTradingSys/backtest/layers/rsi/test_rsi_ma_cross_live.py
```
Result:
`7 passed in 19.34s` (SOURCED: pytest output on live worktree). All assertions covering the 6 clauses pass cleanly.
