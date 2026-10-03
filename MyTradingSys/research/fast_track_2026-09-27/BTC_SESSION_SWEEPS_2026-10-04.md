# BTC session-open sweeps and the US-open move (T054 + T058) [GATED v3.0]

Session: MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps. Gate: `methodology/playbook.md` Part I v3.0.
Items: `items/T054_us_session_news_correlation.md`, `items/T058_broken_extremes_sweep_vs_continuation.md`.
Own study: `research/session_sweeps/session_open_study.py` -> `research/session_sweeps/results_2026-10-04.json`
(pre-registered in the script header before the first run; reruns in ~30 s on local `Dumps/`).
External literature: `BTC_SESSION_EXTERNAL_2026-10-04.md` (subagent /sonnet-01, same gate).
Status: RESEARCH. Nothing here is a rule. Any setup becomes its own layer, never a Tom filter.

## 0. BOTTOM LINE

1. The US cash open is real for VOLATILITY. BTC's busiest 15 minutes of the UTC day start at the NY cash open,
   and that peak moves from 13:30 to 14:30 UTC when US daylight time ends (F1). Confidence H.
2. It is not real for DIRECTION, using the definitions below. The first 10, 15 or 30 minutes after the open
   predict the rest of the session about 50% of the time. That is the same as 24 placebo clock times, and the sign
   flips from year to year (F2).
3. Pre-US sweeps have no measured effect on US-session direction. Cases tested: London sweeps the Asia high or
   low, or the pre-US hours sweep the previous day's high or low, and price is back inside the range at the open.
   The US session then closes up 46-49% of the time; the base rate is 48% (F3, F3b).
4. A sweep of the pre-US range in the first 30 minutes, with price back inside by open+30, gives no edge either
   way: 52% up after both kinds of sweep (F4).
5. Tom's opening-range rule ("small opening range -> trend") is not supported on BTC at the NY open. Trend days
   are 29%, 31% and 33% for small, mid and large ranges (F5).
6. One unplanned signal turned up inside a CONTROL test. Three hours after the open, a new day low that holds is
   followed by a rise 73% of the time (n=59, all 5 years). This is post-hoc: a hypothesis for untouched data,
   nothing more (F6).
External T1 literature agrees: BTC is busiest in EU/US stock hours, and session-of-day return anomalies are not
persistent (F7, F8). No T1/T2 study tests a sweep-then-reversal at an open (F11).
So the operator's "trade the volatility, both directions" premise holds for WHEN, not for WHICH WAY. The closest
sourced logic for "sweep then real move" is Fabio v3's NY-window model, which adds order-flow confirmation
(S5 breakout, S5D failed auction). It is built, but its historical run produced NO RESULT (B099). It is the
next thing to run.

## 1. STEP 1 - METHOD NOTES (written before searching or running)

- **SQ1 Is BTC activity concentrated at the US cash open (and other opens)?** Settled by an intraday profile by
  15-minute bucket on multi-year 1m data, split by US DST regime. This is a natural experiment: if the peak moves
  with DST, the US open drives it, not the UTC clock. T1/T2 intraday-seasonality studies rank it. Descriptive, so
  no costs.
- **SQ2 Do the first 10-15 minutes decide the day?** Settled by day-level sign persistence (first k minutes vs the
  rest of the session) over n > 1000 days, with placebo anchors and per-year stability. Any trade version then
  needs out-of-sample data and costs (taker 0.05% per side, about 10 bp round trip, plus funding).
- **SQ3 Is there a sweep, then a reversal?** In the operator's words: a move "in opposite direction before
  breaking out ... grabbing liquidity". Settled by event classes at the session boundary with base rates, Wilson
  CIs, per-year stability, a placebo anchor, then OOS. "Liquidity sweep" is practitioner vocabulary; no accepted
  academic method labels it. The external T1 work is the mechanism only (Osler, in T058).
- **SQ4 Does it hold better in the US or EU sessions?** The same tests at the London open, the NY open and
  placebo anchors.
- **SQ5 Can Tom + Fabio logic be applied and backtested?** Settled internally. Each parameter needs the trader's
  words with file:line (operator provenance rule, 2026-09-30) and must be computable from data on disk without
  look-ahead.
