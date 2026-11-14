# Gap hunt 1113, worker opus_trade_replay: trade reconstruction (stage T)

Method: 10 trades that Tom or Fabio narrate from start to finish. Each trade is split into the trader's decision steps (context, level, wait, trigger, entry, stop, target, management, exit), each with his own words. Each step is then put through OUR code and marked:
MATCH (the code does what he says), MISSING (no code for it), DIFFERENT (the code does something else), OURS-NUMBER (the code has the step, but with a number he never gave).

Inputs: `origin/fast-track` at 283abe663. Transcripts `raw_transcripts_canonical/<id>_raw.txt`. Code: `auction_context.py` (classify_level_interaction :570, build_auction_trade_plan :821), `layers/fabio/v3/{signals,models,manage,day_gates,engine}.py`. Iteration 1 = `tf_extraction_plan_1113/` (ANSWERS_FROM_DISK, out/tf-x2..x5) plus the fact sheet `concept_decks_1112/TOM_FABIO_FACTS.md` section H.

Quote rules: every double-quoted span is copied from the transcript named in the section heading (or the id written just before it), with the line number of its first word. Timed files are joined across caption lines with the `[m:ss]` stamps removed. Is1HvdfQm5c is ASR (machine transcription): its quotes are labelled ASR. Speaker of 9IliXww64uM is UNSETTLED (iteration 1 Q13: Fabio or Andrea Cimi), so T4 and T5 carry that flag. All quotes were machine-checked (see the last section).

## 0. Desk replay: the narrated geometry run through our code

The traders' charts are NQ / ES / DAX / crude, which we do not hold as bars. I drew each narrated trade as synthetic 5m bars with the same shape (level, sweep size, volume pattern, stop and target distances) and called our real functions on them. Script: `gap_hunt_1113/opus_trade_replay_desk.py` (run: `python -I opus_trade_replay_desk.py <dir holding a git archive of the trunk code>`). These are shape tests, not P&L.

| run | narrated trade | our verdict | our plan | what he did |
|---|---|---|---|---|
| R1 | 9IliXww64uM trade 1: IB low swept 4 pts, volume up both ways, negative delta + up close, long at the 5m close, target other side of range | FAST_REJECTION, V2 sweep, rel vol 6.0 (MATCH) | taker: SKIP_FEE_TRAP (stop 20 bps, fee 0.50 R); maker: SKIP_LOW_RR (stop buffer 5 bps pushes R to 1.15 < 1.20); maker with buffer 0: TAKE, 1.53 net R | took it, closed at the other side of the range |
| R3 | 9IliXww64uM trade 3: opening-range low broken by big sells, short-term value builds outside, then that mini value area breaks | ACCEPTED after only 2 mini-range bars (4 closes beyond = n_early) | SKIP_LOW_RR: stop = broken level + 25 bps min = 69 bps away; target VAL = 0.83 R | waited for the mini range, then sold its break; stop above the mini range = 2.27 R to the same target |
| R4 | k0zm5NYn0IQ: DAX open spike above prior-day VAH on 'I have to buy' volume, flat top, Tom SHORTS | ACCEPTED, continuation | plan side = LONG (opposite); SKIP_LOW_RR | short, 20 pt stop (8.2 bps), R 1:6; fee gate would read 1.22 R fee at 10 bps taker |
| R5 | kXhIAug0Gh8: open far below, rally into prior VAH 6050, stalls under it 7 bars on falling volume, Tom SHORTS | ACCEPTED, balance_hold (bars_in_zone >= 6, no probe) | SKIP | short at the rejection, target value, R about 4:1 |
| R6 | 8CWKfoSJu3c: NQ short, risk 15.75 pts (3,150 USD on 10 NQ), final target 1:19 | model D stop D = max(f x entry, structural) | f 0.3%: D = 77.1 pts (4.9x his); his 1:19 = 3.88 R in our unit; dist BE at +1D = his +4.9 R. f 0.5%: D = 128.5 pts (8.2x); 1:19 = 2.33 R | BE 'immediately', 1:19 |

Reading: on 5 of 6 shapes our code either refuses his trade (R1, R3, R5), takes the opposite side (R4), or shrinks the payoff 4-8x (R6). Only the trigger in R1 matched.

## 1. Trade reconstructions

