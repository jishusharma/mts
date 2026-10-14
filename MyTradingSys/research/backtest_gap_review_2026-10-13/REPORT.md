# Backtest and extraction gap review: are we backtesting correctly? (2026-10-13, cloud session)

Operator ask (chat 2026-10-13, paraphrased): sync to the latest code, look at the latest extraction and backtest changes, find
the crucial gaps, compare our method with published BTC/Binance backtesting studies and methods, and say whether we are going
in the right direction.
Scope: read-only review, one deliverable file. No code, card or NEXT_SESSION.md change. Base: origin/fast-track 38c45bd2.
Reads: STATUS.md, LESSONS_DIGEST.md, LAYERS.md, PROJECT_VISION DIRECTION UPDATE, GO_LIVE_BAR.md, PRE_REG_TEMPLATE.md,
BACKTEST_FAILURES_RESEARCH.md, TOM_LAYER_V2_SPEC.md, PRE_REG_DAX.md, AUDIT_MAJOR_GAPS_2026-10-09.md, published_strats and
mfe_exit reports, fees.py, tom_bt.py, tom_dax_bt.py, dax_data.py, fetch_binance_archive.py, extraction.md, playbook Part I.
Labels: [checked] = re-read or recomputed in this session. [estimate] = my number, not measured. [search] = web search
result only, page not opened (cloud egress blocks WebFetch and the proxy refuses arxiv, dukascopy and deribit hosts).

## 0. Answer in brief
1. **Method: right direction.** Pre-registration before outcomes, placebo and random-entry nulls, Benjamini-Hochberg/Holm,
   sealed holdouts, fee + funding net results, trial registries, provenance for every parameter, recall with fire rate and a
   random-clock control, session-matched nulls. This is stricter than most published BTC technical-analysis papers (several
   report no costs at all). Keep it.
2. **But five gaps can make a verdict wrong, and four of them sit in front of the next big run (the Tom v2 DAX dev run):**
   - G1 **Power.** The pass bars cannot detect the edge they test for. At Tom's own stated numbers (hit rate 40-45 %, R:R 1.5-2)
     the frozen DAX bar has 7-35 % power at 100-150 trades, and "FAIL on dev = stop" makes that miss final. [checked]
   - G2 **Bid/ask.** The DAX harness reads bid-only candles. Family A is short-only, so every exit is a buy that should execute
     at the ask. Target fills are judged on the bid with no spread allowance. [checked]
   - G3 **Testnet fills are not market fills.** The go-live bar is measured on Deribit testnet fills; Deribit says testnet is
     synthetic and does not mirror live liquidity. [checked repo; search for the Deribit statement]
   - G4 **Fill model.** The readiness template asks for touch AND trade-through fills; both Tom harnesses still fill on touch only. [checked]
   - G5 **Free data not on the backtest host.** Binance's archive has 5-minute open interest from 2020-09-01 and depth bands from
     2023-01-01; the fetcher supports both, but the NUC studies report OI as NOT_IN_DATA. [checked, S3 listing]
3. **Where we search is the bigger question.** Our own results and the outside studies agree: at holds of 8 h or less BTC shows
   about zero gross edge, and a 10 bp round trip decides the outcome. The outside evidence that exists sits at 1-8 week trend
   (mostly lower drawdown, not extra return), futures carry (a risk premium with crash risk) and seconds-scale order flow
   (needs passive execution). Tom and Fabio on BTC at their native stop sizes cannot pass by arithmetic (TOM_LAYER_V2_SPEC s1);
   the BTC route needs a wider stop, which is a different holding period and close to a new strategy.

