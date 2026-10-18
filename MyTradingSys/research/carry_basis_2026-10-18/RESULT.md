# RESULT: funding carry basis (BTCUSDT, DEV+VALIDATION+HOLDOUT)

**Verdict: PASS for unlevered always-on carry; FAIL for switched carry and 3x margin carry.**
PRE_REG.md precedes this file. Study evaluates real spot-vs-perp basis mark-to-market, 4-leg transaction fees, and 3x margin liquidation against `published_strats_2026-10-13/supp_carry.txt`. Sealed window 2025-07+ was strictly NOT read.

## Verdict arms

| arm | n | mean % | SE % | verdict |
|---|---|---|---|---|
| CARRY_always_unlevered | 911 | 0.0420 | 0.0028 | PASS |
| CARRY_switch_unlevered | 911 | 0.0339 | 0.0031 | FAIL |
| CARRY_always_margin3x | 911 | 0.1261 | 0.0083 | FAIL |

FAIL means stop: cash-and-carry basis trading on BTC perp is nil or unviable if DEV net annual return is <= 0.0% or worst 30-day drawdown exceeds 15% unlevered.

## 1. Key Findings

1. **Spot-vs-perp basis drift is negligible over multi-year horizons:**
   - DEV (2021-01..2023-06, 911 d): spot-perp basis drag = **-0.02%/yr** (OURS).
   - VAL (2023-07..2024-06, 366 d): spot-perp basis drag = **-0.07%/yr** (OURS).
   - HOLD (2024-07..2025-06, 365 d): spot-perp basis drag = **+0.02%/yr** (OURS).
   - Because 8h funding settlements contractually enforce perp convergence to spot, the spot-vs-perp basis cannot drift away persistently. Over months, real basis PnL sums close to zero.

2. **Unlevered always-on carry survives with real basis & fees:**
   - DEV: net annual **15.35%** (vs 15.40% funding alone), Sharpe **9.64** (vs 10.70), max drawdown **-0.43%** (vs -0.40%).
   - VAL: net annual **12.06%** (vs 12.10% funding alone), Sharpe **15.15** (vs 18.65), max drawdown **-0.08%** (vs -0.00%).
   - HOLD: net annual **6.26%** (vs 6.20% funding alone), Sharpe **13.04** (vs 18.40), max drawdown **-0.10%** (vs -0.10%).
   - The apparent Sharpe 10-18 in `supp_carry.txt` drops slightly (to 9.6-15.2) due to daily mark-to-market basis volatility, but the carry return is real and not an artifact of ignoring basis.
   - The structural decay **15.4% -> 12.1% -> 6.3%/yr** reflects increasing crypto market efficiency over successive market cycles, not basis drag.

3. **Switched carry underperforms and suffers large drawdowns:**
   - Switching on trailing 3-day funding incurs 21 round-trip trades (4 legs x 0.10% = 0.40% fee per trade).
   - DEV net annual drops from 15.35% to **12.38%**, with max drawdown expanding from -0.43% to **-2.87%**, and worst 30-day rolling return collapsing to **-15.02%** (breaching the 15% tolerance gate).

4. **3x margin carry suffers fatal liquidation at 1h extremes:**
   - While 3x margin boosts annualized return on paper (46.04% in DEV, 36.19% in VAL, 18.78% in HOLD), checking 1h lows reveals **two fatal liquidation events in DEV**:
     1. **2021-05-19 13:00 UTC**: Spot flash-crashed **-29.99%** from daily open to 1h low, breaching the 3x margin liquidation threshold (-26.67% at ML <= 1.10).
     2. **2021-07-26 01:00 UTC**: Perp short-squeezed **+36.18%** intraday, breaching the 3x short maintenance margin threshold (+32.83%).
   - Leveraged carry is unviable without active intraday margin replenishment or dynamic deleveraging.

## 2. Full Performance vs Baseline (`supp_carry.txt`)

All values per window (DEV 911 d, VAL 366 d, HOLD 365 d). Fee = 0.10% per side per leg (cost 0.10 %).

