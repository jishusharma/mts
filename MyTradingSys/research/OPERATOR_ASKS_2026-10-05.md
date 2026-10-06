# OPERATOR ASKS 2026-10-05 (5m CoinGlass chart, ~14:55Z): cross-check, answers, task plan

Session: MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Master doc for asks 1-5 below; each ask has its own item
(B136, T063-T067). Read this doc first; it is the work order. Earlier context: MARKET_ANALYSIS_2026-10-05.md (G1-G15),
TOM_FABIO_STORY_2026-10-05.md (M1-M9).

## 0. Verbatim asks (operator, 2026-10-05, with a CoinGlass 5m BTCUSDT screenshot: VWAP, OI candles, CVD candles, Net Delta)

> look what market did - It went up - took out the local highs and then came down but it has not taken out the low yet
> (Horizontal ray) - maybe it will take it out - maybe not - This is also one of many things MTS perhaps need to understand.
>
> 1. I have noticed that when BTC needs to break out of a trend in either direction, then it takes out the local high or low
> in the opposite end and then continues n it's direction. For a 1 min candle (not sure how Claude can apply this to higher
> time-frames), this is particularly visible in OI, CVD and Net Delta indicators -> Comparative to adjacent values, a higher
> magnitude OI drop is visible as price and cvd moves together in the opposite direction. In my understanding it signifies
> stops and ppl coming out of their positions. Perhaps this is what market does - it lets the positions build in the opposite
> direction without taking out the recent pivots of local highs and lows until it does take out those stops and then change
> direction! What is noticeable that these drops in OI in the mentioned condition happen almost every time and then price
> starts to move in the opposite direction. If the push is very strong it can be different than what i am explaining (i am
> not sure, we need to gauge/check) but usually this happens. BUT it is not clear how far back after the price but retract
> and then snap back. This needs to understood from Tom's and Fabio's eyes!
> 2. We have found the Tom and Fabio concepts like Absorption, Distribution etc - My question is - these happen in every time
> frame to so how do when know which ones we have to pick for our trades? Is there a concept of confirmations on which the
> trade entry must be chosen?
> 3. Do a research on LazyBear (https://in.tradingview.com/u/LazyBear/) indicators/ideas that are highly rated and directly
> compliments MTS. What can we add that is worth trying???
> 4. I have some charts in tradingview account that i can share with Calude. No API - just usual account with free
> subscriptions, only meant for reading charts and indicators. I think we can have the source code and make our own
> indicators instead of relying on external source but at the same time we need keep the ROI in mind and use what we can
> for quick wins. So the goal is for you to read my charts as accurately as possible. I have a long term and short term
> charts with my ideas. MTS will need those! So we need a module for this. "My charts" seems nice. This is different from
> the time when i pasted screenshots that were read immediately inside the session using the image reading protocols.
> Instead - these charts are my own that i keep on this trading view account that i can happily share with you if needed.
> 5. How can we improve our alerts? -> Buy detection can be researched
>
> PS - You need to compile all of this and make it stick so that nothing is lost and we are working on these lines.
> I need you to prepare a complete task list of what is pending and what should be done in order/sequentally/on Cloud
> (that i can run in Cloud Mode Wn App NUC to use my credits with awgp a/c) and on Desktop Claude Win APP (this
> gmail-claude a/c that i am using now)

Operator caveat (kept): the observations are assumptions to be tested, not rules.

## 1. Chart vs MTS cross-check (14:00-14:55Z)

Sources: chart = operator screenshot; LOG = `runtime/orderflow_live/2026-10-05.csv` (1m); SNAP = `runtime_data/snapshots/`
(latest 14:57Z); BINANCE = public `fapi.binance.com/futures/data/openInterestHist` 5m (read-only fetch, this session).

| Item | Chart | MTS | Verdict |
|---|---|---|---|
| Last 5m bar 14:50 O/H/L | 85,645.3 / 85,664.1 / 85,440.0 | LOG 14:50-14:54: 85,645.3 / 85,664.1 / 85,440.0 | MATCH |
| Session high | ~86,680 (14:0x) | LOG 14:09 h 86,683.9 | MATCH |
| Flush low | ~85,400 | LOG 14:34 l 85,400.1 | MATCH |
| Horizontal ray (green) | 85,369.0 | 4h swing low 85,369 (MA section 7) | MATCH, not taken (31 pts short) |
| CVD drop in the flush | ~+1.3K -> -1.9K (about -3.2K) | LOG cvd_day 14:29 213.6 -> 14:34 -2,849.4 (-3,063) | MATCH (anchors differ, size agrees) |
| OI | 97.4K -> 96.1K | BINANCE 14:30 97,319 -> 14:40 96,211 (-1,108 BTC, -1.1% in 10 min) | chart correct |
| OI in MTS | | SNAP open_interest change_1h_pct **0.0, flat, every snapshot 10-03..10-05 (3,338 of 3,338)** | **MTS WRONG -> B136** |
| Sweep flag | high swept 14:09, low probed 14:34 | SNAP session.liquidity_sweep_direction = none | gap (G12/T063) |

**B136 (P0, found here):** `src/main/java/datafeed/BinanceClient.java:43,47,51,66,71` call `/futures/runtime_data/...`;
the real path is `/futures/data/...`. Broken since acca1d0 (2026-09-24, folder flatten find/replace `data/` ->
`runtime_data/`). The exception is swallowed, OI reads flat, and confidence stays HIGH (fail-open). Dead for 11 days:
OI direction/delta_state, global + top long/short ratios, taker buy/sell vol. This is the root cause of MA G5
(oi_breakdown unavailable), and every OI-based read since 09-24 (delta_state, quad classify, positioning, Tom proof
items that use OI) ran on a constant. Testnet results 09-24..fix are tainted for OI-dependent logic.

Tape read of the move (data, no forecast):
- 13:31 sweep under 85,787 (weekly/prior-day VAL), back inside in 1 min (MA section 7). Up from there.
- 13:50-14:30 OI rose 96,736 -> 97,319 (+583) while price poked above the 08Z high (86,463) to 86,684 (14:07-14:08 delta
  +564). Rising OI on the poke means **new longs opened on the breakout**, not shorts covering.
- 14:09-14:29: price stalled 86,2xx-86,68x with mostly negative 1m delta = effort without result at the new high.
- 14:30-14:34 flush: OI -1,108 BTC, delta -3,063 BTC in 5 bars, b999 sell prints 3+4+4+13+13. Price, CVD and OI fell
  together = **trapped breakout longs exiting** (stops/liquidations), which matches ask 1's signature exactly.
- 14:35-14:37: delta +541 while price held 85,400-85,520 (absorption at the low). OI kept sinking slowly
  (96,211 -> 96,087): no new shorts piling in after the flush. 85,369 not taken at 14:55.
- The engine missed the 13:31 reclaim long and showed nothing on the flush. Its OI input was a constant, and its zone
  touch uses sampled price (G12).

## 2. Answers so far (analyst, sourced where marked; full work in the items)

**Ask 1 (T063).** The signature you describe is the price/OI/CVD quadrant. Price down + CVD down + OI **down** = positions
closing (long stops/liquidations): forced, finite, and often exhausting. Price down + CVD down + OI **up** = new shorts
opening (initiative), which tends to continue. Today's sequence was a "trap then flush": the opposite extreme was taken
with OI rising (new positions), the move failed (effort without result), then OI collapsed as price and CVD moved
together the other way. Corpus so far: Tom rejects "stop hunting" as intent (RwQBdF9TSvc:13, T058). Fabio's "book
sweeping" at session highs (FawPrRUGNpk:249-260) and "big trades get stopped out" (FR-15) are the sourced handles. A
prior MTS study (BTC_SESSION_SWEEPS_2026-10-04 F3/F4) found no directional edge in plain sweeps at session levels. So the
OI flush is the new, untested ingredient. How far price retraces before it snaps back is not answered anywhere yet.
T063 measures it in ATR and against value-area/node locations (Tom: next volume node; Fabio: next liquidity cluster).
Parameters stay research-only until a trader quote or the event study supports them (provenance rule). If it holds up,
it becomes an [OPERATOR] layer, never a Tom filter.

**Ask 2 (T064).** Both traders answer "which absorption" by **location first, then proof**. Tom: the higher-timeframe
volume profile (weekly/daily value areas, nodes) picks the zone. Absorption or distribution only counts when it shows
**at that zone**. Then the math (R:R) must pass (Idea + Proof + Math, story chapter 5). Fabio: context
(balance/imbalance) -> location (value-area edge / LVN) -> aggression trigger in order flow; "volume plus price
confirmation" (FR-11) and CVD absorption confirming a failed auction (FR-19). The confirmation concept exists, but its
thresholds are UNDEFINED in the rulebook (FR-11, FR-55 "higher time frame"). T064 extracts the verbatim quotes on
timeframe choice and confirmation so MTS can encode "zone TF vs trigger TF" with a source.

**Ask 3 (T065).** Web survey of LazyBear's most-used scripts (T3 practitioner tier), mapped to MTS gaps, with a port cost
per script. WaveTrend is already T061. Shortlist of 5 or fewer, each a separate switchable layer.

**Ask 4 (T066 "My charts").** No API, free account. Recommended route: Claude in Chrome (your logged-in Chrome,
read-only) opens each shared layout. It reads drawings from the Object Tree panel and each drawing's settings (exact
prices), plus indicator names and inputs, and writes `MyTradingSys/my_charts/<layout>_<date>.json` and a short .md
(levels, lines, notes, TF, long/short-term tag). Screenshots serve as backup evidence. Tag = [OPERATOR]: your ideas are
their own layer. Quick win first: read and record. Port Pine source only for open-source indicators worth it (ROI rule).
Claude never signs in or changes the account.

