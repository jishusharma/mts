# EXTRACT: Fabio Valentini (Fabervaale ENG) — cUTsoU-15Tc
# Title: "The Simplest Orderflow Trading Model"
# Duration: 24:46 | Instrument shown: NASDAQ (NQ), multi-session backtest replay
# Source text: auto-generated YouTube captions (word-level timestamps)
#              /mnt/user-data/uploads/BinanceDataFeed/extracts/_staged_2026-09-27/raw/fabervaale_cUTsoU-15Tc_raw.txt
# Extractor: Sonnet worker (Phase 1, clean slate)
# Date extracted: 2026-09-27 | Status: EXTRACTED | Phase: 1 (clean slate)
# Tier: T3 (individual practitioner). Statistical claims (profit factor, Sharpe,
#       65-70% probability) are stated by Fabio with no dataset/methodology shown in
#       this video — treat as unverified vendor claims, not validated statistics.
# ---

## ASSESSMENT
This video documents a named, two-part proprietary model called "IVB" (built on top
of the classic Opening Range Breakout / Initial Balance concept, credited by Fabio to
Toby Crabel, 1990) plus a "deep charts" statistical add-on that plots probability-
weighted profit targets. Model One is a static volume-profile overlay on the opening
range (location/invalidation). Model Two adds order-flow confirmation at the profile's
sensitive levels (entry trigger). A third, minor sub-model (mean reversion inside an
undecided range) is described for use before a breakout resolves. This is the
clearest COMPLETE trade model of the three videos in this set: it has explicit entry
location, entry trigger, stop/invalidation, and target logic, all named by Fabio.

No new explicit statement addressing the reversal-vs-continuation discriminator (U2)
was found in this video beyond re-using "absorption" and "exhaustion" as directional
triggers without resolving when each implies which outcome (see UNCLEAR U2 below —
NOT ADDRESSED here, in contrast to Pz8f0wWW12M).

Clean-slate rule honoured: no Tom Vorwald or other-video (Khgj5q1-ln8, Pz8f0wWW12M)
material used while extracting this file. Caption reads "PC" for what he otherwise
calls "point of control" / "POC" throughout (he audibly self-corrects once, see
UNCLEAR) — bracketed as [POC] at first occurrence for readability, verbatim text
otherwise preserved.

---

## RULES EXTRACTED

### FAB-024 — Opening Range Breakout / Initial Balance: definition and statistical rationale
**Source:** cUTsoU-15Tc @0:00-2:55 | Tier T3 | Tag: DEFINITION + PRINCIPLE
> "A lot of traders are familiar with the opening range breakout. You buy or sell the
> breakout of the first 15 minutes of the cash session. This strategy published in the
> 1990 by Toby Crabel proven to be one of the most consistent edge over the last
> decade with a positive profit factor and an amazing sharp ratio."

> "the New York session is the session that hold the maximum amount of volume for the
> day. So you have the strongest battle between buyers and sellers... This situation
> here define a clear range and from this range you can see rejection you can see
> absorption of the buyers of the sellers exhaustion... the orb method works this way.
> You have two defined levels that are the top and the bottom of the range of the
> first 15, 30 or 60 minutes. It depends how you want to use it... what the model says
> is that the first one that break is telling you who won the battle of the most
> important time of the day."

> "from a statistical point of view, this one have a strong value in predicting the
> direction for the day at least till certain level that you can use as high
> probability profit target."

Definition/rationale as stated: mark the high/low of the first 15, 30 or 60 minutes of
the New York cash session (his choice of window — "depends how you want to use it");
whichever side breaks first is read as the winner of the day's highest-volume battle
and used as a directional signal for the rest of the day, with a target level
computed from that read. The strategy's origin and outperformance claim (profit
factor, Sharpe ratio, "over the last decade") is attributed by Fabio to Toby Crabel's
1990 published work — no dataset or figures are shown in this video.
**UNDEFINED:** which window (15/30/60 min) to use and by what criterion; the
"statistical...strong value" claim is not quantified in this video; no citation/data
for the profit-factor/Sharpe claim beyond naming Crabel.

### FAB-025 — IVB Model One: fixed-range volume profile over the opening range defines location, point of control, and invalidation
**Source:** cUTsoU-15Tc @4:19-6:26 | Tier T3 | Tag: DEFINITION + PROCEDURE
> "the model one of IVB is using the following. We have point A and we have point B.
> How can we define this point A and point B? This is the opening of the New York. We
> have a top. We have a bottom on the first 15 to 30 minutes. Okay. This is our point
> A and this is our point B and the price is inside this value for 15 30 depends on
> what you prefer to use."