- **SQ6 Should we engage Cloud AI?** Settled by SURFACE_POLICY sections 1, 1b and 3b plus data reach.

## 2. STEP 2 - SOURCE-TIER PLAN (fixed before searching)

| SQ | T1 targets | T2 targets | T3 (ideas/definitions only) | Decides |
|---|---|---|---|---|
| SQ1 | journal intraday crypto seasonality (e.g. Hansen-Kim-Kimbrough JFEc; Eross et al. RIBAF; Baur et al. FRL) | arXiv/SSRN intraday crypto; exchange data docs | operator observation | own test T1 |
| SQ2 | Gao-Han-Li-Zhou 2018 JFE; Shen-Urquhart-Wang 2022 (in repo) | Zarattini-Barbon-Aziz ORB (SSRN); Kim-Hansen 2026 (in repo) | Tom opening range; Fabio IB/ORB; Crabel | own tests T2, T5 |
| SQ3 | Osler 2003/2005 (in repo, T058) | preprints on opens / stop runs | ICT, Wyckoff; Fabio "book sweeping"; Tom contra | own tests T3, T3b, T4 |
| SQ4 | as SQ1/SQ3 | as SQ1/SQ3 | - | own tests at the L and O anchors |
| SQ5 | - | - | Tom + Fabio transcripts (corpus search below) | provenance + computability |
| SQ6 | - | - | - | SURFACE_POLICY |

## 3. CORPUS SEARCH - Tom and Fabio (vocabulary mining loop)

Pools: Fabio = the 8 transcripts in `extracts/processed/fabio_valentini`. The other 94 canonical transcripts,
minus CryptoCred (5) and FlowHorse (3), are a mixed pool. Only IDs that `ANGLE_TRADE_CATALOG.md` marks TOM are
quoted as Tom. K8qtT2_axPo and 1utSjHs_Mq8 also discuss the initial balance, but the catalog marks them OTHER,
so they are excluded.
Rounds: R1 seeds (session, new york, london, asia, sweep, stop hunt, liquidity, open, first hour, first 15,
pre-market, daily open, midnight, us open, opening range, initial balance). R2 harvested (wick, fake out,
deviation, american, europe, stock market, nasdaq, opening, volatility, take out, grab). R3 harvested (preession,
pre-session, at the opening, the open). Most R3 hits fell in files already found by "opening"; the loop stopped
after R3 (the exact new-file share was not computed).
Hits (Fabio | mixed pool): session 78|51; liquidity 152|387; opening 8|82; the open 5|37; nasdaq 12|37;
opening range 4|3; initial balance 2|5; sweep 4|2; stop hunt 0|5; new york 3|3; london 2|0; asia 0|3;
us open 0|1; pre-market/first hour/first 15/daily open/midnight 0|0.
Zero hits: "daily open", "midnight", "first 15". Neither trader talks about a UTC-midnight candle or a 15-minute
rule. That part of the ask has NO trader source.

| Trader | Ref (raw_transcripts_canonical/<id>_raw.txt:line) | Says (short) | Use here |
|---|---|---|---|
| Tom | Fj4FDZQxw0I:19 (CONSOLIDATED_RULES.md:241) | opening range: "very large ... likely won't hold ... very small, it likely will" | T5 definition |
| Tom | Ld1dhjGdTCA:19 (CONSOLIDATED_RULES.md:65-67) | narrow opening range at the same liquidity as previous days -> trend more likely | T5 relative size |
| Tom | l8RZrBfzvp4:13 | at the opening "a lot of games take place" | context |
| Tom | n7ZSkjb7JXs:19 | at the open the market may first flush poorly positioned stops; open risk = quick sharp move | supports sweep-at-open as an idea (index futures) |
| Tom | T6hDJcHrVBM:13 | a spike right at the open = major imbalance (options/futures hedging); compare BTC, Nikkei, US, Europe | cross-market idea (no NQ data on disk) |
| Tom | RwQBdF9TSvc:13 | "It's not true that there's any kind of stop hunting going on." (about ICT) | CONTRA "grabbing liquidity" as intent |
| Tom | C9n_d91Uitc:13 | expects "great information at the US open" | context |
| Fabio | StaphlRH8NQ:192-193 | IB = high/low of the first 30 minutes of regular cash trading | T5 window (30 min) |
| Fabio | StaphlRH8NQ:204-206; FABIO_RULEBOOK.md:85 FR-81 | Nasdaq first-30-minute opening range "skew of 13.5%" | T3 claim, Nasdaq only |
| Fabio | FawPrRUGNpk:249-260 | "book sweeping" near the range high/low or the NY session high -> asymmetric entry | his sweep = fast book sweep with order flow, not ICT |
| Fabio | 0KyIEdvVKMQ:4 | London session "not worth to trade for me" (his own stats) | session choice from his own record |
| Fabio | jasv3L-d8ZE:5 | everything absorbed in the first two hours = worst condition | context |