### T1 Fabio 0jM5Y31YJak (NQ short day, world cup; one paragraph, all quotes L4)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | context | "we had some kind of balance here the market was really trying to understand where to explode" | v3 S1 `balance()` signals.py:183, R <= k_bal x sqrt(N) x ATR, k_bal 0.8 | MATCH in kind; k_bal, POC band OURS-NUMBER |
| 2 | hidden pressure | "So the market was balanced at this time but as you can see the direction from the pressure of the market and cumulative volume delta is pretty huge even before the breakout." | S2 `pressure()` :223, p grid, drift 0.25. auction_context: no delta-in-balance read | MATCH in v3 (OURS-NUMBER p, q); MISSING in auction_context |
| 3 | trigger | "the first moment that we had some kind of follow up on volume and confirmation from price was exactly this candle." | S5 `breakout()` :307, close beyond edge + big-trade push. auction_context ACCEPTED needs 4-6 closes | MATCH v3; DIFFERENT auction_context |
| 4 | stop | "The first stop loss was here." (no rule said) | `d_and_stop` models.py:38: max(f x entry, structural) | OURS-NUMBER (f 0.3-0.5%) |
| 5 | break-even | "And the first position went to break even immediately. So, the market exploded in my direction and I put my stop loss to break even." | dist BE at +be_k x D (manage.py:28, :155); D is 5-8x his stop | DIFFERENT (BE comes 5-8 of his R later) |
| 6 | adds | "I put my first stop loss to break even and I can consider to close the first trade and open a second one with the profit of the first one or just continue to add to my position in direction of the trend." | `simulate_trade_legs` manage.py:225, add only at stop >= entry: matches; but no caller outside tests | MATCH in code, MISSING in practice (not wired) |
| 7 | exit leg 1 | "And then I closed all these trades here in the second accumulation phase. Why? Because I start to see that the big trades are not pushing anymore the price down." | S8(a) signals.py:409, net big trades over 15 bars <= 0 | MATCH in kind; 15 bars OURS-NUMBER |
| 8 | re-risk | "So from this moment I waited and I took some profit and I use half of this profit to risk again." | `first_leg_risk` day_gates.py:140 = min(1, day R): risk up to ALL of the day's profit; not wired | DIFFERENT (half vs all) + not wired |
| 9 | management | "So we already commented like we already had a commentary of five different position that were trailed as the market was moving." | one leg per model call; adds max 2 (MAX_ADDS manage.py:22) | DIFFERENT (5 positions; 3-entry cap OURS-NUMBER from FABIO P22) |
| 10 | 2nd model trigger | "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position." | S3 absorbed, z_hi grid, r_abs 0.25 | MATCH in kind; OURS-NUMBER |
| 11 | de-risk at day low | "as soon as the market approach the all-time low for the day you see big traders sell continuing to push down. This is your opportunity to put the risk to zero to put your position to zero" | event mode BE needs the OTHER side's absorbed push (manage.py:167); here it is OUR side pushing at a level | DIFFERENT |
| 12 | exit | "I took profit for this position at this level. That was the low of the day" | models A/C/D: no target; auction plan targets = volume nodes only | MISSING (session extreme as target) |
| 13 | day type | "because we studied auction market theory and we know that this is a sell model day and we continue to sell" | no day-type state that keeps one side for the day | MISSING |

### T2 Fabio 8CWKfoSJu3c (NQ short, 1:19, one-trade commentary)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | risk budget | "we are risking a small amount of profit, only 3,150 to make an additional 23,000 of profit on the short position" L35 | `first_leg_risk` (risk <= day profit) | MATCH in code, not wired |
| 2 | setup | "the path of least resistance of the buyers getting completely absorbed. You can see the punch to the wall I marked for you and you can see the rewarded effort of the sellers." L40 | S5D `failed_auction` signals.py:325 | MATCH in kind |
| 3 | add gate | "We are really high in the curve and I was considering increasing additional position to contract on the way down. But the price was so aggressive that I could only position myself in discount and is not the best idea when you are already loaded with 10 contracts here to raise the exposure low in the curve." L46 | `add_allowed` S7: no short add in discount (manage.py:86-90) | MATCH |
| 4 | first de-risk | "I will lower my risk to be above the eye or a stop to zero and run this train on the way down trailing aggressively my stop loss when I see that buyers might take back control." L57 | dist: BE at +1D; event: E_opp only on an absorbed push of buyers | DIFFERENT (his first move is a stop above the latest high or BE, at once) |
| 5 | trail level | "This is an aggressive trailing stop that I take when we have already a nice floating profit." L73 | dist: trail starts right after BE, always (manage.py:161) | DIFFERENT (trail aggressiveness tied to floating profit) |
| 6 | target | "the total riskto-reward to get to the low of the curve is like 1 to 16 1 to 19 on the final target." L80 | model D: no target; plan: nearest node with net R >= 1.20 | MISSING (target = low of the session profile) |
| 7 | day filter | "This is not common. You need volatility to do these kind of trades." L84 | day gate P40 range ratio, g grid | MATCH in kind; OURS-NUMBER |
| 8 | P&L-keyed mgmt | "So if you were in loss for the day, for example, let's say minus 5,000, it will be smart to take profit and to bring your balance back to break even so you can take a next trade in a calm way." L118 | exits never read day P&L | MISSING |
| 9 | acceleration level | "I marked for you the level of the squeeze that is the level that if the market managed to break this low at 25,570 this small range that is creating now you can expect volatility on the way down." L152 | no mini-range break inside a trade | MISSING |
| 10 | stop in money | "Now I put my stop loss to stopping profit for $9,600. So worst case scenario, we close 36 $37,000." L167 | stops move only by structure (S6/BE) | DIFFERENT (he sets the locked day total) |
| 11 | partial at curve low | "we are low in the curve we are in the last point of absorption and we reach the level where I mark squeeze that is where the catalyst will happen in this case so I cover myself for $20,000 in profit on the single position" L178 | S7 curve used only as an add gate; single exit | MISSING |
| 12 | exit | "I close my stop loss in profit for 23,000 because if these buyers, aggressive buyers take back control, I want to be out of the market." L204 | S8(c) control == -s and close beyond S6 level | MATCH |

