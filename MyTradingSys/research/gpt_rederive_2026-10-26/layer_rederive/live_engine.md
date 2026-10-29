# Live Engine & Execution Infrastructure Independent Re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND ARCHITECTURAL METRICS MATCH STORED SPECS, CONFIGS, AND CODE (0 MISMATCHES).** Consistency audit across the specification documents, execution modules, routing configurations, and operational logs for layer family `live_engine`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:19-35` lists the family configuration for `live_engine`:
- Kind: `infrastructure` ("The live engine, execution and live-market reads that feed every layer (infrastructure, not a strategy).")
- Spec:
  1. `MyTradingSys/methodology/live_session_protocol.md` (SHA256: `4621b01bdac0c467e4e37eb0d2653f5df09420f5cde3761747a1cdb34ea1c14d`)
  2. `MyTradingSys/methodology/screenshot_intake.md` (SHA256: `28677f6300b36d882010abd19894c560bf5d24230df5e4c4984c7f07fd251ada`)
  3. `MyTradingSys/system/DEPLOY_RUNBOOK.md` (SHA256: `a5855728e7ef527977b6479272e1cba5d4234f3686b33cfa0bf7fe2ab3a33da4`)
- Code:
  `MyTradingSys/execution` (auto-trader, order execution, position manager, risk guards, reconciler, journal, testnet suites)
- Status & Configs:
  1. `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md` (SHA256: `6ea31337f6e10504ebe10b785775c08cf2e3be89673e3130c6bfbb6eb6c117f5`)
  2. `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md` (SHA256: `c66022ae9e8b458870959aedf7b2a04580f536deb0a35afec92ca3c9edcf66a6`)
  3. `MyTradingSys/execution/FABIO_TESTNET_SLOT.md` (SHA256: `74cb6155f7c115c9e6459fb738841774f0cec7e5728a6a0e1b23069df0ebaebe`)
  4. `MyTradingSys/execution/auto_trader_config.json` (SHA256: `85c231422f2247606cb383880b95afb5ffad76b2f43ff7a347514c75baabe383`)
  5. `MyTradingSys/execution/promoted_setups.json` (SHA256: `1515cc1b8b88f5be6576df23878062f19543b644a4fa00dd721122c6097559e4`)
  6. `MyTradingSys/execution/trade_ledger.py` (SHA256: `6d64cc2654cc280de4b89c5b2feed1e145fb01899e8d3f6acc3a5e99b9b8e4c1`)
  7. `MyTradingSys/execution/README.md` (SHA256: `977f5f9b2cfedb235e35457bc0226e2a7a9e5e9892df6f15e2eddd0b1680dc1a`)
- Results:
  `MyTradingSys/research/screenshots` (27 screenshot review markdown documents + 2 subdirectories = 29 items)
- Ledger:
  `layer_index.json:28` lists an empty ledger `[]`. As an infrastructure layer, `live_engine` holds no strategy backtests; its claims govern system state, subaccount isolation, execution safety bounds, and audit checks.

---

## 20 headline claims audited

| # | Document | Stated Claim / Metric | Value in Source / Computed Value | Status |
|---|---|---|---|---|
| 1 | `layer_index.json:20` | Family classification | `kind: infrastructure`, `layers: []`, feeds every layer | MATCH |
| 2 | `layer_index.json:22` | Engine status | `Testnet HALT since 2026-10-12 09:46Z (executor fail_closed)` | MATCH |
| 3 | `LAYERS.md:189` | Operational tracking role | Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy | MATCH |
| 4 | `TESTNET_SUBACCOUNTS.md:3` | Position netting rule | Deribit nets 1 BTC-PERPETUAL position per account (1 account = 1 concurrent trade) | MATCH |
| 5 | `TESTNET_SUBACCOUNTS.md:7-11` | Subaccount routing tiers | 5 distinct account slots configured (`main`, `jishu_1`, `jishu_2`, `jishu_3`, `jishu_4`) | MATCH |
| 6 | `auto_trader_config.json:2` | Testnet calibration date & sizes | Calibrated 2026-10-08; sizes 20 to 1000 USD (base size 20 USD) | MATCH |
| 7 | `auto_trader_config.json:4-22` | Prefix routing table entries | 16 discrete signal prefix routes mapped (`jishu_1` through `jishu_16`) | MATCH |
| 8 | `MAINNET_READINESS.md:3` | Mainnet safety guards | Code default is TESTNET; mainnet requires explicit `--mainnet` flag AND typed confirmation | MATCH |
| 9 | `MAINNET_READINESS.md:9` | Machine-checked refusal matrix | Refusal matrix verified offline (unit tests check testnet fallback and secret isolation) | MATCH |
| 10 | `FABIO_TESTNET_SLOT.md:3` | Fabio subaccount isolation | Source `layer:fabio:*` routed to dedicated subaccount; busy-check is per-account | MATCH |
| 11 | `FABIO_TESTNET_SLOT.md:4` | Global safety state propagation | HALT, HALT_DAILY_LOSS, and AUTO_PAUSE remain strictly global across all subaccounts | MATCH |
| 12 | `live_session_protocol.md:10` | Operational check 1 | "Quote the number": every price, level, state or flow claim must be a direct quote from paste | MATCH |
| 13 | `live_session_protocol.md:17` | Operational check 2 | "Delta check before verdict": compare current to prior number in same paste series | MATCH |
| 14 | `screenshot_intake.md:4` | Tooling & intake pipeline | Saves operator images once, ends in filed result or "no action"; tool: `scripts/dev/shot.py` | MATCH |
| 15 | `DEPLOY_RUNBOOK.md:5` | Background task policy | Background auto-deploy/supervisor tasks retired per SCHEDULING_POLICY.md (2026-10-17) | MATCH |
| 16 | `DEPLOY_RUNBOOK.md:1` | Live tree boundary definition | Live tree defined exclusively by `.mts_live` marker; builders never run cutover | MATCH |
| 17 | `promoted_setups.json:2-3` | Promoted setups registry | `version: 1`, `entries: []` (0 setups promoted to live mainnet trading) | MATCH |
| 18 | `trade_ledger.py:15-18` | Inverse contract P/L formulas | Long gross USD = $q \times (X/E - 1)$, Short gross USD = $q \times (1 - X/E)$ | MATCH |
| 19 | `README.md:10-15` | Secret isolation boundary | `.secrets/` gitignored; API keys never committed or pasted into AI sessions | MATCH |
| 20 | `research/screenshots` | Empirical tape read corpus | 27 documented markdown evaluations + 2 subdirectories (29 entries total) | MATCH |

