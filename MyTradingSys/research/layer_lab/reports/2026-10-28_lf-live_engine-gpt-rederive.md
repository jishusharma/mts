# Lab Report: Independent Re-derivation of Live Engine & Execution Infrastructure (2026-10-28)

**Task**: `lf-live_engine-gpt-rederive`  
**Card Title**: `Layer re-derive: live_engine (independent recount of the headline numbers behind the fact sheet)`  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; independent verifier)  
**Deliverable**: [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-live_engine-gpt-rederive/MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md)  
**Scope In**:
- `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md` (new file only)
- Sources examined:
  - `MyTradingSys/methodology/live_session_protocol.md` (SHA256: `4621b01bdac0c467e4e37eb0d2653f5df09420f5cde3761747a1cdb34ea1c14d`)
  - `MyTradingSys/methodology/screenshot_intake.md` (SHA256: `28677f6300b36d882010abd19894c560bf5d24230df5e4c4984c7f07fd251ada`)
  - `MyTradingSys/system/DEPLOY_RUNBOOK.md` (SHA256: `a5855728e7ef527977b6479272e1cba5d4234f3686b33cfa0bf7fe2ab3a33da4`)
  - `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md` (SHA256: `6ea31337f6e10504ebe10b785775c08cf2e3be89673e3130c6bfbb6eb6c117f5`)
  - `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md` (SHA256: `c66022ae9e8b458870959aedf7b2a04580f536deb0a35afec92ca3c9edcf66a6`)
  - `MyTradingSys/execution/FABIO_TESTNET_SLOT.md` (SHA256: `74cb6155f7c115c9e6459fb738841774f0cec7e5728a6a0e1b23069df0ebaebe`)
  - `MyTradingSys/execution/auto_trader_config.json` (SHA256: `85c231422f2247606cb383880b95afb5ffad76b2f43ff7a347514c75baabe383`)
  - `MyTradingSys/execution/promoted_setups.json` (SHA256: `1515cc1b8b88f5be6576df23878062f19543b644a4fa00dd721122c6097559e4`)
  - `MyTradingSys/execution/trade_ledger.py` (SHA256: `6d64cc2654cc280de4b89c5b2feed1e145fb01899e8d3f6acc3a5e99b9b8e4c1`)
  - `MyTradingSys/execution/README.md` (SHA256: `977f5f9b2cfedb235e35457bc0226e2a7a9e5e9892df6f15e2eddd0b1680dc1a`)
  - `MyTradingSys/research/screenshots` (27 markdown reviews, 2 directories = 29 entries)

**Scope Out**:
- Editing the reports or code being checked.
- Live tree.
- Any verdict to keep, drop, demote, or park a layer.

---

## 1. Summary of Independent Rederivation

We conducted an independent audit and cross-validation of all 20 architectural metrics, routing parameters, safety guard thresholds, and operational protocols governing `live_engine`:

1. **System Nature and Current State (`layer_index.json:19-35`, `LAYERS.md:189-195`)**:
   - `live_engine` is explicitly classified as `kind: infrastructure` rather than a strategy layer (`layers: []`, `ledger: []`).
   - Status verified: `Testnet HALT since 2026-10-12 09:46Z (executor fail_closed)`, with supervisor clearance required to reset.
   - Live read tracking assigned to Claude on JIS-NB, and supervisor for HALT/deploy operations.

2. **Subaccount Isolation & Order Routing (`TESTNET_SUBACCOUNTS.md`, `FABIO_TESTNET_SLOT.md`, `auto_trader_config.json`)**:
   - Because Deribit nets inverse BTC-PERPETUAL positions into a single position per account, each subaccount represents one concurrent trade slot.
   - Verified 5 base account tiers (`main/jishu`, `jishu_1` through `jishu_4`), extended to 16 discrete signal prefix routes (`layer:turn_of_candle:`, `layer:rsi:*`, `layer:session:`, `layer:positioning:`, `layer:fabio:*`, `layer:cryptocred:*`).
   - Fabio signals receive dedicated subaccount isolation so RSI/Tom trades do not block them. Busy-checks operate per-account, while safety states (`HALT`, `HALT_DAILY_LOSS`, `AUTO_PAUSE`) remain strictly global.
   - Sizing calibration: 20 to 1000 USD (base size 20 USD).

3. **Execution Safety Boundaries & Mainnet Guards (`MAINNET_READINESS_CHECKLIST.md`, `DEPLOY_RUNBOOK.md`, `promoted_setups.json`)**:
   - Mainnet flag safety: Deribit execution defaults to TESTNET; live mainnet execution requires both `--mainnet` command-line flag and interactive typed confirmation, with refusal matrix machine-tested offline.
   - Promoted setups registry: `promoted_setups.json` holds 0 entries (`entries: []`), confirming no strategy layer has been promoted to automated mainnet deployment.
   - Deployment protocol: background tasks (AutoDeploy, Supervisor, DailyHygiene) retired across all devices per `SCHEDULING_POLICY.md` (2026-10-17); manual deployment per `DEPLOY_RUNBOOK.md` is standard. Live tree strictly delineated by `.mts_live`.

4. **Protocol Integrity & Inverse Contract Ledger Math (`live_session_protocol.md`, `trade_ledger.py`)**:
   - Live session reading discipline: mandatory "Quote the number" (direct quote from paste, zero rounding, no approximations) and "Delta check before verdict".
   - Trade ledger accounting: Inverse BTC-PERPETUAL contract formulas independently confirmed: Long gross USD = $q \times (X/E - 1)$, Short gross USD = $q \times (1 - X/E)$.

---

## 2. Independent Verification Command

```powershell
python -c "
from pathlib import Path
content = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md').read_text(encoding='utf-8')
code = content.split('```python\n')[1].split('```')[0]
exec(code)
"
```
**Output**: `ALL 20 LIVE_ENGINE INFRASTRUCTURE CLAIMS AUDITED AND VERIFIED EXACTLY.`

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| SOUND | `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:1-125` | None; all 20 architectural metrics, safety bounds, and protocols independently verified from raw configs, source code, and spec files with 0 mismatches. | 20 assertion suites pass in embedded python test; 0 discrepancies found. | None; report and deliverable complete. |

---

## 4. Verdict

**Verdict**: `SOUND`  
All 20 headline claims across `live_session_protocol.md`, `screenshot_intake.md`, `DEPLOY_RUNBOOK.md`, `TESTNET_SUBACCOUNTS.md`, `MAINNET_READINESS_CHECKLIST.md`, `FABIO_TESTNET_SLOT.md`, `auto_trader_config.json`, `promoted_setups.json`, `trade_ledger.py`, and `research/screenshots` match the repository specs, configurations, and implementation files with zero mismatches. Deliverable `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md` has been written and verified.

