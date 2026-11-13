# Extract: Fabio Valentini (Fabervaale), "Corso completo di Auction Market Theory" (`Ur8-c-bDGqU`)

- **Video ID:** `Ur8-c-bDGqU`
- **Speaker:** Fabio Valentini (Fabervaale), Italian professional trader (his words: 10 years trading, four World Cup rankings)
- **Market in the video:** swing view on equities (Leonardo, earnings gaps), commodities (palladium, copper, gold), FX (COT), and Bitcoin / Ripple (halving cycle, value area). It is a swing / macro talk, not a scalp talk; no order-flow footprint, no delta, no session clock. All numbers are chart examples.
- **Source:** `raw_transcripts_canonical/Ur8-c-bDGqU_raw.txt` (Italian caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim Italian quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading or parameter, no quote. English translation of each quote is on the `(en)` line after the GPS line.
- **Overlap:** fair value / value area / balance-to-breakout logic is the same idea as `extract_VHhvg96W6lc.md` V1 and V4 (not re-derived here). No stop, no target and no entry timeframe is stated anywhere in this video.

## Rules

### A1. Fair value is where operators spent the most time, not the last price (SOURCED)

Rule: fair value (equilibrium price of the auction) = the price zone where operators stayed and traded for the longest time; a single spike candle away from it does not move fair value. Computable as time-at-price / volume profile POC and value area (SOURCED definition, window length NOT stated, OURS/unknown: 3 days is only his example).

> "Il fair value è il valore accettato dagli operatori a mercato per la maggior parte del tempo." [0:01:10]
**Source GPS: Ur8-c-bDGqU | BEGIN**
(en) Fair value is the value accepted by the operators in the market for most of the time.

> "È dove hanno stazionato e contrattato per la durata più lunga gli operatori." [0:01:28]
**Source GPS: Ur8-c-bDGqU | BEGIN**
(en) It is where operators stayed and traded for the longest duration.

### A2. New information is a value shift, not noise: gap into a new value area (SOURCED)

Rule: a strong new piece of information makes price gap out of the old accepted value area; the gap is a shift of value to a new value area, and the market then re-balances inside the new area. Gap size threshold NOT stated (OURS/unknown). For BTC the analogue is a news or macro bar that opens outside the prior value area (computable from klines + volume profile).

> "non è successo nient'altro che uno shift di valore, cioè siamo passati da questa condizione dove l'area di valore accettata questa, ha una nuova area di valore che è questa qua." [0:08:44]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) Nothing else happened than a shift of value: we went from this condition where the accepted value area is this one, to a new value area that is this one.

> "Quand'è che il mercato supera dopo tanto stazionamento? Quando viene introdotta una nuova informazione." [0:10:43]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) When does the market break out after so much stationing? When a new piece of information is introduced.

### A3. Re-entry on the retest of the previous value area after a gap and new balance (SOURCED)

Rule: sequence = old value area, gap out (impulsive), market balances in a new value area, then price steps back down to test the previous value area; that retest (the "re-entry") is the second long entry, trade with the information direction. Trigger bar, stop and target NOT stated (OURS/unknown). He says an earlier gap trade stayed unfilled because the market was too strong, so the first entry (gap) may never be available.

> "Quello che vedrete molto probabilmente è mercato stazionario, nuovo scalino positivo post earni, mercato che torna giù a testare, avete la valuea precedente." [0:09:16]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) What you will most probably see is a stationary market, a new positive step after earnings, the market coming back down to test, you have the previous value area.

> "c'è la seconda entrata che è quella di dire se ti crea un'altra area di valore con il gap tu puoi prenderti il reent." [0:11:32]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) There is the second entry, which is to say: if it creates another value area with the gap, you can take the re-entry.

### A4. Buy below the value area and above the anchored VWAP in a trend (SOURCED)

