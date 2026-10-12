# TOM AND FABIO ROADMAP after the 2026-10-11 transfer probe (Opus, operator chat)

Goal (operator 2026-10-11): get the Tom and Fabio layers **redefined completely** to match these findings.
Plan of record for the probe: PROBE_PLAN.md (hypotheses H1-H5, option arms S/Q/M/F, branch rules). This file is the road map that follows from its first results.

## 1. What we know now (each line has its file)
| # | Finding | Evidence |
|---|---|---|
| F1 | Coded Tom fired on **0 of 7** of Tom's own chart-verified DAX trades (as coded and with DAX fees). The loss is in the encoding, before any transfer to BTC. | RECALL_DAX.md |
| F2 | Transcripts are not evidence for prices/dates (transcript "18,258", chart 24257). Frames are (taskbar clock, chart header, order labels). | RECALL_DAX.md section 1 |
| F3 | 4 of 7: engine had a same-side zone within 0.15 % but proof 1-2 (3 needed), and net_rr used BTC perp fees on every market. | RECALL_DAX.md section 2 |
| F4 | 3 of 7 (his most typical trade, fade of the opening/morning spike top): no candidate type exists. His reasons (profile shape P/b, inside bar, ledge of old highs, no liquidity above) are not in the code. | RECALL_DAX.md section 3 |
| F5 | On data without an aggressor split (DAX CFD) proof is capped at 2 (rejection_wick + volume_spike, SetupCandidatesBuilder.java:557-575), so WATCH (3) is unreachable by construction. | DAX build report, card tom-dax-backtest note |
| F6 | Tom's stops are 20-63 points (0.08-0.26 %). Fine on FDAX (round turn ~0.1 point); on BTC perps they sit inside noise and fees cost ~2.8 R per loss. A transfer rule (minimum stop width / cost-aware R) is required. | DIAG_BTC.md, RECALL_DAX.md section 3.4 |
| F7 | BTC diagnostics on the three discretion axes: session S SKIP (no window beats the rest), selection Q SKIP (thin), management M GO (40 % reach +1R before the stop; 28 % of stopped trades were +1R first). | DIAG_BTC.md |
| F8 | Management is part of Tom's trade: stop-out then re-entry (T3 -> T3b), partials with a runner (T1, T5). | RECALL_DAX.md section 3.3 |
| F9 | Gap rules: 27 rules, DAX-only, 10 CONTEXT-NEEDED (need the frames he points at). Not coded. | conditions/gap_rules.md |
| F10 | Fabio v3: L3-FAIL for all four models on BTC; never tested on his home market or against his own trades. Same blind spot as Tom before today. | P2_FABIO_V3_HOLDOUT_STATUS.md |
| F11 | DAX tooling exists and is tested: dax_data.py (Dukascopy), dax_engine.py (-Dmts.symbol), tom_dax_recall.py, tom_dax_bt.py (29 tests, read-once holdout). | commits 1e67b85, d6409fe, this folder |

## 2. STOP now
- BTC backtests, variants, re-runs or tuning of the **current** Tom or Fabio encoding. They can only re-prove "no edge" (F1, F10).
- Session-window (S) and selection (Q) arms on BTC: parked until a v2 encoding exists (F7).
- Transcript-only extraction of prices, levels, dates or setups. Every trade fact needs a frame (F2).
- Judging any non-BTC market with the BTC fee term, and any BTC test with Tom's DAX-sized stops without the transfer rule (F3, F6).
- The full DAX backtest run, until spike-fade passes recall >= 4/7 (PROBE_PLAN stop rule). The build stays ready.
- New layers or indicator systems while Tom/Fabio are being redefined.

## 3. FOCUS (in this order)
1. **Ground truth first:** trade ledgers from frames, Tom (>= 30 trades) and Fabio (>= 20). Cards tom-trade-ledger, fabio-trade-ledger.
2. **Redefine each layer from its ledger (Opus research, two cards each: A families/rules, B markets/cost/build cards):** setup families, sourced rules, proofs per market data, cost model, stop-width transfer rule, management, session; keep/change/drop vs the current engine. Cards tom-layer-v2-spec, fabio-layer-v2-spec.
3. **Encode family by family behind a flag (Sonnet):** default off so live BTC stays bit-identical; spike-fade first (tom-encode-spike-fade). Pass bar = recall on his own trades (>= 4/7 now, then the full ledger).
4. **Home-market backtest:** tom-dax-backtest (built), dev then holdout once; the pre-registered arm plus labelled --shifts extension arms, all counted.
5. **Transfer to BTC:** only the families that work at home; stop-width/cost rule from the v2 spec; management arms (tom-probe-prereg, reduced to M arms).

