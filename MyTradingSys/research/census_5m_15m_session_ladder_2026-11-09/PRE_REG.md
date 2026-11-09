# PRE_REG: 5m/15m session x HTF-ladder x node-target census (card census-5m-15m-7y-session-ladder-1109)

Status: written before any outcome was simulated. Only the event COUNT pass ran (`census_session_ladder.py --count-only`, no R computed).
Template: MyTradingSys/backtest/PRE_REG_TEMPLATE.md. Diagnostic only: testnet does not wait on it (d-phase-first-method-1106).
Code: MyTradingSys/research/tom_fabio_course_correction_2026-11-07/census_session_ladder.py (header = parameter table, SOURCED file:line / OURS).
Inputs: public BTCUSDT 5m, data.binance.vision: futures/um monthly 2020-01..2026-10 + um daily 2026-11-01..07; spot monthly 2019-01..2019-12
(the mirror holds no um 5m monthly before 2020-01, probed 2026-11-09, so "2019-09 on" is 2020-01 on). 15m = three aligned 5m bars.
Window 2019-11-08..2026-11-06 (same start as the 1h census). Bars carry taker-buy volume: delta = 2 x taker_buy - volume (the 1h census had none).

## Context

- Regime: ladder D = prior-day close vs SMA20, W = last full week close vs SMA10w, M = last full month close vs SMA6m (idea SOURCED Tom TOM-053 Ld1dhjGdTCA:19; lengths OURS). align_n = how many of the 3 agree with the trade direction. HEADLINE gate align_n >= 2 (OURS, fixed now); align_n 0..3 reported in full.
- Phase: FAST_REJECTION (probe beyond a prior-day/week level, reclaim, classifier unmodified). Bible phase (range 75.4-80.9k since 2026-10-24, BIBLE.md:28) reported as its own split; the other 7 y is the pool.
- Session: HEADLINE = in-block only: LON 09:00-12:00 Europe/Berlin (Tom DAX cash, 5Ljfwvtktek_raw.txt:7), NY 09:30-12:30 America/New_York (Fabio, Pz8f0wWW12M:655); DST-aware. All three blocks (LON/NY/OTHER) reported; OTHER is the comparison.
- Entry: market at the close of the first firing bar (as the 1h census; maker fill at that price is assumed under model D = optimistic, stated).

## 1. Source home
Tom: DAX cash 9-12, weekly/daily profile then 5m (TOM-041, TOM-015). Fabio: NQ, NY session, 1m footprint (8CWKfoSJu3c_raw.txt:7). BTC 24/7 has no cash session, so the blocks are the closest analogue (OURS). Holding period: 8 h horizon (OURS).
## 2. Ground truth ledger
NOT_ANSWERED by design: this is a census of the classifier's events in the traders' frame, not a recall test of their trades (Fable review a.: "Hand-picked winners are not evidence"). Label: diagnostic, no core.
## 3. Recall / fire rate
Fire rate = counts below. Recall is not claimed.
## 4. Data inputs
Aggressor side: taker-buy volume per bar = delta (bar level, not footprint). Footprint, OI, funding: NOT_IN_DATA, not used. Funding omitted (FORMULAS s13: fee_r understated ~20% in the 1h census; here +2 bps RT slippage is added on both models).
## 5. Profile parity
Profile code = unmodified `compute_volume_profile` on prior UTC-day bars (spread_range). NY-session profile not built (card tf-ny-session-va-profile-1109); no parity check against the operator's drawn levels (0g waived: no operator marks involved).
## 6. Cost per instrument
Model T taker 5 bps/side (fees.py:32). Model D FEES_DERIBIT (fees.py:48; entry+target maker 0, stop/BE/timeout taker 5 bps). +2 bps RT slippage both. Stop width reported (bps, p25/median/p75); fee gate 10 bps RT / stop bps <= 0.25 R (d-stops-follow-trade-1106) reported as a split, not applied to the headline.
## 7. Fills
Touch and trade-through NOT separated: entry assumed at the signal close for both models. Model D's maker entry is therefore an upper bound on net R (no-fill and adverse-selection unmodelled).
## 8. Exits
Variants: B1R (old 1R bracket, the baseline), NODE (T1 = nearest prior-day POC/VAH/VAL/HVN/PDH/PDL/PWH/PWL >= 1.5R), NODE_BE (BE once +1R traded), HALF_BE (BE +1R, half off at T1, rest to T2 else horizon), TRAIL (BE +1R, stop trails 1R behind best, no target). Trader sources: TOM-018, TOM-014/017, fZlNGWvd2Ko:43-61 (all SOURCED in kind; node floor 1.5R, half split, 1R trail OURS). Node variants only exist when a node >= 1.5R is on the trade side; the count with a node is reported.
## 9. Null like-for-like
B1R on the SAME events is the null; the 1h census null is -0.087 R at 1R (REVIEW_FABLE.md). Out-of-session events (OTHER) and align_n < 2 are the in-frame comparison sets. Placebo (random-time events) NOT run; a positive result would need it before any claim.
## 10. Power (computed before the run, from the event count pass)
Count pass: 5m 6791 events, in-session 1394, headline (in-session and align_n >= 2) 698; 15m 5617 / 1192 / 601. Net R per trade SD ~1 R at a 1R shape, so SE ~ 1/sqrt(698) = 0.038 R and the minimum detectable mean at 80% power is ~0.105 R for the headline cell (15m ~0.114 R). Per-session x regime x year cells fall to n < 100: marked UNDERPOWERED, never "no edge". Overlap: events share bars within a 4 h cooldown per level, so the true SE is a little larger.
## 11. Holdout
None: single-pass census, 0 redesigns, 1 trial per timeframe x variant (10 headline cells; any p-hacking is bounded by reporting all 10 plus the 2 fee models). A positive headline cell goes to testnet forward (card tf-testnet-forward-range-phase-amend-1109), not to a holdout fit.
## 12. Stratified readout
By session block, ladder align_n, regime (D SMA20 +-2%), year, Bible phase, fee gate, delta, next to the pooled number: see RESULT.md.

Kill / read rule (OURS, fixed now): the frame "has something" only if the HEADLINE cell net R (model D) is > 0 by at least 2 SE on BOTH 5m and 15m for some node/mgmt variant, AND the same variant is not positive in OTHER-session / no-gate cells to a similar degree (then it is not a session/ladder effect). Anything else = no edge in this frame; the testnet forward run is unaffected.
