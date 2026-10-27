# Trust re-check: gpt-formulas-rederive (2026-10-28)

**Verdict: VERIFIED-C2.** Cross-vendor independent reviewer requirement is satisfied: Producer is CODEX / GPT, Reviewer is Gemini (Google, Google AI Pro, Antigravity, DESKTOP-F7IU69N). All decisive numbers from FORMULAS.md sections 13 and 17 have been independently re-derived and verified against repo code. The fail-first mutation test turned 3 tests RED. No holdout or outcome data was read or rerun; no audited source file was altered.

## 1. Producer and Reviewer Identity

- **Producer**: CODEX / OpenAI GPT (task `gpt-formulas-rederive`, 2026-10-17).
- **Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N).
- **Independence**: Different vendor family (`Producer != Reviewer` strictly enforced).

## 2. Independent Calculations and Re-Derivations

Derived directly from `MyTradingSys/backtest/layers/FORMULAS.md` definitions before reading repo code, using exact rational arithmetic:

| Example | Independent Derivation | Repo / Table Comparison | Status |
|---|---|---|---|
| **S17 net R:R**, entry 100 / target 104 / stop 98 | `cost = 2 * 0.0005 * 100 = 0.1`<br>`net_rr = (\|104 - 100\| - 0.1) / (\|100 - 98\| + 0.1) = 3.9 / 2.1 = 13/7 = 1.857142857...` | [FORMULAS.md:400-406](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/layers/FORMULAS.md#L400-L406) gives 1.8571.<br>`calculate_net_rr(100.0, 104.0, 98.0)` in [mts_math.py:78-85](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/runtime/mts_math.py#L78-L85) returns `1.857142857142857`.<br>[fees.py:23](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/fees.py#L23) `DERIBIT_TAKER = 0.0005`.<br>[FORMULAS_REDERIVE.md:17](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/research/layer_lab/gpt-formulas-rederive/FORMULAS_REDERIVE.md#L17) gives `1.85714`. | **MATCH** |
| **S17 tight stop**, entry 100 / target 100.3 / stop 99.9 | `cost = 0.1`<br>`net_rr = (0.3 - 0.1) / (0.1 + 0.1) = 0.2 / 0.2 = 1.0` | [FORMULAS.md:405-406](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/layers/FORMULAS.md#L405-L406) gives 1.0.<br>`calculate_net_rr(100.0, 100.3, 99.9)` returns `1.0`.<br>[FORMULAS_REDERIVE.md:18](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/research/layer_lab/gpt-formulas-rederive/FORMULAS_REDERIVE.md#L18) gives `1`. | **MATCH** |
| **S17 zero risk**, stop == entry (100 / 104 / 100) | `stop == entry -> 0.0` | `calculate_net_rr(100.0, 104.0, 100.0)` returns `0.0`.<br>[FORMULAS_REDERIVE.md:19](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/research/layer_lab/gpt-formulas-rederive/FORMULAS_REDERIVE.md#L19) gives `0`. | **MATCH** |
| **S13 long**, 100 -> 101, t_in=0, t_out=16h, funding at 8h=0.0001, 16h=0.0003 | `gross = +1 * (101 - 100) / 100 = 0.01`<br>`fee_rt = 0.0010`<br>`slip_rt = 0.0002`<br>`sum(rate) = 0.0004`<br>`net = 0.01 - 0.0010 - 0.0002 - 0.0004 = 0.0084` | [FORMULAS.md:353](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/layers/FORMULAS.md#L353) gives 0.0084.<br>Repo call `net_return('long', 100, 101, 0, 16h, [(8h, 0.0001), (16h, 0.0003)])` **RAISES ValueError**: [trade_costs.py:26-29](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/layers/positioning/trade_costs.py#L26-L29) B103 fail-closed span guard triggers (`t_in < funding[0][0]`, since 0 < 8h).<br>With padding record at t=0 (`(0, 0.0)`), `net_return` returns `0.0084`. | **MISMATCH** (example input vs B103 guard; arithmetic is sound, verified by calculation) |
| **S13 short**, 100 -> 99, t_in=0, t_out=16h, funding at 8h=0.0001, 16h=0.0003 | `gross = -1 * (99 - 100) / 100 = 0.01`<br>`funding_term = -1 * 0.0004 = -0.0004`<br>`net = 0.01 - 0.0012 - (-0.0004) = 0.0092` | [FORMULAS.md:353-354](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gpt-formulas-rederive/MyTradingSys/backtest/layers/FORMULAS.md#L353-L354) gives 0.0092.<br>Repo call raises ValueError without padding at t=0 due to B103.<br>With padding record at t=0, `net_return` returns `0.0092`. | **MISMATCH** (example input vs B103 guard; arithmetic is sound, verified by calculation) |

### Findings on S13 Mismatch:
The recorded S13 mismatch is confirmed by calculation:
1. FORMULAS.md:352 specifies the trade window as `t_in=0, t_out=16h` and gives funding records only at `t=8h` and `t=16h`.
2. `trade_costs.py:26-29` enforces the B103 fail-closed guard: `if t_in < funding[0][0] or t_out > funding[-1][0]: raise ValueError(...)`.
3. Because `t_in = 0 < 8h = funding[0][0]`, the repo implementation strictly rejects the unpadded input to avoid unmonitored funding intervals.
4. When a boundary record at `t=0` is present, the formula arithmetic matches `0.0084` and `0.0092` to 12 decimal places.
5. This is an input coverage specification mismatch in the documentation example, not an arithmetic defect in code or math.

## 3. Test Suite and Mutation Check

- **Baseline Test Command**:
  `python -m pytest MyTradingSys/tests/test_mts_math.py MyTradingSys/backtest/layers/positioning/test_trade_costs.py -q`
  Result: **93 passed in 1.48s**.

- **Fail-First Mutation Probe**:
  Mutated `DERIBIT_TAKER = 0.0005` -> `0.0010` in `MyTradingSys/backtest/fees.py:23`.
  Executed test command:
  Result: **3 failed, 90 passed in 0.91s**.
  - `FAILED test_net_rr_fee_model_long`: expected `3.9 / 2.1 = 1.857142857142857`, received `1.727272727272727` (diff 0.12987 > 1e-12).
  - `FAILED test_net_rr_fee_model_short_mirrors_long`: expected `3.9 / 2.1 = 1.857142857142857`, received `1.727272727272727`.
  - `FAILED test_net_rr_tight_stop_costs_more_r`: expected `1.0`, received `0.33333333333333015` (diff 0.66667 > 1e-9).
  - Mutation cleanly reverted immediately; `fees.py` was restored to `DERIBIT_TAKER = 0.0005`.
  - Subsequent baseline run: 93 passed.

- **Note on trade_costs tests**:
  `test_trade_costs.py` tests `trade_costs.py`, which uses Binance perp taker defaults (`fee_rt=0.0010`, `slip_rt=0.0002`) and accepts custom fee arguments; it does not import `DERIBIT_TAKER`.

## 4. Tag Decision

**Tag Proposal: VERIFIED-C2.**
- The producer arithmetic in `gpt-formulas-rederive` is verified sound across all re-derived numbers.
- Independent vendor requirement (`Producer != Reviewer`) is fully satisfied by Gemini / Google.
- Mutation test confirmed fail-first test coverage of fee constants.
- The single S13 mismatch is confirmed to be an example input vs B103 span guard specification difference (severity LOW), with identical underlying math.