## 4. Sessions needed next
| Session | Model | Card(s) | Input -> output |
|---|---|---|---|
| T0 background | script | tom-dax-data | finish Dukascopy fetch (F:/MTS/data/dax_fetch.log ALL_DONE; re-run the same fetch command if the shell died, it skips files already there), `dax_data.py convert`, close the card |
| Build | Sonnet | tom-verdict-fee-per-market | finish/verify per-market fee (GER40 netRR(24229,24111,24257)=4.1696 (the brief said 4.1662: hand error, (118-0.24229)/(28+0.24229)=4.1696); BTC bit-identical) |
| Frames | Sonnet | tom-trade-ledger | videos -> TOM_TRADE_LEDGER.csv/.md |
| Frames | Sonnet | fabio-trade-ledger | videos -> FABIO_TRADE_LEDGER.csv/.md |
| Research | **Opus** | tom-layer-v2-spec (A), then tom-layer-v2-cost (B) | A: ledger -> families + sourced rules + keep/change/drop. B: per-market proofs/cost, BTC stop-width transfer rule, Sonnet build cards. One card per session (each M; the original L card was split 2026-10-11) |
| Research | **Opus** | fabio-layer-v2-spec (A), then fabio-layer-v2-markets (B) | A: ledger -> families + rules. B: NQ vs BTC data plan, cost, recall-harness + encode cards |
| Build | Sonnet | tom-encode-spike-fade, then the cards the spec creates | flag-gated Java + recall V2 report |
| Run | Sonnet/DSA | tom-dax-backtest, then tom-probe-prereg (M arms) | reports, holdout read once |

## 5. Open items carried
- Worktree `../mts-daxbt` holds ~45 stray untracked files from a stash pop (never committed; the stash entry is intact). Delete the worktree when nothing else is in it.
- l8RZrBfzvp4 video: yt-dlp 403; retry inside tom-trade-ledger.
- Dec 2025/Jan 2026 FDAX-CFD offset ~200 points vs 100-120 theory: anchor trades on frames + price shape, not on the basis formula alone.

## 6. Addendum 2026-10-11 (C-Cloud research, BACKTEST_FAILURES_RESEARCH.md)
Beyond Tom and Fabio: the other trader layers (Malkan RSI, CryptoCred, positioning) show the same pattern (tested off home market, timeframe or exits), while volume/candle/MA/RSI-divergence/session layers are fair negatives and stay parked with sealed holdouts.
| New finding | Consequence | Card |
|---|---|---|
| N1 DAX holdout contains Tom's ledger days | drop ledger days +-1 from the holdout, add forward holdout from 2026-10-10, split ledger design/check | tom-holdout-clean-split |
| N2 recall >= 4/7 alone can be met by firing on every spike | pass bar = recall on CHECK set AND fire rate per day; recall iterations are trials | tom-encode-spike-fade |
| N3 DAX feed volume is not Eurex volume | profile parity vs Tom's drawn POC/VAH/VAL before encoding volume proofs | tom-profile-parity-check |
| N4 Fabio ledger lacks minute timestamps; stops tighter than Tom's | read clocks from frames; NQ tick data = operator cost decision | fabio-ledger-minute-timestamps, fabio-layer-v2-markets |
| N5 MFE measured on noise-level stops | re-measure after the stop-width rule | tom-probe-prereg |
| N6 snapshots lack market state / day type | write them so selection (Q) is testable later | tom-layer-v2-cost |
| N7 null not session-matched; touch fills only | session-matched null, report touch and trade-through | tom-dax-backtest, tom-probe-prereg |
Home-fit audits (CryptoCred first, then Malkan, positioning) run only after Tom/Fabio v2 part B and the readiness template: cards `*-home-fit-audit`.