Rule: take the VWAP anchored at the start of the value area (static = fixed-range profile, dynamic = anchored VWAP drawn forward) with its standard-deviation bands; in a trend with positive fundamentals the market dips and restarts, and the buy zone is below the value area (a discount) but still above the dynamic value (the anchored VWAP). He says it works with the trend only. Anchor = start of the balance range (SOURCED); SD multiple, timeframe, stop, target NOT stated (OURS/unknown). Computable from Binance klines (anchored VWAP + SD bands + profile): yes.

> "il vap ancorato, lo prendete dall'inizio e lo tracciate avanti." [0:12:57]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) The anchored VWAP, you take it from the start and you draw it forward.

> "Quindi qua sotto voi comprate sotto alla value area, quindi a sconto e sopra il valore dinamico." [0:13:44]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) So here below you buy below the value area, so at a discount, and above the dynamic value.

> "Questa strategia qua funziona da Dio a favore di trend." [0:13:51]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) This strategy works great in favor of the trend.

### A5. Value area on top of value area is a trend; breakout with gap, then balance (SOURCED)

Rule: a trend is read as a staircase of value areas: balance, breakout of the value area with a gap and impulsiveness, balance again between operators, next step. Stripped of fundamentals the chart itself shows value area on value area. Computable as sequential session/range profiles whose value areas migrate in one direction (OURS definition of "staircase": VAL of the new area above VAH of the old).

> "Leonardo sta continuando a creare aria di valore su area di valore" [0:11:55]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) Leonardo keeps creating value area on top of value area.

> "Bilanciamento fra operatori, breakout dell'area di valore anche qui con gap" [0:12:11]
**Source GPS: Ur8-c-bDGqU | MIDDLE**
(en) Balance between operators, breakout of the value area here too with a gap.

### A6. Halving cycle as the long-term context for BTC (SOURCED, context not a trigger)

Rule: a supply cut (halving) is treated as a shock that creates a parabolic trend condition; he lists the move after each past halving (9400 percent, 3500 percent, 700 percent, current 105 percent when recorded). Context filter for direction only; no entry or exit trigger is given. Percentages are his chart read, not independently checked (OURS: unverified). Computable from BTC daily klines: partly (halving dates are public, not in aggTrades).

> "La riduzione della supply, ragazzi, non ci si gira intorno, crea uno shock da quando esiste l'asse, ok? Quindi crea una condizione di trend parabolico." [0:17:09]
**Source GPS: Ur8-c-bDGqU | END**
(en) The reduction of supply, guys, there is no way around it, creates a shock since the asset exists, ok? So it creates a parabolic trend condition.

> "Questo halving qua si è fatto un 9400%. Questo halving qua, il secondo, si è fatto un 3.500%. Questo halving qua si è fatto un 700%." [0:17:18]
**Source GPS: Ur8-c-bDGqU | END**
(en) This halving did 9400 percent. This halving, the second, did 3,500 percent. This halving did 700 percent.

### A7. BTC: new factor makes a new value area; buy the breakout from the prior high then the rebalance (SOURCED, probability claim unverified)

Rule: when a new factor enters, a new value area forms; his BTC example is a breakout of the previous highs after which price came back to balance inside the new area and buyers took control. He says he entered with the whole company account, not leveraged, because he gave the increase about a 95 percent probability (OURS: unverified claim, no backtest shown). Current-cycle read: back at the highs, breakout attempted and achieved, a new bull starts. Stop and target NOT stated. Do not copy the sizing.

> "perché quando tu mi inserisci un fattore nuovo, mi crei una nuova area di valore." [0:18:05]
**Source GPS: Ur8-c-bDGqU | END**
(en) Because when you insert a new factor, you create a new value area.

> "Quindi Bitcoin poi cosa ha fatto? È ritornato a bilanciare quest'area di valore qua e hanno ripreso controllo poi i buyers" [0:18:10]
**Source GPS: Ur8-c-bDGqU | END**
(en) So what did Bitcoin do then? It went back to balance this value area here and then the buyers took control again.