Every Tom and Fabio statement above is about index futures (DAX, NQ), which have a real cash open, an overnight
gap and a closing auction. BTC has none of these. Applying them to BTC is interpolation: T3, "requires
validation" (Part I, Tom-content rule). The tests below are that validation.

## 4. FINDINGS

Own-study tag for F1-F5: `Own backtest, descriptive | 1178 NY trading days 2022-01-03..2026-09-25, 1m Binance
USDT-M, DST-aware opens, no OOS split (nothing selected), no costs (no trades), per-year stability, Wilson 95% CI`.
Anchors: A = 00:00 UTC, L = London open (07:00/08:00 UTC), O = NY cash open (13:30/14:30 UTC), E = O+390 min.

**F1 - Volatility peaks at the US cash open and moves with DST.** `Own | DST natural experiment, 1178 days | H`
- US-DST days, top buckets (volume x | |return| x the day's mean 15-min bucket): 13:30 2.55|1.92; 14:00 2.48|1.77;
  13:45 2.38|1.72; 14:15 2.21|1.68; 14:30 2.16|1.59; 12:30 1.95|1.51.
- US-standard days: 14:30 2.81|2.03; 14:45 2.66|1.81; 15:15 2.23|1.76; 15:00 2.56|1.74; 15:30 2.11|1.62; 16:00 2.01|1.56.
- The peak tracks 09:30 ET, not a UTC clock time. 12:30 UTC in summer is 08:30 ET, the US macro-release time
  (CPI/NFP); this is a hint for the T054 news leg, not tested here.

**F2 - The first 10, 15 or 30 minutes do not decide the direction of the rest of the session.**
`Own | n=1176-1178, 24 placebo anchors, per-year | M`
- P(sign of the rest of the session = sign of the first k minutes): k10 49.8% [47.0, 52.7]; k15 49.4% [46.6, 52.3];
  k30 50.1% [47.2, 52.9]. London k15 52.4% [49.6, 55.3]. O-60 k15 49.8%.
- Placebo, 24 fixed UTC hours (k15): 44.9%..53.6%, median 49.3%. The US open sits mid-pack.
- k15 by year: 52.8 / 46.0 / 49.4 / 48.2 / 51.1 (2022-2026). The sign flips.
- The median absolute rest-of-session move is 99.9 bp, about 10x the taker round trip. There is room to trade,
  but no direction from the first 15 minutes.

**F3 - London sweeping the Asia range says nothing about the US session.** `Own | n per class 113-237 | M`
- Base P(US session up) 47.9% [45.0, 50.7]. Swept the Asia high and back inside at O: 48.1% [41.3, 54.9] (n=206).
  Swept the Asia low and back inside: 48.6% [41.5, 55.8] (n=183). Broke and held: high 50.6%, low 48.1%.
  Both sides swept: 43.4% (n=113).
- High-sweep-back by year: 36 / 50 / 51 / 51 / 53. Low-sweep-back: 49 / 45 / 41 / 49 / 61. No stable sign.

**F3b - Pre-US sweeps of the previous UTC day's high or low: nothing, except one small cell.** `Own | M (null), L (cell)`
- Swept the previous-day high and back: 49.2% (n=177). Swept the previous-day low and back: 45.5% (n=178).
  Broke and held: 49.5% / 51.8%.
- Both previous-day extremes swept before the open: US session up 29.3% [17.6, 44.5], n=41. This is 1 of 12
  cells and the n is small. Noise until tested OOS.

**F4 - Sweeping the pre-US range in the first 30 minutes and closing back inside: no edge.** `Own | n 103-132 | L-M`
- Rest-of-session P(up): high swept and back 51.9% (n=106); low swept and back 52.3% (n=132); high break-hold
  52.8%; low break-hold 44.7%. The prior was "high sweep -> down": not seen.
  High-sweep-back by year: 36 / 53 / 41 / 70 / 56.
- The same test at the London open (Asia range as the reference): 49-55% in every class. No edge.

**F5 - Tom's opening range (IB 30 min) does not sort trend days on BTC.** `Own | 386 days per tercile | M`
- IB width relative to the median of the previous 20 days; tercile cuts 0.814 / 1.216 (ex-post, for reporting
  only). A trend day is |close-open| / range >= 0.6 over [O, E) (day_gates.TREND_RATIO).
- Trend days: small 29.0% [24.7, 33.7]; mid 31.1% [26.7, 35.9]; large 32.6% [28.2, 37.5]. That is the opposite
  order to Tom's rule, but the difference is not significant. By year there is no consistent order (2022 small >
  large; 2023-2026 small <= large).
