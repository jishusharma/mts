# Live Aid review, 2026-11-13 (declutter, WaveTrend, 5m chart)

Operator 11-13: what was done, what is clutter, WaveTrend takes too much space, make the 5-minute chart explain itself.
Review from code at trunk `6b22ac394` + learnings `research/live_aid_learning/2026-11-13.md`. No browser was used: height shares are
ESTIMATES from the layout code (Home = 70% chart column / 30% rail, 900 px tall screen assumed), not measured.

## 0. Facts that change the picture
| fact | evidence |
|---|---|
| IDEA / SETUP banners no longer exist on the page | home.js `flashes()` comment: gone since card live-aid-board-render-1111 |
| So the flag log only gets news / liq / touch rows | test_flag_log_records_each_banner: kinds liq, touch |
| The 51% / 47% scores are of banners he no longer sees | learnings 2026-11-13: replay of removed flags |
| WaveTrend is already one line, strips behind a click | home.js `wtSoWhat`, commit 35888094e (11-13 00:18 IST) |
| That line is a ~40-word sentence, choice not remembered | `wtOpen` is a JS var, resets on reload |
| His screen may predate 35888094e | page reaches him only after a deploy |

## 1. Sections: Home tab (what he looks at)
Shares: est. of Home screen height, wide column = chart column.
| section | share | tells him | evidence behind it | verdict |
|---|---|---|---|---|
| Header: price + next level up/down | 3% | price, nearest levels | levels SOURCED (his chart) | KEEP |
| 5m chart (candles, levels, sessions, volume, CVD) | ~55% | what price did, where levels are | none scored | KEEP, make explain itself (part C) |
| WaveTrend one-line sentence | 3% | timing/frame/4h state | WT crosses not proven (his own backtest critique, OPERATOR_DECISIONS) | SHRINK to chip strip (part B) |
| WaveTrend six strips (open) | +25% | WT lines 6 timeframes | none; 4h "too frequent" | MOVE BEHIND A CLICK (already; remembered now) |
| Bias line | 3% | which clock wins | none scored | KEEP |
| Two-sided board (LONG / SHORT) | 12% | both sides, n and rate of current mix | base_rates n shown, flags 47-51% | KEEP, grey if n<30 |
| Direction gauge + so-what | 10% | 6-vote lean | votes: no single reading beats 52% (11-11 review) | SHRINK (REMOVE-CANDIDATE: gauge) |
| Level story card | 9% | state at nearest level | fades: only Europe high passes | KEEP, show hit rate |
| Indicator read card | 8% | VFI, squeeze, ADX, WT, RSI sentences | stacking adds nothing (51% vs 49%) | MOVE BEHIND A CLICK |
| Liquidations card | 7% | forced selling | no scoring log (R08) | KEEP, SHRINK |
| Money (OI) card | 7% | OI vs price per venue | oi_poller not running here | REMOVE-CANDIDATE until fed |
| News card | 6% | scored headlines | news_study separate | KEEP |
| Flash banners (news, liq, touch) | 0-6% | events | logged now | KEEP |

## 2. Sections: other tabs (opened on a click, 0% of Home)
| tab / section (live_aid.html) | what it tells him | evidence | verdict |
|---|---|---|---|
| Money: What the money is doing | OI sentences per venue | no feed here | KEEP, fed by poller |
| News | feed + weight | news_study | KEEP |
| US open: if up, if down | levels at 14:30Z | scenario ledger 25 rows | KEEP |
| In trade: readings, Resting limits ladder | his position | not Live Aid evidence | KEEP |
| Now (p-ov) | price + tabs | none | KEEP |
| Map (p-playbook) + Detail | dial of six verdicts | dial = same votes | MOVE BEHIND A CLICK (already in details) |
| Verdict and watch list | lean from analysts, VWAP, RSI | none scored | REMOVE-CANDIDATE (duplicates gauge) |
| Pre-US-open risk flag | NQ / Kospi risk | none seen here | KEEP |
| Forced selling on other exchanges | BTC liqs, 3 venues | xliq_collector not running | REMOVE-CANDIDATE until fed |
| Same data, other readings (antic) | price x OI split | duplicates Money | REMOVE-CANDIDATE |
| Big candle story | 8-story read of last 60 min | no scoring | REMOVE-CANDIDATE |
| Value area and acceptance | prior-day VA, POC | levels SOURCED | KEEP |
| Level approach prep | levels within 0.5% | duplicates level story | REMOVE-CANDIDATE |
| Macro calendar | next USD event | FF feed | KEEP |
| Analysts / Liquidations / Momentum / Levels / Funding / Coil and pierce | raw tables | none scored | MOVE BEHIND A CLICK (one "raw tables" fold) |
Remove-candidates: nothing is deleted without his yes. Gauge, Verdict, Antic, Big candle story, Level approach prep, Money-until-fed, Forced-selling-until-fed.

## 3. WaveTrend: done and not done
| when | what | source |
|---|---|---|
| 11-07 | WaveTrend usage + crypto filter research | commit 18cd0ac90, card tvfav-usage-wavetrend-1107 |
| 11-09 | WT in 11-timeframe lean grid | b58d13a0a |
| 11-10 | six WT lanes 1m-4h (timing 1-3m, frame 15-30m, 4h context) | cdd5dd2dc, OPERATOR_DECISIONS 11-10 21Z |
| 11-10 | timing-check strip (big dot + 15m + 30m + level + tape) | 61be0d9cc; trigger row removed 11-12 (unreadable) |
| 11-12 | "every panel gets a so-what line or is cut" | OPERATOR_DECISIONS 11-12 |
| 11-13 00:18 IST | six strips collapsed to one sentence, click opens strips | 35888094e |
| 11-13 (this review) | sentence -> one row of timeframe chips; choice saved per viewer | part B |
Still not done / asked: WT settings question (channel/average length) unanswered (REQUIREMENTS Q1); WT proof (his note: buying on crosses in a downtrend invalidates the backtest); WT feeds no flag or weight (11-11 review).

## 4. Top 5 improvements (ranked by value)
| # | improvement | why | card |
|---|---|---|---|
| 1 | Log what the page really shows incl. board LONG/SHORT state changes, auto-export to a file | log has no idea/setup rows; learner starved; browser-only | live-aid-log-idea-setup-rows-1113, live-aid-flag-log-autoexport-1113 |
| 2 | Hit rate + n beside each flag, unproven greyed (n<30 or gap<10 pts) | stops trusting 47-51% flags | live-aid-flag-hitrate-grey-1113 |
| 3 | CBP analyst levels + MTS layer state as one row on Home | he looks at Home only; fired/silent per layer (R15) | live-aid-cbp-mts-state-on-home-1113 |
| 4 | Fold 7 remove-candidates behind one click (his yes first) | clutter, none evidence-backed | needs his yes; card after |
| 5 | Daily learner trigger + liquidation history log | the loop never ran for 11-12; liq trust unmeasured | live-aid-learn-daily-trigger-1113, live-aid-liq-history-log-1113 |

## 5. Market, MTS, CBP in one line each
| source | state today |
|---|---|
| Live Aid log | unreadable (browser); replay only: setup 51% n 1342, idea 47% n 763 |
| MTS layers | 0 of 40 fee-net rows carry a surviving PASS (STATUS 11-11) |
| CBP | analyst levels are Context, never signals; shown only as lines in chart levels |
| Market | replay 11-10: event sweep to 73,525 then squeeze to 74,844; page flagged both sides |
