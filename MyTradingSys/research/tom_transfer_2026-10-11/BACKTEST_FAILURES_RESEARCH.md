# BACKTEST FAILURES RESEARCH: why our layer backtests fail, what a fair test needs (2026-10-11, cloud session, read-only)

Operator ask (chat 2026-10-11, paraphrased): the Tom and Fabio layers are being redefined after the DAX transfer probe
(Tom traded on BTC, not on his home DAX; transcripts extracted without looking at the screen). Think the same way about the
other layers: current state, goal, what backtesting is trying to achieve; look at the backtest failures and the Tom/Fabio
advances; research backtesting failures, so the next research knows what it needs.
Scope: read-only research. No code, no card, no NEXT_SESSION.md change. Inputs: ROADMAP.md, PROBE_PLAN.md, RECALL_DAX.md,
DIAG_BTC.md, PRE_REG_DAX.md, DAX_BT_REPORT.md (smoke), both trade ledgers, BUGS.md, MARKET_GUIDE_RESULTS_2026-10-07.md,
TOM_CORE_BT_REVIEW_2026-09-30.md, PROJECT_VISION.md DIRECTION UPDATE, layer code headers, extracts. Web: search results only (see section 8).

## 0. Answer in brief
1. Every layer has failed the S3 bar so far. Our failures fall into 8 classes (section 2). Only the literature-based,
   BTC-native layers (volume, candles, MA, session momentum, RSI divergence) were tested fairly, so their "no edge" is real.
   The trader-derived layers (Tom, Fabio, Malkan RSI, CryptoCred, FlowHorse positioning) were all tested away from the trader's
   own market, timeframe, exits or data. Their "no edge" mostly measures our encoding, not the trader.
2. Tom/Fabio: the ROADMAP is right, and this pass adds five things it does not cover (section 5). The most urgent: **the DAX
   holdout is contaminated by Tom's own trade ledger**. T3-T6 and T10-T12 (2026-05-12..2026-09-01) sit inside the DAX
   holdout window (2026-04-11..2026-10-09). The spike-fade encoding will be designed from those videos, which show
   the outcomes. Fix this before tom-encode-spike-fade runs (N1).
3. A pass bar of recall >= 4/7 alone can be met by a rule that fires on every opening spike. It needs a precision /
   fire-rate check and ledger trades held back from design (N2).
4. Before any layer backtest, apply one readiness checklist (section 6). It would have stopped most of our wasted runs.

## 1. What backtesting is for here
PROJECT_VISION DIRECTION UPDATE (2026-10-10): stages S1 trustworthy measurements, S2 survive fees, S3 real edge
(walk-forward OOS net R > 0, CI above 0), S4 testnet, S5 go-live. "A core or layer that fails S3 on fixed data is parked,
not tuned into passing." Status: S1-S2 in progress, no source has passed S3.
The 2026-10-11 lesson: a backtest answers "does THIS ENCODING have edge on THIS DATA". It answers "does the trader's method
work" only if (a) the encoding fires where the trader fired (recall), (b) the data carries the inputs the trader reads,
(c) the market, timeframe, session and costs are the ones the method was built for, and (d) exits match how he manages.
None of (a)-(d) was checked before 2026-10-11 for any trader-derived layer.

