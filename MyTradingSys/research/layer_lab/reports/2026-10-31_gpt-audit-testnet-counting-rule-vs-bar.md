# GPT audit: testnet counting rule versus bar

**Verdict: FIX-FIRST.** `trade_ledger.jsonl` records the source but not the promotion decision. The testnet status reader labels calibration sources but still includes their resolved rows in its closed-trade totals; the ledger CLI summary also includes them. Neither is a valid promoted-only GO_LIVE_BAR count as implemented.

## Checked

- `MyTradingSys/system/GO_LIVE_BAR.md:7,17`: the sample requires 200 closed testnet trades from configs that passed walk-forward; the measurement source is `trade_ledger.jsonl` per source/account.
- `MyTradingSys/execution/auto_trader.py:250-268,501-520`: promotion gate calls `decision_for_source`; `layer_signal` rejects shadow/unregistered and permits `trade` decisions.
- `MyTradingSys/execution/auto_trader_config.json:142-250`: 27 entries under `pre_pipeline_sources`, described at line 252 as grandfathered pre-pipeline testnet calibration.
- `MyTradingSys/execution/trade_ledger.py:124-145,201-207,316-339`: resolved and unresolved ledger row construction and CLI summary.
- `MyTradingSys/execution/test_auto_trader_promotion.py:22-32,70-80,155-164`: independent source fixtures and gate assertions.
- Reader cross-check: `scripts/dev/testnet_status.py:95-133,169-238,276-337` reads and classifies the ledger.

## Findings

| Severity | Evidence | Finding |
|---|---|---|
| HIGH | MATCH - `trade_ledger.py:124-145` constructs a resolved row with `source`, `account`, `plan_id`, and outcomes, but no promotion mode, registry setup id, or calibration marker. `trade_ledger.py:201-207` unresolved rows likewise have source/account only. `auto_trader.py:741-750` passes only plan id, source, account, manager return code to the ledger. | A row can be grouped by its recorded `source`, then classified by comparing that source with the current config's `pre_pipeline_sources` prefixes and promoted registry sources. The row itself does not preserve the gate decision or a registry/config snapshot. Historical classification is therefore conditional on those external files still representing the rule at trade time. |
| HIGH | MATCH - `testnet_status.py:121-133` labels source sets as calibration/promoted/unlabelled and says calibration never counts. But `analyse` at `:221-237` iterates all ledger rows, checks only trade shape/window, then increments `closed`, `net`, and `wins`; it does not consult the label. `:330-337` calculates the label after aggregation. | The reader labels calibration rows but does not filter them from the closed/win/net totals. The label is descriptive only; calibration trades can inflate the status readout's sample. |
| HIGH | MATCH - `trade_ledger.py:316-328` `summarize` skips only unresolved rows, then increments `n` for every other row, grouped by source; `:333-339` prints that result. | The ledger's own `--summary` reader also counts pre-pipeline calibration rows. It has no promoted-only filter. |
| MED | MATCH - `GO_LIVE_BAR.md:7` requires all 200 trades to come from walk-forward-passed configs; config's pre-pipeline note (`auto_trader_config.json:252`) calls those sources calibration. In `test_auto_trader_promotion.py:22-32`, `TODAYS_SOURCES` has 18 concrete layer source fixtures; `:70-74` asserts each gets `plan_args` under the shipped config, and `:76-80` separately asserts Tom passes. | Re-derived fixture count: **18 layer sources + Tom = 19 sources allowed through the gate as shipped**. This is an acceptability count, not a trade or GO_LIVE_BAR count. The fixture explicitly derives its list independently of the grandfather list (`:22-23`); test method `:155-164` checks the shipped pre-pipeline list's completeness against configured overrides/accounts plus Tom. |

## Conclusion

The relevant distinction is derivable from source plus external promotion/config data, but it is not encoded as immutable row provenance. `scripts/dev/testnet_status.py` claims calibration never counts but includes calibration ledger rows in its aggregation; `trade_ledger.py --summary` also counts every resolved row. GO_LIVE_BAR's walk-forward eligibility cannot be inferred from the ledger row alone. Use a source-to-promotion snapshot or explicit row classification and filter calibration rows before treating any reader's total as the bar sample.

No code changes. No follow-up card created.

Noticed: the testnet status reader's calibration label does not currently exclude those rows from its totals.

