# Krown layer audit: where it stands, what it adds, how it feeds the other layers (2026-10-22)

Scope (operator request 2026-10-22): look at the Krown layer end to end: how much work is done, where it sits, its vision; compare what
Krown adds with what MTS needs from it; which layers can take Krown as a confluence input (example: an RSI + Bollinger Band setup);
sample his recent YouTube uploads and his web app; say what should be taken and where it helps. Audit findings included.
Read from `origin/fast-track` at 86949e48 (2026-10-22 16:03 +0530). Labels as in CLAUDE.md: SOURCED (his words + file:line) / OURS.
Nothing here is a result or an edge claim; no price data from VALIDATION or HOLDOUT was read.

Companion files in this folder: `YOUTUBE_SAMPLE.md` (recent uploads, dated-call ledger), `APP_AND_WEB.md` (web app, TradingView,
BBWP formula check).

## 1. Answer in ten lines
1. Krown is a **daily/weekly swing-and-context trader on BTC** (TA 101 corpus) who now publishes **daily event studies**
   (trigger, n priors, % green, median, target, window). MTS trades **intraday (1m-1h) on BTC perps**. So Krown is not a natural
   entry engine for MTS; he is the best-sourced **higher-timeframe context** we have.
2. Work done: ledger of 127 rules from 16 videos, setup catalogue KR-S1..S16 (G2 in substance), v0 detectors S1-S9 with 49 passing tests,
   daily/weekly data with checksums, fire counts, a recall check (FAIL: only 3 of 12 of his examples verify on klines; 0 strict hits),
   EP08 order book + Ep7 liquidation cascades folded in. **No DEV event study has run.** Nothing is wired live (correct for now).
3. Registries lag: `gate_board.json` and STATUS say G1 "next G2", LAYERS.md says "Not built, not backtested". Both are wrong: the
   catalogue (f4a5182a) and detectors (a9e179c7) shipped. See audit A1.
4. **His own confluence stack is the answer to the RSI + BB question.** In hNfjyrJEytI (transcript on disk since 2026-10-16, never
   extracted) he ranks four layers "in order of importance": (1) trend = where/direction, (2) volatility (BBWP) = when, (3) structure =
   how, (4) momentum (RSI) = least important, "absolutely interpreted in the context of the previous three"
   (`krown_capture_2026-10-16/transcripts/ta101_missing4/hNfjyrJEytI_timed.txt` lines 321-350).
   MTS's RSI and BB layers are layer 4 (momentum/location) with nothing above them. Krown supplies layers 1-3.
5. The BB link is direct: **BBWP is a Bollinger-band statistic** (percentile of band width). An intraday BB touch means different things
   in a compressed vs an expanded regime: fade at a volatility extreme (KR-S16 / KR-Q07) vs do not fade the first close outside after a
   compression (KR-S8). That is the single most testable Krown -> BB+RSI hypothesis (H-K1 below).
6. What MTS needs from Krown, in order: (a) a **context read** per bar: daily/weekly trend state, BBWP regime, distance to the nearest
   daily zone and range position (edge vs middle), daily RSI regime, weekly 55 EMA side; (b) a **volatility exit/size rule** (size down as
   BBWP rises, take profit at a BBWP peak); (c) **event-study families** as daily bias tags; (d) a **forward call ledger** to score him.
7. What MTS does NOT need from Krown: more intraday entry setups, his candle-pattern rules alone (repo evidence: no edge), RSI divergence
   alone (no edge on any TF in our tests), his stated hit rates (claims, H-ids only).
8. The seam exists already: `fabio/htf_context_live.py` writes a collection-only HTF JSONL per 4H close and the Supervisor keeps it running
   (f435453c). A `krown_context_live` writer of the same shape (1d/1w state at 00:00 UTC) can tag every alert without gating anything,
   which is exactly the PROJECT_VISION rule "isolate, then combine; read layers annotate, never gate".
9. Highest-value next steps: (1) refresh registries, (2) extract the 4 transcripts already on disk, (3) build the context writer +
   tag join (alerts x Krown state, DEV only), (4) run H-K1..H-K5 conditional tables on existing layer event sets, (5) start the
   forward call ledger. Cards drafted in section 9.