## 2. Our backtest failures, by class (evidence = repo id)
| # | Class | What went wrong | Evidence |
|---|---|---|---|
| C1 | Encoding fidelity | Coded Tom fired on 0/7 of his own trades; his most common trade (opening spike fade) has no candidate type; live rule 0 signals in 4.7 y vs 19 in an older run | RECALL_DAX.md; B147 |
| C2 | Extraction | Transcript prices and dates wrong (stop "18,258" vs chart 24257); pointing words ("here", "this level") carry the rule; vendor clones taken as source (Fabio 2.0x/0.3 ATR) | RECALL_DAX s1; gap_rules.md (10 of 27 CONTEXT-NEEDED); ANGLE_TRADER_SOURCES L8 |
| C3 | Data mode / missing inputs | Historical mode zeroed trade_flow/book/funding/OI and leaked live fields (look-ahead); book_imbalance 0.0 read as ask-heavy; OI fail-open 0.0; funding silently 0 outside range; DST off by 1 h; htf bal fields null on every row; proof cap 2 on CFD data | B075, B084, B136, B103, B102, B141, ROADMAP F5 |
| C4 | Cost model | Four fee sets for one instrument; no minimum stop width, so median stop is 0.082 % and fees cost ~2.8 R per loss; BTC perp fee term applied to DAX | B081, B146, ROADMAP F3/F6 |
| C5 | Fill model / null | Touch fills on both maker legs; zone not checked to be on the passive side; random-entry null used market entries (not like-for-like); null randomises within the UTC day, not the session; CryptoCred fills on touch and drops signals using a future event | TOM_CORE_BT_REVIEW H2/M1/M2; DIAG_BTC "Null column"; B151 |
| C6 | Exit model | Fixed bracket, 8-bar timeout (unsourced), one trade at a time; the trader's management (re-entry, partials, trailing) is not modelled. 28 % of stopped trades had been +1 R first | tom_bt.py:11-19; DIAG_BTC; ROADMAP F7/F8 |
| C7 | Statistics / protocol | Tom BTC holdout read twice (burned); best-of-18 anchor cell; aggregate verdicts with no regime/session split; HTF cells with n 5-17 reported as "no edge" | B147; t090 RESULT; B154; MARKET_GUIDE row rsi malkan |
| C8 | Market / timeframe transfer | DAX-sized stops on BTC; Fabio NQ order flow on BTC; Malkan's daily/weekly/monthly equity swing method run on BTC 1m-1h with a 10-bar horizon; CryptoCred's daily/weekly swing method run as 15m 1 %/2 %/8-bar brackets | DIAG_BTC; FABIO ledger; rsi_divergence_mtf REPORT; EXIT_POLICIES_REPORT |
C1, C2 and C8 decide whether a test measures the trader at all. C3-C7 decide whether its number can be trusted.
We fixed many C3-C5 items one by one. C1/C2/C8 were never checked before a run until 2026-10-11.

## 3. What outside research says, mapped to our classes
Tier: all items below come from web search results. No page was opened in this session (WebFetch to quantpedia.com failed
with DNS; the 2026-09-30 ANGLE pass hit EGRESS_BLOCKED). The named academic papers are standard references, known
from background knowledge. Treat them as method guidance, not as evidence for any BTC rule.
| Class | Finding | Use for us |
|---|---|---|
| C7 | PBO via combinatorially symmetric cross-validation (Bailey, Borwein, Lopez de Prado, Zhu, J. Comp. Finance) estimates how often the in-sample best config falls in the bottom half out of sample; plain hold-out is called unreliable for strategy selection. Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014, JPM) corrects for the number of trials and non-normal returns | Already in our tooling (PBO_019, DSR in tom-probe-prereg). Gap: trial count must include every arm, extension shift and recall iteration (N2), or DSR is inflated |
| C7 | White's Reality Check is conservative and loses power when many poor rules are included; Hansen's SPA is more powerful and less sensitive to them (Hansen 2005; Hsu & Kuan 2005) | Volume research used RC max-T over 216 trials. For a wide arm grid, SPA (or stepwise SPA) is the better test. Don't pad grids with junk arms |
| C7/C8 | Brock-Lakonishok-LeBaron rules re-tested on the next 10 years of DJIA: the best rule was insignificant before costs (Sullivan, Timmermann, White 1999). Hsu & Kuan 2005 find profitable rules in "young" markets (NASDAQ, Russell 2000) but not in mature ones | Edge is market- and period-specific. A rule found in one market or period is a hypothesis elsewhere, so transfer needs its own pre-registered test. No search found a study that selects rules in one market and tests them in another: we are on our own for the transfer design |
| C5 | Fill rules: fill on touch overstates results, fill on trade-through understates them, and a queue model sits between. Practitioner reports say trade-through is close to live on liquid futures | Run every limit-entry backtest twice (touch and trade-through) and report both. A result that holds only on touch fills is not a result. Tom/Fabio entries are limits at levels, so this applies to them first |
| C3 | CFD/cash-index "volume" is tick or feed volume, not exchange contract volume; delta on a CFD can move differently from the matching futures delta; the usual fix is to take volume from the matching futures contract | Tom's DAX proofs that read volume (profile shape P/b, POC, low-volume nodes) are computed from Dukascopy feed volume. See N3 |
| C6/C4 | Stop-out probability rises steeply with volatility for a fixed stop width; stop effects depend on sampling frequency; intraday edges of a few bp vanish after costs | Matches B146/F6: a stop is only meaningful in units of the instrument's noise. The BTC transfer rule must be stated in noise/ATR units and fee-as-share-of-R, not in Tom's points |
| Selection (Q) | Quantpedia summary of a 2024 study (unopened): a discretionary trader overriding a non-profitable systematic strategy picked ~18 % of signals and made it profitable | A lead, not evidence. It supports keeping Q (selection) in the v2 spec even though the BTC diagnostic was SKIP: that test lacked the features Tom selects on (market state, day type). See N6 |
| C8 (session) | BTC intraday patterns exist (volume rises through the GMT day; Quantpedia hourly study: weakest 03-04 UTC, strongest 22-23 UTC, one exchange, not peer-reviewed, costs unclear) | Weak and sample-specific. Consistent with our S = SKIP. It gives no BTC equivalent of Tom's 09:00 CET or Fabio's NY cash open, so any session mapping stays NO-SOURCE |