## 1. What changed in the last week (extraction + backtest), from the git log [checked]
| Area | Change | Where |
|---|---|---|
| Readiness gate | 12-item pre-registration template adopted 2026-10-12; required before any layer backtest | backtest/PRE_REG_TEMPLATE.md; PROJECT_VISION.md:208 |
| Tom | v2 spec part A: one family (imbalance fade, short-only, 3 entry paths); fee-net pass bar frozen before build; 69/69 quotes verified | research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md |
| Tom | clean holdout: ledger days +-1 trading day removed (26 of 156 days), design/check split by session, forward holdout from 2026-10-10 | PRE_REG_DAX.md:40-45; HOLDOUT_CLEAN.json |
| Tom/DAX harness | Codex lab fixes H2-H8 (net-fee verdict, holdout boundaries, session-matched null, readiness gate, trial identity); RV02 found 4 more HIGH (cards rv02-fix-*) | research/layer_lab/reports/ |
| Ledgers | Tom ledger repaired (identities, instrument, time provenance); Fabio ledger audited FIX-FIRST (3 HIGH, then 3 HIGH carried in rv05) | layer_lab reports 2026-10-12/13 |
| Extraction | Krown TA101: 8 of 18 transcripts extracted, quotes verified; check_spec_quotes.py for spec quotes | commit 8930cabd; scripts/dev/check_spec_quotes.py |
| BTC studies | 62 published rules: 0 survive; ETH replication 0 of 9; MFE exit study: no exit recovers fees; Q33 matrix: nothing survives | research/published_strats_2026-10-13, mfe_exit_2026-10-13, tom_fabio_guidance_2026-10-12 |

## 2. Method note (playbook Part I step 1)
What would settle "are we backtesting correctly": for each verdict, (a) the test could have detected an edge of the size the
source claims (power at the stated effect, out-of-sample, after fees + funding + spread + slippage), (b) fills and costs match
the venue that will execute, (c) the number of looks at data across the project is counted. Accepted methods exist for all three
(power / minimum track record length, fill-model sensitivity, deflated Sharpe / PBO / Reality Check / SPA), so this is not an
unvalidated domain. External items below only rank what to check first; our own backtest decides (playbook Part I 3e).

## 3. What outside studies say (all [search]; abstracts/snippets only, none opened here; verify on the desktop before citing further)
| Finding | Source | Tier \| method \| confidence | What it means for us |
|---|---|---|---|
| ~15,000 rules on BTC and other coins: break-even costs high in-sample, results do not hold out-of-sample; multiple-hypothesis correction used | Hudson & Urquhart, "Technical trading and cryptocurrencies", Annals of OR (hull-repository.worktribe.com/output/2328042) | T1 \| RC-type correction, OOS \| M | Same pattern as our 62-rule and volume studies: in-sample "edges" vanish OOS |
| BTC/USDT and ETH/USDT technical strategies with Reality-Check-style adjustment: none profitable in analysis or prediction periods (2023) | articlegateway.com/index.php/JAF/article/view/6453 | T2 \| RC-style \| L-M | Agrees with our nulls |
| 3,312 five-minute BTC rules: many profitable after snooping and cost adjustment, but unstable and declining over time | Bakker, EUR thesis (thesis.eur.nl/pub/41546/Bakker.pdf) | T3 (thesis) \| RC + costs \| L | Intraday edges, if any, decay; a single dev window is not enough |
| BTC/USDT perpetuals: returns depend on fees, funding, slippage and leverage limits; naive one-stage tuning makes backtests unreliable; overfitting diagnostic shows substantial residual risk | arXiv 2512.22476 (arxiv.org/html/2512.22476v1) | T2 \| nested tuning + overfit diagnostic \| M | Supports our nested DEV/VAL/HOLD; perp costs must include funding (we do) |
| Strong time-series momentum in BTC at daily/weekly horizons; market return predicts returns up to ~8 weeks | Liu & Tsyvinski, "Risks and Returns of Cryptocurrency", RFS 34(6) 2021 (nber.org/papers/w24877) | T1 \| full sample, costs not in snippet \| M | Our TSMOM 30 d result (p 0.12, risk reduction only) is consistent; the effect is weak after costs |
| Trading-range breakout beats buy-and-hold on bootstrapped Sharpe, daily 2010-2019, best in strong trends; costs not stated | Gerritsen, Bouri, Ramezanifar, Roubaud, FRL 34 (2020) (ideas.repec.org/a/eee/finlet/v34y2020ics1544612319303770.html) | T1 \| bootstrap, no costs in abstract \| M | Already in FABIO_BTC_RESEARCH E1; regime-dependent, needs a long sample |
| Bitcoin intraday time-series momentum (first half-hour predicts last half-hour, volume-defined sessions) | Shen, Urquhart & Wang (research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/) | T1 \| in-sample, costs unclear \| M | We tested this as session momentum: Sharpe 0.008 (genuine negative) |
| Futures-spot carry in BTC/ETH large and time-varying (avg ~7-8 %/yr, peaks > 40 %); high carry predicts crashes; margin calls make the trade risky | Schmeling, Schrimpf & Todorov, "Crypto Carry", BIS WP 1087 (bis.org/publ/work1087.htm) | T1 \| BIS WP \| H | Matches our carry supplement (15.4 -> 6.2 %/yr, decaying); it is a risk premium, not alpha |
| Order-flow imbalance at the best quotes linearly predicts very short-horizon price changes | Cont, Kukanov & Stoikov (foundational OFI); related BTC cross-exchange order-flow work: arxiv 2108.09750 | T1/T2 \| seconds horizon \| M | Only usable with passive execution and a queue model; not with 15-min snapshots and taker exits |
| Testnet is a synthetic environment and does not mirror live liquidity; to get fills, match against your own subaccount | Deribit support, "How to match trades on Testnet" (support.deribit.com/hc/en-us/articles/28685385297053) | T2 (exchange doc) \| n/a \| H | G3: testnet P&L is not evidence of live fills |
| Minimum track record length: observations needed before a Sharpe can be told apart from a threshold; skew/kurtosis lengthen it; Deflated Sharpe corrects for the number of trials | Bailey & Lopez de Prado, J. of Risk (ideas.repec.org/a/rsk/journ4/2223785.html); DSR (papers.ssrn.com/abstract=2460551) | T1 \| method \| H | G1 and G6 |
Earlier passes already cover PBO, White RC vs Hansen SPA, fill models and CFD tick volume
(research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md s3) and eight BTC items E1-E8
(research/fast_track_2026-09-27/FABIO_BTC_RESEARCH_2026-09-30.md:67-74). Not repeated here.