**Ask 5 (T067).** Improve alerts in three ways: (a) fix inputs first (B136 OI; G12 zone touch on 1m high/low; G2 feed
watchdog); (b) add event alerts for the T063 signature (sweep of a pivot + OI flush + CVD in step) and for absorption at
a marked zone; (c) "Buy detection": read as detecting large aggressive buying (b99/b999 buy tiers already logged per
minute, plus OI up = new longs vs OI down = short covering). Operator to confirm this reading (it could also mean bot
detection).

## 3. TASK LIST (in order). D = Desktop App (gmail account, this machine). C = Cloud (awgp account, offline, pushed refs).

Cloud sees only pushed commits. The operator pushes `fast-track` after this commit (sessions never push).
Live-path rule for every D item touching execution/, layers/alerts/ or the Java producer: stage .new / build only, the
supervisor rebuilds and restarts after gates.

| # | Where | Item | Task | Blocks | Done when |
|---|---|---|---|---|---|
| 1 | D (SUP) | B136 | Fix 5 BinanceClient paths; fail-closed (`confidence UNAVAILABLE` when OI fetch fails, never HIGH on a default); test: mocked 404 -> not HIGH, real JSON -> change_1h_pct computed; Maven gate; rebuild + restart producer | 2, 5, 7, 11 | SNAP OI non-zero and matches BINANCE within 0.05% |
| 2 | D (T0) | B136 | List consumers of open_interest/oi_breakdown; mark 09-24..fix testnet rows OI-tainted in TESTNET_STATUS | 11 | taint note committed |
| 3 | D (T0) | T063 | 1m OI recorder (`/fapi/v1/openInterest` each minute -> `runtime/oi_live/YYYY-MM-DD.csv`) + backfill 30 d of 5m openInterestHist; commit data | 7 | csv files growing, backfill committed |
| 4 | D | G6/M9 | DST-aware US-open anchor **before 2026-11-01** (MA section 6 P0) | - | test for 13:30Z/14:30Z switch passes |
| 5 | D | G2/G3/G4/G15 | Feed watchdog + HTF writer restart + 1D structure refresh + daily kline refresh job | - | MA section 6 P0 rows closed |
| 6 | D | G12 | Zone touch uses 1m bar high/low, not sampled last price | 10 | replay of 13:31Z sweep shows the touch |
| 7 | C | T063 | Event study: pivot sweep + OI flush + CVD-in-step, TFs 1m/5m/15m/1h; outcome reversal vs continuation; retrace depth (ATR, VA/node) before snap-back; strong-push exception | 10 | report + pre-registered rule candidates committed |
| 8 | C | T064 | Corpus extraction: Tom + Fabio quotes on timeframe choice, confirmation, stop runs, retrace depth; `verify_extract_quotes.py` passes | 7 (read), 10 | extract committed, gate green |
| 9 | C | T065 | LazyBear survey (playbook Part I), shortlist of 5 or fewer with Pine source links, port cost, MTS gap each fills | - | report committed |
| 10 | C | T067 | Alert improvement spec: input fixes, T063 event alert, zone-absorption alert, buy-aggression detector (after operator confirms meaning); tests from spec | after 6-8 | spec + tests committed |
| 11 | C | G1/M1/M2 | Replay 10-04/05 with "next node beyond nearest" targets and sourced R:R floor (MA P1) | after 1 | replay report |
| 12 | D | T066 | My charts pilot: operator names 1 long-term + 1 short-term layout, logged in to Chrome; Claude in Chrome reads -> json/md; operator checks accuracy | - | pilot files match the operator's chart |
| 13 | D (SUP) | all | Gate and merge cloud branches, log in SUPERVISOR_LOG, wire accepted layers as switchable modules | after 7-11 | merged + gated |

Can start now in parallel: 1, 3, 4 (D); 8, 9 (C). Item 7 starts after item 3's backfill is pushed (or fetches public
5m OI itself, read-only).

Operator actions: (a) push fast-track after this commit; (b) start Cloud sessions with the prompts in CLOUD_INBOX.md;
(c) confirm "buy detection" meaning; (d) for item 12, name the layouts and be logged in to TradingView in Chrome.
