# Second-Model Review (Gemini): Deribit Settlement/Funding Booking in Daily P/L

- **Reviewer:** Gemini (Antigravity session, JIS-NUC)
- **Task:** `wave1-review-item2-settlement-booking`
- **Scope:**
  - `MyTradingSys/execution/mainnet_pnl.py`
  - `MyTradingSys/research/loose_code/txlog_capture_2026-10-10_jishu_11.json`
- **Date:** 2026-10-30

---

## 1. Deribit Field Definitions & Semantics

Per Deribit API public documentation (`https://docs.deribit.com/`):
- **`change`** (transaction log): Change in cash balance for this entry. For futures trades, this reflects cash deductions (such as commissions).
- **`cashflow`**: Signed cash-related amount for this entry in the log currency.
- **`profit_as_cashflow`**: Present on trades; `true` on futures/perpetual trades when realized session PnL is carried in `cashflow` and has not yet been settled at the daily 08:00 UTC settlement.
- **`futures_session_upl`** (account summary): Session unrealized profit and loss for open futures and perpetual positions.
- **`futures_session_rpl`** / **`session_rpl`**: Gross realized trading profit/loss during the current session (excluding fee commissions and pre-session settlements).
- **`settlement`** entry type: At the 08:00 UTC settlement, Deribit books the mark-to-market session PnL into a `settlement` transaction record where `change == cashflow`.

Therefore, the net daily P/L formula is:
$$\text{Total Daily PnL (BTC)} = \sum_{\text{trade, settlement}} \text{change} + \sum_{\text{trade, profit\_as\_cashflow=True}} \text{cashflow} + \text{futures\_session\_upl}$$

---

## 2. Hand Computation from Recorded Log

Using `MyTradingSys/research/loose_code/txlog_capture_2026-10-10_jishu_11.json`:
- 13 total entries: 12 `trade` entries and 1 `settlement` entry.
- `account_summary`:
  - `futures_session_upl`: `0.0`
  - `session_rpl`: `1.17e-06` BTC
  - `equity`: `0.99999232` BTC
  - `balance`: `0.99999114` BTC

### Breakdown of Entries:
1. **Sum of `change`** across all allowed entries (12 trades + 1 settlement):
   $$\sum \text{change} = -8.88 \times 10^{-6} \text{ BTC}$$
   (Commissions totaling $-7.29 \times 10^{-6}$ BTC + 08:00 UTC settlement of $-1.59 \times 10^{-6}$ BTC)
2. **Sum of `cashflow`** on trades with `profit_as_cashflow is True`:
   $$\sum \text{cashflow} = (-0.60 - 3.05 + 0.99 - 0.82 + 4.70 - 0.04) \times 10^{-6} = +1.18 \times 10^{-6} \text{ BTC}$$
3. **Unrealized PnL (`futures_session_upl`)**:
   $$\text{futures\_session\_upl} = 0.0 \text{ BTC}$$
4. **Net Total PnL (Hand Calculated)**:
   $$\text{Total} = -8.88 \times 10^{-6} + 1.18 \times 10^{-6} + 0.0 = -7.70 \times 10^{-6} \text{ BTC}$$

---

## 3. Comparison with `mainnet_pnl.daily_pnl_btc`

- Hand calculated value: **`-7.7000000000e-06 BTC`**
- `mainnet_pnl.daily_pnl_btc(entries, summary)`: **`-7.7000000000e-06 BTC`**
- **Difference:** **`0.0 BTC`** (Exact match)

### Explanation of the Relationship to `session_rpl`
`account_summary["session_rpl"]` reports `1.17e-06` BTC (the gross trade profits before fees and before the 08:00 settlement). Deribit's `session_rpl` omits commissions and prior settlement sweeps; `mainnet_pnl.daily_pnl_btc` correctly accounts for both net commissions and the settled balance change, reflecting true net equity delta.

---

## 4. Verdict

**SOUND / EXACT MATCH**
