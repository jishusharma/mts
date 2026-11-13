# Answer ledger: our parameters vs the trader's own words (2026-11-13)

Card tf-s1-answer-ledger-1113. Inputs: ANSWERS_FROM_DISK.md, out/tf-x1..x5/ANSWERS.md (all CHECKED-AFTER-FIX by the Haiku review of 2026-11-13, not independently re-reviewed; tf-r1 re-checks), ITERATION_2.md for OURS values and code places. Labels: SOURCED = trader said a value or rule in words; NOT_SEEN = no value in any held transcript; CONTRADICTION = his words point the other way from our parameter; OURS-STAYS = our own design, no trader line could settle it. Quotes below are copied from the ANSWERS files only. Fabio quotes from Is1HvdfQm5c are ASR (machine caption), numbers can be misheard. No code change, no backtest, no new number.

## Ledger

| Row | OURS param (value, where) | Trader value | Label | Source (id) | Answers file + Q |
|---|---|---|---|---|---|
| L01 | Acceptance = 6 closes x 5m (auction_context.py:724 n_acc) | No bar count. Form: close beyond level, then a new sideways phase with liquidity | NOT_SEEN (count) | Ly62G168MkQ, Sy-x5AQ9-Pk | x3 Q3, ANSWERS_FROM_DISK Q3 |
| L02 | Acceptance form: new balance forms outside the level (I2-09) | Break-out ideally at the close, then another sideways phase | SOURCED (form, no number) | Ly62G168MkQ | x3 Q3 |
| L03 | Reclaim within 3 bars = speed of rejection | Speed is tape tempo (high or low vs the product), no bar count | NOT_SEEN (bar count) | G0CiJcuXCRs, Is1HvdfQm5c | x5 Q4, x1 Q4 |
| L04 | Stop buffer: sweep extreme + 5 bps; v3 floor 0.3-0.5% (models.py:38) | No tick, bps or percent buffer in the 22 videos of x1 and x2 | NOT_SEEN | all of x1, x2 | x1 Q5, x2 Q5 |
| L05 | Stop placement: sweep extreme (long and short) | Long: below last swing low / beyond the absorbed area. Short: Fabio above the area; Tom short-side quote NOT_SEEN | SOURCED (structural) | QClPWDJ-BrU, Is1HvdfQm5c | x2 Q5, x1 Q5 |
| L06 | LVN fraction (value not in the answers files) | No fraction stated; Fabio LVN = lowest bin in a fixed A-to-B profile (tf-y2 pending) | NOT_SEEN | none | ITERATION_2 I2-16 |
| L07 | Big trade = 99th percentile of prior 30 days, 1m bars (signals.py:25) | Fabio fixed filter 60 (units and product not stated, ASR); 30 gives more setups | SOURCED (fixed 60) | Is1HvdfQm5c | x1 Q9 |
| L08 | Big trade = a percentile, not a fixed size | Tom: product-specific, no universal size ("not blocks of 80 or blocks of 60" for ES) | OURS-STAYS (percentile idea) | G0CiJcuXCRs, y67l86cSqb8 | x5 Q9 |
| L09 | Absorption: z-score grid on result | "zero" or "almost zero", judged by eye against effort; no threshold | NOT_SEEN | 0jM5Y31YJak, o-w5Gxss6T0 | x1 Q9, x5 Q9 |
| L10 | Session blocks: UTC blocks; v3 NY 13:30/14:30 + 390 min | Fabio says NY only in one video, shows London trades in others; Tom DAX 9 to 12 | CONTRADICTION (hours NOT_SEEN) | Pz8f0wWW12M, 06R-ebyOhDI, fZlNGWvd2Ko | x1 Q7 |
| L11 | Tom DAX/Bund core window | 9 to 12 before lunch | SOURCED | 5Ljfwvtktek | x4 Q7 |
| L12 | NY open: our block starts at the cash open, no skip (census_session_ladder.py:138) | Opening range or initial balance of 15, 30 or 60 minutes (Fabio); Tom judges gap and open behaviour | SOURCED (minutes, Fabio) | cUTsoU-15Tc | x1 Q7, x4 Q7 |
| L13 | Profile anchor: every value area = 24h UTC day (vp_return_to_value.py:7) | Daily profile on the cash session only; weekly profile; composite last major high to low | CONTRADICTION | BB3c8visnkI, sQ_biBKhPVU | x4 Q8, x3 Q8 |
| L14 | Anchor for a 24/7 market | Never stated | NOT_SEEN | all x3, x4 ids | x3 Q8, x4 Q8 |
| L15 | Proof counts: 3 WATCH / 5 SETUP | Ordered stack (location, balance and acceptance, footprint and speed), no count | NOT_SEEN (count) | -dMWA_bbm3o, 3o1VVsfBmmU | x5 Q11 |
| L16 | Balance thresholds: 60-minute box (signals.py:183, true in 3.1% of windows) | Balance read by profile shape, P/B/D letters; closing-price count named, never numbered | NOT_SEEN (threshold) | jXR1afMy-3o, m3IMdc7QwN4 | x3 Q1 |
| L17 | 70% claim (E6 tested return-to-value 57% vs placebo 47%) | Three claims: value area 70% of volume; balance 60-70%+ of time; 30% run / 70% come back (period not in the sentence, market not named) | SOURCED (three separate claims) | aursfDVYzUk, BB3c8visnkI, Fj4FDZQxw0I | x4 Q2, ANSWERS_FROM_DISK Q2 |
| L18 | Add rule (two add rules cannot be coded, I2-12) | Add at the breakout while pace holds | SOURCED (words) | 4MoNjEQ2Dd8, 0jM5Y31YJak | x2 Q6, x1 Q6 |
| L19 | Add size / count | None stated | NOT_SEEN | all x1, x2 | x1 Q6, x2 Q6 |
| L20 | Break-even at +be_k x D, distance about 5-8x his stop (manage.py:28) | An event, not a distance: after the next confirmation, even "immediately"; tick trigger NOT_SEEN | CONTRADICTION | 0jM5Y31YJak, Pz8f0wWW12M | x1 Q6, x2 Q6 |
| L21 | Trail distance (manage.py:155, :161 starts right after BE) | Trail behind last big trade or last volume area; sometimes not trailed; distance never stated | NOT_SEEN (distance) | Pz8f0wWW12M, 4MoNjEQ2Dd8 | x1 Q6, x2 Q6 |
| L22 | Target = nearest volume node, sorted nearest first (auction_context.py:931) | Next major level (far side of range, VPOC, value high); set before entry, never deleted | SOURCED (structural) | QClPWDJ-BrU, UrZ4vpHJ97g | x2 Q10 |
| L23 | Target multiple / min net RR 1.20 (auction_context.py:49) | Fabio quotes 1:2.5 to 1:5; 1:19 once planned | SOURCED (Fabio examples) | cUTsoU-15Tc, Is1HvdfQm5c | x1 Q10 |
| L24 | Target offset short of the level | "just slightly below", "a few ticks off"; no number | NOT_SEEN | QClPWDJ-BrU, 4MoNjEQ2Dd8 | x2 Q10, x1 Q10 |
| L25 | Risk per trade: fixed R | Tom 0.5% day, 0.7% swing from a 20% drawdown cap; 1% often too much. Fabio fixed dollar stop | SOURCED | UrZ4vpHJ97g, WSCIURybK3U, Is1HvdfQm5c | x2 Q12, x1 Q5 |
| L26 | Daily loss limit | Not stated | NOT_SEEN | all x2 | x2 Q12 |
| L27 | Sizing tier from candle bias (auction_context.py:953) | Setup grade by profile location; no tier values | OURS-STAYS | none | ITERATION_2 I2-17 |
| L28 | Bitcoin: rules transferred from index futures | Tom draws P/B/D on Bitcoin; no BTC entry, stop, target | NOT_SEEN (rules) | 0CrkbfuIhkc, Kg6sYKgtkrY | x3 Q14 |