- IB broken on both sides after O+30: small 56.7% vs large 33.2%. This is mostly mechanical, because a narrow range
  is easier to break twice. It is not evidence for the rule.

**F6 - An unplanned signal in a control (POST-HOC, hypothesis only).** `Own | post-hoc, ~70 cells reported | L`
- At O+180 (3 hours into the US session, reference range = day so far), a new day low that holds for 30 minutes
  is followed by a rise over the next 6.5 hours 72.9% of the time [60.4, 82.6], n=59. By year: 75 / 82 / 73 / 56 / 85.
- At the same anchor, "swept the day high and back" is followed by a rise 32.8% of the time [22.3, 45.3], n=61.
  By year: 62 / 21 / 25 / 38 / 11.
- About 70 cells are reported at 5%, so about 3.5 false positives are expected by chance. Do not use this until
  it is pre-registered and passes on untouched 2019-09..2021-12 data (N1). It belongs to the T058 H3 family
  (fade the late break).

External literature (F7+): see section 4b.

## 4b. EXTERNAL EVIDENCE (/sonnet-01)

Full table, tags and discards: `BTC_SESSION_EXTERNAL_2026-10-04.md`. That file is 145 lines and opened 14 sources.
Supervisor spot-check: Gao-Han-Li-Zhou 2018, JFE 129(2):394-414, re-fetched on RePEc 2026-10-04. Title, authors,
venue and year match, and the abstract confirms "predicts the last half-hour return". PASS.
Worker-declared deviation: its Step-1 notes were written after its first citation searches. This section's
Step 1 (above) came first.

- **F7 Session activity (T1).** BTC volume and volatility are higher during European and US stock hours
  (Wang 2020; Eross et al. 2019, 4th author Wolfe). Brauneis et al. 2024 put the single biggest hour at 16:00-17:00
  UTC across 38 exchanges. `T1 | descriptive, no OOS/costs, abstract only for some | M`
  Agrees with F1 on "US hours are busy". F1 is sharper (1m Binance perps, 15-min buckets, DST split) and places the
  peak AT the open. Brauneis's hour bins and multi-exchange spot sample probably explain the difference. Not
  resolved: the Brauneis full text was not read.
- **F8 Session direction (T1).** Time-of-day return anomalies in BTC are not persistent; volume patterns are
  (Baur et al. 2019, >15M obs, 7 exchanges). `T1 | descriptive | M-H` This matches F2-F4. For the post-2024
  spot-ETF era: No validated evidence found. The candidate paper (Schmidt and Kraft, SSRN 7384239) could not be
  opened (403).
- **F9 First half-hour (T1, equities).** The first half-hour from the PREVIOUS close predicts the LAST half-hour,
  not the rest of the day (Gao et al. 2018, SPY 1993-2013). `T1 | 20 yr, costs/OOS not in abstract | M-H (equities)`
  F2 tested a different form (first k minutes from the open -> the rest of the session). The Gao form on BTC
  (r[prev US close -> O+30] vs r[E-30 -> E]) is untested and goes into N1.
  The equity opening-range breakout: Barbon-Aziz-Zarattini SFI 24-97 is `T2 | net of costs, OOS not mentioned | M`.
  A third-party replication of the 5-min QQQ version breaks even at about one spread of slippage, and 76% of its
  profit came from 2022. `T3 | M that the edge is cost- and regime-fragile`
