CONSISTENT 6, CONTRADICTION 0

# Gemini blind read of forward_readout.py against its docstring

Audit date: 2026-11-11
Auditor: Gemini (gemini-3.8-flash-low)
Target: `MyTradingSys/research/fable_run7_forward_test/forward_readout.py`
Scope in: `MyTradingSys/research/fable_run7_forward_test/forward_readout.py` (read); `MyTradingSys/research/fable_run7_forward_test/test_forward_readout.py` (read)

## Summary Table

| Clause | Docstring Specification | Implementation & Test Citation | Verdict |
|---|---|---|---|
| 1. Three slots by source prefix | "Slots (source prefix; Krown also needs account krown_s8, else the fill is CONTAMINATED and excluded):<br>krown_s8 layer:krown:s8_break:4h testnet FAIL-A/B/C apply (FORWARD_PREREG s3)<br>malkan_level_short layer:rsi:malkan_level_short paper E+/E- only<br>t06_rsi_ma layer:rsi:rsi_ma_cross paper E+/E- only" (`forward_readout.py:8-11`) | `forward_readout.py:31-35`, `forward_readout.py:198-202`, `forward_readout.py:217-220`; verified by `test_forward_readout.py:124-132` | CONSISTENT |
| 2. Krown account filter | "Krown also needs account krown_s8, else the fill is CONTAMINATED and excluded" (`forward_readout.py:8`) | `forward_readout.py:32`, `forward_readout.py:204-206`, `forward_readout.py:221`, `forward_readout.py:239-240`; verified by `test_forward_readout.py:101-106` | CONSISTENT |
| 3. Risk fallback order | "the risk in USD, first found of: risk_usd \| stop with entry.price and entry.amount (\|price - stop\| / price x amount) \| net_r." (`forward_readout.py:4-6`) | `forward_readout.py:56-64` in `row_r(row)` | CONSISTENT |
| 4. Unresolved counted not scored | "Rows with \"unresolved\" or no R are counted, never scored." (`forward_readout.py:6`) | `forward_readout.py:54-55`, `forward_readout.py:178`, `forward_readout.py:207-213`, `forward_readout.py:221`, `forward_readout.py:239-240`; verified by `test_forward_readout.py:108-113` | CONSISTENT |
| 5. Day cluster observation | "One observation per UTC-day cluster (mean R of that day's trades); n in the table counts trades, n_obs counts clusters." (`forward_readout.py:12-13`) | `forward_readout.py:126-131`, `forward_readout.py:214-220`, `forward_readout.py:238`; verified by `test_forward_readout.py:133-138` | CONSISTENT |
| 6. sim_sequential loaded not copied | "The E+/E- math is sim_sequential.py's (eh-f1-testnet-design), loaded not copied." (`forward_readout.py:12-13`) | `forward_readout.py:27-28`, `forward_readout.py:40-45`, `forward_readout.py:135-140`, `forward_readout.py:175`; verified by `test_forward_readout.py:115-122` | CONSISTENT |

## Detailed Clause Verification

### Clause 1: Three slots by source prefix
- **Docstring quote**: `"Slots (source prefix; Krown also needs account krown_s8, else the fill is CONTAMINATED and excluded):` / `  krown_s8            layer:krown:s8_break:4h        testnet   FAIL-A/B/C apply (FORWARD_PREREG s3)` / `  malkan_level_short  layer:rsi:malkan_level_short   paper     E+/E- only` / `  t06_rsi_ma          layer:rsi:rsi_ma_cross         paper     E+/E- only"` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:8-11`)
- **Code verification**:
  - `forward_readout.py:31-35`: `SLOTS = [("krown_s8", "layer:krown:s8_break:4h", "krown_s8", True, "Krown S8 4h (testnet)"), ("malkan_level_short", "layer:rsi:malkan_level_short", None, False, "Malkan level short 4h (paper)"), ("t06_rsi_ma", "layer:rsi:rsi_ma_cross", None, False, "T06 RSI-MA 4h (paper)")]`
  - `forward_readout.py:198-200`: `slot = next((s for s in SLOTS if src.startswith(s[1])), None)` matching by source prefix.
  - `forward_readout.py:217-220`: Iterates through each of the 3 slots in `SLOTS`.
- **Test verification**:
  - `test_forward_readout.py:124-132`: `test_markdown_table_has_every_slot_and_columns` verifies slots `"krown_s8"`, `"malkan_level_short"`, `"t06_rsi_ma"`.
- **Verdict**: CONSISTENT.

### Clause 2: Krown account filter
- **Docstring quote**: `"Krown also needs account krown_s8, else the fill is CONTAMINATED and excluded"` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:8`)
- **Code verification**:
  - `forward_readout.py:32`: `("krown_s8", "layer:krown:s8_break:4h", "krown_s8", True, "Krown S8 4h (testnet)")` defines `"krown_s8"` as the required account.
  - `forward_readout.py:204-206`: `if acct and row.get("account") != acct: contaminated += 1; continue` excludes rows with mismatched account and increments the contaminated count.
  - `forward_readout.py:239-240`: Markdown output records `f"Excluded: contaminated (Krown source, other account) {res['contaminated']}..."`.
