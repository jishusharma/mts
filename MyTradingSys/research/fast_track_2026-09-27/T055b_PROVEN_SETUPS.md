> **CORRECTION (operator 2026-09-29):** operator states this file misquotes the 44-concept ICT/SMC study (SSRN 7483658).
> Verified 2026-09-29 via search-result abstract summary (SSRN page itself returned HTTP 403, full text not opened): Tangirala, "Do Smart Money Concepts Predict Returns? Evidence from 44 Formalised Detectors on S&P 500 Daily Bars, 2010-2026", posted 18 Sep 2026. 496 S&P 500 constituents, 2.20 M events, 17.6 M simulated trades, 8 horizons; against a composition-matched null with Benjamini-Hochberg over 352 concept x horizon hypotheses, "none beats random entry at any horizon" and none is significantly worse; best point estimates 11-12 bp over 10 days (liquidity-sweep detectors), p >= 0.23. So: (1) the pre-gate "combination transforms it to positive" claim is unsupported (body already removes it); (2) NOT VERIFIED: the body's statement that the paper "does not test combinations" (HTF/killzone/RR) - the abstract summary is silent on it, so treat as unknown, not as "not contradicted"; (3) sample is US equity daily bars, not BTC; the null is "no evidence of edge", also not evidence of harm. Body not edited.

# T055b - Proven BTC Setups: Evidence Survey [GATED v3.0]

Scope: T055 part (b) - which BTC setups have verifiable evidence, by style (scalp <15m, intraday,
swing), buildable from Binance/Deribit public data. Superseded: pre-gate version (A/B/C/D/F
grades) backed up at `T055b_PROVEN_SETUPS.md.pre_gate3`. This version applies playbook.md Part I
v3.0 (fixed T1/T2/T3/REJECT table). Reused prior gated research:
`research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md` (funding, order-flow tiers already settled).

## STEP 1 - METHOD NOTE (one, covers all styles)

A setup "works" only if a disclosed-method study or our own backtest shows positive expectancy
net of realistic costs (fees + funding + slippage) on an out-of-sample sample large enough to
clear the noise floor at BTC's volatility; win-rate or Sharpe claims without a cost model or
without an OOS split do not settle anything, regardless of source polish. Scalp-style claims need
the round-trip fee floor (below) cleared before any other test matters.

## SCALPING FEE FLOOR (unchanged, internal arithmetic, not an external citation)

Binance USDT-M perp: taker 10bps RT, maker 4bps RT. Deribit perpetual: taker 7bps RT, maker nets
-3bps (rebate) before adverse selection. Add 1-3bps realistic slippage. Any scalp candidate needs
gross edge comfortably above ~10-15bps RT (Binance taker) or ~8-10bps (Deribit taker) to survive.

## STEP 3a - CITATION CHECK (opened 2026-09-28)