- **F10 Hour-scale reversal (T1).** BTC 1-4 h returns show negative autocorrelation, and larger moves reverse
  more (De Nicola 2021, 1m data 2012-2021). `T1 | in-sample style, costs not on page | M` This leans against
  continuation rules and is consistent in sign with F6 (late low -> up). It does not validate F6.
- **F11 Sweep then reversal at an open, any market:** No validated evidence found. Adjacent only: FX shows
  negative serial correlation around the 16:00 London WMR fix (Evans 2018). `T1 | abstract only | M (FX), L (BTC transfer)`
- **F12 ES/NQ -> BTC direction in the US session:** No validated evidence found. E-mini crash risk relates to
  BTC futures volatility, not returns (Tang et al. 2024, daily, 2017-2021). `T1 | no time of day, pre-ETF | M (vol), L (direction)`

## 5. ANSWERS TO THE OPERATOR

- **"Does BTC move the opposite way first to grab liquidity, then go the real direction?"** As a mechanism, yes:
  stop orders cluster beyond levels (Osler, T1, FX), and BOTH outcomes happen, reversal and cascade. At the BTC
  session boundaries tested (F3, F3b, F4), "swept and back" and "broke and held" give the same US-session
  direction as a coin flip. "After the sweep, the real move is the other way" is NOT supported at these anchors.
  Tom himself rejects stop hunting as intent (RwQBdF9TSvc:13). His version is an opening imbalance that flushes
  poorly positioned traders (n7ZSkjb7JXs:19).
- **"Better in the US / EU sessions?"** No session made the sweep definitions directional (F2-F4 at both L and O).
- **"The first 10-15 minutes decide the day?"** Not for BTC at the US open (F2). For volatility, yes: the open is
  the day's biggest bucket (F1).
- **"Asia/Europe moves after the daily candle relate to the US open?"** The volatility link holds (F1). The
  directional link was not found (F3, F3b). Neither Tom nor Fabio mentions the UTC daily candle (zero corpus hits).
- **"Apply Tom and Fabio books, test on history?"** Tom's opening-range rule: tested, not supported (F5). Fabio:
  his NY-window model (v3: balance -> breakout S5 or failed auction S5D, with order-flow confirmation and a
  defended level) is the sourced version of "sweep, then the real move". It is built and pre-registered; its
  historical run hung (B099, now closed), so there is NO RESULT yet. Rerun it (N2). Price-only definitions failed
  here; order flow is what v3 adds.
- **"Trade the volatility both ways"**: the timing is predictable (F1). A context layer that knows when the US
  open is coming (N3) is supported. A direction rule from these definitions is not.

## 6. BACKTEST FEASIBILITY - FILE MAP