- **Test verification**:
  - `test_forward_readout.py:101-106`: `test_other_account_krown_is_contaminated_and_excluded` asserts that 20 rows with non-matching accounts are excluded (`k["n"] == 2 and res["contaminated"] == 20`).
- **Verdict**: CONSISTENT.

### Clause 3: Risk fallback order
- **Docstring quote**: `"and the risk in USD, first found of: risk_usd | stop with entry.price and entry.amount (|price - stop| / price x amount) | net_r."` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:4-6`)
- **Code verification**:
  - `forward_readout.py:56-64`:
    - Priority 1: `risk = row.get("risk_usd")` (`forward_readout.py:56`)
    - Priority 2: `if risk is None and row.get("stop") and e.get("price") and e.get("amount"): risk = abs(e["price"] - row["stop"]) / e["price"] * e["amount"]` (`forward_readout.py:58-59`)
    - Calculation from risk: `if risk: return row["net_pnl_usd"] / risk` (`forward_readout.py:60-61`)
    - Priority 3: `if row.get("net_r") is not None: return float(row["net_r"])` (`forward_readout.py:62-63`)
- **Verdict**: CONSISTENT.

### Clause 4: Unresolved counted not scored
- **Docstring quote**: `"Rows with \"unresolved\" or no R are counted, never scored."` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:6`)
- **Code verification**:
  - `forward_readout.py:54-55`: `if row.get("unresolved") or row.get("net_pnl_usd") is None: return None` in `row_r(row)`.
  - `forward_readout.py:207-209`: `if row.get("unresolved"): unresolved += 1; continue` skips scoring and increments `unresolved` count.
  - `forward_readout.py:210-213`: `r = row_r(row); if r is None: unscored += 1; continue` skips scoring and increments `unscored` count.
  - `forward_readout.py:239-240`: Markdown lists excluded counts for `unresolved` and `no risk/R`.
- **Test verification**:
  - `test_forward_readout.py:108-113`: `test_unresolved_rows_counted_not_scored` asserts `res["unresolved"] == 1` and slot trade count `n == 1`.
- **Verdict**: CONSISTENT.

### Clause 5: Day cluster observation
- **Docstring quote**: `"One observation per UTC-day cluster (mean R of that day's trades); n in the table counts trades, n_obs counts clusters."` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:12-13`)
- **Code verification**:
  - `forward_readout.py:126-130`: Groups trades by date: `clusters = {}; for r, d in zip(rs, days): clusters.setdefault(d, []).append(r); obs = [sum(v) / len(v) for _, v in sorted(clusters.items())]` computing the daily mean R.
  - `forward_readout.py:131`: `res = {"slot": key, "n": n, "n_obs": len(obs), ...}` where `n` is total trades and `n_obs` is cluster count.
  - `forward_readout.py:214-220`: Extracts entry date `[t.date() for t, _ in items]` from UTC timestamps `_ts(ts)`.
- **Test verification**:
  - `test_forward_readout.py:133-138`: `test_same_day_trades_pool_into_one_observation` verifies that 4 trades across 2 UTC days result in `r["n"] == 4` and `r["n_obs"] == 2`.
- **Verdict**: CONSISTENT.

### Clause 6: sim_sequential loaded not copied
- **Docstring quote**: `"The E+/E- math is sim_sequential.py's (eh-f1-testnet-design), loaded not copied."` (`MyTradingSys/research/fable_run7_forward_test/forward_readout.py:12-13`)
- **Code verification**:
  - `forward_readout.py:27-28`: `ROOT = Path(__file__).resolve().parents[3]`; `SIM_PATH = ROOT / "MyTradingSys/research/edge_hunt_2026-11-09/results/eh-f1-testnet-design/sim_sequential.py"`
  - `forward_readout.py:40-45`: Dynamically loads module via `importlib.util.spec_from_file_location("sim_sequential", SIM_PATH)`.
  - `forward_readout.py:135-140`: Uses loaded `sim.RuleCfg()`, `sim.e_promote(x, cfg.mu0, cfg.a)`, `sim.e_kill(x, cfg.delta, cfg.b)`, and `sim.decide(x, cfg)`.
- **Test verification**:
  - `test_forward_readout.py:115-122`: `test_matches_sim_sequential_math` dynamically imports via `fr.load_sim()` and compares calculated E+/E- outputs directly with `sim.e_promote` and `sim.e_kill`.
- **Verdict**: CONSISTENT.