### T3 Fabio fZlNGWvd2Ko (NQ long, best session of October)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | day stop | "with a maximum drawdown that is break even. So if we go back to break even, we stop the session." L28 | `first_leg_allowed` P26 floor at 0 (day_gates.py:120) | MATCH in code, not wired |
| 2 | setup | "we see that this consolidation area got completely wrecked by buyers that took control. The sellers got absorbed here. So what I'm trying to do is capitalize on the failed auction of the seller and then aggression of the level of the buyers." L36 | S5D failed_auction + model D | MATCH in kind |
| 3 | BE trigger | "So I will be really fast in putting my position to break even if this level failed, okay? Because if this level failed, this one become the new pivot" L43 | event (iii): defended level broken -> S6 trail, not BE | DIFFERENT |
| 4 | scale-in | "I'm loading and scaling in position trying to get my losses smaller and smaller. As you can see, I'm only risking the profit of the day, okay?" L57 | add_mode "day" budget (manage.py:56); not wired | MATCH in code, not wired |
| 5 | de-risk on one print | "So I want to lower my risk because if this big trade sell gets stopped out, I don't want to be in the position because we will have a really fast snapback of the market." L68 | no link from a single big print's price to the stop | MISSING |
| 6 | worst-case lock | "So the worst case scenario, I close $10,000." L124 | no day-P&L stop placement | DIFFERENT |
| 7 | exit | "You see all these aggression and a failed auction and this is the reason I closed my trade." L143 | S8(d) climax (event mode) | MATCH in kind |

### T4 9IliXww64uM trade 1 (ES long; speaker UNSETTLED)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | bias frame | "The most important one being for framing the bias, my composite volume profile." L101; "And I typically load the last 10 days." L106; "we have a double distribution" L108 | ladder = prior day / prior week / month (auction_context build_mtf_context :384); no 10-day composite, no double-distribution read | MISSING |
| 2 | day type | "we opened the session exactly inside of the previous value area. This is already a good sign that we're probably going to stay inside of this range for the rest of the day" L173 | `price_vs_prior_va` exists (UTC day), never selects fade-vs-breakout; `prior_ny_session_profile` unused | MISSING (open location as day-type selector) |
| 3 | level | "I saw this was the initial balance, and we had an attempt that already failed, another attempt that already failed. So, I know that this is already fair value." L207 | IB only in model C (breakout); failed IB attempts not counted | MISSING |
| 4 | volume shape | "You see volume here increasing on the way out, but then also increasing all the way up back inside of the range." L232 | max rel vol >= 2.0 anywhere in the window | DIFFERENT (one spike, not both legs); 2.0 OURS-NUMBER |
| 5 | trigger | "so you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry." L239 | `absorption_seen` delta < 0 and c >= o (auction_context:675) -> FAST_REJECTION (desk R1) | MATCH; entry timing DIFFERENT (he enters before the close) |
| 6 | stop | not said for this trade | sweep extreme + 5 bps (:863); fee gate 0.25 R (:895) | OURS-NUMBER; desk R1: SKIP_FEE_TRAP |
| 7 | target | "And then I traded all the way to the other side of the range where sellers are likely to get aggressive." L249 | nearest node with net R >= 1.20 (:931-946) | DIFFERENT (desk R1: SKIP_LOW_RR with the 5 bps buffer) |

### T5 9IliXww64uM trades 2 and 3 (ES short fade, then short continuation; speaker UNSETTLED)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | trade 2 target | "Why did I take profit so early? Well, because the beginning of a strong impulse happened here, and that's typically a very strong area for a buyer response." L301 | targets are volume nodes only | MISSING (impulse origin as target) |
| 2 | breakout rule | "I don't want to just see an impulse during the breakout." L145; "So, in order to qualify a breakout, I wait for a range to form." L157 | ACCEPTED = 4-6 consecutive closes (:724-726); desk R3 fires after 2 mini-range bars | DIFFERENT |
| 3 | breakout proof | "We broke the opening range with a strong sell candle, big trades inside of the candle" L316; "Do we have a dry up in volume immediately? No." L322 | ACCEPTED ignores volume; v3 S4 big push only at the break bar | DIFFERENT (no 'volume does not dry up' check) |
| 4 | wait | "So, what I wanted to see now was from this area, from the sell zone, value being created inside of the big range." L325 | none | MISSING |
| 5 | trigger | "I take my volume profile from the top to the last of the range, and whenever I see on this short-term bearish value area, I want to see a breakout of this level." L338 | none (trigger = count of closes beyond the old level) | MISSING |
| 6 | stop | (implied: above the short-term value area) | broken level + max(buffer, 25 bps) (:868) | DIFFERENT (desk R3: 69 bps stop, 0.83 R vs his 2.27 R) |
| 7 | target | "we reached the final target, which was the other side of the previous day value area." L357 | VAL is a valid node | MATCH in kind; plan rejects it on R (desk R3) |
| 8 | day end | "Three trades, perfectly executed, no need to force the hand anymore." L353 | MAX_FIRST_LEGS 10 (day_gates.py:15) | OURS-NUMBER (no 'done after a good day' rule) |

