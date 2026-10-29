# Analyst views on BTC, as of 2026-10-29 (digest, no trade advice)

Labels: SOURCED = read in a named file this session; PARAPHRASE = not a verified quote; NOT_IN_DATA = not found. Account data excluded (public repo).
Where the live rows come from: the CBP store `F:/CryptoScrapper/cbp_store/rows.json` (7 rows, stamp last_run 2026-10-28 10:53Z, 5-day window) plus the raw transcript folder `F:/CryptoScrapper/raw_transcripts_canonical/`. Both exist on this host.

## 1. Operator's claim about Habib

**CONFIRMED, from a raw transcript dated 2026-10-27 (not from a CBP row).** Video `hymqmEfCGrw`, Qriptal channel, "Bitcoin: ONE last retest before the dump?!" (SOURCED `raw_transcripts_canonical/hymqmEfCGrw_raw.txt`, header "Published: 2026-10-27", uploader Qriptal).
- Verbatim, caption text: "what I was hoping for was to see a retest near $81,600 to look for a short position there, and then look for further downward continuation."
- Verbatim: "If we move up from here and test $81,000, then that should offer a very easy short position to look for that downward reversal, targeting again the quarterly pivot at $ 78,000."
- Verbatim: "overall, on longer timeframes and for large trades, the best option should be near $73,000."
- Verbatim: "I would expect a continuation of the downward trend."
- Caveat 1: the CBP row for this video was REJECTED by the quote gate (`rows.json` `rejected`: "quote not in transcript: the quarterly pivot at $78,000, which for me is the first ta"). So it is not a verified CBP row; the lines above were read straight from the transcript.
- Caveat 2: the transcript does not name the speaker. Habib = the Qriptal analyst per `research/gemini_burn_2026-10-24/habib_yt_rules.md` header. Nothing newer than 10-27 exists in the transcript folder (checked, newest by mtime).
- Wording: he says the short is a retest of about 81.0-81.6k (a lower-high area under the 85k rejection), not "the top" of the whole move.

## 2. Who is who

| Operator's name | Real name/channel in data | Source |
|---|---|---|
| Tom | Tom (futures auction / order-flow trader; transcripts of DAX and US futures) | `research/TOM_VERBATIM_INDEX.md` |
| Fabio | Fabio (NQ/ES order-flow, "Testable core" from the DSA rulebook) | `backtest/layers/fabio/FABIO_OF_REPORT.md`, `research/fabio_transfer/` |
| Malkan | `@malkansview`, RSI 40-60 | `cbp_v2/analysts.json` (enabled:false) |
| Krown | `@ECKrown` | `cbp_v2/analysts.json` |
| Habib | analyst on `@qriptal` (CBP short name "Qriptal"; the Qriptal row is excluded from the thesis vote) | `cbp_v2/analysts.json`, `habib_yt_rules.md` |
| "Jason" and "Michael" | Jason Pizzino `@JasonPizzinoOfficial`; Michael Pizzino `@MichaelPizzino`. Italian and Australia: NOT_IN_DATA (only the surname and channels are in the repo). Not to be confused with "Michaal" `@michaelvdpoppe`, a different analyst | `cbp_v2/analysts.json`, `research/pizzino_layer_2026-10-27/PLAN.md` |

## 3. Digest per person