> "we take this top, we drag down with the fixed profile to this level. Why this gets
> interesting? Because now we not only have price but we have the volume distribution
> of the most important interaction of the day. And we can notice that the major point
> of control so the P[O]C so the level where the majority of volume of the market
> participant it's here. Okay, this takes the name of P[O]C."

> "the most sensitive level after you have this is the level contained between the
> value area and the P[O]C. This is our real block of orders. This is where when you
> retrace you can expect buyers to reload."

> "you also have a level of invalidation if broken. So you have a value area low that
> if it gets broken, so the market accept it, it's an invalidation point... If we close
> a candle here, okay, the setup is invalidated. So our real risk-to-reward is this
> from here to the first protection point."

Procedure exactly as stated:
  1. Anchor a fixed-range volume profile from point A (opening-range top) to point B
     (opening-range bottom), over the first 15–30 minutes of the New York session.
  2. Identify the point of control (POC — "the level where the majority of volume...
     it's here") within that profile.
  3. Treat the zone between the value area and the POC as "the real block of orders" —
     the level where, on a retracement, buyers (or the winning side) are expected to
     reload.
  4. Treat the value-area low (or high, direction-dependent) as the invalidation
     point: a closed candle beyond it invalidates the setup, and risk is measured from
     entry to this level, not to the far side of the range (his stated risk-to-reward
     is therefore not a naive 1:1 of the range).
**UNDEFINED:** exact profile bin/tick size; precisely which boundary (VAL vs VAH) is
the invalidation reference depends on trade direction, not spelled out generically;
how "the first protection point" is chosen when there are multiple candidate levels.

### FAB-026 — Deep-charts algorithmic "protection level" target with stated probability (unverified, black-box)
**Source:** cUTsoU-15Tc @7:56-9:06 | Tier T3 | Tag: TARGET
> "let's do deep statistical analysis. Okay let's go through years and years of data
> and use an algorithm using neural network machine learning or digging into the data
> to see what's the highest probability point that the market reach when you have a
> breakout of the initial balance or orb. Okay. And what the IVB does is that when you
> have a breakout, okay, it plot for you the high probability profit target, okay, and
> the potential TP2. So you know that with 65 to 70% probability, you go here and you
> know that with another lower probability, of course, you go to the TP2."

Rule as stated: after an IVB/ORB breakout, a proprietary algorithm (stated as
"neural network machine learning," undisclosed methodology) plots a first profit
target ("protection level," 65–70% stated hit probability) and a second, lower-
probability target (TP2). This is a quantified claim, but it comes from an
undisclosed, unverified black-box model with no dataset, sample size, instrument
scope, or backtest methodology shown — flag as vendor claim, not validated statistic.
**UNDEFINED:** the algorithm's inputs/training data; sample size and time period
behind the 65–70% figure; TP2's probability (only described as "lower"); whether the
figure is specific to NASDAQ/this session type or general.

### FAB-027 — IVB Model Two: order-flow confirmation at the profile's sensitive level (absorption → long trigger; exhaustion+momentum → tight-stop trigger)
**Source:** cUTsoU-15Tc @6:53-8:04 | Tier T3 | Tag: ENTRY + STOP + SETUP-CONDITION
> "the model two of IVB is using orderflow... it's using the confirmation after the
> breakout. Okay, so we have a range, we have a point A, we have a point B, we have
> our profile... we have our framing area to seek buy. Okay, we have a breakout, we
> have the market retracing, and now we can start using the confirmation of order
> flow... Maybe we have a lot of aggressive sellers here with zero result. This means
> that there is a big absorption on this level on the P[O]C. Okay, so we can use this
> as a confirmation trigger to go long or maybe you can see an exhaustion. So you can
> see that the sellers don't interact. We have aggressive buyers with momentum at the
> top and you can take a momentum trade with a really tight stop-loss to go to the
> protection level."

Rule as stated: after a breakout of the IVB range and a retracement back to the
profile's sensitive zone (value area / POC, per FAB-025), read the order flow at that
level for one of two confirmation patterns: (a) heavy aggressive selling with zero
price result = absorption at the POC → trigger to go long; or (b) sellers failing to
interact at all while aggressive buyers show momentum at the top = exhaustion of the
opposing side → take a momentum trade with a tight stop, targeting the protection
level (FAB-026).
**UNDEFINED:** what counts as "zero result" vs a small result (threshold); how tight
"really tight stop-loss" is; how long to wait at the level for either pattern to
appear before abandoning the setup.

### FAB-028 — Mean-reversion sub-model while the range's direction is undecided, switching to trend-following once confirmed
**Source:** cUTsoU-15Tc @9:55-10:40 | Tier T3 | Tag: SETUP-CONDITION + PROCEDURE
> "if you are inside this level okay you have the opportunity to fade the top and the
> bottom using a mean reverting okay because you know that till the market don't break
> completely this level the direction is not clear so you can also use a mean
> reverting model that is spotting the absorption of the sellers of the buyers the
> exhaustion on sensitive areas that are the top and the bottom of the range to take
> some mean reverting trades okay with high probability and then maybe use this profit
> to get trend following when you have enough confirmation that the market decided
> where to go."

Rule as stated: while price stays inside the IVB range (direction not yet resolved),
fade the top and bottom of the range using the same order-flow patterns (absorption,
exhaustion) as mean-reversion trades; once the range breaks with "enough
confirmation," redeploy that accumulated profit into trend-following trades in the
confirmed direction.
**UNDEFINED:** "high probability" is an unquantified claim; what specifically counts
as "enough confirmation" of a decided direction (distinct from FAB-027's single-level
confirmation, but not distinguished further here).

### FAB-029 — Entry and stop at a level being actively defended by aggressive orders
**Source:** cUTsoU-15Tc @19:59-20:08 | Tier T3 | Tag: ENTRY + STOP
> "when you have aggression of the buyers for example here okay they are protecting
> the area you can consider a buy with a stop loss below that goes to the protection
> level."

Rule as stated: when the buy side shows aggression actively defending (protecting) a
level, that is itself an entry trigger for a buy, with the stop placed below the
defended area and the target set at the protection level (FAB-026).
**UNDEFINED:** how much aggression / how many defense attempts qualify as
"protecting" the area versus an isolated print; exact stop distance below the area.

---

## UNCLEAR
- U1 caption "PC" for point of control: he says "PC" repeatedly ([5:07], [5:09],
  [7:11]) then self-corrects once at [7:11]-[7:14] ("we have the value area low, we
  have the PC, sorry, the value area high, the P[OC]") — read throughout this file as
  a transcription of "POC" (point of control), bracketed as [POC] where quoted.
- U2 (open question carried from the template/other extracts): does this video state
  when absorption/exhaustion at a level implies REVERSAL vs BREAKOUT/continuation?
  NOT ADDRESSED. FAB-027 and FAB-028 both use "absorption" and "exhaustion" purely as
  entry TRIGGERS in a predetermined direction (the direction already established by
  the IVB range break or the fade side he has chosen) — he never states a rule for
  which pattern, on its own, would predict a reversal versus a continuation. The video
  assumes the direction is already known (from the ORB/IVB break, FAB-024) and uses
  order flow only to time/confirm entries within that known direction.
- U3 @19:00-19:28: garbled/self-contradictory passage about "rewarded buyers" and
  "absorbed sellers" at one interaction versus the reverse at another ("the buyers are
  actually trying to push the auction up and they are winning this battle" following
  a description that reads as sellers having more result) — likely auto-caption
  damage or a mid-sentence topic switch between two different chart clusters he is
  pointing at live. Best guess: he is contrasting two separate order-flow clusters to
  illustrate "who is winning the battle" as a way to locate a reload level, consistent
  with FAB-027/029, but the transcript does not support extracting this as its own
  clean rule.
- U4 @19:44-19:52: "view up" — possibly a mis-transcription of "VWAP," mentioned in
  passing as one of several ways to "qualify important areas" alongside volume
  profile and supply/demand; too brief and uncertain to extract as a rule.

## EXCLUDED
- @1:04-1:14: subscribe/like call-to-action and "go on deeparts.com" promo for the
  IVB model product — marketing, no rule content.
- @11:01-24:46 (large portion): live backtest replay narration ("let's speed up,"
  "let's go to the next one," session-by-session play-by-play) — illustrates FAB-025/
  027/028/029 with specific chart numbers (e.g., "122 total contract," "273") that are
  EXAMPLE VALUES only, not thresholds; not separately extracted as new rules beyond
  what FAB-025–029 already state.
- @0:00-0:11, @24:20-24:46: intro/outro framing.

## SUMMARY
| Category | Count |
|---|---|
| DEFINITION | 1 (FAB-024, also tagged PRINCIPLE) |
| PROCEDURE | 2 (FAB-025, FAB-028, both also tagged with a second category) |
| TARGET | 1 (FAB-026) |
| ENTRY | 2 (FAB-027, FAB-029, both also tagged STOP) |
| SETUP-CONDITION | 2 (FAB-027, FAB-028) |
| Total rules | 6 (FAB-024–FAB-029) |
| Numeric thresholds given | 1 stated but unverified/black-box (FAB-026: 65–70%) |
| UNCLEAR items | 4 |
| U2 verdict | Not addressed — order flow used only to time entries within an
  already-established directional bias, not to discriminate reversal vs continuation |
| Trade model named | "IVB" (Model One: profile/location/invalidation; Model Two:
  order-flow confirmation entry), layered on the Opening Range Breakout / Initial
  Balance concept credited to Toby Crabel |

# END
