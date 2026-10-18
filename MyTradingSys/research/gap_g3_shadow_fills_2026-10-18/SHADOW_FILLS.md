# G3 GO_LIVE_BAR on Shadow Fills from the Real Tape (2026-10-18)

## 0. Context and Operator Decision

- **Background (G3 Gap)**:
  `MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:125-131` identified:
  > "G3 (HIGH): the go-live bar is measured on synthetic testnet fills
  > Evidence: GO_LIVE_BAR.md:6 'measured on testnet'; :10 'using the exchange's real fills and fees'. EXEC_PROVENANCE_AUDIT.md:92: testnet order book not replayed, testnet liquidity untested. Deribit says testnet does not mirror live liquidity [search].
  > Why it matters: 200 testnet trades with PF > 1.2 can come from fills the real book would not give (limit fills, stop slippage). Testnet proves the plumbing (orders, stops, loss guard), not the P&L.
  > Fix: log a shadow fill for every testnet order, computed from the real market tape at the same timestamps (Binance aggTrades, already fetchable), and measure the go-live bar on shadow fills; testnet fills become a plumbing check. Changing GO_LIVE_BAR needs an operator decision on the page (D06-gate)."

- **Operator Decision (q-gap-b, 2026-10-15)**:
  > "2026-10-15 q-gap-b answered: no change to GO_LIVE_BAR; report shadow-fill and testnet numbers side by side."
  `MyTradingSys/system/GO_LIVE_BAR.md` remains completely untouched. GO_LIVE_BAR criteria (`GO_LIVE_BAR.md:6-15`) continue to govern testnet plumbing, while this tool provides the side-by-side verification against the real tape.

---

## 1. Schema & Methodology

### 1.1 Input Order Record Schema
The utility scores recorded testnet/paper orders against real market tape (1m OHLCV bars or tick/aggTrades tape):

| Field | Type | Description |
|---|---|---|
| `order_id` | str | Unique identifier of the order / attempt |
| `placed_time` | int (ms) | Timestamp when order was placed |
| `side` | str | `buy` / `long` or `sell` / `short` |
| `order_type` | str | `limit` (maker) or `stop` / `market` (taker) |
| `price` | float | Order limit price or stop trigger price |
| `amount` | float | Order size |
| `window_ms` | int (ms) / None | Order lifespan before timeout/cancellation |
| `testnet_status` | str | `filled` or `no_fill` / `cancelled` |
| `testnet_fill_price` | float / None | Actual recorded fill price on testnet |
| `testnet_fill_time` | int (ms) / None | Actual fill timestamp on testnet |

### 1.2 Tape Matching & Fill Realism Models
Following `MyTradingSys/backtest/maker_model.py`:
- `TICK = 0.5` USD (SOURCED: `MyTradingSys/backtest/maker_model.py:34 TICK = 0.5`)
- **Touch Model**:
  - BUY Limit: $Low \le Price_{limit}$
  - SELL Limit: $High \ge Price_{limit}$
  - STOP Market: $High \ge Price_{stop}$ (BUY) or $Low \le Price_{stop}$ (SELL)
  - Fill price for Limit: $Price_{limit}$ (maker, 0 slippage)
  - Fill price for Stop: $Price_{open}$ if gapped past stop, else $Price_{stop}$ (SOURCED: `maker_model.py:8`)
- **Trade-Through Model**:
  - BUY Limit: $Low \le Price_{limit} - TICK$
  - SELL Limit: $High \ge Price_{limit} + TICK$
  - Requires public tape to trade strictly *through* the order price by at least 1 tick, eliminating queue priority assumptions.

### 1.3 Metrics Definition
- **Fill Rate**: $N_{\text{filled}} / N_{\text{orders}}$
- **Phantom Fill Rate**: Orders filled on synthetic testnet that were *not* reached on the real tape:
  - Touch Phantom: Filled on testnet, but real tape never touched price ($Low > Price$ for BUY).
  - Trade-Through Phantom: Filled on testnet, but real tape never traded through price.
- **Adverse Slippage (`slip_bp`)**:
  - For BUY: $\frac{Price_{\text{fill}} - Price_{\text{order}}}{Price_{\text{order}}} \times 10^4$ [OURS]
  - For SELL: $\frac{Price_{\text{order}} - Price_{\text{fill}}}{Price_{\text{order}}} \times 10^4$ [OURS]
  - Discrepancy: $slip\_bp_{\text{testnet}} - slip\_bp_{\text{shadow}}$ (negative indicates testnet was optimistic).

---

## 2. DEV Fixture Verification

A 5-order canonical DEV test fixture was evaluated against synthetic 1m tape bars:
1. `ord_1`: BUY limit at 80,000.0 (touches bar 0, trades through bar 1). Filled on both.
2. `ord_2`: SELL limit at 80,500.0 (high touches 80,500.0 on bar 2, never trades through). Touch fill only.
3. `ord_3`: SELL limit at 81,000.0 (max tape high is 80,500.0). Testnet synthetic fill, real tape never reached: **Phantom fill**.
4. `ord_4`: BUY limit at 79,000.0. Unfilled on testnet and unfilled on tape.
5. `ord_5`: SELL stop at 79,800.0. Bar 3 gaps open at 79,750.0 (50.0 USD adverse gap = 6.2657 bp slippage).

### Side-by-Side Comparison Table (DEV Fixture)

| Metric | Testnet Fills (Synthetic) | Shadow Touch (Real Tape) | Shadow Trade-Through (Real Tape) |
|---|---|---|---|
| Total Orders Evaluated | 5 [OURS] | 5 [OURS] | 5 [OURS] |
| Fills Count | 4 [OURS] | 3 [OURS] | 2 [OURS] |
| Fill Rate (%) | 80.0% [OURS] | 60.0% [OURS] | 40.0% [OURS] |
| Phantom Fills vs Real Tape | 0 (baseline) | 1 (20.0%) [OURS] | 2 (40.0%) [OURS] |
| Mean Adverse Slippage (bp) | 0.00 bp [OURS] | 2.09 bp [OURS] | 3.13 bp [OURS] |
| Slippage Discrepancy (bp) | 0.00 bp [OURS] | -2.09 bp [OURS] | -3.13 bp [OURS] |

### Interpretation
- **Fill Overstatement**: In this canonical fixture, synthetic testnet fills overstate true market execution rate by 20.0% against touch fills (80.0% vs 60.0%) and by 40.0% against trade-through fills (80.0% vs 40.0%).
- **Slippage Understatement**: Testnet recorded 0 bp slippage on stops, masking an adverse gap slippage of 6.27 bp ($50 / 79,800 \times 10^4$).
- **Role in MTS Stack**: Testnet validates connectivity, cancel/replace, and balance reconciliation; `shadow_fills.py` evaluates true execution feasibility against public market tape without modifying `GO_LIVE_BAR.md`.