| Person | Core rules (one or two lines) | Latest BTC view (date) | Our backtest verdict |
|---|---|---|---|
| Tom | PARAPHRASE: idea, then proof, then risk; trade session extremes of oversized legs and zones (VAH/VAL/POC, prior-day value) when order flow proves absorption or rejection. Verbatim: "Such a finished auction. So, a completed auction, this gives you the overview that the market was done here." (TOM-009, oa8kxSLLkAo) | NOT_IN_DATA (his material is DAX/futures; no BTC call in CBP rows 10-22..10-29) | UNTESTABLE-AS-BUILT; tested encodings dead: TOM-CORE-0929 net -0.30 R, holdout -0.32 R n=254 (`research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` s.1). Order-flow bars start 2024-12, after DEV. Map of what we got right/wrong: `research/tom_btc_2026-10-13/TOM_ON_BTC.md` |
| Fabio | PARAPHRASE (model as simulated, `FABIO_OF_REPORT.md:32-46`): location (VAH/VAL/POC/LVN) then state (balance vs imbalance) then trigger (absorption fade, or aggression bar plus holding retest) then management (stop beyond trigger, BE at +1R, target min(3R, HVN/POC)). | NOT_IN_DATA (trades NQ/ES; no BTC call in CBP) | v3 OOS FAIL n=79 mean -0.1038 R fee-net; L1 CVD absorption / escalation / volume FVG: "no edge" every timeframe (`backtest/layers/fabio/FABIO_L1_REPORT.md`, `R1_EDGE_OR_STOP.md` s.1). OF report: "Keep Fabio context-only" (`FABIO_OF_REPORT.md:142`) |
| Malkan | RSI 40-60 regime: PARAPHRASE of web research (`research/malkan_rsi_2026-09-28/WEB_RESEARCH.md`, no transcript quote): bull trend RSI holds above 40, bear trend capped under 60; daily candle at 40 = buy, at 60 = short; multi-timeframe gate. 0 dated calls in the corpus, so the layer is a HYPOTHESIS (`research/malkan_ledger_2026-10/` Gate 0c). | NOT_IN_DATA (channel disabled in CBP) | DEAD intraday; UNTESTABLE on 1d (2 filled trades in 27 months, mean -1.036 R). RSI divergence 31 of 32 cells net negative (`R1_EDGE_OR_STOP.md` s.1; `backtest/layers/rsi/TEST_PLAN.md` for definitions) |
| Krown | PARAPHRASE: daily/weekly swing and context; his stack ranked trend, then volatility (BBWP), then structure, then RSI least important (`research/krown_audit_2026-10-22/REPORT.md` s.1). 16 setups KR-S1..S16 (zone test, break-close, range edge, coil break, 21/55 EMA context) in `research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md`. Latest style: daily EMA/close-level event studies. | **10-27 BULLISH** (`dLq5Jyir3Iw`, verified): "if you ask me which direction I'm looking, it's still up."; a close below 75,000 "would be, you know, the final nail in the coffin for me". Pointers: daily close above 79,700 means pullback 77.5-78.5k; reclaiming 81,000 = first step to a higher low. **10-27 NEUTRAL** (`zay_owGmjo0`, verified): "I would highly expect a correction to pull the price lower."; 2-day setup target about 77,292 if close below 80,990. 10-24 NO_VIEW (order types lesson, `YAF6fCuVWaI`) | UNTESTABLE-AS-BUILT. Detector recall FAIL 3 of 12, S1-S9 `enabled:false`. Only fee-net 4h result S5: n=35, +0.278 R, 95% -0.161..+0.750 (`R1_EDGE_OR_STOP.md` s.1; fire counts `backtest/layers/krown/FIRE_COUNTS_BTC_DEV.md`) |
| Habib (Qriptal) | PARAPHRASE: a trade needs three pillars: a pre-planned HTF level, a volume-anomaly imbalance candle (30m/1h/4h) with small body and wick, then a rejection reaction; large-body high-volume candle = never fade, join on retest; Monday open trap; stop above the wick (`habib_yt_rules.md` s.1.2, quotes with timestamps there). | **10-27 bearish-leaning** (`hymqmEfCGrw`, raw transcript, see section 1): short on a retest of 81.0-81.6k, target quarterly pivot 78k, larger support about 73k; no long interest. Earlier: 10-22 `c9qf7QJroAE` "the first part of the plan played out perfectly because we got the sweep below that double bottom"; 10-18 Sunday plan: sweep low, push up, "bull trap early in the week", then a drop (`research/habib_plan_imbalance_2026-10-20/README.md`) | His candle faded fee-net: NO EDGE on 30m-1d, all FAIL (`research/VERDICTS.csv`, `research/imbalance_qriptal_2026-10-16/`). His "large body = do not fade" veto is supported (gross -0.10 to -0.42 R). Weekly Sunday plan: n=1, not scorable |
| Jason Pizzino | PARAPHRASE: 50% retracement levels, "overbalance in time and price", and a three-bar signal off a significant turning point (`research/pizzino_layer_2026-10-27/method_jason.md`; verbatim there: "three in a row from a significant turning point which tells you over balance is coming"). | **10-26 BEARISH** (`dH-Y0pxOPD8`, verified): "So I still think prices will go down"; weekly low 79,155 expected to break; "a close below $72,000" with the 200-day MA would start a bear market; 67k = previous double top; resistance 82k then 92 and 98k; long-run range "90-150" | None. Layer only has PLAN, SPEC and method notes; no backtest found (`research/pizzino_layer_2026-10-27/`) |
| Michael Pizzino | PARAPHRASE: 1-bar / 2-bar / 3-bar trend indicator (Gann Swing Pro), 50% levels, retests, pivots (`method_michael.md`). | **10-26 BEARISH** (`E_AP5kudK5Y`, verified): "The bears are clearly in control of the situation now."; wants a break back above about 81,200 plus trend change; support near 78k, major 75k. 10-23 NEUTRAL (`KKnktsvQMyo`): "I expect a decline to 78 thousand, with the main support zone at 75 thousand in mind." | None (same as Jason) |

## 4. Reading across (what the sources say, not what to do)

| Level / theme | Who names it |
|---|---|
| 81.0-81.6k = resistance / retest area | Habib (short area), Michael (50% level about 81.2k), Krown (81,000 reclaim = first step bullish) |
| 78k area | Habib (quarterly pivot target), Michael (midpoint just below 78k), Krown (77.3-78.5k pullback target) |
| 75k | Krown (close below = "nail in the coffin"), Michael (major support), Habib (not named; his larger support is 73k) |
| Direction, 10-26/27 | Bearish: Habib, Jason, Michael. Mixed: Krown (up as base case, near-term correction expected). Tom, Fabio, Malkan: no view in data |

- Quote verification: CBP rows carry `quote_verified: true` from the store's gate; Habib's lines come from the raw transcript and are not gate-checked.
- All views are claims, not signals. No analyst has a scored call count above 0 (56 needed): `research/cbp/SCORECARD_GPT.md` s.2. `consensus` layer only writes observation rows and is not wired live (`backtest/layers/consensus/README.md`).
- WaveTrend (LazyBear, `FORMULAS.md` s.20) and RSI (Wilder, `FORMULAS.md` s.1) are indicators, not a person's rule set here; WaveTrend atlas: DEAD (1h band 53 n=369, -0.158 R; `R1_EDGE_OR_STOP.md` s.1).
- Stale items: CBP store stamp is 2026-10-28 morning, so nothing from 10-28 afternoon to 10-29 is in it.

## 5. Missing

- Tom, Fabio, Malkan: no BTC views dated 10-22..10-29 anywhere in data (Malkan channel disabled in CBP; Tom and Fabio not BTC channels).
- Habib: no CBP row (rejected by quote gate); raw transcript used instead.
- Pizzino brothers: nationality and residence not in data; no backtest.
- `layer_lab/INDEX.md` was not re-read for this digest; verdicts come from `R1_EDGE_OR_STOP.md`, `VERDICTS.csv` and the layer reports named above.