> "Siamo tornati sui massimi, abbiamo cercato un breakout, ci siamo riusciti. Adesso parte una nuova bull." [0:18:22]
**Source GPS: Ur8-c-bDGqU | END**
(en) We are back at the highs, we looked for a breakout, we managed it. Now a new bull starts.

### A8. Intermarket benchmark: buy the asset that retraces while its benchmark keeps going (SOURCED, commodities; analogue for BTC is OURS)

Rule: compare the asset with an equal-weighted benchmark of related assets (copper vs gold and silver) and look for technical discounts, i.e. the asset divergent below the benchmark; his last example is gold retracing while the benchmark kept going. Weights equal (SOURCED); lookback, divergence size, stop, target NOT stated. For BTC the benchmark would be OURS (e.g. equal-weight ETH/SOL), not what he uses; computable from klines: yes once the benchmark is chosen.

> "copper me lo comparo con Gold e con silver, equi pesati e mi vado a vedere quando ho dei discount tecnici sull'asset" [0:20:45]
**Source GPS: Ur8-c-bDGqU | END**
(en) Copper, I compare it with gold and silver, equal weighted, and I look for when I have technical discounts on the asset.

> "L'ultimo trade che mi sono preso, grazie a questa logica, è Gold, perché Gold m'ha ritracciato mentre il benchmark mandava." [0:21:05]
**Source GPS: Ur8-c-bDGqU | END**
(en) The last trade I took, thanks to this logic, is gold, because gold retraced while the benchmark was pushing up.

### A9. Few trades, high claimed win rate; hold winners, trim and re-buy the pullback (SOURCED, claim unverified)

Rule: swing account style = 10 to 15 trades a year with a claimed 90 percent win rate (OURS: unverified, no data shown); no scaling out on projects he believes in; instead he takes out a bit of profit, waits for the pullback and re-buys. Fixed fraction trimmed NOT stated.

> "Io posso fare 10-15 operazioni sul conto swing l'anno, ma sono operazioni con un 90% win rate." [0:19:40]
**Source GPS: Ur8-c-bDGqU | END**
(en) I can do 10-15 trades on the swing account a year, but they are trades with a 90 percent win rate.

> "Piuttosto tiro fuori un po' di profitto, aspetto il ritracciamento e ricarico, così faccio soldi anche quando il mercato va giù." [0:20:14]
**Source GPS: Ur8-c-bDGqU | END**
(en) Rather I take out a bit of profit, wait for the pullback and reload, so I make money even when the market goes down.

### A10. Market is predictable only in narrow windows: do not try to call every candle (SOURCED, what NOT to do)

Rule: edge exists only in isolated market conditions; asking where the next three candles go is close to random. The aim is to trade only the moments where the auction gives information, not every movement (noise). Fits a regime filter: no trade outside a defined condition.

> "il mercato ha dei restritti intervalli di prevedibilità, cioè l'obiettivo del trader non è capire ogni singolo movimento" [0:02:19]
**Source GPS: Ur8-c-bDGqU | BEGIN**
(en) The market has restricted intervals of predictability, that is, the trader's goal is not to understand every single movement.

### A11. Stack independent structural filters (SOURCED)

Rule: his edge claim is the union of structural asset information (intermarket, seasonality, long-term positioning of operators) with advanced price action and volume analysis; positioning data (COT non-commercial, asset manager net contracts) is used as value construction. COT is not computable from Binance data (no); the rest partly.

> "andare a unire delle logiche che sono strutturali nell'asset, quindi l'intermarket, la seasonality, il posizionamento degli operatori di lungo termine, una price action avanzata, l'analisi volumetrica" [0:23:23]
**Source GPS: Ur8-c-bDGqU | END**
(en) To unite logics that are structural in the asset, so intermarket, the seasonality, the positioning of long-term operators, advanced price action, volume analysis.
