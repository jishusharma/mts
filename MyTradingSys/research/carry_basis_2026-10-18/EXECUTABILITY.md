# Carry executability memo (R1 E3)

Read date for all web sources: 2026-10-28. No backtest, no sealed read, no order, no account. Registry: `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` row E3.

**Result: a venue exists (Binance, Bybit and OKX all list spot + USDT perp at <= 0.10 % per leg, taker, no borrow for the unlevered arm); the latest year that is already read paid 6.26 %/yr (>= 4 %/yr OURS); the sealed 2025-07+ read is still needed and not taken; the testnet live path has no spot leg. Status: PARK until the operator answers the one line in section 4.**

## 1. Venue x fee per leg (non-VIP, taker unless stated)

| Venue | Spot fee/leg | USDT perp fee/leg | Spot + perp both listed | Source (read 2026-10-28) |
|---|---|---|---|---|
| Bybit | 0.100 % maker / 0.100 % taker | 0.020 % maker / 0.055 % taker | yes | https://www.bybit.com/en/help-center/article/Trading-Fee-Structure (fetched; page itself says region may differ) |
| Binance | 0.10 % / 0.10 % (VIP0; 0.075 % paying BNB, third party) | USD-M 0.02 % maker / 0.05 % taker (10 % off with BNB in futures account) | yes | Official page https://www.binance.com/en/support/articles/360033544231 could not be fetched; numbers via search summary of Finder/CryptoPotato: UNVERIFIED on the official page |
| OKX | about 0.10 % taker (0.08 % maker; sources conflict) | 0.02 % maker / 0.05 % taker (Regular tier, schedule dated 2026-04-08) | yes | https://www.okx.com/fees not fetchable; third-party GitHub/Matrixport pages only: UNVERIFIED |
| Deribit | standard tier shows about 2 bps maker / 5 bps taker for spot (table garbled in search text) | perp 1.5 bps maker / 3.5 bps taker (VIP1: 0 / 3 bps) | spot BTC/USDC launched 2023-04 (Forklog) | https://support.deribit.com/hc/en-us/articles/25944746248989 (search snippet only: UNVERIFIED); fetch of deribit.com/kb/fees returned no fee content |

- The card's gate is <= 0.10 % per leg. Spot at 0.10 % meets it with zero margin on the three large venues; every perp fee is lower. The study's cost model charged 0.10 % on all four legs (`RESULT.md` s.4 SOURCED `run_pub.py:15`), so it overstates cost against these perp fees (conservative).
- Zero borrow: the PASS arm is unlevered (spot BTC held, perp short sized to it), borrow = 0.0 % (OURS, `RESULT.md` s.4). The 3x margin arm FAILED (liquidated 2021-05-19) and is not proposed.
- Caveat OURS: only Bybit was read from an official page. Binance, OKX, Deribit need a second look at the official fee pages (browser) before any decision; the order of magnitude is not in doubt but exact tiers are.
- Not checked: withdrawal, KYC/region availability, perp-spot collateral rules on each venue, and whether BTC held as spot can serve as perp margin (venue-specific, OURS assumption in `RESULT.md`).

## 2. What the latest year needs

| Window | Net ann. (always-on, unlevered) | Status | Source |
|---|---|---|---|
| DEV 2021-01..2023-06 | 15.35 % | read | `RESULT.md:3,12` |
| VAL 2023-07..2024-06 | 12.06 % | read | `RESULT.md` s.2 |
| HOLD 2024-07..2025-06 | 6.26 % | read (it is the project VALIDATION window, `PRE_REG.md:16`) | `RESULT.md` s.2 |
| 2025-07+ | not known | SEALED, strictly unread | `RESULT.md` s.4 (`run_pub.py:17,438`) |

- The yield decays 15.35 -> 12.06 -> 6.26 %/yr. The latest read year clears the 4 %/yr bar (OURS) by 2.26 points, but the trend points down, so the sealed year may not.
- What a sealed read needs: one operator approval line (section 4). Nothing else: funding and 1m/spot data already exist in `carry_basis.py` / `fetch_spot.py`; the read is a single run of the existing script on 2025-07+ with the pre-registered gate. This memo does not run it.

## 3. What the testnet live path lacks

- The live path trades Deribit testnet perpetuals only; carry needs a spot BTC long on the same venue as the short perp, and the live path has no spot leg (R1 s.2 row "Funding carry", OURS).
- Missing pieces (OURS list, not built): spot order placement and balance tracking; delta-neutral sizing and rebalance; funding-accrual accounting; margin monitoring for the short leg; a testnet spot market if one exists (unverified).
- Mainnet is forbidden by project rules, so even a venue pick cannot be executed here; carry would need operator-run mainnet and going private (`q-go-private-on-edge`).

## 4. PASS / park rule (R1 E3) and the one-line ask

PASS = venue exists (met on fees, see s.1) AND latest-year net >= 4 %/yr OURS (read year 6.26 % met; sealed year unknown) AND operator approves the sealed read and going private. Not met until approval; otherwise carry parks and GO-PRIVATE trigger B is withdrawn.

**Operator one-liner: approve one read of carry's sealed 2025-07+ window (yes/no), and say whether carry alone justifies going private.**
