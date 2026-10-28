# Layer Fact Sheet: live_engine

Facts compiled strictly from repository files per `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34` item C and task `lf-live_engine-gemini-facts`.
No verdicts on keeping, dropping, demoting, or parking any layer. Every fact line cites `file:line` or `NOT_IN_DATA`.
Component covered: `live_engine` (Live engine, execution and live-market reads that feed every layer; `MyTradingSys/system/LAYERS.md:202-205`; `MyTradingSys/system/layer_index.json:19-35`).

---

## 1. live_engine

### ORIGIN (Quoted Source)
- **Primary Infrastructure Specification**: "The live engine, execution and live-market reads that feed every layer (infrastructure, not a strategy)." (`MyTradingSys/system/layer_index.json:34`).
- **Family Classification**: "kind: infrastructure, layers: [], ledger: []" (`MyTradingSys/system/layer_index.json:20-28`).
- **Live Session Reading Protocol**: "Operational discipline for live market reading and state tracking... Check 1: Quote the number (direct quote from paste, zero rounding)... Check 2: Delta check before verdict (compare current to prior number in same paste series)" (`MyTradingSys/methodology/live_session_protocol.md:1-25`).
- **Screenshot Intake Specification**: "Takes incoming chart screenshots from the operator, classifies them against the setup library, extracts levels and annotations, logs an intake event, and files a finding or no-action note" (`MyTradingSys/methodology/screenshot_intake.md:1-20`).
- **Deployment Runbook Specification**: "Single procedure for promoting validated research code to the live execution runner... Live tree defined exclusively by `.mts_live` marker; background deployment tasks retired 2026-10-17" (`MyTradingSys/system/DEPLOY_RUNBOOK.md:1-25`).
- **Execution Architecture Overview**: "Auto-trader, order execution, position manager, risk guards, reconciler, journal, testnet suites" (`MyTradingSys/execution/README.md:1-35`).
- **Trader Association / Ledger**: NOT_IN_DATA ("kind: infrastructure... layers: [], ledger: []" in `MyTradingSys/system/layer_index.json:20-28`; infrastructure engine, not an individual trader strategy; no trader trade ledger exists).