10. Expect small effects. Prior repo evidence for generic S/R, candles, volume direction and RSI divergence is negative; the honest
    hope is that Krown context **removes bad trades** from other layers (a filter), not that it creates trades.

## 2. Where the layer sits (verified on disk and git this turn)

| Stage | Evidence | State |
|---|---|---|
| Extraction TA 101 | 16 extracts, quote and number gates 16/16 PASS (`krown_ta101_2026-10-13/STATE.md`) | done for 16 of 20 public videos |
| Ledger | `KROWN_RULES.csv`: 127 rules (105 READY, 6 BLOCKED, 16 REJECT) + LQC rows from Ep 7 (1abed63b) | done |
| Spec | `KROWN_LAYER_SPEC.md` v0.2 (modules tf/swings/zones/volume/vol_regime/candles/mas/rsi/range/topdown/tops/events) | done |
| G2 catalogue | `KROWN_SETUP_CATALOG.md` KR-S1..S16, 229 quotes, cross-trader overlap table; GPT audit SOUND (2 MED unpatched) | done (registry still says G1) |
| Data | Binance BTC/ETH/BNB/SOL 1d, BTC 1w, Coinbase BTC-USD 1d, checksummed (`DATA_COVERAGE.md`), files on F:/MTS | done (not in git, correct) |
| v0 detectors | `backtest/layers/krown/krown_core.py`, `krown_events.py`, params with SOURCED/OURS labels; `pytest`: **49 passed** (run 2026-10-22 in this container) | done; S10-S16 have no detector |
| Fire counts | `FIRE_COUNTS_BTC_DEV.md`: all S1-S9 under 1 event / 10 daily bars | done |
| Recall | `RECALL.md`: 3 of 12 examples verify on klines, 0 strict hits; card dropped; FAIL recorded honestly | done (FAIL) |
| DEV event study | card `krown-dev-event-study` refined, never claimed | **not started** |
| Daily-video method | `krown_capture_2026-10-16/RULES_DRAFT.md`: 6-video pilot of event-study families | pilot only |
| Live | nothing wired, `enabled: false` | correct |

Work volume: about 22 commits on Krown paths between 2026-10-13 and 2026-10-20 (git log, depth 400). Last code change 15084064 (RSI flat
window 50, consistent with FORMULAS.md s1 step 4).

## 3. The vision for the layer (as written in the repo)
- Spec s0 item 7: "the best role may be a **filter or regime context** for other layers".
- INVENTORY s6 ranks five constructs: K-CTX (HTF context/veto), K-FILT (sweep/false-break filter: 3 closes beyond a level to confirm,
  wick-and-reclaim in 1-3 bars), K-EVT (event-study setup book), K-TGT (median-return targets, 55 EMA minimum target), K-CAL (dated-call
  ledger). Order: K-CTX and K-FILT first, K-EVT after a family catalogue, K-CAL accrues in the background.
- PROJECT_VISION (2026-10-13 direction + 2026-09-28 note): no fixed core; isolate each system, then look for confluences; read layers
  annotate and never gate until evidence says so.
This audit agrees with that vision and makes it concrete: section 5.

## 4. What Krown adds vs what MTS needs

| MTS need (from repo state) | Does Krown supply it? | Krown source | Gap / note |
|---|---|---|---|
| Intraday layers fire with no regime awareness (every live adapter in `live_runner_cli.build_default_registry` emits on its own; `consensus/` is observation-only and not wired) | **YES, best fit.** Trend state, BBWP regime, range mode, top-down agree rule | KR-L10, KR-Q01/Q02, KR-T03/T06/T07, R01 | definitions on 1d/1w only; mapping to 1h/4h is OURS |
| Stop/exit discipline beyond fixed brackets | partial: structural stops (far side of compression zone KR-Q05, close back beyond zone KR-X01), BBWP-peak exit (KR-Q06), size down as volatility rises | KR-Q05, Q06, X01, P02 | no stop distance, no risk per trade anywhere in his corpus |
| A volatility regime for intraday BB/RSI layers | **YES**: BBWP is BB-derived and is his "when" layer | KR-Q01/Q02, hNfjyrJEytI | his settings are for BTC "higher term time frames"; intraday BBWP is OURS |
| Daily levels for intraday trades | yes: wick-to-close zones with >= 2 turns, max 5 ranked, 2x volume flag | KR-Z01..Z18 | LC levels (prior day H/L, POC, round 1000) already cover part; Krown zones are a different object (structural) |
| Event-level bias (days to weeks) | yes: daily event-study families (stochastic > 80, golden cross day-path, 5/21 EMA cross, 5-EMA reconnect, three green weeks) | RULES_DRAFT A1-A6 | n per family 8-19; his stats are claims |
| An independent judge of the market (analyst verdict pipeline, PROJECT_VISION item 5) | yes: one dated call per day with target, window, invalidation | YOUTUBE_SAMPLE.md ledger | accrues slowly; never compare inside sealed windows |
| Order-flow / intraday triggers | no (he is OHLCV daily/weekly) | - | Tom, Fabio, positioning stay the trigger layers |
| Funding/OI regime | thin: Ep 7 "hot funding + stacked OI = cascade weather" (KR-LQC02) | Ep 7 | positioning layer owns the data; Krown gives a sourced reason to use it as a size throttle |