## Evidence for SOURCED rows

### L02 Acceptance form
> "If the market now decides to break out upwards again from such a sideways phase, ideally at the closing price, then our initial assumption is that the trend will continue."
**Source GPS: Ly62G168MkQ | MIDDLE**

### L05 Stop placement
> "And I'd position the stop-loss below that."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "this is your opportunity to jump in with a super small stop loss okay you can cover yourself above the area and shoot for a 1 to 4.5"
**Source GPS: Is1HvdfQm5c | BEGIN** [21:04] (ASR)

### L07 Big-trade filter 60
> "so the big trades guys are 60 the filter it's on 60"
**Source GPS: Is1HvdfQm5c | MIDDLE** [1:29:41] (ASR)

### L11 DAX window
> "9 to 12 is a trading time I would use for DAX futures or for example the bund because that is the core cash time for the stock markets before the lunch break"
**Source GPS: 5Ljfwvtktek | END**

### L12 Opening range minutes
> "You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes. It depends how you want to use it"
**Source GPS: cUTsoU-15Tc | BEGIN** [2:10]

### L17 The 70% claim (three separate claims)
> "As a rule, you use 68.2 or 70% of all trades of the day and say that where 70% of the highest trading volume occurred is the so-called value area."
**Source GPS: aursfDVYzUk | MIDDLE**

