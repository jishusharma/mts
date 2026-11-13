# PRE_REG: win rate vs expectancy, long scalps on Bybit perps (slug edge9-winrate-vs-expectancy-1114)

Written and committed BEFORE any outcome is computed. Only `fetch_klines.py` (raw download) has run. Origin: operator 2026-11-14, a signal app (CoinSwitch Pro "Zing")
showing 41 live signals with 56-86% win rates; question: how, when MTS finds no edge? Two goals: (1) show on our own data that an 80%+ win rate is made by the
target/stop shape alone and what that does to profit per trade after fees; (2) search honestly for a long scalp with BOTH a high win rate and positive fee-net expectancy.

## Context
Regime: none as an entry gate; the BTC daily close vs its 200-day SMA share per split is reported (see Regime mix). Phase: none. Session: none (24h market, no hour filter).
Entry: the open of the 5m bar after the signal bar's close (taker variant) or a limit at the signal bar's close (maker variant).
Regime mix: reported in RESULT.md per split as % of days BTC closed above / below / within 5% of its 200-day SMA; a split >85% one regime is flagged ONE-REGIME and cannot carry a PASS alone.

## Data
| Item | Choice |
|---|---|
| Source | Bybit v5 public linear USDT perps (`api.bybit.com`, no key): 5m klines and 1h open interest (OI). Cache `runtime_data/edge9-winrate-1114/` (git-ignored). |
| Universe | 20 perps, fixed now (OURS): BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM TRX BCH ETC UNI NEAR FIL XLM AAVE. |
| History | From 2021-01-01 (OURS; not 2020, to fit the 75 min time box with 5m bars) to the last closed bar. Coins start at their Bybit listing. 15m bars are built from aligned 5m triples (all 3 present). |
| Cut rule | If the 5m download of all 20 is not finished 35 min into the session, run on the coins that finished (list order, minimum 10) and say so in RESULT.md. |
| Gaps | The 5m series sits on a full time grid with NaN holes. A signal needs finite inputs; a trade whose entry..exit window (288 bars) has a NaN or runs past the last bar is dropped and counted. |

## Signals (long only; each is a row family; signal evaluated at a bar close, fill on the next 5m bar)
| Family | Rule | Label |
|---|---|---|
| S0 | random entry: each 5m bar is a signal with probability 1/288 (about one a day per coin), seed 20261114; the baseline for the same exit shape | OURS |
| S1 | 15m Wilder RSI(14) of 15m closes <= 25 at the 15m bar close (every qualifying bar; one position at a time handles repeats) | SOURCED RSI (Wilder 1978, n=14); 25 = card, OURS |
| S2 | 5m close <= 0.985 x the rolling 48-bar (4 h) mean of the typical price (H+L+C)/3 on 5m | OURS |
| S3 | 5m close <= 0.985 x close 12 bars (1 h) earlier AND OI down >= 2% over 1 h: latest OI snapshot with timestamp <= signal close vs the snapshot exactly 1 h before it (the OI series is point-in-time, up to 1 h stale; a limitation). Skipped, and said so, for a coin or period without OI | OURS |
One open position per coin per cell; a signal while a position is open (in that cell and coin) is skipped. Cells are simulated independently.

## Exit grid (12 shapes per family, OURS)
Target T in {0.3%, 0.5%, 1%} x stop S in {0.5%, 1%, 2%, 3%}, fixed percent of the entry price; time stop = close of the 288th bar (24 h) after the entry bar start.
Stop-first rule: if one bar's range contains both the stop and the target (L <= stop and H >= target), the STOP counts (conservative). The fill bar itself is walked too. A stop fills at the stop price, or at the bar open if it opens below. A target fills at the target price.
Taker variant: entry at the next bar's open. Maker variant: a limit buy at the signal bar's close; filled only if the next bar's LOW < limit (trades through); fill price min(limit, open of that bar); an unfilled signal is no trade (and does not block).

## Costs (round trip, as a fraction of price, fee-net)
- Taker: 5 bp per side (SOURCED: `backtest/fees.py` BINANCE_TAKER = 0.0005, used for Bybit as the same class of fee) + 12 bp round-trip slippage (operator order, OURS) = 22 bp.
- Maker-entry: 2 bp entry (SOURCED: Bybit VIP0 maker 0.02%) + 5 bp exit taker + 6 bp half the slippage on the exit leg = 13 bp. The label "assumes the limit fills" applies; the through-fill rule above is the only fill filter. Funding is not charged (holds <= 24 h; limitation).
- Net per trade = gross return - cost, in percent.

## Splits (by ENTRY time)
DEV 2021-01-01..2023-12-31; VALIDATION 2024-01-01 onward. The verdict is read on VALIDATION; DEV is reported only.

## Columns reported per cell (signal x shape x taker/maker), on VALIDATION and DEV
trades, win rate, average win %, average loss % (gross, before cost), mean % per trade fee-net, profit factor (fee-net), worst 5-day drawdown (fee-net percent PnL summed per exit day across coins, worst 5 consecutive calendar days sum), breakeven win rate (S+c)/(T+S) for the shape. Cells with win rate >= 75% are marked.

## PASS gates (a cell passes only if ALL hold; family = the 72 non-S0 cells, i.e. 3 signals x 12 shapes x 2 fills, minus skipped ones)
1. VALIDATION fee-net mean > 0 and the day-cluster bootstrap 95% CI lower bound > 0 (cluster = UTC entry day, pooled across coins, 4000 resamples, seed 7).
2. >= 200 VALIDATION trades.
3. Beats S0 with the same shape and same fill variant: one-sided day-cluster bootstrap p < 0.05 on the difference of fee-net means (both resampled independently).
4. BH at 10% over the one-sided bootstrap p-values (mean > 0) of the family.
5. Mean stays > 0 after dropping the 5 best entry days.
Verdict PASS if at least one cell passes all five; else FAIL. A passing cell with win rate < 75% is reported honestly as a pass but not as the "high win rate AND positive expectancy" answer to the question; the answer needs win rate >= 75% too.

## Tests (fail-first)
`test_study.py`: stop-first on a same-bar touch; target fill; gap-through-stop fill at open; time stop; maker not-filled when low does not trade through; RSI hand value. Run once against a deliberately wrong version (target checked before stop) and show it fails.