## 5. Wiring: which layers take Krown as a confluence input

Principle (his, SOURCED): momentum "needs to be absolutely interpreted in the context of the previous three" (hNfjyrJEytI 00:10:32-00:10:36).
Principle (MTS, PROJECT_VISION): read layers annotate; a gate only after a DEV/VALIDATION result. So step 1 is always **tag, then
condition, then (maybe) gate**.

### 5.1 The Krown context vector (one row per closed 1d bar; 1w row per Monday 00:00 UTC close)
All fields are already computable from `krown_core.py` except where marked NEW.

| field | values | from |
|---|---|---|
| `trend_1d`, `trend_1w` | up / down / range | `swings` + KR-L10 dominant highs/lows |
| `topdown_agree` | both up / both down / mixed | KR-T03 (1w tide, 1d decide) |
| `bbwp_1d` (+ `bbwp_4h`, `bbwp_1h` NEW, OURS) | 0-100 and regime compression <= 30 / normal / expansion >= 85 | FORMULAS 21.5 |
| `bbwp_dir` | rising / falling over last 3 bars (OURS) | KR-Q05 "ideally falling from a high" |
| `zone_dist_atr` | distance from close to nearest ranked daily zone, in ATR14 units, + side (floor/ceiling) | `zones` |
| `range_pos` | edge-low / middle / edge-high / none | `range` + KR-R01 |
| `rsi_regime_1d`, `rsi_regime_1w` | bull > 60 / range / bear < 40 | KR-S03 (same 40/60 as Malkan) |
| `ema55w_side`, `sma200_1d_side` | above / below | KR-M10, KR-M07 |
| `post_expansion` | true if BBWP_1d >= 85 within last N bars (OURS N) | KR-Q07 "no entry after expansion" |
| `event_tags` | active Krown event-study families (NEW, K-EVT) | RULES_DRAFT, YOUTUBE_SAMPLE |
Point in time: a 1d row exists only after its 00:00 UTC close; an intraday alert at time t joins the **last closed** 1d/1w row (no lookahead).

### 5.2 Layer by layer (live adapters from `alerts/live_runner_cli.py:430-525` + drafts)