> "especially 60 to 70% of the time, we have so-called balance equilibrium profiles."
**Source GPS: BB3c8visnkI | MIDDLE**

> "But unfortunately that is only the case about 30% of the time and the other 70% he will try and strive to run back here."
**Source GPS: BB3c8visnkI | MIDDLE**

### L18 Add rule
> "I'll add to the position again at the breakout."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

### L22 Target is a named level set in advance
> "Now we have carefully planned our exit strategy up at the corresponding next major level, which is sitting at 7,513."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "you must never ever delete this predefined target"
**Source GPS: UrZ4vpHJ97g | MIDDLE**

### L23 Target multiple
> "It's amazing but the win rate goes low. So it's better to take 1 2 3 1 to 2.5 with a really consistent way of executing it"
**Source GPS: cUTsoU-15Tc | END** [23:04]

### L25 Risk per trade
> "And that's how I arrived at the figure of 0.5%."
**Source GPS: UrZ4vpHJ97g | MIDDLE**

> "In swing trading, look, we risk 0.7% per trade with a maximum draw down of 12.9%."
**Source GPS: UrZ4vpHJ97g | END**

### Contradiction evidence (L10, L13, L20)
> "I only trade in the New York session for US indices because it's where the majority of the volume get traded, and I find it from statistical validation, the London session to be usually for US indices not so valuable to add to the profile"
**Source GPS: Pz8f0wWW12M | END** [29:00]

> "I'm showing you two execution that I took. One in London session and one in New York session"
**Source GPS: 06R-ebyOhDI | BEGIN** [0:36]

> "these profiles only show you the period where the so-called cash session is"
**Source GPS: BB3c8visnkI | MIDDLE**

> "the first position went to break even immediately"
**Source GPS: 0jM5Y31YJak | MIDDLE** (no [m:ss] in this file)

## Open (not settled)

Rows with NOT_SEEN: L01 acceptance count, L03 reclaim bars, L04 stop buffer, L06 LVN fraction, L09 absorption result threshold, L14 24/7 anchor, L15 proof count, L16 balance threshold, L19 add size, L21 trail distance, L24 target offset, L26 daily loss limit, L28 Bitcoin entry/stop/target.
Rows with CONTRADICTION: L10 session blocks (NY-only vs London trades, hours never stated), L13 UTC-day anchor vs cash-session anchor, L20 break-even distance vs break-even event.
Pending extraction cards (ITERATION_2): tf-y2 (LVN, profile shapes), tf-y3 (open, day filters), tf-y4 (management, targets), tf-y5 (proof), tf-y6 (units of 60, entry, BTC order flow).

## Rows that stay OURS

L08 big-trade percentile (Tom says size is product-specific; only the fixed filter 60 is Fabio's), L27 sizing tier from candle bias. Until a trader line appears, L01 (6 closes), L03 (3 bars) and L04 (5 bps) are also OURS numbers and must be labelled so in code and pre-regs.