## 4. Layer by layer: home market vs what we tested
| Layer | Source and home | What we tested | Fit | Verdict on record | What a fair test needs |
|---|---|---|---|---|---|
| Tom (core) | Tom Vorwald, FDAX (also ES, GC), pre-market/open, stops 20-63 pt (0.08-0.26 %), managed trades | BTC perp 24/7, 15-min cadence, fixed bracket; now DAX CFD (smoke only) | Poor (being fixed) | No edge on BTC; 0/7 recall on DAX | ROADMAP + N1-N3 below |
| Fabio (core) | Fabio Valentini, NQ/ES futures, NY session, order flow, stops 3.4-15.75 NQ pt (0.014-0.061 %) | BTC 4 models (v3), cvd_absorption/escalation/volume_fvg on BTC | Poor | L3-FAIL (C: OOS -0.10 R; A/B/D 0 trades); lift ~1.0 | N4 below; home test needs NQ trade data with aggressor side |
| RSI / Malkan | Vishal Malkan, Indian equities (Nifty universe), daily/weekly/monthly RSI regimes, swing | BTC 1m..1d events, 10-bar horizon; malkan_40_60 at 1h/4h/1d | Poor: wrong market, timeframe and horizon | NO-EDGE intraday; 4h n 17, 1d n 5 | His own timeframes (D/W/M), his horizon, and a universe of assets to get N (he applies it across many stocks). BTC alone gives ~57 monthly bars since 2022: underpowered. "n 5" is no evidence either way |
| CryptoCred | CryptoCred, crypto (BTC/ETH), daily/weekly swing and position, stop = invalidation, soft stops for swing, no break-even | 15m failed_msb / sr_flip / fib_pullback, brackets 1 %/2 %/8 bars and ATR brackets, 0.1 % buffer NO-SOURCE | Market right; timeframe and exits wrong | NO-EDGE | Daily/4h structure, his invalidation stop, his targets (1.5R is CC Rule 9), trade-through fills; this is the one trader layer whose home market is BTC |
| Positioning (FlowHorse / whale) | FlowHorse extracts (crypto positioning); thresholds UNDEFINED in source (grid) | funding_cvd_fade grid | Source too thin | NO-EDGE (OOS -0.045 %) | A sourced threshold, or label the layer a NO-SOURCE research test (VISION exception 2) |
| Session momentum | Shen, Urquhart, Wang 2022 (BTC, academic) | BTC, DST-aware gates (B102 fixed) | Good | NO-EDGE (Sharpe 0.008) | Genuine negative; park |
| Volume, candles, MA, RSI divergence, OI | Literature / operator ideas, BTC-native | Pre-registered, RC-corrected, VALIDATION sealed | Good | 0 survivors (volume: 553 trials; candles: 0/108) | Genuine negatives; park. The holdouts are still sealed: keep them sealed |
| Turn of candle | own | timer | n/a | excluded (no gross edge) | none |
| Tick, timeframe, consensus, alerts | infrastructure (data tiers, resample gate, observation writer) | correctness tests | n/a | not edge layers | correctness only |
Reading: the fair tests (bottom rows) give real negatives. The unfair ones (top four rows) give negatives that say little.
They match the 2026-10-11 Tom finding: test the trader where he trades before asking whether it transfers.