### T6 Fabio Is1HvdfQm5c (NQ short, live session; ASR)

| # | step | his words (ASR) | our code | mark |
|---|---|---|---|---|
| 1 | setup | "the trade that in 2025 gave me the most amount of money is the test of this level with the confirmation of absorbed buyers" L139 | S5D (absorbed, then break) / FAST_REJECTION | MATCH in kind |
| 2 | proof count | "you have an absorption at the top okay you have an aggression that is rewarded so these buyers no follow through the aggression rewarded and the buyers again absorbed you have three order flow information going in the same direction" L140 | S5D needs one absorbed bar + one push; FAST_REJECTION needs rel vol OR absorption | DIFFERENT (his trigger is a 3-step sequence) |
| 3 | stop + R | "this is your opportunity to jump in with a super small stop loss okay you can cover yourself above the area and shoot for a 1 to 4.5" L144 | stop above the area: MATCH; size floor f 0.3-0.5% and fee gate 40 bps | DIFFERENT (floor) |
| 4 | targets | "when you have an absorption and a strong move down, the aggression of the last sellers is your first point of interest." L156; "We are going to the origin of the movement from where they from where they rejected" L161 | targets are volume nodes | MISSING (aggression points as targets) |
| 5 | BE speed | "we have time To go stop losing at zero so fast not even one candle it's better to take three brekivan for brekivan that losing money" L435 | BE at +1D | DIFFERENT |
| 6 | partial | "You will take out your take profit your partial your first take profit." L459 | single exit per leg | MISSING |
| 7 | day stop | "if I start with a loss I continue till 3 if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day" L466 | DAILY_STOP_R = -3.0 R (day_gates.py:16, NO-SOURCE) | DIFFERENT (count of stops vs R sum) |
| 8 | limit entry | "you can put a limit order this level with a stop loss between this aggression and when you have another confirmation from the buyers you can put your stop loss to zero like we did before" L891 | model rest limit (models.py:62) | MATCH (entry); BE-on-confirmation DIFFERENT |

### T7 Fabio DyS79Eb92Ug (NQ long from VAL, live with host)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | wait at open | "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session." L114 | models A/B/D can enter from the open bar (only C waits for the IB) | DIFFERENT |
| 2 | chart type | "I I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated." L149 | 1m / 5m time bars everywhere | MISSING |
| 3 | plan | "This this is the the setup that I explained in chart fanatic that is going from the value area low in a momentum day to the value area high" L186; "Going to target the value area high." L174 | plan takes the NEAREST qualifying node | DIFFERENT |
| 4 | order type | "I can start to build by stop. What does it mean that if the market gets heavily absorbed here I want to be cover below this low." L198 | rest = limit at the level; confirm = taker next open | DIFFERENT (buy-stop entry) |
| 5 | cancel | "They breached the level. Okay. So, what I'm doing now is cancelling the buy stop and going to consider another area. So, this one is not valid." L208 | model D cancels on a close beyond lvl (models.py:248) | MATCH |
| 6 | fallback + day bias | "So this is the second area that I can consider. If this area gets broken, I don't want to be long for the day." L222 | no second area; no day-side lock | MISSING |
| 7 | partial size | "One, two, three contract going for four. We are going to cover ourself below here. It's only $2,000 risk." L230; "Now, I didn't load it full size because I want to scale as we go up." L237 | first leg = full q1 | MISSING |
| 8 | grade | "Why AAA setup? Value area low. So we are really low on the curve." L261 | sizing_tier from HTF bias only (:957) | DIFFERENT |
| 9 | BE | "In 1 minute the position is risk-free. So we are risking zero to make 10,000." L271 | BE at +1D | DIFFERENT |
| 10 | tight stop near target | "so I will be really tight with my stop loss because every tick down that it takes is like five 5 $500 that I give back to the market." L355 | trail by structure only | DIFFERENT |
| 11 | day stop | "I don't let the market take seven, eight stop loss. My rule was three losing trades to stop is exactly what we did here" L2012; "in the starting of the session. I give more room. I have four or five because usually you have consolidation and then expansion." L2016 | -3R sum, same all day | DIFFERENT |