## 4. Our practice against standard practice [checked unless marked]
| Practice | Standard | MTS today | Gap |
|---|---|---|---|
| Pre-registration, frozen before outcomes | yes | yes (PRE_REG_TEMPLATE, PRE_REG_DAX, published PRE_REG) | none |
| Out-of-sample / holdout read once | yes | yes; BTC Tom holdout burned and recorded (B147); clean DAX holdout | none for the study; project-wide see G6 |
| Multiple-testing correction | RC / SPA / BH / DSR | BH + Holm per study; RC max-T in volume | no project-wide trial count (G6) |
| Placebo / random-entry null | yes | yes, session-matched for DAX (lab H3) | none |
| Fees + funding | yes | yes (fees.py one source; funding in studies with holds > 8 h) | none |
| Spread / bid-ask | yes | BTC: negligible; DAX: bid-only bars, no spread | G2 |
| Slippage on market legs | measured | BTC default 0 (tom_bt.py:176), stress optional; DAX +1 pt on stop/timeout | G7 |
| Limit-fill realism (touch vs trade-through vs queue) | report both bounds | CryptoCred: trade-through (B151); Tom BTC + DAX: touch only | G4 |
| Execution venue = backtest venue | yes | signals/backtests on Binance, execution on Deribit; basis and mark-price stops not modelled (tom_bt_report.py:229) | G8 |
| Power / minimum detectable effect | stated before the run | volume study prints MDE (PRE_REG_VOLUME:63); template item 10 is a fixed N >= 100; Tom v2 and the 62-rule study print none | G1 |
| Paper/testnet stage measures execution | shadow fills against real market data | GO_LIVE_BAR counts testnet fills | G3 |

## 5. Gaps, ranked
### G1 (HIGH): pass bars are underpowered against the edge the source claims; a FAIL can be a miss
- Evidence: TOM_LAYER_V2_SPEC.md:43 PASS = >= 100 fills AND 95 % CI lower bound of net R > 0; :49 "FAIL on DAX dev = stop".
  Tom's own numbers (spec s0/s1): hit rate 40-45 %, minimum R:R 1.5, claimed edge 0.1-0.35 R. PRE_REG_TEMPLATE.md:52 item 10
  asks only for N >= 100. Dev window 2024-11-04..2026-04-10 (PRE_REG_DAX.md:25), clean holdout 130 days.
