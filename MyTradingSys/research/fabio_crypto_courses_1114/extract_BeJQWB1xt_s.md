# Extract: Fabio Valentini (Fabervaale), "Identificare la fase di Spring in sessione" (`BeJQWB1xt_s`)

- **Video ID:** `BeJQWB1xt_s`
- **Speaker:** Fabio Valentini (Fabervaale), order-flow scalper on NQ/ES futures; free live lesson, 2022-11-12, Italian. This 2022 lesson is a forex (EUR/USD, GBP) session lesson, not an order-flow lesson.
- **Market in the video:** EUR/USD and GBP/USD (M15 charts, Italian local clock), BTC mentioned only as a macro cycle example. All clock rules here are forex/index session clocks and are tagged `index-futures-only`; the sweep logic itself is price-only and testable on BTC klines.
- **Source:** `raw_transcripts_canonical/BeJQWB1xt_s_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Note on the title:** he never defines "Spring" as a Wyckoff phase with a formula; he describes the liquidity sweep below a range, a quick re-entry and a directional explosion (B3, B5). Wyckoff names (reaccumulation) appear only as labels. No stop, no entry price rule and no fixed target distance is stated in the lesson; the TP1 pip distance is shown on a chart and not spoken (B5).
- **Overlap:** sweep followed by explosion; trapped traders in `extract_3MID2HLZS30.md` S3 and S5 and `extract_cLgdXZnLL_0.md` D4; stop-run fade in `extract_kYX05qESJMs.md` S1. This lesson adds the session-high/low liquidity map and the double sweep.

## Rules

### B1. A sweep (manipulation) is the trigger, not the bias (SOURCED)

Rule: market manipulation (liquidity sweep) gives a clue on the execution trigger, not on the trend/bias; it cannot be used alone, it must sit inside a strategy context. What happens after a particular move is the statistical edge. He notes that some traders use it for bias (waiting for a manipulation and a structure change) but that is not how he uses it. Parameters: none numeric.

> "Che cos'è ci dà l'indizio su bias o ci dà l'indizio sul trigger esecutivo esattamente C Damo un indizio sul trigger Ok" [0:04:38]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) What is it, does it give the clue on bias or the clue on the execution trigger? Exactly, it gives us a clue on the trigger.

> "Perché la manipolazione non puoi utilizzarla da sola la manipolazione Va inserita all'interno di un contesto di strategia" [0:04:21]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) Because you cannot use manipulation alone; manipulation must be inserted inside a strategy context.

### B2. Trapped traders = the wrong direction taken by most operators, visible on the footprint (SOURCED)

Rule: what stop hunting is called in footprint terms: trapped traders, meaning the wrong direction taken by most operators; that is the clue. Not necessarily retail, often funds. He says institutions target liquidity clusters, not individual stops. Parameters: how many contracts or what ratio defines "most operators": NOT stated. Partly computable from aggTrades (aggression at an extreme that gets reversed, thresholds OURS). Same family as `extract_cLgdXZnLL_0.md` D4.

> "il concetto di traed Traders che si può vedere dal footprint ragazzi vuol dire semplicemente direzionalità errata Ok che hanno preso gran parte degli operatori e quello è un indizio" [0:07:14]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) The concept of trapped traders, which can be seen from the footprint, simply means wrong direction, which most operators took, and that is a clue.

### B3. Liquidity map: highs and lows of the Asian session, Monday and the previous day (SOURCED)

Rule: resting orders (liquidity) sit above the high and below the low of the Asian session, of Monday and of the previous day; these are the levels the market sweeps. For BTC: define the three levels from klines (previous UTC day high/low, Monday high/low of the week yes; "Asian session" hours NOT stated, OURS). He says the weekly cycle belongs to swing trading, not the intraday sweep he teaches here.

> "massimi del lunedì e massimi del giorno precedente perché questi livelli in particolare perché i massimi della sessione asiatica abbiamo parlato in precedenza Perché dove ci sono la maggior parte dei resting orders quindi della liquidità ok" [0:24:46]
**Source GPS: BeJQWB1xt_s | MIDDLE**
(en) Highs of Monday and highs of the previous day, why these levels in particular; why the highs of the Asian session, we talked about it before: because that is where most of the resting orders, so the liquidity, are.

### B4. Asian session closes in consolidation 65 percent of the time (SOURCED, index-futures-only: forex session clock)

Rule: he states "a statistic of 65%" of Asian sessions closing in consolidation, which builds liquidity above the highs and below the lows for the later sweep. Source of the statistic NOT given (not shown, no sample size, forex pairs with the dollar, not BTC) so treat as an unverified claim to measure ourselves. Computable (yes): range-bound fraction of a fixed UTC window on BTC klines, with the "consolidation" test OURS.

> "c'è una statistica del 65% delle sessioni asiatiche che chiudono in consolidamento quindi formano un mercato che effettivamente crea stabilità" [0:06:03]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) There is a statistic that 65% of Asian sessions close in consolidation, so they form a market that effectively creates stability.

### B5. Sweep at the London open (and the 14:30 Italian time spike), then directional explosion (SOURCED, index-futures-only: forex session clock)

Rule: the liquidation of orders placed in the Asian session happens at the London open; after orders below a level are liquidated, expect direction and exit from the contraction (range). Clocks (Italian local time): volume peak between 14:00 and 15:00 with the biggest at 14:30 (New York session key hour), most liquidation spikes at that hour; London open about 09:00 (the "GBP manipulates at 9" remark, chat answer). He fixes only the clocks, not UTC; the Italian clock shifts with daylight saving (he says it is always 14:30 in his local time). Target: average first target TP1 "at some pips distance" from a statistic of the last 10 weeks, shown on a chart; the number is NOT spoken (example trade on GBP M15 was 60 pips, not a rule). Stop: NOT stated. Entry: NOT stated beyond "after the sweep". Computable from klines (yes: Asian range break at a UTC hour, then displacement); clock mapping to BTC is OURS, which is why the clock part is tagged index-futures-only.

> "Ricordatevi che durante la apertura di Londra Noi abbiamo la liquidazione e l'ingegnerizzazione della liquidità per gli ordini che sono stati piazzati in asiatica" [0:10:55]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) Remember that during the London open we have the liquidation and engineering of liquidity for the orders that were placed in the Asian session.

> "ma l'esplosione più grande ce l'abbiamo fra le 14 e le 15 in particolare le 14:30 che sono un orario specifico" [0:09:40]
**Source GPS: BeJQWB1xt_s | BEGIN**
(en) But the biggest explosion we have between 14 and 15, in particular 14:30, which is a specific time.

> "Ricordatevi ragazzi che quando noi andiamo a liquidare degli ordini che si trovano al di sotto di determinati livelli la fase successiva che dobbiamo aspettarci è direzionalità e uscita proprio dalla contrazione" [0:27:33]
**Source GPS: BeJQWB1xt_s | END**
(en) Remember, guys, that when we liquidate orders located below certain levels, the next phase we must expect is direction and exit from the contraction.

> "ci fornisce anche mediamente un target un primo target il tp1 a che quantità di a che sì A che distanza di pips può essere posizionato" [0:36:06]
**Source GPS: BeJQWB1xt_s | END**
(en) It also gives us on average a target, a first target, TP1, at what quantity, at what distance in pips it can be placed.

### B6. After the explosion leaves an inefficiency, rebalancing (mitigation) into it is very likely, then continuation (SOURCED)

Rule: the directional explosion out of balance leaves an inefficiency/imbalance; a return into it (rebalancing or mitigation) is "very probable", leaving clusters above, then the market resumes direction (Wyckoff: reaccumulation). Sequence on his charts: balance, liquidity grab at the cluster hour, explosion, mitigation, new consolidation (POC stays where price stayed longest), repeat. Parameters: depth of mitigation (full fill or partial) NOT stated; no entry or stop; no hit rate (he says it repeats every week on EUR/USD, no count). Computable (yes, klines): gap from the explosion leg, first return into it, later direction (thresholds OURS).

> "mi trovo in una situazione dove il mercato Non è efficiente e è probabilissimo quello che viene definito riban camento ok o mitigazione all'interno di questi livelli" [0:29:50]
**Source GPS: BeJQWB1xt_s | END**
(en) I find myself in a situation where the market is not efficient and what is called rebalancing, or mitigation, inside these levels is very probable.

> "questa cosa l'aveva contestualizzata e si chiamava fase di reaccumulation il mercato successivamente riprende direzionalità" [0:30:11]
**Source GPS: BeJQWB1xt_s | END**
(en) This was put in context and was called the reaccumulation phase; the market afterwards resumes direction.

### B7. Double sweep: a second low with a liquidity spike that is not re-absorbed (SOURCED)

Rule: the more frequent recent pattern is a double liquidity sweep: another low below, spike, then a "cannon" that does not re-absorb; the market does not allow you to enter and goes. Explanation: when the Smart Money logic became crowded, the clusters moved, so a mega cluster forms under the first sweep. Parameters: the size of the second sweep NOT stated; entry, stop, target NOT stated (he says it is advanced and can be traded and "raises the win rate", not covered). Computable (yes, klines: two lows in sequence, second lower, price leaves without a close back inside).

> "il doppio sweep di liquidità ovvero un'altra un altro minimo qua sotto con Spike di liquidità e poi tirano un cannone non riassorbono più cioè non vi permettono più di entrare ma lo fanno liquidano e partono" [0:22:18]
**Source GPS: BeJQWB1xt_s | MIDDLE**
(en) The double liquidity sweep, that is another low down here with a liquidity spike, and then they fire a cannon, they no longer re-absorb, that is they no longer let you enter but they liquidate and go.

### B8. What NOT to do: stop at breakeven right after the first temporary profit (SOURCED, what NOT to do)

Rule: the market makes the imbalance, returns to test it, then launches giving a temporary profit, and most traders put the stop at zero (breakeven); the following double sweep takes them out. For us: test "stop moved to breakeven after the first pop" against a stop that stays at the structure. Parameters: how far the first pop goes NOT stated. Computable (yes, klines) as an exit-rule comparison; the breakeven trigger distance is OURS.

> "il mercato ti fa lo sbilanciamento ti torna a testare lo sbilanciamento ti parte quindi ti fa un Temporary profit e la maggior parte dei Trader metono stop a zero" [0:22:06]
**Source GPS: BeJQWB1xt_s | MIDDLE**
(en) The market gives you the imbalance, returns to test the imbalance, then launches, so it gives you a temporary profit, and most traders put the stop at zero.

### B9. Midpoint of the dealing range as the equilibrium level where liquidation is likely (SOURCED)

Rule: take the dealing range of the move, its 50 percent is the equilibrium level where liquidation is most probable; he adds that supports drawn by traders who do not know these concepts form there. Range definition (which swing high and low) NOT stated; threshold is 50 percent (SOURCED). Computable (yes, klines): reaction at the 50 percent of a defined swing range.

> "si può anche andare a valutare il dealing Range e vedere che questo è il nostro livello di equilibrio il 50 quindi è dove molto probabilmente andranno a fare liquidazione" [0:32:35]
**Source GPS: BeJQWB1xt_s | END**
(en) You can also evaluate the dealing range and see that this is our equilibrium level, the 50, so it is where they will very probably liquidate.

## Not testable (one row per topic)

| Topic | Why not testable |
|---|---|
| Definition of manipulation as engineering of liquidity, only under 20 percent of manipulation types known, spoofing and Navinder Sarao story, regulators | Context and history; no trigger, no number we can compute |
| Volatility needs volume; volume peak by hour of day on EUR/USD and GBP (shown on a chart site) | The 14:00 to 15:00 and 14:30 clock is carried as the clock part of B5; the volume curve itself is not given numerically |
| Macro cycle: the peak is the point of maximum financial risk, the panic low the point of maximum opportunity (BTC "back to fair value at 50k" example) | No trigger, no threshold, long-term opinion; our own BTC cycle work is elsewhere |
| Retail mass psychology, toxic positivity, psychology versus method (reply to another video) | Behaviour advice |
| Smart Money vocabulary (fair value gap, market structure break, order block, liquidity grab) derived from order flow and VSA on CFD without volume | Naming only; mechanical versions are in other extracts |
| Weekly cycles from Monday high and low | Announced for the next lesson, not taught here |

Noticed: the lesson is a forex session lesson sold as a Spring lesson; the caption has no stop, no entry rule, no hit rate and no target number (TP1 distance is on screen only). Caption errors: "doppio sweep" and "mutazione" are said to be a named advanced concept he does not explain; "(he) says it is always 14:30" refers to local-time daylight saving.