### T8 Tom k0zm5NYn0IQ (DAX counter-trade short; one paragraph, all quotes L19)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | context | "From the volume profiles, we are of course above the previous day. That means it's a very risky trade" | price above prior VA + closes beyond -> ACCEPTED continuation LONG (desk R4) | DIFFERENT (opposite side) |
| 2 | idea | "In my opinion, the market open was too extreme. And above all, it wasn't accompanied by real volume, but rather there was an I have to push sentiment." | no 'forced open / no real volume' state | MISSING |
| 3 | idea | "And we also had a finished auction. That means the market formed a completed auction at the top." | no finished-auction detector | MISSING |
| 4 | cross-check | "If I look at the American futures as a counterpart, I also see that there is much much less action there." | E10 tested a divergence trick, not this 'activity' check | MISSING |
| 5 | entry | "I'm entering a short trade right here. Even though the market looks extremely strong, I can clearly see that there's no liquidity left." | needs probe + reclaim (:747) | DIFFERENT (he enters before any reclaim) |
| 6 | stop | "For the first position, I'm setting a stop-loss of 20 points in the DAX." | fee gate stop >= 40 bps; 20 pts = 8.2 bps | DIFFERENT (gate blocks; fee 1.22 R) |
| 7 | target | "I actually want to get back below the liquidity from this morning specifically into this free session impulse that we saw here." | volume nodes only | MISSING (pre-session impulse origin) |
| 8 | no trail | "In this case, I don't do that because I just see that the overall position with a riskreward ratio of about 6 to1 is simply so good that I don't worry about it." | dist: trail always after BE | DIFFERENT |
| 9 | add before BE | "If we now see the area around 13 again, right here and here, and see the sellers show up, yes, then I'm definitely willing to increase the position once more. With this, I now also have my total loss of about $1,000." | add_mode be: add only when stop >= entry (manage.py:91) | DIFFERENT (Tom adds while at full risk) |
| 10 | stopped, re-enter | "Now we've been stopped out and that's just part of it." ; "And now I am actually going to proceed with entering another trading position. I'm giving the market an initial stop of $500 again for now." | one filled trade per model call; no same-idea re-entry | MISSING |
| 11 | re-entry rule | "if you realize that your basic idea wasn't correct, but you just got stopped out, you can definitely do this. Then you can definitely enter the position again here." | none | MISSING |
| 12 | add trigger | "Now, here we have our range from our P. That's our P. And if I now see that we actually break out of this range to the downside, then I would definitely look for another position down here" | none (P/B/D not coded) | MISSING |
| 13 | re-entry stop | "That's why my stop loss is now set exactly above the last volume levels." | structural stop | MATCH in kind |
| 14 | partial | "So now we're taking a part out here and yes, nothing can really go wrong anymore." | single exit | MISSING |
| 15 | PBD stop | "those of you who know the PBD logic know that it's time at the latest after a retrace to get out of the whole thing. Therefore, from now on, it's simply effective to definitely place the stop loss here" | none | MISSING |
| 16 | 2nd partial | "The market speed is decreasing. And for me, that's always a sign to take a closer look here as well." ; "That's also the value area high from yesterday's range. So, I'm taking some profit here" | node target MATCH in kind; speed not read | MISSING (speed) |
| 17 | runner | "my stop loss for the remaining position, I've now adjusted it to the 310 area. That means I'm just going to let it run now" | single exit | MISSING |

### T9 Tom kXhIAug0Gh8 (S&P short, Nasdaq limit re-fill, crude long with re-entry; one paragraph, all quotes L19)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | prior day | "There was a nice buying tail here, so strong buyers. A nice selling tail, strong sellers and with a huge volume as well. And here was the equilibrium zone." | no tail (excess) levels | MISSING |
| 2 | open | "Day two after that was the market opening. Very very very very very far away from the previous day." | open location not a state | MISSING |
| 3 | level | "here was value high. Ah, here was a buying tail where strong buyers came in. Therefore, I assume that a reaction will occur here." | prior VAH in the ladder | MATCH (VAH); tail MISSING |
| 4 | trigger | "the market simply had rejection up here. And I could then dynamically recognize that there was simply an absolute selling overhang." | 7 bars under VAH, no probe -> ACCEPTED balance_hold -> SKIP (desk R5) | DIFFERENT |
| 5 | proof | "look here very crucially, the volumes kept getting lower and lower. That means the people up here weren't blasting in like crazy anymore." | rel vol must SPIKE >= 2.0 | DIFFERENT (he reads falling volume as proof) |
| 6 | why | "Because we had the market opening down here and the market opening was very fast. And when something is very fast, there's usually no big foundation in between." | LVN_FAST_TRAVERSE is an entry, not a target path | MISSING (fast leg = thin path back) |
| 7 | target | "I said, if we go over this again, there's a high probability we'll run to value." | POC / node target | MATCH in kind |
| 8 | trail + R honesty | "And then I decided to also trail the stop loss to the high." ; "That wasn't the actual risk. The actual risk was a bit higher and therefore always consult the math of the first trade for the whole thing." | R unit = initial D (manage.py:204) | MATCH |
| 9 | 2nd fill | "And then I did the following and placed another limit order here in case it picked me up again and it did. And so I had a risk reward ratio of eight here." | rest limit | MATCH |
| 10 | stop zone | "Look here, the level of our value area and also of the previous day's V POC was in the range between 9250 and 9220. But in the end, I set my stop loss here in a price range where there's always a my mind was still stuck on this price range" | stop = sweep extreme + buffer, never 'beyond the whole value/VPOC zone' | DIFFERENT |
| 11 | re-entry | "So I then started a re-entry. Why did I do that? Because I saw that down here after I was stopped out, the market was incredibly stable and started moving in my favor again." ; "And I then placed my stop loss below the last swing low again." | none | MISSING |
| 12 | re-entry proof | "Or else I also have real proof from dynamic buyers that it makes sense there." | none | MISSING |

### T10 Tom qLnQan0KGmQ (crude long; one paragraph, all quotes L19)