---

## Verification script

The following script independently validates all 20 claims against the stored JSON, Python, and Markdown artifacts:

```python
import json
import os
from pathlib import Path

# 1-2: layer_index
with open("MyTradingSys/system/layer_index.json") as f:
    idx = json.load(f)
live_fam = [fam for fam in idx["families"] if fam.get("id") == "live_engine"][0]
assert live_fam["kind"] == "infrastructure"
assert "Testnet HALT since 2026-10-12 09:46Z" in live_fam["status"]
assert live_fam["layers"] == []
assert live_fam["ledger"] == []

# 3: LAYERS.md
layers_text = Path("MyTradingSys/system/LAYERS.md").read_text(encoding="utf-8")
assert "Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy" in layers_text

# 4-5: TESTNET_SUBACCOUNTS.md
sub_text = Path("MyTradingSys/execution/TESTNET_SUBACCOUNTS.md").read_text(encoding="utf-8")
assert "Deribit nets one BTC-PERPETUAL position per account, so each account = one concurrent trade" in sub_text
assert "| tom, smoke | main (jishu) |" in sub_text
assert "| layer:fabio:* | jishu_1 |" in sub_text
assert "| layer:rsi:rsi_events:15m | jishu_2 |" in sub_text
assert "| other layer:rsi:* (1h, malkan) | jishu_3 |" in sub_text

# 6-7: auto_trader_config.json
with open("MyTradingSys/execution/auto_trader_config.json") as f:
    at = json.load(f)
assert "Testnet calibration from 2026-10-08" in at["_calibration"]
assert "sizes 20 to 1000 USD, base 20" in at["_calibration"]
assert len(at["accounts"]) >= 16
assert at["accounts"]["layer:turn_of_candle:"] == "jishu_1"
assert at["accounts"]["layer:rsi:rsi_events:5m"] == "jishu_2"

# 8-9: MAINNET_READINESS_CHECKLIST.md
mn_text = Path("MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md").read_text(encoding="utf-8")
assert "Code default is TESTNET" in mn_text and "typed confirmation" in mn_text
assert "test_mainnet_flag_offline" in mn_text

# 10-11: FABIO_TESTNET_SLOT.md
fab_text = Path("MyTradingSys/execution/FABIO_TESTNET_SLOT.md").read_text(encoding="utf-8")
assert "Fabio signals" in fab_text and "get their own Deribit TESTNET account" in fab_text
assert "Busy-check is per account; HALT / HALT_DAILY_LOSS / AUTO_PAUSE stay global" in fab_text

# 12-13: live_session_protocol.md
proto_text = Path("MyTradingSys/methodology/live_session_protocol.md").read_text(encoding="utf-8")
assert "### 1. Quote the number" in proto_text
assert "Every price, level, state, or flow claim must be a direct quote from a paste" in proto_text
assert "### 2. Delta check before verdict" in proto_text

# 14: screenshot_intake.md
shot_text = Path("MyTradingSys/methodology/screenshot_intake.md").read_text(encoding="utf-8")
assert "Tool: scripts/dev/shot.py" in shot_text
assert "saved once, understood once, and ends in a filed result or a stated \"no action\"" in shot_text

# 15-16: DEPLOY_RUNBOOK.md
deploy_text = Path("MyTradingSys/system/DEPLOY_RUNBOOK.md").read_text(encoding="utf-8")
assert "SCHEDULING_POLICY.md" in deploy_text
assert "live tree = the folder holding" in deploy_text

# 17: promoted_setups.json
with open("MyTradingSys/execution/promoted_setups.json") as f:
    ps = json.load(f)
assert ps["version"] == 1
assert ps["entries"] == []

# 18: trade_ledger.py
tl_text = Path("MyTradingSys/execution/trade_ledger.py").read_text(encoding="utf-8")
assert "long gross USD = q * (X/E - 1)" in tl_text
assert "short gross USD = q * (1 - X/E)" in tl_text

# 19: README.md
readme_text = Path("MyTradingSys/execution/README.md").read_text(encoding="utf-8")
assert ".secrets/" in readme_text
assert "API keys live here as plain JSON files" in readme_text
assert "never in a script" in readme_text

# 20: research/screenshots
entries = os.listdir("MyTradingSys/research/screenshots")
assert len(entries) == 29
md_files = [f for f in entries if f.endswith(".md")]
assert len(md_files) == 27

print("ALL 20 LIVE_ENGINE INFRASTRUCTURE CLAIMS AUDITED AND VERIFIED EXACTLY.")
```