## 5. New findings for the Tom/Fabio redefinition (not in ROADMAP.md)
N1. **DAX holdout contaminated by the trade ledger (HIGH).** PRE_REG_DAX: holdout = 2026-04-11..2026-10-09, kept clean because
"recall reads no outcomes". But TOM_TRADE_LEDGER holds T3/T3b (05-12), T4 (05-18), T5 (05-19), T6 (06-02), T10 (06-08),
T12 (07-14), T11 (09-01), all in the holdout. The videos show the outcomes, and tom-encode-spike-fade designs the setup from
exactly these frames. A holdout backtest then re-scores days the rule was shaped on. Options: (a) drop each ledger day +-1
trading day from the holdout and report how many were dropped; (b) add a forward holdout from 2026-10-10 on (Dukascopy keeps
publishing), read once at >= 100 trades; (c) both. Default (c). This must be decided in tom-layer-v2-cost, before tom-encode-spike-fade.
N2. **Recall alone is not a pass bar.** A spike-fade rule that fires on every opening spike reaches 4/7 trivially. Add:
(i) fire rate: signals per DAX day across dev, compared with Tom's stated frequency, or reported as NO-SOURCE if he never
states one; (ii) design/check split of the ledger: encode from about 2/3 of the ledger, measure recall on the held-back 1/3,
once; (iii) count every recall iteration as a trial in TRIAL_REGISTRY. Without these, recall itself overfits 7 points.
N3. **Volume truth on DAX.** The spike-fade proofs (profile shape P/b, POC, low-volume node, "no liquidity above") read the
volume distribution. Dukascopy DEUIDXEUR volume is the feed's own unit, not Eurex FDAX contracts (PRE_REG_DAX "Data"). Cheap
check before encoding: compare the engine's session POC/VAH/VAL from Dukascopy with the POC/VAH lines Tom draws on the ledger
frames (a profile-parity check, like the snapshot-close check). If they do not match, volume-based proofs are
NOT_IN_DATA on this feed. Then either buy FDAX volume (an operator cost decision) or encode only the price-shape proofs (inside bar, ledge of old highs, spike).
N4. **Fabio's transfer is harder than Tom's, and his ledger cannot be replayed yet.** (i) His stops are 0.014-0.061 % of price,
tighter than Tom's, so the fee/noise problem on BTC perps is worse. (ii) BTC does carry an aggressor side (Binance aggTrades),
so order-flow proofs are testable on BTC (unlike DAX CFD); what has no BTC analogue is the NY cash open / initial balance.
(iii) Of 65 ledger rows (18 entries, ~all NQ), dates are mostly month-only or "unknown": a recall test needs minute timestamps
from frame clocks, the same way Tom's were read. Add "minute timestamp from a frame" to fabio-trade-ledger DONE-when.
(iv) A home-market test needs NQ trades with aggressor side (CME). No free source is known in the repo, so this is an operator
cost decision for fabio-layer-v2-markets.
N5. **Management GO is measured on noise-level stops.** DIAG_BTC's 40 %/28 % MFE figures come from 0.084 % stops, with a 4 h MAE
median of 5.7 R. Re-measure MFE after the stop-width transfer rule exists. Otherwise the M arms (break-even, partial, trail) will
be tuned to noise. Note: CryptoCred calls break-even stops "psychological cope" (extract_XeQV2ECtZVQ L151), so an M arm is
per trader, never global.
N6. **Selection needs the features in the snapshot.** Q was SKIP because rows carry no market state, day type or HTF bias. Tom
selects on exactly these (conditions/market_state_rules.md). v2 should write them into each snapshot so a later Q test is possible.
N7. **Null must be session-matched for session traders.** DIAG_BTC's null randomises the time within the UTC day. Tom (open/
pre-market) and Fabio (NY open) trade session structure, so the null must draw from the same session window and use the same
limit/ran/no-fill mechanics (TOM_CORE_BT_REVIEW H2).
N8. **Video trades are selected trades.** Teaching videos show chosen moments, so the ledger cannot tell us trade frequency or
the share of losers. Fabio's ledger does include stopped trades (F12-F14), which is good. Frequency stays NO-SOURCE unless
he states it, and "max N per day" (Q5) stays NO-SOURCE too.