| target layer (tf) | what it does | Krown inputs that matter | hypothesis (DEV, conditional table, OURS) |
|---|---|---|---|
| **wlow_bounce `bbrsi60` (1h)**: weekly-low break, bounce, RSI holds under 60 near upper BB | trend_1w, rsi_regime_1d, bbwp_1d, zone_dist (weekly low is a Krown zone candidate) | H-K2: the short works only when trend_1d/1w is down or range and BBWP_1d is not in compression-rising (a breakout regime) |
| **bb_top_reversal (15m)**: green candle into upper BB, red close below its open, short | bbwp (1h/4h, OURS) + range_pos + trend_1d | **H-K1**: fading an upper-band touch pays more when BBWP of the trading tf is >= 85 (volatility extreme, KR-S16) and less/negative when BBWP rose from <= 30 in the last N bars (compression breakout, KR-S8) |
| **MAL-BB-RSI-4060 draft (1m/5m)**: BB mid + RSI 40/60 short in a short-term downtrend | rsi_regime_1d/1w (Malkan's own MTF filter is monthly/weekly RSI < 40: Krown's 40/60 regime is the same object), trend_1d | H-K3: shorts with rsi_regime_1d = bear and trend_1d = down vs the rest |
| **rsi `rsi_events` 40-level (5m/15m/1h)**, **malkan_bull/bear (1h)** | rsi_regime_1d, topdown_agree | H-K3 (same table) |
| **rsi_divergence (1h)**: no edge alone | trend_1d (regular divergence only counter-trend at a zone; hidden divergence with the trend: KR-S14 + MAL-7..9), zone_dist | H-K4: divergence at a ranked daily zone in the trend's direction vs anywhere |
| **levels confluence (1m)**, **session_levels (1m)**, cryptocred sr_flip / failed_msb (1h/15m) | zone_dist (does the intraday level coincide with a Krown daily zone?), range_pos (middle = "no man's land", KR-R01), post_expansion | H-K5: level touches in range_pos = middle underperform edge touches |
| **candle_close (1m)** | KR-Z07 close-is-the-verdict is already its definition; add trend_1d | tag only |
| fabio v3 / escalation / cvd (1m-1h), tom | trend_1d, bbwp_1d, range_pos | tag only; Tom's own TOM-2/TOM-12 balance logic overlaps KR-S3 (catalogue s4) |
| positioning funding_cvd_fade (1h) | KR-LQC02 says hot funding + stacked OI = cascade risk: Krown supplies the reason, positioning supplies the data | size throttle candidate, no test yet |
| risk/exits (auto_trader brackets) | bbwp rising -> size down (KR-P02 spirit), BBWP peak exit (KR-Q06) | H-K6: exit-at-BBWP-peak vs fixed target on the same entries |

### 5.3 Worked example: the operator's RSI + BB short
Setup (MAL-BB-RSI-4060, operator 2026-10-15): 1m BTC, price rejected at the BB mid, RSI rejected near 60 or flows out of 40, short in a
short-term downtrend. Krown adds, without touching the setup:
1. **Where (trend)**: is the 1d/1w trend down or range? Malkan's own primary source says the daily-60 sell is taken only inside monthly
   and weekly RSI < 40 (`extract_2HcJ3NeZmEQ.md:39-58`); Krown's 40/60 regime on 1d/1w is the same filter, already coded (`rsi_zone`).
2. **When (volatility)**: is 1h/4h BBWP rising out of compression (then the lower-band "dance" is a walk, not a bounce: Bollinger rule 8,
   and the 2026-10-15 13:26-13:30 data, four closes outside the band in a row) or at an extreme >= 85 (then fades of the mid work better)?