- Computed here (payoff +RR with probability p, else -1 R, minus cost c; two-sided 95 % CI lower bound > 0; script in section 9):

| p | R:R | cost R | mean net R | power at 100 | at 150 | at 300 | trades for 80 % power |
|---|---|---|---|---|---|---|---|
| 0.45 | 1.5 | 0.012 | +0.11 | 15 % | 20 % | 35 % | 951 |
| 0.45 | 1.5 | 0.062 | +0.06 | 7 % | 9 % | 14 % | 3,059 |
| 0.40 | 2.0 | 0.012 | +0.19 | 25 % | 35 % | 60 % | 480 |
| 0.40 | 2.0 | 0.062 | +0.14 | 15 % | 21 % | 37 % | 890 |
| 0.45 | 2.0 | 0.062 | +0.29 | 49 % | 66 % | 92 % | 211 |
| 0.45 | 2.5 | 0.062 | +0.51 | 84 % | 95 % | 100 % | 90 |
  Reading: if Tom's edge is real but at the low end of his own range, the frozen bar fails 65-93 % of the time at 100-150 trades,
  and the FAIL rule then parks the family for good. Only an edge at the top of his range is reliably detected.
- Same issue in the 62-rule study: BH q <= 0.10 over 62 tests on a 2.5-year DEV needs an annual Sharpe of about 2.4 for 80 % power
  (1.9 for 50 %); published BTC trend Sharpes are about 0.5-1. "Nothing survives" was close to certain whatever the truth.
  The report does say slow rules "could only fail to show an effect", but the headline reads as a negative.
- Fix (before the DAX dev run, the last point it can change without reading outcomes): (1) every pre-registration prints the MDE
  and the trades needed for 80 % power at the source's claimed edge (reuse volume_2026-10-09/vstats.py); (2) verdicts read
  "no edge larger than X R", never "no edge"; (3) a FAIL with power < 80 % at the claimed edge is INCONCLUSIVE: extend the sample
  (forward holdout, or pool family A on FDAX + ES, which Tom also trades, if the data exists) instead of stopping; (4) daily
  rules use a longer history (BTC index/spot from 2013 for daily bars, perp costs applied). Changing the stop rule is a protocol
  change: operator decision.

