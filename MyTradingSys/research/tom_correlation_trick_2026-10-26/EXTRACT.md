# Tom's "correlation trick": extract, gap check, test plan (2026-10-26)

Status: the live stream "LIVE TRADING: DAX Short Using My Correlation Trick!" is NOT yet read (live streams have no captions until they end; card `tom-corr-live-captions`). Everything below is from two older Tom videos already on disk that describe the same idea. SOURCED = Tom's words; OURS = our reading.

## 1. What the trick is (SOURCED)

Definition:

> "Correlation is when markets usually behave the same way, but suddenly one market, for example, takes a completely different direction."
**Source GPS: T6hDJcHrVBM | BEGIN**

Basket and risk-off premise (Bitcoin is one of the four):

> "my logic and analogy is that when Bitcoin starts to weaken, then it's definitely a bit of a riskoff"
**Source GPS: T6hDJcHrVBM | BEGIN**

The anomaly he trades (DAX up while Nikkei, S&P, Bitcoin down):

> "the DAX rose extremely sharply even though the Nikki, Bitcoin, and the SNP were simultaneously following this specific path"
**Source GPS: T6hDJcHrVBM | BEGIN**

Why the DAX open spike is expected to correct (this is about the intraday open spike, NOT cross-market reversion; linking it to the divergence is OURS):

> "a move like this is always caused by a major imbalance, usually by option traders finding themselves in significant trouble or futures traders hedging their bets"
**Source GPS: T6hDJcHrVBM | MIDDLE**

The rule, in one sentence (ambiguous: 'trade the weakest market' may mean with or against its move; the two-sided fade reading is OURS):

> "always look at how Bitcoin is doing, how Nikki is doing, how America is doing, and how Europe is doing. And if you see that something is very non-uniform, then you can trade the strongest market in the opposite direction or even the weakest market"
**Source GPS: T6hDJcHrVBM | END**

Exclusion (news story):

> "if for example fundamental news had led to one market being extremely strong and the other not then that's a different story"
**Source GPS: T6hDJcHrVBM | END**

Second variant, trade of the month (divergence turns, DAX stalls while the others recover):

> "the DAX future, and this is the truly decisive point, stopped rising even though it had been coming from a strong downtrend"
**Source GPS: zQTbdEweG3c | BEGIN**

The correlation is only the idea; entry needs proof and a setup:

> "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management"
**Source GPS: zQTbdEweG3c | BEGIN**

> "I used correlations for myself in a way that they are logical and also work. And that's exactly a point that many people get wrong again and again and enter such trades far too early"
**Source GPS: zQTbdEweG3c | BEGIN**

## 2. OURS interpretation (not Tom's numbers)

- Tom gives NO threshold: no lookback, no divergence size, no correlation figure. Everything numeric is OURS and pre-registered below.
- Timing matters more than the divergence: in zQTbdEweG3c he entered when the divergence began to RESOLVE (S&P and BTC recovering, DAX "stopped rising"), and names entering on the divergence itself as the common error ("far too early").
- It is an idea source ("strategy when things go differently") feeding the TOM-1 counter-trade chain, not a gate and not a stand-alone entry; most TOM-1 ledger trades cite no divergence.
- Third source on disk: ledger row T11 = liEJMfE_PXg "DAX Future Short with Correlation Trick" (frames only, `TOM_TRADE_LEDGER.csv:32`); the live stream is a fourth.

## 3. Gap check vs the Tom catalogue

| Item | In catalogue? | Where |
|---|---|---|
| Counter trade after an imbalance push | YES | TOM-1 (T6hDJcHrVBM, zQTbdEweG3c are TOM-1 evidence) |
| Other markets (index/crypto) not confirming the push, as a condition | PARTIAL | `tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:62` condition A-C4 (ES, NQ, BTC same-window return); no basket, threshold or news test; catalogue row "other markets not confirming" sits in TOM-1a's intraday BTC table |
| Divergence as a named candidate generator with a basket, a convergence-start trigger and fade direction | NO | not a numbered setup or rule |
| "Bitcoin weak = risk-off" premise | NO | Tom's claim, not a tested rule |
| News-explained divergence excluded | NO (untestable now) | catalogue: news = NO; proxy by macro-calendar days only |
| Operator item T054 (BTC vs US equities) | OPEN, nothing built | MyTradingSys/items/T054_us_session_news_correlation.md |

Data: DAX ticks (`F:/MTS/data/dax_raw`, bi5 from 2024-10) and `nq_raw` exist on disk, so "ES/NQ not on disk" in the older catalogue is stale for the intraday window; the long daily history still needs Yahoo.

Verdict: a rule gap on top of A-C4. Proposed Tom-layer change (propose only; layer is G2, rules change only after fee-net OOS):
1. ADD TOM-DIV as an additive FLAG and candidate generator (OURS parameters), never a gate; trigger = convergence start, not divergence day.
2. A-C4: extend with the basket definition once TOM-DIV passes; news half stays NOT TESTED.
3. Do NOT add the BTC risk-off premise; test it as H2.

## 4. Pre-registered test (frozen before running)

Baseline (OURS, Eagle_Eyes 2026-10-26): BTC vs SPX/NDX same-day daily r=+0.34/+0.35 over 60 sessions, +0.58/+0.57 over 20; BTC prior-day vs next index session r~0. Same-day member only, not a lead.

- Alignment: all returns computed as-of ONE timestamp (the traded market's close) from hourly bars (BTC, ES, Nikkei, DAX); nothing after that timestamp is used. Closes differ (Nikkei 06:00 UTC, Xetra 16:30, US 20:00-21:00, BTC 00:00), so Nikkei is stale by design and flagged. Rules for BTC weekends and market holidays fixed in the card before running.
- Instrument: state DAX cash (^GDAXI) vs FDAX/FDXM future; fee+slippage numbers written in the card (OURS) before running.
- Primary variant (one, named): H1 = DAX top-quintile 2-day move (vs trailing 250 d) with sign opposite to the median of ES, Nikkei, BTC; trigger fires at CONVERGENCE START (basket turns toward the DAX direction and the DAX fails to make a new extreme); short-only if DAX up, long mirror declared. Secondary: divergence-day entry (the timing Tom warns against), reported not selected.
- H2 (BTC as outlier): basket ES, NQ-or-ES (one of them; they are near-duplicates), DXY with sign flipped.
- Controls: (a) same DAX top-quintile move WITHOUT the cross-market sign condition (isolates cross-market information from plain mean reversion); (b) shuffled-basket placebo.
- Events non-overlapping; cluster-robust SE. Expected raw events about 12-18/yr, so about 100-150 on 2017+ BTC-era data; n>=30 in the holdout may be unreachable: state in advance that a holdout with n<30 is reported as INCONCLUSIVE, not pass.
- Splits: DEV older 70%, VALIDATION once, holdout read once and ONLY if VALIDATION passes. Every variant (lookback 1/2/3/5 d, basket sets, quintile cut) goes in the trial ledger; none selected on VALIDATION.
- Pass bar (OURS): primary variant fee-net expectancy > 0 on VALIDATION with bootstrap 95% lower bound > 0 and beating control (a); then holdout. Otherwise the TOM-DIV flag is not added.
- Data: ES/Nikkei/DAX from Yahoo chart API (free public) and local `dax_raw`/`nq_raw` for intraday; BTC from data-api.binance.vision.

## 5. Review

Fable review of the first draft (12 defects) applied in this version; open question taken at default: `dax_raw` counts as DAX on disk (intraday window only).