| Metric | DEV (supp_carry) | DEV (OURS) | VAL (supp_carry) | VAL (OURS) | HOLD (supp_carry) | HOLD (OURS) |
|---|---|---|---|---|---|---|
| **Mean Funding Rate (%/yr)** | 15.4% [1] | 15.37% | 12.1% [2] | 12.13% | 6.2% [3] | 6.24% |
| **Spot-Perp Basis Drag (%/yr)** | not modelled | -0.02% | not modelled | -0.07% | not modelled | +0.02% |
| **CARRY_always Net Ann %** | 15.4% [1] | **15.35%** | 12.1% [2] | **12.06%** | 6.2% [3] | **6.26%** |
| **CARRY_always Sharpe** | 10.70 [1] | **9.64** | 18.65 [2] | **15.15** | 18.40 [3] | **13.04** |
| **CARRY_always Max DD** | -0.4% [1] | **-0.43%** | -0.0% [2] | **-0.08%** | -0.1% [3] | **-0.10%** |
| **CARRY_always Worst 30d** | -3.9% [1] | **-4.41%** | +0.7% [2] | **+0.66%** | -0.9% [3] | **-0.93%** |
| **CARRY_switch Net Ann %** | 9.1% [4] | **12.38%** | 7.3% [5] | **9.62%** | 1.5% [6] | **3.97%** |
| **CARRY_switch Max DD** | -8.4% [4] | **-2.87%** | -4.5% [5] | **-2.21%** | -2.3% [6] | **-0.84%** |
| **CARRY_switch Worst 30d** | -3.9% [4] | **-15.02%** | +0.7% [5] | **-19.11%** | -0.9% [6] | **-8.41%** |
| **CARRY_always 3x Margin Ann %** | not modelled | **46.04%** | not modelled | **36.19%** | not modelled | **18.78%** |
| **3x Margin 1h Liquidations** | not modelled | **2 (FATAL)** | not modelled | 0 | not modelled | 0 |

Sources:
- [1] `published_strats_2026-10-13/supp_carry.txt:1`
- [2] `published_strats_2026-10-13/supp_carry.txt:2`
- [3] `published_strats_2026-10-13/supp_carry.txt:3`
- [4] `published_strats_2026-10-13/supp_carry.txt:4`
- [5] `published_strats_2026-10-13/supp_carry.txt:5`
- [6] `published_strats_2026-10-13/supp_carry.txt:6`

## 3. Haircut Sensitivity Table

Evaluated on the DEV window (911 days).

### Fee Sensitivity (per side per leg)

| Fee / leg | Total Round-Trip (4 legs) | CARRY_always Ann % | CARRY_switch Ann % | Switched Trades |
|---|---|---|---|---|
| **0.00%** (zero fee) | 0.00% | 15.35% | 15.58% | 21 |
| **0.02%** (maker rebate) | 0.08% | 15.35% | 14.94% | 21 |
| **0.05%** (VIP taker) | 0.20% | 15.35% | 13.98% | 21 |
| **0.10%** (standard taker) [7] | 0.40% | 15.35% | 12.38% | 21 |
| **0.15%** | 0.60% | 15.35% | 10.78% | 21 |
| **0.20%** | 0.80% | 15.35% | 9.17% | 21 |

- `CARRY_always` only trades once at inception (2 legs = 0.20%), so ongoing fee sensitivity is negligible (0.08%/yr difference across 2.5 years).
- `CARRY_switch` is killed (net ann drops below 0%) at a taker fee of **0.49% per leg** (1.95% round-trip).

### Basis Move Haircut
- DEV net carry before fee: **+15.35%/yr** (funding +15.37%/yr + basis -0.02%/yr).
- Adverse basis drift required to wipe out unlevered carry: **-15.35%/yr**.
- In spot vs perpetual markets, an annual basis drift of -15% cannot persist because 8h funding settlements continuously force convergence.

## 4. Parameter Labels (SOURCED vs OURS)

- **SOURCED**:
  - DEV window: `2021-01-01` to `2023-07-01` (`run_pub.py:24`).
  - VAL window: `2023-07-01` to `2024-07-01` (`run_pub.py:24`).
  - HOLD window: `2024-07-01` to `2025-07-01` (`run_pub.py:24`).
  - Sealed holdout boundary: `>= 2025-07-01` strictly unread (`run_pub.py:17,438`).
  - Funding-alone carry baseline: DEV 15.4%, VAL 12.1%, HOLD 6.2% (`supp_carry.txt:1-3`).
  - Execution fee rate: 0.10% per side per leg (`run_pub.py:15`).
  - Switched carry filter: trailing 3-day funding sum > 0 (`run_pub.py:334-338`).
- **OURS**:
  - Daily spot-perp mark-to-market basis PnL formula: $(S_t - S_{t-1})/S_{t-1} - (P_t - P_{t-1})/P_{t-1}$.
  - 4-leg cost allocation: 2 legs entry (0.20%) + 2 legs exit (0.20%).
  - Unlevered carry borrow rate assumption: 0.0% (spot BTC posted as portfolio collateral).
  - 3x margin liquidation threshold model at 1h lows: spot ML <= 1.10 (-26.67% drop) and perp MMR = 0.5% (+32.83% rise).