## 6. Backtest readiness checklist (proposed gate before any layer backtest)
A run is not started until each line has an answer in its pre-registration:
1. Source home: market, timeframe, session, holding period (with quote + file:line).
2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.
3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.
4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).
5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).
6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).
7. Fills: touch AND trade-through reported; the entry is on the passive side of price.
8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).
9. Null like-for-like: same session window, same order type, same fill rules.
10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".
11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.
12. Stratified readout by regime and session (B154) next to the pooled number.

## 7. What to do (proposals, ordered; no card created here)
- Now, inside the existing Opus cards (ROADMAP Q4/Q5): put N1, N2, N3 into tom-layer-v2-cost, and N4, N7 into
  fabio-layer-v2-markets. Add "minute timestamp from frame" to fabio-trade-ledger DONE-when (N4 iii).
- Before tom-encode-spike-fade: the profile-parity check (N3) is a small Sonnet job on frames + dax_archive.
- Keep ROADMAP's STOP list as is. This research adds no new layer and no BTC rerun.
- After Tom/Fabio v2 (not before): one "home-fit audit" card per trader layer (Malkan, CryptoCred, positioning) using the
  section 6 checklist. CryptoCred first: it is the only trader layer whose home market is BTC, so it needs no transfer, only
  his timeframe and his exits.
- Keep the literature layers parked. Their negatives are honest, and their sealed holdouts should stay sealed.
- Adopt section 6 as the pre-registration template (alongside PRE_REG_DAX.md) once the operator agrees.

## 8. Sources (web search results; no page opened in this session)
- Bailey, Borwein, Lopez de Prado, Zhu, The Probability of Backtest Overfitting: https://papers.ssrn.com/abstract=2326253 ; free copy https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf ; CRAN pbo: https://ftp.fau.de/cran/web/packages/pbo/vignettes/pbo.html
- Bailey, Lopez de Prado, The Deflated Sharpe Ratio: https://papers.ssrn.com/abstract=2460551
- Hsu & Kuan 2005, Re-examining technical analysis with White's RC and Hansen's SPA: https://ideas.repec.org/a/oup/jfinec/v3y2005i4p606-628.html ; review incl. Sullivan-Timmermann-White replication: https://repository.essex.ac.uk/18805/1/1-s2.0-S1057521916301958-main.pdf
- Fill models: https://nautilustrader.io/docs/nightly/concepts/backtesting/fill-models/ ; https://www.mintlify.com/nkaz001/hftbacktest/concepts/queue-position ; https://www.quantconnect.com/forum/discussion/11944/how-to-simulate-queuing-and-latency-on-limit-orders-with-tick-data/ ; https://elitetrader.com/et/threads/limit-order-fills.253428/ ; https://llmquant.substack.com/p/why-your-perfect-limit-order-never
- Tick vs real volume, CFD vs futures: https://tradingwyckoff.com/en/tick-volume-vs-real-volume/ ; https://www.tradingview.com/chart/EURUSD/7ah80iiY-The-Value-of-Comparing-Futures-and-CFD-Data ; https://www.mql5.com/en/forum/453534/49147809
- Stops vs volatility and costs: https://www.actuaries.org.uk/documents/stop-loss-and-investment-returns ; https://arxiv.org/pdf/1411.5062 ; https://arxiv.org/pdf/1005.3535
- Discretion as selection (lead, unopened): https://quantpedia.com/combining-discretionary-and-algorithmic-trading/
- BTC intraday: https://researchportal.hw.ac.uk/en/publications/the-intraday-dynamics-of-bitcoin/ ; https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/
