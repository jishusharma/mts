4 CONTRADICTIONS / 9 CLEAN PAIRS

## Contradictions

| # | Docs | Topic | Side A (quote + file:line) | Side B (quote + file:line) | Newer by git log |
|---|---|---|---|---|---|
| 1 | INDICATOR_MAP vs SPEC_INDICATOR_MAP | Dimension table rows (7 vs 9) | `MyTradingSys/system/SPEC_INDICATOR_MAP.md:28-29`: "Dimension table, rows = what is measured: price action, levels/volume profile, volume/participation, momentum, volatility/compression, trend strength, time/cycles/sessions." | `MyTradingSys/system/INDICATOR_MAP.md:24-25`: "Positioning (funding, OI, whales)" and "Calls (posted trade calls)" (9 rows total in lines 17-25) | `INDICATOR_MAP.md` (2026-11-08 09:02:19 +0530 `43aa9f8da` vs 2026-11-07 21:09:08 +0530 `52077cf01`) |
| 2 | INDICATOR_MAP vs SPEC_INDICATOR_MAP | Four USAGE files vs three | `MyTradingSys/system/SPEC_INDICATOR_MAP.md:26`: "built from the four USAGE files, FAVORITES, LAYERS.md and the analyst notes" | `MyTradingSys/system/INDICATOR_MAP.md:6`: "USAGE_adx.md does not exist yet (card tvfav-usage-adx-1107 still ready); the ADX row rests on FAVORITES_2026-11-07.md and Wilder (SOURCED) only" | `INDICATOR_MAP.md` (2026-11-08 09:02:19 +0530 `43aa9f8da` vs 2026-11-07 21:09:08 +0530 `52077cf01`) |
| 3 | INDICATOR_MAP vs SPEC_INDICATOR_MAP | Mechanism timing (same ship vs on promotion) | `MyTradingSys/system/SPEC_INDICATOR_MAP.md:36-37`: "every \"X confirms Y\" sentence in the map is also a scenario_ledger.py add row or a wiring_registry entry the same ship" | `MyTradingSys/system/INDICATOR_MAP.md:90-92`: "No sentence in this map states as a rule that one read verifies another ... When a connected set is promoted to a testnet-forward test, its claim becomes a scenario_ledger.py add row the same ship" | `INDICATOR_MAP.md` (2026-11-08 09:02:19 +0530 `43aa9f8da` vs 2026-11-07 21:09:08 +0530 `52077cf01`) |
| 4 | LAB_RECIPES (internal) | Supported vendors vs GPT-only | `MyTradingSys/system/LAB_RECIPES.md:19`: "Supported vendor labels are `codex`, `gemini`, and `claude`" | `MyTradingSys/system/LAB_RECIPES.md:80`: "Recipe cards are GPT-only, so fallback never silently replaces a promised independent GPT lens with Claude." | Same file/commit: `LAB_RECIPES.md` (2026-10-18 01:59:44 +0530 `0c0686359`; line 80 is stale relative to cross-vendor line 19) |

## Clean pairs (9 of 10 cross-doc pairs)

1. `INDICATOR_MAP.md` vs `LAYER_INTEGRATION.md` — clean (context-only phase-first rule vs 12-step integration).
2. `INDICATOR_MAP.md` vs `PROMOTION_PIPELINE.md` — clean (both describe `MyTradingSys/backtest/layers/promotion/` as the registry/gate deciding what may trade).
3. `INDICATOR_MAP.md` vs `LAB_RECIPES.md` — clean (disjoint scopes: indicator map vs lab recipes).
4. `SPEC_INDICATOR_MAP.md` vs `LAYER_INTEGRATION.md` — clean (disjoint scopes: indicator spec vs 12-step layer integration).
5. `SPEC_INDICATOR_MAP.md` vs `PROMOTION_PIPELINE.md` — clean (disjoint scopes: indicator spec vs promotion pipeline).
6. `SPEC_INDICATOR_MAP.md` vs `LAB_RECIPES.md` — clean (disjoint scopes: indicator spec vs lab recipes).
7. `LAYER_INTEGRATION.md` vs `PROMOTION_PIPELINE.md` — clean (`MyTradingSys/system/LAYER_INTEGRATION.md:16` matches `MyTradingSys/system/PROMOTION_PIPELINE.md:15,23,25-26` on `promote.py check`, `n >= 30`, `register --mode shadow`, and `size_overrides`).
8. `LAYER_INTEGRATION.md` vs `LAB_RECIPES.md` — clean (disjoint scopes: 12-step integration vs pilot lab recipes).
9. `PROMOTION_PIPELINE.md` vs `LAB_RECIPES.md` — clean (disjoint scopes: `promote.py` pipeline vs `lab_flow.py` recipes).