| # | step | his words | our code | mark |
|---|---|---|---|---|
| 1 | plan | "that was our plan where we clearly said if the market returns to its fair price, we have the opportunity to plan a logical trade from there." | level = HVN / POC | MATCH in kind |
| 2 | structure | "This here is a typical B structure." ; "Then there was a balance as you can see, which was below the previous balances. This means that supply and demand have now shifted." | P/B/D not coded | MISSING (iteration 1 Q1) |
| 3 | event | "whenever there are absolute volume peaks, the market does special things." | no volume-climax event | MISSING |
| 4 | proof | "If you go into a small time frame now, you see excessive buying and balance here. And again, excessive buying and balance and that's always exciting. Then you have proof twice that there is really very strong buying." | one FAST_REJECTION event | DIFFERENT (two proofs on a lower TF) |
| 5 | entry | "Now you have options to enter here via pullback or to enter here again via pullback." | entry at reclaim close / next open | DIFFERENT |
| 6 | target | "I look, where was the last highest liquidity in terms of the reference ratio? And that was here." | next node | MATCH in kind |
| 7 | stop | "The stop loss belonged right here." (no rule) | sweep extreme + 5 bps | OURS-NUMBER |
| 8 | continuation | "Oh, but now the market bounced off there and went back again. And bounced off again. So what can I plan then? Quite simple. In theory, I can plan the next leg up to the next high volume area." | ACCEPTED = closes beyond, not repeated holds at a level | DIFFERENT |
| 9 | bias | "Always check what was the previous reaction. Ah, it was bullish. And if it was bullish, the probability is initially higher that this path will then continue upwards. Even if there was a really massive downtrend before" | htf_bias = monthly colour vs 20M SMA + weekly streak (:424-454) | DIFFERENT |

Step count over 10 trades (104 steps, counted by the checker script): MATCH or MATCH in kind 23, MATCH in code but not wired 4, DIFFERENT 37, MISSING 36, OURS-NUMBER as the main mark 4 (many MATCH rows also carry an OURS number).

## 2. Gap table