| Need | State | Path | Note |
|---|---|---|---|
| 1m BTCUSDT perp klines + taker-buy vol | ON DISK 2022-01..2026-09-26 | `Dumps/backtest/raw_1m_2022/klines`, `Dumps/backtest/raw/klines` | gitignored; `backtest/bt/bt_data.py` load_klines, cvd_delta, check_gaps |
| Untouched OOS sample | FETCHABLE | `backtest/fetch_binance_archive.py --start 2019-09-01 --end 2021-12-31 --datasets klines --out Dumps/backtest/raw_1m_2019` | USDT-M BTCUSDT archive start date to verify |
| DST-aware session opens | BUILT | `backtest/layers/fabio/v3/day_gates.py` ny_open_utc, london_open_utc, asia_open_utc, us_dst, uk_bst, window_bars, TREND_RATIO | US_CLOSED starts 2024-12-24; the study adds 2022-2024 NYSE closures (NYSE_EXTRA, from memory, VERIFY) |
| Session-sweep descriptive study | BUILT (this session) | `research/session_sweeps/session_open_study.py` | T1-T5 + placebos; descriptive |
| Fabio NY-window model | BUILT, NO RESULT | `backtest/layers/fabio/v3/` signals.py (S1 balance, S2 pressure, S5 breakout, S5D failed_auction, S9 defended_level), models.py, engine.py, manage.py, costs.py; runner `backtest/layers/fabio/run_v3_l3.py`; pre-reg `PRE_REG_FABIO_V3.md` | needs order-flow 1m bars (`orderflow_bars.py`); IS 2024-12-02..2025-12-31, OOS 2026-01-01..06-25 |
| Fabio older session model | BUILT | `backtest/layers/fabio/fabio_of_model.py` (prior-session VA fade/break) | fixed-UTC sessions, no DST (B102) |
| Session momentum (C2) | BUILT | `backtest/layers/session/session_momentum.py`, grid in `backtest/layers/run_t055.py` | fixed-UTC start (B102); superseded by F2 |
| Swing/break/outcome event study | SPEC ONLY | `T058_BROKEN_EXTREMES.md` 3.2-3.6 (F-SW1, F-BRK1, F-OUT1) | candidates; not in FORMULAS.md |
| Tom opening-range rule | RULE TEXT, no code | `extracts/processed/tom/CONSOLIDATED_RULES.md:65-67, :241` | tested as T5 |
| Tom core backtest | BUILT | `backtest/tom_bt.py` (snapshot-driven) | Tom core is not a session model; session logic stays a separate layer |
| OI / funding conditioning | 2025-09+ only | `bt_data.load_metrics`, `load_funding` | last year only |
| NQ/ES for cross-market (Tom T6hDJcHrVBM:13) | NOT ON DISK | - | data decision |
| Stats / verdict | BUILT | `backtest/bt/bt_stats.py`, `ref_pbo.py`, `backtest/verdict.py`, `backtest/fees.py` | for any trade version |

Feasibility: price-only session tests are DONE (this note). Fabio v3 at the NY open is runnable now (new trial
row). The T058 event study needs a FORMULAS.md acceptance step, then a build. The cross-market test is blocked on
data.

## 7. CLOUD AI - ENGAGE OR NOT

**Not needed for this question now.** The deciding evidence is our own backtest (Part I 3e). It ran locally in
30 s on `Dumps/`, which is gitignored and invisible to the cloud: SURFACE_POLICY section 1, CLD = "pushed git
refs only; no LAN, no gitignored files". The literature pass fit one Sonnet subagent.
If the operator wants the follow-up work (N1 OOS replication, N4 T058 build) off the desktop, the named surface is
**CLD - Claude Code cloud (free pool)**, the section 1 row "offline research, specs, reviews, docs, backtests on
committed data". Run one session, Sonnet/medium, Ultracode OFF, at most 1 subagent (section 3b "CC one
deliverable"). It must fetch the Binance archive itself with the committed `fetch_binance_archive.py`.
Under section 1b (App first), the **APP** desktop surface does the same work locally, with the data already here,
and is the recommended choice.
DSA chat is not useful here (no disk, no compute). Outside "deep research" AIs are not MTS surfaces. Their output
would enter as T3, or as REJECT until each citation is opened (Part I 3a).

## 8. NEXT STEPS (proposals; operator decides)

- **N1** Pre-register F6 (late-session low-hold reversion), the F3b "both swept" cell, the Gao form (F9) and
  F2-F5 as frozen definitions. Fetch 2019-09..2021-12 (command in section 6), run once, and give a verdict. T0 script, APP surface.
- **N2** Rerun the Fabio v3 historical test as a new trial row after the B099 fix. It is the only sourced model
  with order-flow conditioning in the NY window.
- **N3** T054 alert proposal: a context-only "US cash open in N min, expected volatility x2-3" line (F1). It never
  gates Tom.
- **N4** T058 event study: accept the F-SW1/F-BRK1/F-OUT1 candidates into FORMULAS.md, build, and add a session tag
  (A/L/O) as a conditioner.
- **N5** NQ/ES intraday data for Tom's cross-market imbalance (T054 step 3); data-source decision.

## DISCARDED (not to be re-researched)

- ICT "Judas swing" / "London sweep" / "kill zones": T3 vocabulary with no quantified source. Their definitions
  are tested as F3/F4 and come out null.
- "First 15 minutes decides the day" applied to BTC: no trader source in the corpus (0 hits for "first 15").
  Tested as F2 and null.
