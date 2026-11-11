# Live Aid review, 2026-11-11

Operator: "is it worth it, what did it print, why no long from the lows, I see no weightage".
Review, not a backtest: descriptive, in-sample, no fees, BTCUSDT spot only, 29 days to 2026-11-10 20:51Z.

## Method
The page keeps no log of what it flashed, so `replay.js` runs the page's own code (`pulse.js`, `levelstory.js`, `indread.js`)
every 5 minutes on closed bars and records each flag when it first appears. `analyze.py` scores it on 1m closes (`tables.md`).
Run: `python fetch.py`, `node replay.js 28`, `python analyze.py`.

Limits: levels are rebuilt here (yesterday / 2-day / last-week high and low, day open, completed Asia and Europe high and low);
the page also merges analyst and moving-average levels, which cannot be replayed. Direction uses 3 of its 6 votes (VWAP, RSI 1h, RSI 4h).

## Numbers
| | flags | right after 1h | avg move 1h |
|---|---|---|---|
| IDEA banner | 759 | 47% | -0.01% |
| SETUP FORMING banner | 1262 | 51% | -0.01% |
| Timing check ALIGNED | 41 | 56% | +0.03% |

- 71 flags a day; 58% are followed by an opposite flag within 30 minutes.
- Stacking the readings adds nothing: with 4+ of 6 readings agreeing (direction, pulse grid, ADX/DI 15m and 1h, Volume Flow 15m,
  WaveTrend 30m) an idea is right 51%; against them 49%. No single reading moves an idea past 52%.
- ADX regime, session, level type: all 40-60%, none with the count to trust (best: fade at last week low 72%, n 18).

## 2026-11-10 (the day he asked about)
| UTC | what price did | what the replayed page flagged |
|---|---|---|
| 13:30 | event drop to 73,525: swept yesterday low 73,750, tagged the 2-day low 73,510 | nothing |
| 13:45 | bounce | LONG idea, rejected at yesterday low (+0.56% in 1h) |
| 14:00 | | SHORT idea, accepted below Europe low (-0.88%) |
| 14:25 | | LONG idea, failed break of yesterday low at 73,714 (best +1.53%: the run to 74,844) |
| 14:45-14:55 | squeeze through the US open to 74,844 | SHORT idea, rejected at Asia low near 74,300 (+1.8% in 1h, after 0.7% against) |
| 15:15 | the top | LONG idea, accepted above Asia low at 74,470 (-1.5%) |
| 16:00 | low 72,727 | SHORT idea, accepted below the 2-day low (+0.46%) |

The long and the short were both flagged, and each was contradicted within 20-30 minutes while Direction read SHORT all day.
The page reads each level on its own; it has no notion of his sequence (event sweep, squeeze the shorts, then take the low).

## Asked vs present
| asked | state |
|---|---|
| Volume Flow, Squeeze (LazyBear), ADX/DI, WaveTrend | on Home as a display card and lanes; none feeds a flag or a weight |
| Tom / Fabio acceptance and absorption | in the level card (2 closes, absorbed touch) |
| Value area 80% rule, big-candle story, US-open base rates | on other tabs only; Home does not use them |
| weight / confidence across contradicting reads | absent |
| a record of what was flashed | absent |
| live volume profile (today's value area and POC) | absent: only yesterday's value levels as lines |

## Changed here
`home.js`: when direction banners on screen point both ways, one amber BOTH SIDES line replaces them. It names the level and
carries the newest LONG case and SHORT case in full, so no forming setup is dropped (test in `test_levelstory.py`).