### G2 (HIGH): DAX harness uses bid-only bars; every exit of a short is a buy at the ask
- Evidence: dax_data.py:7,24 load `BID_candles_min_1.bi5` only. Family A is short-only (TOM_LAYER_V2_SPEC s2 "Side: short in all
  10 ledger groups"). The cost table (spec s1) has fee 0.24 pt and +1 pt slippage on stop/timeout (PRE_REG_DAX.md:17-18), no spread.
  tom_bt.sim_limit_trade fills the target when the bar's low touches it (tom_bt.py:212); on bid bars the ask is still one spread above.
- Why it matters: the target leg has no allowance at all, so the backtest books winners whose buy order never filled; the stop
  leg is covered only where the spread is <= 1 pt. Tom trades pre-market and the open, when CFD spreads are widest. With a 20 pt
  stop, every 1 pt is 0.05 R, against a claimed edge of 0.1-0.35 R. [estimate: CFD spreads of 1-2 pt in cash hours and wider
  pre-market are typical; measure, do not use my number]
- Fix: fetch Dukascopy ASK candles (same URL with `ASK_` in place of `BID_`; not reachable from this cloud session), judge buy
  legs on ask and sell legs on bid, and print the spread by session minute in the dev report. Add the measured spread to the
  spec's cost table before the dev run.

### G3 (HIGH): the go-live bar is measured on synthetic testnet fills
- Evidence: GO_LIVE_BAR.md:6 "measured on testnet"; :10 "using the exchange's real fills and fees". EXEC_PROVENANCE_AUDIT.md:92:
  testnet order book not replayed, testnet liquidity untested. Deribit says testnet does not mirror live liquidity [search].
- Why it matters: 200 testnet trades with PF > 1.2 can come from fills the real book would not give (limit fills, stop slippage).
  Testnet proves the plumbing (orders, stops, loss guard), not the P&L.
- Fix: log a shadow fill for every testnet order, computed from the real market tape at the same timestamps (Binance aggTrades,
  already fetchable), and measure the go-live bar on shadow fills; testnet fills become a plumbing check. Changing GO_LIVE_BAR
  needs an operator decision on the page (D06-gate).

### G4 (MED-HIGH): template item 7 (touch AND trade-through) is not implemented in either Tom harness
- Evidence: PRE_REG_TEMPLATE.md:37 item 7; tom_bt.py:184-188 fills when low <= entry (touch); tom_dax_bt.py:357 "the strategy's
  touch model". CryptoCred already moved to trade-through (B151, test_run_cc_setups.py:208); bt/bt_ladder.py has a
  `through_ticks` parameter to copy.
- Fix: a `through_ticks` argument in sim_limit_trade (entry and target), both runs in every report; a result that holds only on
  touch is not a result (BACKTEST_FAILURES_RESEARCH s3). Must land before the DAX dev run.

### G5 (MED): free BTC data the studies call NOT_IN_DATA
- Evidence: S3 listing of data.binance.vision (this session): `futures/um/daily/metrics/BTCUSDT` starts 2020-09-01 (5-minute OI,
  top-trader and taker long/short ratios); `bookDepth/BTCUSDT` starts 2023-01-01. fetch_binance_archive.py:14,16 supports both.
  mfe_exit REPORT.md:19 "OI change: NOT_IN_DATA (no open-interest series on disk)"; LAYERS.md:14 "book_imbalance never counts in
  historical snapshots (no raw source)"; screenshot_context REPORT.md:63 OI exists only on JIS-NB (live recorder).
- Fix: one fetch run on the NUC into the primary tree's Dumps/ (metrics 2020-09..now; bookDepth 2023-01..now). bookDepth is
  +-1..5 % depth bands, not top of book: it needs its own FORMULAS.md definition before any proof uses it.

### G6 (MED): no project-wide count of trials or holdout looks
- Evidence: about 1,080 rows in 6 TRIAL_REGISTRY files (volume 613, published 133, candles 132, mfe 102, bt_runs 36, smoke 64;
  some are sensitivity duplicates), plus grids outside any registry (Q33 matrix, CryptoCred stop sweep, VP pivot 48 cells,
  Fabio OF 64 variants). Each study corrects within itself, which is right.
- Why it matters: the first config that "passes" will be the best of thousands of looks across studies, and the choice of the
  next study depended on earlier outcomes. Its Deflated Sharpe must use the whole count, and the shared sealed holdout
  (2025-07..2026-09, decision A7) needs a read log so a second look is visible.
- Fix: one append-only `research/TRIAL_LEDGER.csv` (study, variant, date, data window, verdict) fed by each registry, a DSR helper
  that reads it, and a holdout-read log per sealed window.

### G7 (MED): stop-leg slippage defaults to zero on BTC
- Evidence: tom_bt.py:176 `slip=0.0`; maker_model.py:19 "slippage on stop fills ... NOT modelled".
- Why it matters: at a 0.08 % stop, 3 bp of slippage is 0.37 R; at 0.25 % it is 0.12 R. [arithmetic; the 3 bp is an example]
- Fix: measure stop slippage from aggTrades (first trade price after the stop level trades, by volatility bucket) and make the
  measured median the default, with the current zero as the optimistic bound. Low urgency while the BTC Tom encoding is STOP.

### G8 (MED): backtest venue is not the execution venue
- Evidence: tom_bt_report.py:229 "Not modelled: funding, Deribit-vs-Binance basis, queue position, mark-price stops".
- Fix: a parity check on a sample of past signals using Deribit BTC-PERPETUAL 1m candles (public get_tradingview_chart_data).
  That is a read of public mainnet market data, no account: the operator decides whether the "never mainnet" rule covers it.

## 6. Extraction gaps
- E1 Translation layer. Tom's captions are AI-translated (TOM_LAYER_V2_SPEC header). check_spec_quotes.py proves the English
  string is in the translated file, not that Tom said it. Fix: keep the original-language caption line next to every
  rule-bearing quote (thresholds, side, stop, target) and have a second, independent translation checked for those lines only.
- E2 Frame reads have no measured error rate. Both ledgers came back FIX-FIRST (Tom 4 HIGH; Fabio 3 HIGH, then 3 HIGH carried in
  rv05), found after the fact. The parameter audit already used a second reader (kappa 0.446). Fix: two independent reads per
  rule-bearing field (price, time, side, stop, target), agreement reported per field, and only agreed fields become replay-ready.
- E3 Ground truth is small and selected. The Tom check set is 2 trades and the spec says so (s7); videos are chosen trades (N8).
  Recall can only falsify. Growing the check set (frames-only recaps, card tom-check-set-find-frames-only-tom-trade) is the
  only fix; it does not replace G1.
- E4 Source edge unverified. Fabio's record is a vendor bio, T3 (FABIO_BTC_RESEARCH_2026-09-30.md:18-19); no record for Tom is in
  the repo; a search found no official championship result for Fabio. The DAX dev run is therefore the first test of whether
  Tom has an edge at all, which is why its power (G1) matters most.

## 7. Are we going in the right direction?
- Method: yes. The project now does almost everything the literature asks; fix G1-G4 before the DAX dev run and the next verdict
  can be trusted in both directions.
- Search space: partly no. More than 1,000 registered trials (plus unregistered grids), mostly at holds of 8 h or less, have found nothing that survives; the MFE study shows
  random entries have the same favourable/adverse excursions as our setups. That is what the outside studies predict for
  short-horizon taker trading on BTC. Proposal (operator decision, no source behind the number): before any new intraday
  encoding is built, the DEV gross edge must be at least 2-3 times the round-trip cost; anything below is not built.
- Where outside evidence points, ranked: (1) Tom family A on its home market with G1-G4 fixed (in progress, correct next step);
  (2) multi-week trend on BTC as a risk-reduction overlay, tested on a long history with a Sharpe/drawdown metric against
  buy-and-hold rather than mean return; (3) carry only with basis, margin and crash risk modelled; (4) order flow only if
  execution becomes passive with a queue model.

## 8. Proposed cards (not created here; a desktop session files them after reading this)
Live overlap: card `tom-layer-v2-cost` (Tom v2 part B: per-market cost, stop-width rule, build cards) was claimed by JIS-NUC
(account sharma) at 2026-10-13 11:57 IST (system/claims/tom-layer-v2-cost.md). G1, G2 and G4 belong inside that card; hand them
to its owner rather than opening parallel cards.
| Card | Lane | Blocks |
|---|---|---|
| Pre-reg power: MDE + trades-for-80 % beside every verdict; INCONCLUSIVE when power < 80 % (template item 10, Tom v2 bar) | OPUS (protocol) + operator decision | tom-dax-backtest |
| DAX ASK candles: buy legs at ask, spread by session minute, cost table update | SONNET | tom-dax-backtest |
| Tom harnesses: through_ticks fills, report touch and trade-through | SONNET (or CODEX build) | tom-dax-backtest |
| GO_LIVE_BAR on shadow fills from the real tape | OPUS + operator decision | S4 evidence |
| Fetch Binance metrics 2020-09.. and bookDepth 2023-01.. on the NUC | DSA-NUC | OI/book studies |
| Project trial ledger + DSR helper + holdout-read log | SONNET | first survivor |
| Stop slippage measured from aggTrades | SONNET | BTC transfer |
| Deribit vs Binance venue parity (after operator ruling on public mainnet data) | SONNET | S4 |

## 9. Reproduce, sources not opened, open questions
- Power table: payoff model above, mean = p*RR - (1-p) - c, sd from the two-point payoff, power = 1 - Phi(1.96 - mean/(sd/sqrt(n))),
  trades for 80 % = ((1.96 + 0.8416) * sd / mean)^2. Sharpe for the 62-rule gate: z = Phi^-1(1 - 0.10/62) = 2.95,
  SR = (z + 0.8416) / sqrt(2.5). Plain arithmetic, no repo code used (LESSONS 1: expected numbers from the definition).
- Not opened (egress blocked here): every external row in section 3. Desktop step: open each, match title/authors/venue/year,
  mark "verified 2026-10-xx" or REJECT, per playbook Part I 3a.
- Not verified: Dukascopy ASK file availability for DEUIDXEUR; real DAX CFD spreads by minute; Deribit testnet behaviour beyond the
  support article; whether bookDepth bands can approximate the engine's book_imbalance.

## 10. Desktop follow-up (JIS-NUC, 2026-10-13/14): source check and G2 RESULT
### 10.1 Section 3 sources, opened 2026-10-13 from JIS-NUC (title/authors matched against the cited row)
| Source | Result |
|---|---|
| arxiv 2512.22476 "AutoQuant ... Cryptocurrency Perpetual Futures" | verified 2026-10-13 (page mentions perpetuals, funding, slippage, overfitting) |
| BIS WP 1087 "Crypto carry" (Schmeling, Schrimpf, Todorov) | verified 2026-10-13 |
| Gerritsen et al., "The profitability of technical trading rules in the Bitcoin market", FRL 34 (repec) | verified 2026-10-13 (authors match; costs not checked) |
| Liu & Tsyvinski, NBER w24877 "Risks and Returns of Cryptocurrency" | verified 2026-10-13 |
| Shen, Urquhart & Wang, "Bitcoin intraday time series momentum" (Birmingham) | verified 2026-10-13 (abstract: first half-hour predicts last) |
| Bakker, EUR thesis pdf (3,312 rules text found in the PDF) | verified 2026-10-13 (thesis, T3) |
| Li, Wang, Wang, Yang, JAF 23(4) 2023 (articlegateway, opened in the browser pane) | verified 2026-10-13 (no profitable rule after data-snooping adjustment) |
| arxiv 2108.09750 | verified as a page; title is "Fragmentation, Price Formation, and Cross-Impact in Bitcoin Markets", i.e. cross-impact, a looser fit than "order-flow work" in s3 |
| Hudson & Urquhart (hull-repository.worktribe.com/output/2328042) | REJECT 2026-10-13: HTTP 403 (bot challenge), page did not open |
| Deribit support article 28685385297053 | REJECT 2026-10-13: HTTP 403 (bot challenge) from curl; the browser-pane load timed out. G3 text stays "search snippet only" |
| Bailey & Lopez de Prado (ideas.repec.org/a/rsk/journ4/2223785.html) | REJECT 2026-10-13: HTTP 404, wrong URL |
| Deflated Sharpe (papers.ssrn.com/abstract=2460551) | REJECT 2026-10-13: HTTP 403 content blocked |
REJECT here means "did not open or did not match", not "wrong"; the claim stays labelled [search] until a second route opens it.
### 10.2 G2 RESULT: Dukascopy DEUIDXEUR ASK minus BID, 1-minute close, 10 weekdays 2026-09-28..2026-10-09
ASK_candles_min_1.bi5 is served (HTTP 200 after backoff on 429). 15-minute buckets, Berlin time (UTC+2 in the window), 150 minute-pairs per bucket.
| Berlin | median spread (index pt) | p90 |
|---|---|---|
| 07:00-08:00 | 2.65 | 2.68 |
| 08:00-09:00 | 1.65 | 1.68 |
| 09:00-11:00 | 1.15 | 1.18 |
All 2,400 minute-pairs 07:00-11:00: median 1.19 pt. Spreads are flat inside each hour (the feed quotes a stepped spread), so the 15-minute table is three levels.
Reading: the frozen cost table has 0.24 pt fee + 1 pt slippage on stop/timeout only (PRE_REG_DAX.md:17-18) and nothing on the target leg.
For a short, the buy-to-cover target fill pays the ask: 1.15 pt from 09:00, 1.65 pt 08:00-09:00, 2.65 pt 07:00-08:00. Against a
20 pt stop that is 0.06-0.13 R per trade, the same size as Tom's claimed 0.1-0.35 R edge. G2 is confirmed HIGH.
Method: stdlib script, raw files kept off-repo; per minute `(ask_close - bid_close)/1000`; no forward fill; closed-market filler minutes dropped.
