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

Why the divergent market is expected to revert:

> "a move like this is always caused by a major imbalance, usually by option traders finding themselves in significant trouble or futures traders hedging their bets"
**Source GPS: T6hDJcHrVBM | MIDDLE**

The rule, in one sentence (either side):

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

- Tom gives NO threshold: no lookback, no "how divergent", no correlation figure. Everything numeric is ours to pre-register.
- Divergence = a pre-set basket (BTC, Nikkei, S&P/ES, DAX) where one member's multi-day return sign or size differs from the rest; the outlier is the fade candidate.
- It is a CONTEXT filter plus candidate source; entry stays the existing TOM-1 counter-trade chain (idea -> proof -> setup -> stop). Never a stand-alone entry.

## 3. Gap check vs the Tom catalogue (SETUP_CATALOG.md)

| Item | In catalogue? | Where |
|---|---|---|
| Counter trade after an imbalance push (the trade he takes on the DAX) | YES | TOM-1 (T6hDJcHrVBM and zQTbdEweG3c are TOM-1 evidence) |
| "Other markets not confirming" as required context | YES, PARTIAL | TOM-1 s.4 context; checklist row "other markets not confirming" = PARTIAL (ETH on disk, ES/NQ not) |
| Correlation/divergence as a rule with a basket, trigger and fade-the-strongest/weakest direction | NO | no numbered setup, no rule |
| "Bitcoin weak = risk-off" premise as a filter | NO | not in catalogue |
| Entry-timing discipline ("enter far too early" is the common error) | PARTLY | TOM-1 proofs/setup chain; not tied to divergence |
| Operator item T054 (BTC vs US equities correlation) | OPEN, nothing built | MyTradingSys/items/T054_us_session_news_correlation.md |

Verdict: this is a GAP in a rule, not a new setup. Proposed Tom-layer change (propose only; nothing edited, layer is G2 and rules change only after fee-net OOS):
1. ADD a context-filter rule TOM-CTX-DIV (OURS parameters, label OURS): "TOM-1 counter trade is allowed/prioritised only when the target index diverges from the basket; blocked when a fundamental story explains the divergence".
2. CHANGE the TOM-1 checklist row "other markets not confirming" from PARTIAL to testable once ES/NQ/Nikkei/DAX daily bars are on disk.
3. Do NOT add BTC to the DAX rule on faith: his BTC premise is a claim, test it (Section 4).

## 4. Pre-registered test (frozen before running; details in the cards)

Baseline (OURS, Eagle_Eyes 2026-10-26): BTC vs SPX/NDX same-day daily-return r=+0.34/+0.35 over 60 sessions, +0.58/+0.57 over 20; BTC prior-day vs next index session r~0. So BTC "leading" is not supported at daily lag; use BTC as a same-day basket member only.

- H1 (DAX leg, primary): daily bars DAX, ES, Nikkei, BTC. Divergence day = DAX 2-day return sign opposite to the median sign of the other three AND |DAX 2d return| in top quintile of its trailing 250d. Event: TOM-1 style fade (short if DAX up). Outcome: DAX next-1/2/3-day forward return net of fee+slippage; entries through the existing Tom entry chain on intraday data where available, else daily proxy (state which).
- H2 (BTC leg): BTC as the outlier vs ES/NQ/DXY, same rule, forward BTC return.
- Control: same entries without the divergence filter (does the filter add edge over plain TOM-1?).
- Splits: DEV (older 70%), VALIDATION once, holdout read once (date fixed in the card). Variants (lookback 1/2/3/5d, basket sets, quintile cut) all logged in the trial ledger; no variant picked on VALIDATION.
- Pass: fee-net expectancy > 0 on VALIDATION and holdout with n >= 30 events and filter beats control. Otherwise layer rule stays unadded.
- Data: ES/NQ/Nikkei/DAX from Yahoo chart API (free public), BTC from data-api.binance.vision.