### PARAMETERS (SOURCED or OURS)
- **Venue & Contract Market**: Deribit BTC-PERPETUAL inverse contract (`SOURCED`, quote: "Deribit BTC-PERPETUAL inverse contract" in `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md:3`; `MyTradingSys/execution/trade_ledger.py:15-18`).
- **Position Sizing Calibration**: 20 to 1000 USD notional, base testnet size 20 USD (`OURS`, quote: "size_usd: 20" in `MyTradingSys/execution/auto_trader_config.json:2-10`; `MyTradingSys/execution/FABIO_TESTNET_SLOT.md:12`).
- **Subaccount Routing Tiers**: 5 primary tiers (`main`, `jishu_1` through `jishu_4`) expanding to 16 discrete signal prefix routes (`OURS`, quote: "16 discrete signal prefix routes" in `MyTradingSys/execution/auto_trader_config.json:4-22`; `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md:7-11`).
- **Position Netting Isolation**: 1 concurrent trade per subaccount (Deribit nets inverse contracts per account) (`SOURCED`, quote: "Deribit nets 1 BTC-PERPETUAL position per account (1 account = 1 concurrent trade)" in `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md:3`).
- **Execution Fee Floor**: Deribit taker fee 0.05% (5 bps per side = 10 bps RT) (`SOURCED`, quote: "DERIBIT_TAKER = 0.0005 per side" in `MyTradingSys/backtest/fees.py:5`; `MyTradingSys/backtest/layers/FORMULAS.md:403`).
- **Safety State Propagation**: Global propagation of `HALT`, `HALT_DAILY_LOSS`, and `AUTO_PAUSE` across all subaccount slots (`OURS`, quote: "HALT, HALT_DAILY_LOSS, and AUTO_PAUSE remain strictly global" in `MyTradingSys/execution/FABIO_TESTNET_SLOT.md:4`).
- **Unsourced Bracket Parameters**: Stop percentage 1.0%, target 2.0%, horizon 8 bars (1h) (`OURS` / `NO-SOURCE`, quote: "Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 20" in `MyTradingSys/research/BUGS.md:229` [B118]).
- **Unsourced Stop Floors**: Minimum stop floor 0.1% and fallback stop 0.2% (`OURS` / `NO-SOURCE`, quote: "Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in code" in `MyTradingSys/research/BUGS.md:227` [B116]).
- **Unsourced Proof Gating Bands**: Proof bands 3 and 5 gating entry (`OURS` / `NO-SOURCE`, quote: "Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING" in `MyTradingSys/research/BUGS.md:228` [B117]).
- **Unsourced Net R:R Hurdle**: Net R:R floor 1.25 (`OURS` / `NO-SOURCE`, quote: "net_rr floor 1.25 is NO-SOURCE" in `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`; `MyTradingSys/research/BUGS.md:264`).
- **Mainnet Confirmation Guard**: Interactive confirmation and `--mainnet` command-line flag required; testnet default (`SOURCED`, quote: "mainnet requires explicit `--mainnet` flag AND typed confirmation" in `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md:3-9`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Architecture Status Overview (2026-10-26)** [`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`]:
   - **Path**: `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`
   - **Fee-Net**: Evaluated via operational logs and testnet ledger; no standalone strategy backtest row exists (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20` "no backtest row").
   - **IS / OOS Partition**: NOT_IN_DATA (infrastructure component; partitions apply to strategy backtests that consume its data).
   - **Sample Size (n)**: Feeds all 19 kline live layers (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
2. **Deribit Testnet Live Execution Sample (2026-10-09)** [`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`]:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`
   - **Fee-Net**: Fee-net evaluated with live testnet order fills and exchange fees (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`).
   - **Sample Size (n)**: 372 total testnet trades recorded; 300 generated by `turn_of_candle` (net -3.69 USD, 100% time exits); 72 across all remaining layers (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:28`).
3. **Time Exit Domination Diagnostic T085 (2026-10-09)** [`MyTradingSys/research/BUGS.md:181`]:
   - **Path**: `MyTradingSys/research/BUGS.md:181`
   - **Fee-Net**: Evaluated on live execution trade journal (`MyTradingSys/research/BUGS.md:181`).
   - **Sample Size (n)**: 94% to 97% of all live testnet trades exit via time-out rather than hitting stop or target (`MyTradingSys/research/BUGS.md:181` [T085]; `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:39`).
4. **Kline Fires Parity Replay FIRES-B1 (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - **Fee-Net**: Parity audit comparing offline kline fire generation against live alert logs (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,16`).
   - **Sample Size (n)**: 244,543 total fires; parity PASS on spot rerun (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,20-40`).
5. **Empirical Screenshot Tape Read Corpus (2026-10-26)** [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53`]:
   - **Path**: MyTradingSys/research/screenshots/ (MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53)
   - **Sample Size (n)**: 27 documented markdown evaluations + 2 subdirectories = 29 items (`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B075**: "Historical mode unfit for backtesting; zeroes trade_flow/book_imbalance/funding/OI, produces hollow snapshots" (`MyTradingSys/research/BUGS.md:167`). Closed 2026-09-27.
- **Ruling B081**: "Live runner crashes on unhandled connection reset in Deribit ws thread; auto-reconnect unhandled" (`MyTradingSys/research/BUGS.md:173`). Closed 2026-10-01.
- **Ruling B116**: "Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in code" (`MyTradingSys/research/BUGS.md:227`). Closed 2026-10-04.
- **Ruling B117**: "Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading logic" (`MyTradingSys/research/BUGS.md:228`). Open.
- **Ruling B118**: "Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 20" (`MyTradingSys/research/BUGS.md:229`). Closed 2026-10-04.
- **Ruling B136**: "Live execution logs show time exit domination (97% time exits; targets/stops almost never reached)" (`MyTradingSys/research/BUGS.md:247`).
- **Task T085**: "97% of testnet trades end on the time exit: find why targets/stops are almost never reached (unreachable brackets on short horizons)" (`MyTradingSys/research/BUGS.md:181`).
- **Operational State HALT**: "Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it" (`MyTradingSys/system/LAYERS.md:203`; `MyTradingSys/system/layer_index.json:22`).

### CONFLUENCE
- **Infrastructure Backbone Role**: Ingestion, execution, and dispatch pipeline that feeds every layer (`MyTradingSys/system/layer_index.json:20`; `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`).
- **Promoted Setups Status**: `promoted_setups.json` holds 0 entries (`entries: []`), confirming no strategy layer has been promoted to automated mainnet execution (`MyTradingSys/execution/promoted_setups.json:2-3`).
- **Actual Live Confluence**: Zero live trades combined ("Nothing combines on a live trade. `promoted_setups.json` ships empty... So no confluence rule has ever decided a real trade" in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).
