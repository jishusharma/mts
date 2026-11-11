# C30 H2 long, paper forward rule (frozen 2026-11-11)

Source tag `layer:wt:c30_h2_long`; params id `c30_h2_long_15m_2026-11-11`. Paper only, no orders, flag BELOW-SIZE-RULE.
Planned move averages about 0.26 % (under the 500 USD / 40 bp size line; it runs as frozen, paper only, flagged BELOW-SIZE-RULE).

## Pins (git blob hashes, `git hash-object`)
| File | Blob |
|---|---|
| MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md (section 1 = the rule) | e6d858f57f125704deda18f1f13c8e727a1124ec |
| .../wt_rsi_div.py | 36469318f48d33b3c79baeef530e83be3c03abde |
| .../wavetrend_dots.py | fde5d3259a1b3679abae36a21579fc3ae8f1fd4b |
| .../wt_context.py | f298579fae4510532b00f4236ccad6da8bdf0677 |
| .../wt_lower_tf.py | d7e15c4e7c36431db4b42a07723e498eec281b94 |
| MyTradingSys/backtest/fees.py (BINANCE_TAKER) | ceeb05a337ed92bc1ebca6e40ba706c9a80d6059 |

## Parameters
| Item | Value | Label |
|---|---|---|
| WaveTrend | hlc3; EMA 10; EMA 10 of abs dev; ci = (ap-esa)/(0.015 d); wt1 = EMA 21; wt2 = SMA 4 | SOURCED (LazyBear) |
| Buy dot | wt1 crosses above wt2 on the close, wt1 <= -53 | SOURCED band, OURS level |
| RSI | 14 Wilder on closes | SOURCED |
| Bullish divergence | p = lowest low bars i-40..i-8, q = lowest low i-7..i; L[q]<L[p], RSI[q]>RSI[p], RSI[p]<=40 | OURS |
| 2h trend | swing structure W=5 on 2h bars, value of last 2h bar closed by the 15m close; must be up | OURS |
| Entry | open of bar i+1 | OURS |
| Exit | first bar k>i with wt1>0, filled at open of k+1; cap 60 bars; also exit if 2h trend turns down | OURS |
| One trade at a time | new signal ignored while a paper trade is open | OURS |
| Fee | BINANCE_TAKER x 2 from backtest/fees.py (via wavetrend_dots.FEE), no funding | SOURCED constant |
| R of a paper trade | net return / risk; risk = (entry - low of divergence second pivot q) / entry | OURS |
| Warm-up | MIN_BARS = 2000 closed 15m bars (250 2h bars for the structure, EMA settled); fetch 3000; fail closed below 2000 | OURS |

The frozen rule has NO stop. The risk distance is only a yardstick to express the result in R; no trade is stopped at it.
A signal whose entry open is not above the pivot low (risk <= 0) is journaled as unresolved (not counted).

## Kill rule (OURS, same as the Malkan forward)
After 30 closed paper trades with net R sum <= 0: one `kill` row, verdict KILL, no further signals.

## Journal (runtime_data/c30_h2_forward.jsonl, git-ignored)
Kinds: signal | outcome | no_fill (unused here, entry is the next open, always fills) | unresolved | kill.
outcome fields: kind, t (fill bar open ms), t_trigger, side ("long"), source, params_id, status ("closed"), net_r, net_pct, risk_frac,
entry, exit, bars, why (X1 | trend flip | cap), t_fill, t_exit_bar.
signal fields: kind, t, t_trigger, side, source, params_id, entry_ref, pivot_low, wt1, flag.
Run: `python c30_paper_log.py --once [--journal PATH] [--history-warmup N]` once per closed 15m bar by hand or by a coordinator; no scheduler here.
