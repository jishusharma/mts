# tf-g3-fabio-shorts-partners-1113 ANSWERS

Sources (real caption text, read whole):
- 5 Fabio short transcripts in `raw_transcripts_canonical/`:
  - `_xEhztnK2g0_raw.txt` (Market micro mechanics, Fabervaale ENG short, 219 words)
  - `3GwHv2FF4Hw_raw.txt` (Reload on Deepdom, Fabervaale ENG short, 169 words)
  - `5H1MCBG87YI_raw.txt` (How I set up my take profit, Fabervaale ENG short, 185 words)
  - `FDrHnl7StOM_raw.txt` (What professional traders actually use, Fabervaale ENG short, 95 words)
  - `3JZH06L28us_raw.txt` (My tools Tier list, Fabervaale ENG short, 241 words)
- Partner videos (`agjftXPkLUE`, `cLgdXZnLL_0`, `feV6CATGUqo`, `pZai3k1e-Jg`): NOT fetched. Caption fetcher `scripts/dev/fetch_captions_timed.py --analyst Tom --status` is locked until `2026-11-16T14:21:46+00:00` (lockout level 3 of 3 on host JIS-NUC). Answers are produced strictly from the 5 local canonical transcripts.

### Q5 Stop: exact placement and buffer (Tom "below last liquidity / sideways phase"; Fabio "super small, above the area")
**Verdict: PARTIAL**
Fabio states qualitative stop placement rules: "below the low" for entry/stop, and using ATR to "manage the stop loss and take profit". However, no numerical buffer, point buffer, tick count, or percentage distance is stated anywhere in these transcripts (buffer is NOT_SEEN).
> "You enter a trade, you put a stop loss below the low, but where do you take profits?"
**Source GPS: 5H1MCBG87YI | BEGIN**
> "You can use it to frame the correct risk and points to manage the stop loss and take profit, but on itself, it's not giving you any kind of edge."
**Source GPS: 3JZH06L28us | END**

### Q6 Adds, trail, break-even, partials: rules?
**Verdict: PARTIAL**
Fabio covers multiple take profit levels ("TP1 and TP2") and taking profits into reloaded liquidity ("as a scalper, it's better to take profits"). He notes that fresh liquidity reloading fuels downward momentum ("reload, reload, reload, reload. This is all fresh liquidity fueling the movement down"). No trail distances, break-even ticks, or add rules/distances are stated in these 5 shorts (trail distance / BE rules are NOT_SEEN).
> "And we have this cluster, so we have TP1 and TP2 here, okay?"
**Source GPS: 3GwHv2FF4Hw | BEGIN**
> "If as soon as the level is taken, they reload more liquidity, it's likely that we will reverse. So, as a scalper, it's better to take profits."
**Source GPS: 5H1MCBG87YI | END**
> "On top of this you see reload, reload, reload, reload. This is all fresh liquidity fueling the movement down."
**Source GPS: 3GwHv2FF4Hw | MIDDLE**

### Q9 Absorption: how little price result counts as "almost zero"; big-trade size; what he reads on footprint
**Verdict: PARTIAL**
Fabio explicitly describes absorption occurring at liquidity levels and visible aggressive bubbles interacting with passive liquidity. However, he gives no numerical contract threshold for big-trade size ("almost zero" price delta threshold and specific contract count filters are NOT_SEEN).
> "You see this amazing absorption. On top of this you see reload, reload, reload, reload. This is all fresh liquidity fueling the movement down."
**Source GPS: 3GwHv2FF4Hw | BEGIN**
> "And you have always an interaction of two forces. You have the aggressive market orders, bubbles, and the passive liquidity. These two match together."
**Source GPS: _xEhztnK2g0 | BEGIN**

### Q13 Who speaks in 9IliXww64uM (Fabio or Andrea Cimi)?
**Verdict: NOT_SEEN**
9IliXww64uM is not among the 5 Fabio shorts examined (`_xEhztnK2g0`, `3GwHv2FF4Hw`, `5H1MCBG87YI`, `FDrHnl7StOM`, `3JZH06L28us`). The partner video fetch is blocked by the timed caption fetcher lockout until 2026-11-16T14:21:46+00:00. In the 5 local Fabio shorts, the speaker is Fabio Valentini (Fabervaale ENG). Neither Andrea Cimi nor video 9IliXww64uM is mentioned or settled.

## Parameter table
| parameter | trader's value | SOURCED or NOT_SEEN | id |
|---|---|---|---|
| stop buffer / tick distance | none stated ("below the low", ATR to frame points) | NOT_SEEN | 5H1MCBG87YI, 3JZH06L28us |
| break-even trigger distance | none stated | NOT_SEEN | all 5 shorts |
| trailing stop rule / distance | none stated | NOT_SEEN | all 5 shorts |
| take profit levels | TP1 and TP2; take profit when liquidity reloads | SOURCED | 3GwHv2FF4Hw, 5H1MCBG87YI |
| big-trade size / bubble threshold | none stated (reads bubbles and aggressive market orders) | NOT_SEEN | _xEhztnK2g0, 3GwHv2FF4Hw |
| "almost zero" price result threshold | none stated | NOT_SEEN | all 5 shorts |
| speaker of 9IliXww64uM | not addressed in the 5 shorts | NOT_SEEN | all 5 shorts |