| Source | Claimed for | Result |
|---|---|---|
| Shen, Urquhart, Wang, *Financial Review* 2022 | intraday momentum, first-half-hour predicts last-half-hour | Verified. Vol. 57(2), 319-344, DOI 10.1111/fire.12290. Matches (liquidity-provision mechanism, not late-informed trading). T1. |
| Zarattini & Aziz 2023 | Opening Range Breakout, sustainable long-term profits, US equities | Verified. SSRN 4416622, "Can Day Trading Really Be Profitable?", 2016-2023 US stock sample. Matches. SSRN working paper = T2, not T1 (not a peer-reviewed journal placement as originally graded A). No BTC replication found - confirmed still true. |
| Fan, Jiao, Lu, Tong, SSRN 4666425 | funding carry, Sharpe 0.74, 43% ann. | Verified. "The Risk and Return of Cryptocurrency Carry Trade", numbers match exactly. T2. |
| Han, Kang, Ryu, SSRN 4675565 | TSM survives but many portfolios liquidated once realistic assumptions applied | Verified. "Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions" - liquidation-risk modeling matches claim exactly. T2. (Original report cited this by URL only, without author names - confirmed same paper.) |
| arXiv 2212.06888 (He/Manela/Ross/von Wachter) | perpetual funding-rate theory backing funding-reversion mechanism | Verified, see T055a. T2. |
| "net Sharpe -3.22" walk-forward study | cross-sectional OHLCV+funding alpha fails OOS | Verified. Azka Fayez Junior, SSRN 6701738, "Failure of Cross-Sectional Alpha Screening on Cryptocurrency Perpetual Futures" - Model A net Sharpe -3.22, rank IC -0.0097 (t=-1.54), 10 Binance USDT-M perps, Jul 2022-Apr 2026. Exact match. T2. |
| 44-detector ICT/SMC SPX study, SSRN 7483658 | "combining HTF liquidity draw + session killzone + 1:2.5 RR transforms it to positive" | **PARTIAL MISMATCH.** Paper verified real - Tangirala, "Do Smart Money Concepts Predict Returns? Evidence from 44 Formalised Detectors on S&P 500 Daily Bars, 2010-2026", SSRN 7483658. Verified abstract states **none of the 44 concepts beats a matched null baseline at any of 8 horizons, with multiple-testing correction** - no combination-rescues-it result is stated. The "transforms it to positive" claim in the pre-gate report does not match the verified source. Logged to 02b_DECISIONS_LOG.md; claim removed, replaced with the verified null result below. |
| CME BTC futures 24/7, end of May 2026 | mechanism for CME weekend-gap-fill setup being dead | **Verified TRUE.** CME Group press release + Coindesk: 24/7 Globex trading for BTC/ETH futures and options launched Friday 29 May 2026, one 2-hour weekly maintenance pause (Sat 03:00-05:00 UTC). Weekend gap mechanism is confirmed eliminated going forward. |
| PMC10015199 (Shanaev, Vasenin, Stepanov) | turn-of-candle effect | Verified. *Heliyon* (peer-reviewed, Cell Press), PubMed-indexed. OOS-robust across exchanges per abstract; originally graded B, upgraded to **T1** (peer-reviewed journal, not just a preprint). |
| SSRN 6579278 (Lim) + cryptoslate.com | liquidation-cascade stylized facts + "no metric warns all 7 crashes" | Both verified - Lim's Oct-2025-crash minute-level study (5 stylized facts, 22x volume surge) matches; cryptoslate's "strongest recurring liquidation warning signs cannot warn of an individual crash" headline matches the 7-crash null result. Both citations correctly attributed, no mismatch. |
| arXiv 2510.14435 (Borri, Liu, Tsyvinski, Wu) | funding-carry Sharpe regime-dependent, 6.45 -> negative in 2025 | Verified exactly: full-sample (2020-2025) Sharpe 6.45, falls to 4.06 from 2024, negative in 2025. T2 (arXiv, disclosed data/method, established authors). |
| paperswithbacktest.com (time-of-day 21:00-23:00 UTC, combined trend+MR overlay) | seasonal window, breakout+touch overlay | Verified page exists and describes the claimed mechanism (NYSE-hours mapping, overnight drift). No peer review, no formal OOS split disclosed - stays T3 as originally graded. |
| BB/Keltner squeeze, VWAP-band reversion, anchored VWAP (blog/vendor only) | intraday/swing mean reversion | Opened; vendor/blog only, no disclosed cost-adjusted OOS test for any of the three. **REJECT** per Step 2 table ("win-rate/profit claims without costs"). |
| RSI divergence standalone | reversal trigger | No new evidence found beyond hindsight-dependent definition already noted; stays **REJECT** as a standalone claim (existing `rsi` layer already requires confirmation filters, which is consistent with this). |

## SURVIVING FINDINGS BY STYLE

**Scalping (<15m).**
- Order-flow imbalance (aggressor volume predicts next-bar direction): `T2 | two 2026 BTC/USDT-
  specific preprints (Vafin SSRN 6938742; Schmalz SSRN 7227998, explicitly framed as needing more
  scrutiny) | L`. Verified both exist and match claimed content.
- Turn-of-candle effect (returns concentrated at 15-min candle opens): `T1 | peer-reviewed,
  cross-exchange OOS robustness, no cost model in the paper | M`.
- Opening Range Breakout: `T2 | equities-only evidence (2016-2023 US stocks), no BTC replication
  | L for crypto transfer`.

**Intraday.**
- Intraday session-momentum (first-half-hour predicts rest of session): `T1 | peer-reviewed,
  liquidity-provision mechanism, no explicit cost model in abstract | M`.
- Funding-extreme mean reversion: reuse `whale_positioning_evidence_2026-09-12.md` tier - `T2
  (Memon 2026, 7y Binance) | M` - not re-derived here.
- Liquidation-cascade risk filter (de-risk, not entry timing): `T2 | single-event case study for
  stylized facts, separately-verified null result across 7 events for predictive entry use | M for
  risk overlay, REJECT for predictive entry`.
- Time-of-day 21:00-23:00 UTC window: `T3 | practitioner backtest, no formal OOS split | L`.

