# Layer Fact Sheet Report: live_engine family (`lf-live_engine-gemini-facts`)

**Date:** 2026-10-28 (UTC) [SOURCED: system clock UTC]  
**Card:** `lf-live_engine-gemini-facts` [CODEX, size S, prio 2]  
**Worker:** Google Gemini (Antigravity worktree `mts-desktop-f7iu69n-lf-live_engine-gemini-facts`)  
**Artifact:** [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/live_engine.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-live_engine-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/live_engine.md)  

---

## 1. Execution Summary

Per task card instructions and `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34` item C:
1. Ran `python scripts/dev/lab_query.py layers live_engine` and checked `MyTradingSys/system/layer_index.json:19-35`:
   - `live_engine` classified as `kind: infrastructure`, feeds every layer (`layers: []`, `ledger: []`).
   - Status: `Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it. Live-market screenshot reads file findings as task cards.`
2. Queried active rulings using `python scripts/dev/lab_query.py rulings live_engine` and examined `MyTradingSys/research/BUGS.md`:
   - Checked rulings B075, B081, B116, B117, B118, B136, and task T085 in `MyTradingSys/research/BUGS.md:167,173,181,227,228,229,247`.
3. Examined all spec, ledger, configuration, and execution files:
   - `MyTradingSys/system/LAYERS.md:202-205`
   - `MyTradingSys/system/layer_index.json:19-35`
   - `MyTradingSys/methodology/live_session_protocol.md:1-60`
   - `MyTradingSys/methodology/screenshot_intake.md:1-50`
   - `MyTradingSys/system/DEPLOY_RUNBOOK.md:1-80`
   - `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md:1-50`
   - `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md:1-70`
   - `MyTradingSys/execution/FABIO_TESTNET_SLOT.md:1-40`
   - `MyTradingSys/execution/auto_trader_config.json:1-60`
   - `MyTradingSys/execution/promoted_setups.json:1-10`
   - `MyTradingSys/execution/trade_ledger.py:1-60`
   - `MyTradingSys/execution/README.md:1-50`
   - `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`
   - `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8,39`
4. Created fact sheet [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/live_engine.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-live_engine-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/live_engine.md) covering the infrastructure component across all 5 requested sections:
   - ORIGIN (quoted source)
   - PARAMETERS (labeled SOURCED or OURS)
   - BACKTESTS (path, fee-net, IS/OOS, n trades/days/events)
   - KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (rulings)
   - CONFLUENCE
   - Strictly zero verdicts on keeping, dropping, demoting, or parking any component.
   - Every fact carries a concrete repo `file:line` citation or `NOT_IN_DATA`.

---

## 2. Key Facts Count

- **Component covered:** 1 infrastructure component (`live_engine`).
- **Facts documented:** 45 bullet fact items across the 5 standard sections, every line carrying a `file:line` citation or `NOT_IN_DATA`.
