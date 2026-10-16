# Krown (Krown's Crypto Cave, Eric Krown, @ECKrown) - capture inventory, 2026-10-16

Method: titles, durations and playlist membership from `yt-dlp --flat-playlist` (no content read for the list); 8 caption pilots; existing repo work reused, not redone.
No login, no cookies, no tokens, no paid content, no Discord tooling. Discord was NOT re-read this session (the earlier read-only screen pass stands: #trading-technical-analysis blocked for the operator account).
Files: `VIDEO_LIST.csv` (3,841 rows: id, duration, tab, class, playlists, title), `classify_channel.py`, `enumerate_channel.py`, `vtt_to_timed.py`, `check_quotes.py`, `transcripts/`, `RULES_DRAFT.md`.

## 0. What the repo already holds (not redone)
| Item | Where | State |
|---|---|---|
| TA 101 corpus: 15 transcripts, 15 extracts, 120-rule ledger (99 READY), layer spec v0.2, pre-reg draft | `../krown_ta101_2026-10-13/` | gate G1; next G2 setup catalog (card krown-g2) |
| Daily/weekly majors data for the layer | `../krown_ta101_2026-10-13/DATA_COVERAGE.md` (files on F:/MTS, not git) | done |
| Free-vs-paid triage, 15 newest titles, one CBP transcript (dNlcBehUW9o) with 15 numeric quotes | `options/research/KROWN_FREE_VS_PAID.md` | done 2026-10-09 |
| Discord read | `../imbalance_qriptal_2026-10-16/discord/krown_trades.md` | zero trades; TA channel blocked |
| Candle/event-count work | `../krown_malkan_g3_2026-10-16/` | exists |

**Unblocked today:** the 4 TA 101 videos stuck on HTTP 429 (hNfjyrJEytI, fMRvOt26xcA, LB3DRYxnA0A, _JoJbu_Ug-A) downloaded on the first try with `--write-auto-subs --sub-langs en-orig` (no cookies). Timed transcripts are in `transcripts/ta101_missing4/` (593 / 884 / 142 / 185 caption lines). Extraction (one fresh worker each per PROTOCOL.md s3) is not done here.

## 1. Public source inventory
| Source | What | Count | Access | Teaches |
|---|---|---|---|---|
| YouTube channel UCnwxzpFzZNtLH8NgTeAROFA, Videos tab | uploads, 2018-06 to 2026-10-15 | 3,310 | FREE | all classes below |
| same, Streams tab | live replays (1.5 to 2 hours typical) | 531 | FREE | live chart reading, Q&A, strategy tests |
| 24 playlists | curated series | 24 | FREE | see section 2 |
| Captions | en-orig auto track | 11 of 11 `en-orig` fetches worked (0 blocked); the `en.*` pattern got HTTP 429 on the plain `en` track once, which is why `en-orig` alone is the rule | FREE | text |
| Teachable (krown-trading.teachable.com) | Options 101, TA 101, Long Game free; Bible, Kulti, Quant Prime paid | per FREE_VS_PAID | free tier needs account (not created); paid = out of scope | rules, definitions |
| TradingView indicators (Krown pivots / "Pivot syndicator", Karuku RSI, ribbons, optimism index) | proprietary | n/a | PAID (lifetime sale ends 2026-11-01 per his videos) | the level, pivot and sentiment constructs |
| Discord server | #trading-technical-analysis blocked, #streams only video links, #cave-links one 2018 post | - | BLOCKED / no content | n/a |
| X @KrownCryptoCave, app.krowntrading.net, Twitch | not opened this session; earlier note: x.com 402, app refused | - | UNVERIFIED | n/a |
| Third-party interviews (Cointelegraph, 2 videos) | listed in FREE_VS_PAID s1c | 2 | FREE | options short, buy zone (old) |

Dates: the flat list carries no dates. Sampled every 150th video (newest first): idx0 2026-10-15, 150 2026-02-04, 300 2025-05-25, 450 2024-12-04, 600 2024-06-24, 900 2023-09-06, 1200 2022-11-22, 1650 2022-01-05, 2100 2021-09-10, 2550 2020-10-16, 3000 2019-06-17, 3309 2018-06-02. So about 450 uploads sit in the last 18 months, and the 2018 to 2020 era is the long tail.

## 2. Classes (title/playlist based, `VIDEO_LIST.csv`; hours = sum of listed durations; classifier fixed after an independent audit)
| Class | Videos | Hours | What it is | Value for a layer |
|---|---|---|---|---|
| TEACH_TA101 | 19 listed (18 more hidden by YouTube) | 8 | the TA 101 series | rules; 15 already extracted, 4 transcripts now in hand |
| TEACH_OTHER | 122 | 26 | "New to TA? Start HERE", TA strategies, Psychology, Inside the Machine, Options 101 | rules and definitions; older series overlap TA 101 |
| EVENT_STUDY_STRICT + CALL_LIVE_STRICT | 21 + 4 | 6 + 8 | titles with a hit count / "Within N days" / median / priors, all 2026 | the real event-study setups: the first-priority reads |
| TARGET_TALK + LIVE_TARGET_TALK | 409 + 53 | 140 + 97 | titles with Signal/Setup/Target but no count (includes 2018-2021 "price prediction" commentary and non-BTC) | dated targets and levels; most are NOT event studies |
| LIVE_STREAM | 474 | 860 | other streams | too long to read; sample only |
| COMMENTARY_OTHER | 2,651 | 844 | daily price analysis, weekly wraps, old (2018 to 2021) commentary | dated record of what he said |
| ALTS / QA / SPX_NDX | 45 / 33 / 10 | 17 / 35 / 3 | alt analysis, weekly Q&A, index forecast | ALTS: not our universe yet; QA: rules in answers |
Class sizes are title-regex counts (not content reads); the strict classes are a floor (the audit found about 45 more real event studies with other wording, e.g. "+41% Median After This Rare Cross (8 Priors)"; the regex now catches Median/Priors).
Playlists with the richest dated record: Daily Bitcoin Price Analysis (376, 11 hidden), Long Term Analysis (260), Strategy Development & Breakdown (36), Testing YOUR Strategies - Live (7), Meta Signals (4), Monthly Analysis (9), Trading Psychology (52).
Cautions: titles are changed after upload (key by video_id); classification is by title, so CALL_EVENT_STUDY is an upper bound; 361 of 2,416 stream-playlist entries and 168 of 613 Shorts are hidden/private.

## 3. What the pilot shows (6 videos mined, see RULES_DRAFT.md)
- His current method is **event-study setups**: a named trigger, n prior cases, % green at +1/+2/+3 months, median return (all history and since 2018), converted to a price target and a window. 6 families seen: 10-day and weekly stochastic momentum above 80, golden cross day-path (leg up near day 40), corrective 5/21 EMA cross with the 55 EMA as minimum target, 5-day EMA reconnect bounce, three green weeks/months, death cross with 200 SMA slope filter.
- **Levels** are trending-higher-low pivots per timeframe, 5/21/55 EMA, quarterly 5 EMA, a ribbon mid band (proprietary). Verdicts on closing basis.
- **Odds language:** "% of the time green", "median", "no certainty", "I reserve the right to be wrong". No stop distance, no sizing, no fee/slippage in any setup.
- He refuses macro-print trading (CPI conditional 43% green) and says he has "zero edge" on the Fed.
- His call in the pilot (BTC 90k to 100k by end of October 2026; 12h higher low 80k; invalidation 75k/62k) is post-2026-09-30 and therefore a free out-of-sample record.
- The studies cite BTC history back to 2011/2013; his "since 2018" medians are about half the all-history ones (14.5% vs 18.2%; 23.5% vs 38.7%; ~8% vs 14 to 60%). Any layer must be tested on our own split, not on his numbers.

## 4. Exposure ledger
No price series was read this session. Nothing is added to `EXPOSURE_LEDGER.csv` for Krown (convention: `../imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv`). The numbers in his videos are his claims (T3), not our readings. Reading his dated calls against price later is a ledger event: calls before 2026-07-01 are DEV material, 2026-07-01 to 2026-09-30 is sealed HOLDOUT (do not compare calls to price there), calls after 2026-09-30 are free out-of-sample.

## 5. Ranked reading plan for the full capture (cheap first; transcripts only, no video, no bulk dump)
1. **Extract the 4 recovered TA 101 videos** (unblocks `krown-g2`; 4 workers, 1 video each). Cost: small.
2. **Event-study setup catalogue: the ~25 STRICT titles plus the newest 40 TARGET_TALK titles** (since 2026-07): read titles only to list the families, then 1 transcript per family (about 8 to 10 videos). Output: SETUP_FAMILIES.csv with trigger, n, % green, median, window, venue, all SOURCED. These define the testable events.
3. **Dated calls ledger from post-2026-09-30 videos** (Daily BTC playlist, about 1 per day): log {date, call level/target/window, invalidation}. Forward record only, zero price-reading of sealed windows. Cheapest source of a genuinely out-of-sample test of his judgement.
4. **Strategy Development & Breakdown (36) and Testing YOUR Strategies (7)**: the only place he states entry/exit/stop/size for tested systems. Read 5 titles with BTC and a defined rule first.
5. **Long Term Analysis (260) sample of 10 across 2022 to 2025**: top/bottom calls and their stated reasons (for the tops framework in KR-P01..).
6. **Free tier**: operator enrols in Teachable (Options 101 and TA 101 text). Operator action; a single decision card.
7. **Skip:** ALTS, SPX/NDX, SALES, Shorts, 2018 to 2020 commentary (unless a later ledger shows it is needed), stream replays beyond a 3-video sample. Paid indicators: ask the operator whether to buy lifetime before 2026-11-01 only if pivots/ribbon become the blocker (the pilot says the pivot and the ribbon carry the level map).
Cost guard: transcripts cost about 40k characters each; 25 videos is the whole near-term plan.

## 6. Which layer(s) it could become (constructs only; no edge claim, nothing pre-registered)
Per PROJECT_VISION: layers combine, filter or switch off; fee-net out-of-sample decides.
| Layer | Construct (testable) | Sourced? | Main risk |
|---|---|---|---|
| **K-CTX: higher-timeframe context/veto** | THL (trending higher low) state per 12h/1d/1w, EMA 5/21/55/200 slope and position, closing-basis breaks | sourced: definitions from TA 101; pilot C1/C2/C4 only restate them | lagging; "outranks" undefined for conflicts (OURS rule needed) |
| **K-EVT: event-study setup book** | each family in section 3 as an event with horizon +21/+42/+63 days; test P(green) and median vs his stated; DEV/VAL/HOLDOUT | trigger sourced, parameters (stochastic length, reconnect) OURS | small n per family (13 to 19); overlapping windows (require one event per reset, non-overlapping horizons); multiple-comparison correction across ALL families he tried, not only those shown; his "since 2018" cut was chosen after seeing results (look-ahead): use our own split; a median return says nothing about drawdown, so add a max-adverse-excursion/stop measure; regime decay (post-2018 medians about half) |
| **K-TGT: target and band generator** | median-return arithmetic (A3) and the minimum-target-to-55-EMA rule (B2) as exit/TP inputs for other layers | sourced | targets without stops; a target is not an entry |
| **K-FILT: sweep/false-break filter** | 3 consecutive closes beyond a level to confirm; wick-and-reclaim within 1 to 3 bars = sweep (E1) | rule sourced from one chart example (dzH7m9cQeZA); applying it as a layer filter and the 1 to 3 bar window are OURS | shared with other analysts; value is as a filter for Tom/Fabio/Malkan entries |
| **K-CAL: dated-call ledger (judgement score)** | his stated level/target/window per day, scored forward on post-2026-09-30 data | sourced (his statements) | discretionary; post-2026-09-30 data accrues slowly (about one call a day), so few samples for months |
Order of testing: K-CTX (cheap, daily data already in place) and K-FILT first; K-EVT after the setup catalogue (plan step 2); K-CAL accrues in the background. Prior repo results are not friendly to generic S/R, candle patterns and volume direction (KROWN_LAYER_SPEC s0 item 7), so the likely value is K-CTX/K-FILT as filters, and K-EVT only if a family survives a fee-net multiple-comparison correction.

## 7. Blockers and decisions
- None blocking the next step. Operator-only: Teachable free account (step 6); paid TradingView indicators (only if needed).
- Discord TA channel needs a permission the operator account does not have; the user can check role/permissions manually (not tried: no clicks, no posting).