**Swing.**
- Funding-rate carry (cross-sectional): `T2 | Sharpe 0.74/43% ann. full-sample, but a second
  T2 source (Borri et al.) shows the same style of carry going to Sharpe 6.45 -> negative by 2025 -
  regime-dependent, not a stable edge | M`.
- Vol-scaled time-series momentum: `T2 | crypto-specific, realistic liquidation modeling shows
  "many portfolios liquidated," net edge thin after costs | M`.
- Combined trend+MR overlay: `T3 | no cost model, no OOS split disclosed | L`.

**No validated evidence found**: BB/Keltner squeeze, VWAP-band reversion, anchored VWAP,
standalone RSI divergence, standalone ICT/SMC concepts (now with a verified T2 null result against
them, not merely "unverified" as before).

## TOP CANDIDATES TO BACKTEST FIRST (revised ranking after re-tiering)

1. **Turn-of-candle effect** (now T1, was B) - cheapest to test, klines only, peer-reviewed basis.
   Data: 1m/15m klines. Split: walk-forward by year. Costs: 10bps RT Binance taker. Kill if:
   net-of-cost edge does not survive on >=2 OOS years.
2. **Funding-extreme mean reversion** (T2, already gated via whale_positioning_evidence). Data:
   funding + mark price (have). Split: train 2020-2023 / test 2024-2026. Kill if OOS Sharpe < 0.3.
3. **Intraday session-momentum** (T1). Data: 1h/5m klines. Split: train 2020-2023 / test
   2024-2026. Kill if effect sign-flips or vanishes post-2023.
4. **Funding-rate carry, single-asset directional variant** (T2, regime-flagged). Data: funding
   history (have). Split: expanding walk-forward, explicit 2024-2025 fold given the known
   regime break. Kill if OOS Sharpe < 0.3 or the 2025 negative-Sharpe regime dominates the test
   window.
5. **Order-flow imbalance scalp** (T2, self-described as needing scrutiny) - test last, cheapest
   confidence, must clear the 10-15bps fee floor above before anything else matters. Data:
   aggTrades. Kill if gross edge does not clear the fee floor in-sample, let alone OOS.

## FORMULA CANDIDATES FOR FORMULAS.md (not added yet)

- `turn_of_candle_return(t)` = return in minutes {0,15,30,45} of each hour vs. other minutes.
  Source: Shanaev, Vasenin, Stepanov, *Heliyon*/PMC10015199, T1.
- `session_momentum_signal(window)` = sign/magnitude of first-half-session return, used to bias
  rest-of-session direction. Source: Shen, Urquhart, Wang, *Financial Review* 2022, T1.
- `funding_percentile_extreme(lookback)` = funding rate's percentile rank vs. trailing window;
  threshold TBD from Memon 2026 (already gated, see whale_positioning_evidence file), T2.
- `carry_signal` = rank perps by funding rate, long low/short high (or single-asset directional
  fade of extreme funding). Source: Fan/Jiao/Lu/Tong SSRN 4666425 (cross-sectional) and
  Borri/Liu/Tsyvinski/Wu arXiv 2510.14435 (regime caveat), both T2.

## DISCARD LIST

- BB/Keltner squeeze - REJECT, vendor/blog only, no cost-adjusted OOS evidence.
- VWAP-band mean reversion - REJECT, same reason.
- Anchored VWAP swing reversion - REJECT, anecdotal only, no backtest with costs found.
- Standalone RSI divergence - REJECT, hindsight-dependent, no robust backtest; existing `rsi`
  layer's confirmation-filter requirement is consistent with this and needs no change.
- Standalone ICT/SMC (order blocks, FVG, OTE) without HTF/session filters - REJECT; verified null
  result (SSRN 7483658) is stronger than the pre-gate report claimed (no combination was shown to
  rescue it, contrary to the original text - see citation-check table). Existing `cryptocred`
  layer's structure+retest combination is not directly validated by this paper either (SPX, not
  BTC) but is not contradicted for the combined case, since the paper does not test combinations.
- "Combining HTF liquidity draw + session killzone + 1:2.5 RR transforms it to positive" - REJECT
  as a citation claim (mismatch, see Step 3a); do not re-cite SSRN 7483658 for this claim again.
- CME weekend-gap fill - confirmed dead (CME 24/7 verified true), setup discarded as before.
- Naive weekend/day-of-week calendar effect - no new evidence, discarded as before (concentrates
  in a single Sunday UTC window, not a tradable weekly pattern).