| id | stage | pattern | gap in one line | evidence | in iteration 1? | fix |
|---|---|---|---|---|---|---|
| TR1 | T | NEW | No re-entry after a stop on the same idea; both traders do it and count it as part of the method | k0zm5NYn0IQ L19 "Then you can definitely enter the position again here." ; kXhIAug0Gh8 L19 "So I then started a re-entry." ; models.py:180 one trade per call | N | extract (count re-entries in all live videos) + re-code (re-arm after stop while level valid) + test |
| TR2 | T | 4 | Break-even is an event that comes 'immediately' or within one candle; ours is a distance of 1 x D, and D is 5-8x his stop, so BE arrives 5-8 of his R late | 0jM5Y31YJak L4 "And the first position went to break even immediately." ; Is1HvdfQm5c L436 (ASR) "not even one candle" ; manage.py:28, :155; desk R6 | Y (FACTS H2 'BE-fast not replicated'); the 5-8x size of the miss is new | re-code (event BE: own side follow-through bar or level failure) + test |
| TR3 | T | 4 | Targets that are not volume nodes: day low, low of the curve, origin of the last impulse, last aggression point, pre-session impulse; our plan only knows nodes, models A/C/D have none | 8CWKfoSJu3c L81 "low of the curve" ; 9IliXww64uM L302 "the beginning of a strong impulse" ; Is1HvdfQm5c L157 (ASR) "the aggression of the last sellers is your first point of interest." ; auction_context:911-946 | N (iteration 1 Q10 covered Tom node targets only) | extract (target type per trade) + re-code (target candidates list) |
| TR4 | T | 1+4 | Plan picks the NEAREST node passing net R >= 1.20 (OURS); traders name a far target (other side of range, VAL to VAH) and take partials on the way | 9IliXww64uM L249 "all the way to the other side of the range" ; DyS79Eb92Ug L188 "from the value area low in a momentum day to the value area high" ; auction_context:931-946 ; desk R1 | N | re-code (primary = named far target; near node = partial) + test |
| TR5 | T | 4 | Partials and a runner cannot be expressed: every engine has one exit per leg | k0zm5NYn0IQ L19 "So now we're taking a part out here" ; Is1HvdfQm5c L459 (ASR) "your partial your first take profit" ; manage.py:97-201 | Y (Q6 partial SOURCED, fraction NOT_SEEN); 'code cannot do it at all' is new | re-code (multi-exit legs) + test |
| TR6 | C/T | 4 | Fabio's continuation = range forms outside value, then its mini value area breaks; ours = 4-6 closes beyond the old level, fires before the range exists, stop at the old level | 9IliXww64uM L158 "I wait for a range to form." ; 9IliXww64uM L341 "I want to see a breakout of this level." ; auction_context:724-726, :868; desk R3 (ours 0.83 R vs his 2.27 R) | Y for Tom 'closes + sideways' (Q3); Fabio stop/trigger at the mini range N | re-frame + re-code (acceptance = new balance outside; stop beyond it) + test |
| TR7 | C | NEW (sign flip) | Tom's 'selling overhang with volume getting lower' under VAH is labelled ACCEPTED balance_hold and skipped; we want a volume SPIKE, he reads FALLING volume as the proof | kXhIAug0Gh8 L19 "the volumes kept getting lower and lower" ; auction_context:726 (bars_in_zone >= 6), :785 (rel vol 2.0); desk R5 | N | re-frame (two proof types: spike-and-reclaim vs drying-up stall) + test |
| TR8 | T | NEW (direction flip) | Counter-trade at an exhausted open ('finished auction', 'I have to push', 'no liquidity left') has no code path; our classifier calls the same bars ACCEPTED and plans the LONG | k0zm5NYn0IQ L19 "And we also had a finished auction." ; desk R4 | N | extract (finished-auction and forced-open signs, all Tom live DAX videos) + re-code |
| TR9 | T | NEW | Day rules are coded but no caller uses them: floor at 0, risk <= day profit, adds (`first_leg_allowed`, `first_leg_risk`, `simulate_trade_legs`) | fZlNGWvd2Ko L30 "if we go back to break even, we stop the session." ; git grep: only tests and __init__ import them; engine.py imports only day_gate_open | N | re-code (wire into engine + census) + test |
| TR10 | T | 1+3 | Daily stop: Fabio counts 3 stop-outs (and allows 4-5 early in the session); code uses -3R sum labelled NO-SOURCE | Is1HvdfQm5c L466 (ASR) "if I reach a maximum of 3 stop loss" ; DyS79Eb92Ug L2013 "My rule was three losing trades to stop" ; day_gates.py:16 | N | re-code (count of full stops; scratches do not count) + test |
| TR11 | T | 4 | Management keyed to day P&L in money (lock a worst-case day total; take profit to get the day back to zero when red); code moves stops only by structure | 8CWKfoSJu3c L120 "it will be smart to take profit and to bring your balance back to break even" ; fZlNGWvd2Ko L124 "So the worst case scenario, I close $10,000." | N | extract (all Fabio sessions) + re-code |
| TR12 | T | 3 | 'Add' means two rules: Fabio adds after BE with day profit; Tom adds at a retest while still at full risk; code has only Fabio's | k0zm5NYn0IQ L19 "then I'm definitely willing to increase the position once more. With this, I now also have my total loss of about $1,000." ; manage.py:91 | N | re-frame (per-trader add rule) |
| TR13 | T | NEW | Scale-in from a partial first size ('going for four', 'didn't load it full size'); first leg is always full q1 | DyS79Eb92Ug L230 "One, two, three contract going for four." ; L237 | N | extract (first-size fraction) + re-code |
| TR14 | T | 4 | Trail is conditional: Tom does not trail at R 6:1, Fabio trails 'aggressively' only with a big floating profit; dist mode trails always after BE | k0zm5NYn0IQ L19 "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that" ; 8CWKfoSJu3c L73 ; manage.py:161 | Y (Q6 'trailing is a per-trade choice') | re-code (trail switch by R to target) |
| TR15 | E/C | 5 | NY open read on range bars (40-range) and no entries in the first 30 min; we use time bars and models A/B/D may enter from the first bar | DyS79Eb92Ug L114 "the first 30 minutes of New York opening" ; DyS79Eb92Ug L149 "So it's a range chart" ; models.py:96-118 | N (FACTS has IB 30 min for model C only) | extract + re-code (open delay; range-bar option) |
| TR16 | E | NEW | 10-day composite profile with double distribution and its LVN is the bias frame; our ladder has none | 9IliXww64uM L106 "And I typically load the last 10 days." (speaker UNSETTLED) | N for Fabio (Tom anchors in iteration 1 Q8) | extract (settle Q13 first) + re-code |
| TR17 | E/C | NEW | Open location sets the day type (open inside prior value = range day, fade edges; open far away = run to value); exists as a field, never a selector, and on UTC day not the cash session | 9IliXww64uM L173 "we opened the session exactly inside of the previous value area." ; kXhIAug0Gh8 L19 "Very very very very very far away from the previous day." ; auction_context:411-419 | Y partly (Q7 open handling, no numbers) | re-code (selector) + test |
| TR18 | E | NEW | Prior-day buying / selling tails (excess) are levels and targets; not in any level list | kXhIAug0Gh8 L19 "There was a nice buying tail here, so strong buyers." ; build_mtf_context :456-504 | Y as a target word (Q10 'buying tail'); as a level N | extract + re-code (tail detector on the cash profile) |
| TR19 | C | 1+3 | 'Proof' count: Fabio's best trade is a 3-step sequence (absorbed, rewarded aggression, absorbed again); Tom wants 'proof twice'; our triggers fire on one event | Is1HvdfQm5c L142 (ASR) "you have three order flow information going in the same direction" ; qLnQan0KGmQ L19 "Then you have proof twice" | Y (Q11 'how many proofs' open) | re-code (sequence state) + test |
| TR20 | T | 4 | Entry mechanics: Fabio buys on a stop order and enters before the 5m close; Tom enters on a pullback after proof; ours = limit at the level or next open | DyS79Eb92Ug L198 "I can start to build by stop." ; 9IliXww64uM L244 "the 5-minute was about to close" ; qLnQan0KGmQ L19 "enter here via pullback" | N | re-code (stop-entry and pullback-entry variants) |
| TR21 | C | 4 | Setup grade (AAA = low in the curve + 30 min into the session) drives size; our sizing tier reads only the monthly / weekly bias | DyS79Eb92Ug L261 "Why AAA setup? Value area low." ; auction_context:953-957 | N | re-frame + re-code |
| TR22 | C | 4 | Bias from the direction of the last reaction out of balance beats the prior trend; ours from monthly colour vs 20M SMA | qLnQan0KGmQ L19 "Even if there was a really massive downtrend before" ; auction_context:424-454 | N | re-frame + test |
| TR23 | T | 1 | His stop sizes fail our gates outright: DAX 20 pts = 8 bps, NQ 15.75 pts = 6 bps; gate needs >= 40 bps and v3 floor 30-50 bps | k0zm5NYn0IQ L19 "I'm setting a stop-loss of 20 points in the DAX." ; auction_context:895; models.py:38; desk R6 | Y (FACTS H2) | test (fee-net at his size on maker venue) |
| TR24 | T | 4 | Stop beyond the WHOLE prior value / VPOC zone, not the sweep wick: Tom calls his crude stop inside the zone a mistake | kXhIAug0Gh8 L19 "the previous day's V POC was in the range between 9250 and 9220" ; auction_context:863 | N | re-code (stop anchor = far edge of the zone) + test |
| TR25 | T | NEW | Day-direction lock and fallback level: after an invalidating break he will not trade that side for the day | DyS79Eb92Ug L223 "If this area gets broken, I don't want to be long for the day." ; 0jM5Y31YJak L4 "this is a sell model day and we continue to sell" | N | re-code (day side state) |

## 3. Top 5 gaps

1. TR3 + TR4, targets: his targets are named levels (other side of the range, low of the curve, impulse origin, day low); our plan takes the nearest volume node with net R >= 1.20, and models A/C/D have no target. This cuts the right tail he lives on.
2. TR2, break-even timing: his BE is an event ('immediately', 'not even one candle'); ours waits for +1 x D with D 5-8x his stop. His losers become scratches; ours stay full losers.
3. TR1, re-entry after a stop: both traders take the same idea again after a stop-out; no engine can.
4. TR8 + TR7, wrong-side and wrong-sign classification: Tom's counter-trade at an exhausted open is labelled ACCEPTED long, and his falling-volume stall under VAH is labelled ACCEPTED and skipped. The classifier reads 'time near a level' as acceptance, whatever the volume does.
5. TR9, day rules not wired: the floor at break-even, risk only the day's profit, and adds exist in v3 but no engine or census calls them, so no test so far has run his day management.

## 4. Single biggest hole

We translate an entry signal, but he trades a managed position. In 10 narrated trades, 41 of 104 steps come after the fill (stop moves, partials, adds, re-entry, day P&L locks, exits). Only 4 of those 41 match code that actually runs: 3 S8 exits and the R unit. The add gate, the adds and the day floor match code that no engine calls. Every test so far scored a single fixed-exit leg; none scored his management (TR2, TR3, TR5, TR9, TR11). Add the context flips (TR8, TR7) and the trades he takes are mostly not the trades our code takes.

Noticed:
- `auction_context.py:47` `DEFAULT_MAKER_RT_BPS = BINANCE_MAKER * 10000` is commented '2 bps per side' but passed as `fee_rt_bps` (round trip); Binance maker round trip is 4 bps. It understates maker fee_r by half wherever used.
- 9IliXww64uM speaker (iteration 1 Q13) is still open; T4, T5, TR16 rest on it.
- The v3 function defaults are `mgmt='dist'` (models.py, manage.py) while the README calls 'event' the v3.1 default; engine.py forces an explicit choice, but direct callers of the model functions get dist.

## 5. Quote check

All quoted spans above were checked by `gap_hunt_1113/opus_trade_replay_quotecheck.py` against `origin/fast-track:raw_transcripts_canonical/<id>_raw.txt` (normalised like `scripts/dev/verify_extract_quotes.py`: lowercase, punctuation and fillers dropped, timestamps removed). Line numbers in the tables are the line of the quote's first word, as the checker found it.

- Checker run 2026-11-13: QUOTES OK 156, MISS 0. Step marks: MATCH 23, MATCH in code not wired 4, DIFFERENT 37, MISSING 36, OURS-NUMBER 4 (total 104).
- The same 156 quotes, written as a ledger (blockquote + Source GPS lines) by the checker's third argument, were run through `scripts/dev/verify_extract_quotes.py`: 0 missing. 1 position tag (qLnQan0KGmQ 'bounced off again') was END in my ledger and MIDDLE in the official script, a thirds-boundary difference in my ledger writer, not a quote problem.
- Post-entry count: the checker's keyword filter flags 42 steps and 7 MATCH. By hand I removed T7 step 5 (cancel happens before the fill) and did not count T2 step 3 (the add gate sits in code no engine calls) or T8 step 13 (the stop of a re-entry that no code makes). That gives the 41 and 4 in section 4.