3. **How (structure)**: is price in the middle of a daily range (no man's land, KR-R01) or just under a ranked daily ceiling zone?
4. **Momentum** = the operator's RSI 40/60 read, now in context.
Output: the same alert, carrying `krown: {trend_1d, bbwp_1h, bbwp_1d, range_pos, zone_dist_atr, rsi_regime_1d}`; after DEV says which
cells pay, a gate may be proposed (VALIDATION once).

## 6. YouTube sample (see `YOUTUBE_SAMPLE.md`)
**Reach (honest):** this cloud container cannot reach youtube.com (proxy refuses the shell; WebFetch gets DNS ENOTFOUND). Two Sonnet
workers got WebSearch snippets only; nothing below was read from a watch page or transcript unless it says "transcript on disk".
- No upload after 2026-10-15 could be listed from here (newest id seen TDQwVve6G3Y, 2026-10-15). Not confirmed empty.
- Snippet-level setups in his newest daily videos (title + snippet, T3 claims): close under 82,692 -> daily 55 EMA target 79,489, "82% within
  10 days, 39 priors" (uFjS2qFEZmE); 5/21 EMA corrective cross -> 55 EMA tested "100%", 88% within 10 days, 16 cases (dQuYp63p5xI);
  55 EMA over 377 EMA, 8 priors, +144% median 12 months (qsPAh6IBNco); three green weeks, 47 priors (AUP1UMotI5w).
- Families listed (YOUTUBE_SAMPLE.md): 10 of them; all but one (CPI-day) need only 1d/1w/1M OHLCV. None needs funding or OI.
- **What to take:** the families are daily bias tags (`event_tags`, 5.1) and a recall set with explicit triggers and n (better than the
  TA 101 captions that failed recall, A5). The 5/21-cross -> "55 EMA is the minimum target" rule is a SOURCED target for K-TGT.
- **What the transcript on disk adds (hNfjyrJEytI 00:16:19-00:19:00, his own worked example of the four layers):** downtrend by lower
  highs/lows; volatility "base out at very low levels"; a lower high "on hidden bearish divergence within the context of a downtrend";
  volatility rises and price continues with the trend; at BBWP "90 percentile ... price action stalls"; a higher low is "a precursor"
  but the reversal is "not confirmed until you get a higher high", i.e. a weekly or daily close back above the last rejection high.
  That is a complete context recipe: divergence is read **with** the trend, low BBWP times the move, high BBWP times the exit.
- Rerun needed on a networked host (JIS-NB/NUC, yt-dlp `--write-auto-subs --sub-langs en-orig`, the method that worked on 2026-10-16):
  the ids in YOUTUBE_SAMPLE.md section 6 ("Next step to finish").

## 7. His web app, TradingView tools, BBWP formula (see `APP_AND_WEB.md`)
**Reach:** WebFetch failed on every host (krowntrading.net, app.krowntrading.net, x.com, tradingview.com, teachable.com: DNS ENOTFOUND).
Snippets only (APP_AND_WEB.md):
- The app is `app.krowntrading.net` ("KROWN TRADING APP 2.0", X account @KrownTradingApp posting daily BTC "market dynamics", e.g.
  hourly leverage financing "Shorts Pay Longs"); a store at /desk/store sells "Quant12". Pages, indicator definitions and series are
  NOT READ: the operator's description (his indicators and values, lots of data) is plausible but unverified from here.
- TradingView: his scripts (Krown Trading RSI, Fibonacci, "The Jewel" = RSI + Stochastics + Fib + DMI) are **invite-only: PROPRIETARY**.
- BBWP: origin is The_Caretaker's open script "Bollinger Band Width Percentile" (he says "type in BBWP", hNfjyrJEytI 00:05:33). A
  secondary guide gives close / SMA / basis 7 / lookback 100, matching FORMULAS.md 21.5 and KR-Q01. Four details are unconfirmed
  against the original (width divided by basis, current bar in window, std multiplier, population vs sample std): audit A8.
- His RSI in the framework video is also a Caretaker script, "not free", used "for divergences" (hNfjyrJEytI 00:10:57-00:11:01).
- **What to take from the app:** only what is public and replicable: if the app shows signal histories (event-study tables with dates),
  those dates become recall examples; funding/OI panels duplicate our positioning data (we already record OI). Proprietary series
  (ribbon, optimism index, pivots) stay out unless the operator decides to buy (lifetime offer ends 2026-11-01 per INVENTORY s1).
- **Operator action (the one thing a cloud session cannot do):** open app.krowntrading.net logged out and send 3-5 screenshots of
  the dashboard and indicator pages via the screenshot intake; a networked host reads the Caretaker BBWP source for A8.

## 8. Audit findings (report -> independent audit -> fix)

| id | severity | finding | evidence | fix |
|---|---|---|---|---|
| A1 | HIGH (planning) | Registries stale: gate_board G1 "next G2", LAYERS.md "Not built, not backtested", STATUS gate line. G2 catalogue + v0 detectors + recall shipped. Planner keeps routing Krown as if nothing exists | `system/gate_board.json:29-34`; LAYERS.md krown status; commits f4a5182a, a9e179c7, 8e5c3647 | advance to G2 (catalogue) with proof KROWN_SETUP_CATALOG.md; rewrite LAYERS status via layer_index.json + make_layers_md.py; regenerate STATUS |
| A2 | HIGH (wasted work) | The 4 "blocked" TA 101 transcripts were **downloaded on 2026-10-16** (`transcripts/ta101_missing4/`, en-orig track) but STATE.md on 10-17 and 10-18 records two more yt-dlp retries "HTTP 429, extraction blocked", and card `krown-ta101-extract-remaining-10` was **dropped**. The KROWN_SETUP_CATALOG s5 still lists them as unread. One of them (hNfjyrJEytI) is his master framework for combining layers | INVENTORY.md s0 "Unblocked today"; STATE.md last two bullets; card state dropped | re-open as a fresh card: extract the 4 files on disk (PROTOCOL.md s3, one worker each), gates, ledger rebuild; fix STATE.md |
| A3 | MED (evidence hygiene) | `KROWN_GAP_AUDIT_2026-10-18.md` (Gemini) describes the 4 videos from "Google Search / YouTube indexing", not from the transcripts on disk. Spot check: the hNfjyrJEytI four-step order (trend, volatility, structure, momentum) **matches** the transcript; its claims about the sponsor-radar titles (H&S needs a 200-day MA break, death-cross filter) are unverified (7CFrrRm5hLw, SOaAP9vBgM4 transcripts on disk are shorts of 1.0-1.4 kB) | `KROWN_GAP_AUDIT_2026-10-18.md` s2; transcript lines 321-350 | label s2 of that file T4 UNVERIFIED until checked against transcripts; never cite it as a source |
| A4 | MED | No live seam for a context read: every live layer emits independently; `consensus/writer.py` is not called anywhere | `consensus/README.md` "nothing calls it yet"; `live_runner_cli.py:430-525` | card K-CTX-1 (section 9) |
| A5 | MED | Recall examples are thin: 3 of 12 verify; the bar of 6 was unreachable by construction | RECALL.md Decision | for K-EVT use his event-study videos (explicit triggers, n, dates) as the recall set, not TA 101 captions |
| A6 | LOW | GPT catalogue audit MED F1 (S3 stop wording) and F2 (S9 60-bar volume) still unpatched | `layer_lab/reports/2026-10-17_krown-catalogue-gpt-audit.md` | patch in the registry card |
| A7 | LOW | `krown_core.rsi` re-implements Wilder RSI instead of importing `rsi/rsi_core.py`; both follow FORMULAS s1 (flat = 50), so no number differs today, but two copies can drift | `krown_core.py:289`; `rsi_core.py:7` | import or a parity test |
| A8 | LOW | BBWP percentile convention (current value excluded, mult 2) is OURS; The_Caretaker's public script is the origin he names ("type in BBWP", hNfjyrJEytI 00:05:33-00:05:38). Check parity before any test | FORMULAS.md 21.5 | see APP_AND_WEB.md s2 |
| A9 | INFO | Holding period mismatch: Krown is days-weeks, MTS live is minutes-hours; Krown entries (S1-S9) cannot feed the testnet auto-trader without a separate daily book | spec s1; live registry | keep Krown as context; daily book only after K-EVT |

## 9. Cards proposed (not filed here; titles + DONE-when)
1. `krown-registry-refresh` (HAIKU, S): gate_board krown -> G2 with proof; LAYERS/STATUS regen; STATE.md corrected (A1, A2); patch F1/F2 (A6).
2. `krown-ta101-extract-missing4-from-disk` (SONNET x4, S each): extract the 4 transcripts in `krown_capture_2026-10-16/transcripts/ta101_missing4/`;
   both gates; ledger rebuild; new family TOP-DOWN ORDER (trend > volatility > structure > momentum) as a SOURCED combination rule.
3. `krown-context-writer` (SONNET, M): `backtest/layers/krown/krown_context.py` (pure: bars -> context row, 5.1) + test with hand numbers;
   DEV backfill to a CSV; later a live writer modelled on `fabio/htf_context_live.py` (collection-only, no gate). DONE: rows for every DEV day, no lookahead test.
4. `krown-context-join-dev` (SONNET, M): join existing DEV event sets (bb_top_reversal, wlow_bounce, rsi_events, malkan, rsi_divergence,
   levels confluence) with the context row at the last closed 1d bar; pre-register H-K1..H-K5 cells first; fee-net; same-window placebo;
   power first. DONE: CONDITIONAL_TABLES.md with n, mean, CI per cell, NO-RECALL-CLEARANCE label.
5. `krown-evt-family-catalogue` (SONNET, M): from YOUTUBE_SAMPLE + RULES_DRAFT, list event-study families with trigger definitions; code
   those that need only OHLCV; recall against the dated examples in his own videos.
6. `krown-call-ledger` (HAIKU, S per week): append his dated post-2026-09-30 calls (target, window, invalidation); score only after the window closes.
7. `krown-dev-event-study` (existing, SONNET): keep, but run after card 4 so the S1-S9 study and the conditional tables share one pre-reg.
