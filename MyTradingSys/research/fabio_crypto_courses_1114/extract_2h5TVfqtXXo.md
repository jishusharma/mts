# Extract: Fabio Valentini (Fabervaale), "Dinamiche di Profile e Auction Market Theory" (`2h5TVfqtXXo`)

- **Video ID:** `2h5TVfqtXXo`
- **Speaker:** Fabio Valentini (Fabervaale), order-flow scalper on NQ/ES futures; free live lesson with chat Q and A, 2023-01-04, Italian
- **Market in the video:** daily session profiles on TradingView (session, fixed, visible range, periodic profile) on index/FX charts; daily bases. No crypto example. Profile rules are computable from Binance aggTrades or klines (volume per price level per UTC day is OURS: he works per session, no session clock stated for a 24h market).
- **Source:** `raw_transcripts_canonical/2h5TVfqtXXo_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Overlap:** value area = 70 percent of volume and HVN/LVN meaning are already in `extract_qihraSSdI_M.md` V1 and V2; POC and value migration as day-to-day read is `extract_VHhvg96W6lc.md` V10 and V12; real traded volume instead of tick volume is `extract_qihraSSdI_M.md` V5. They are referenced below instead of repeated where marked.

## Rules

### P1. Definitions: market profile = time at price, volume profile = volume at price, POC vs VPOC (SOURCED)

Rule: market profile (TPO) builds a distribution of time per price level, its center is the POC (price level with the most time); volume profile builds a distribution of traded volume per price level, its center is the VPOC (most volume traded at one level). The two are not interchangeable; he calls the TradingView "volume profile" a time-based tool. For BTC: VPOC and value area from aggTrades quantity per price bucket (yes); the time-based POC from klines (yes). Bucket size NOT stated for a 24h market (OURS). Value area = 70 percent of volume: same as `extract_qihraSSdI_M.md` V2.

> "il market profile lavora per mettere in luce Una distribuzione temporale per livello di prezzo" [0:02:54]
**Source GPS: 2h5TVfqtXXo | BEGIN**
(en) The market profile works to bring out a time distribution per price level.

> "il v-pock indica il volume più scambiato su un livello di prezzo ok Ovviamente" [0:17:09]
**Source GPS: 2h5TVfqtXXo | MIDDLE**
(en) The VPOC indicates the most traded volume at a price level, obviously over a certain period.

> "Ricordate che la Venere è il 70% dei volumi e ancora scambiato qua dentro" [0:28:52]
**Source GPS: 2h5TVfqtXXo | END**
(en) Remember that the value area (caption wrote Venere) is 70% of the volumes and is still traded in here.

### P2. Delta = direction of the strong hand at a price level (SOURCED)

Rule: delta at a price level is the arm wrestling between aggressive buyers and aggressive sellers; when one side destroys the other you get a very high delta, a red bar if the sellers win. Definition only; the numeric form (taker buy minus taker sell, delta percent) is in `extract_Ni6quY00dcw.md` C1. No threshold for "very high" (NOT stated).

> "il Delta possiamo definirlo come la direzione della mano forte su un determinato livello di prezzo" [0:10:52]
**Source GPS: 2h5TVfqtXXo | BEGIN**
(en) Delta we can define as the direction of the strong hand at a given price level.

> "quando uno dei due distrugge l'altro Quindi arriva aggressione cell ok Voi avete un Delta molto alto perché i Sellers e avrete una barra rossa" [0:11:07]
**Source GPS: 2h5TVfqtXXo | BEGIN**
(en) When one of the two destroys the other, so sell aggression arrives, you have a very high delta because of the sellers and you will have a red bar.

### P3. Mean reversion from the value-area deviation works only in balance, crashes in trend (SOURCED, what NOT to do)

Rule: many volume traders trade the exit from the volume standard deviations back to the center (re-balancing). It works when the market is in equilibrium; if you cannot tell balance from trend you "crash" (a long taken at the exit of the deviation while the market keeps going). The deviation is projected from the value area width: one standard deviation distance projected up and down, logic being that the market tends to return to the central point. Entry, stop: NOT stated. Target: the center is implied by the logic; he is asked if it can be used as a target and replies that he explained it earlier (answer partly inaudible in the caption). The balance-versus-trend classifier is NOT defined here (OURS: see P5). Partly computable (projection formula yes, regime filter OURS).

> "C'è un problema che questo funziona quando il mercato è in equilibrio Che cosa succede se io utilizzo questa tecnica in un mercato in Trend e non so differenziare le due cose che mi schianto" [0:09:21]
**Source GPS: 2h5TVfqtXXo | BEGIN**
(en) There is a problem: this works when the market is in equilibrium; what happens if I use this technique in a trending market and cannot tell the two apart, I crash.

> "si prende questa distanza e si proietta una deviazione standard dove deviazioni standard e così anche sotto perché la logica Qual è che il mercato per tendenza Ok tornerà al suo punto centrale" [0:11:58]
**Source GPS: 2h5TVfqtXXo | MIDDLE**
(en) You take this distance and project one standard deviation, and so also below, because the logic is that the market by tendency will return to its central point.

### P4. Reversal-to-value technique works mainly in a stationary market and can use the center as target (SOURCED)

Rule: the mean-reversion technique works above all when the market is stationary (ranging); in the next line the center of the distribution is discussed as a usable target. Parameters: none numeric; target object stated only by context (center of the distribution, OURS reading of an unclear caption).

> "la tecnica di mi reversal che funziona sopratutto quando noi abbiamo un mercato stazionario Ok si può utilizzare come target" [0:09:46]
**Source GPS: 2h5TVfqtXXo | BEGIN**
(en) The mean-reversal technique, which works above all when we have a stationary market; it can be used as a target.

### P5. POC shift and acceptance mark the start of directional days (SOURCED)

Rule: the shift of the POC (change of the balance point) shows when the market takes direction; if the next day's distribution settles beyond the previous POC (and out of the previous value area) it is acceptance and the market is in trend; a trending market keeps the direction well on a daily-profile base, and when the market accepts below again, price tends to continue. Operational definition of acceptance (his example): a close beyond the previous POC and value area counts as acceptance. Parameters: number of directional days "1 2 3 4" is stated loosely as an observation, no stop, no target. Same family as `extract_VHhvg96W6lc.md` V10 (day-to-day POC and value migration); this rule adds the "close beyond" test. Computable (yes): daily VPOC/value area from aggTrades, close vs previous VPOC/VA.

> "Ovvero lo shifting del boc quindi il cambiamento di bilanciamento del Pok serve per mostrare proprio quando questo mercato prende direzionalità" [0:20:30]
**Source GPS: 2h5TVfqtXXo | MIDDLE**
(en) That is the shifting of the POC, so the change of balance of the POC serves to show exactly when this market takes direction.

> "saremo in fase di Trend ma soprattutto avremo accettato Ok sopra sopra ragazzi il boc precedente" [0:21:28]
**Source GPS: 2h5TVfqtXXo | MIDDLE**
(en) We will be in a trend phase and above all we will have accepted above the previous POC.

> "la cosa che voglio farvi notare è come un mercato quando prende direzionalità tiene molto bene la tendenza e questo strumento è valido perché lavora su base giornaliera" [0:27:44]
**Source GPS: 2h5TVfqtXXo | END**
(en) What I want you to notice is how a market, when it takes direction, holds the trend very well, and this tool is valid because it works on a daily base.

### P6. Spike beyond the value area that is re-absorbed without a close beyond = failed breakout, then the old POC is retested (SOURCED)

Rule: if the market throws a spike outside the previous value area (his sketch: below), then re-absorbs it so that it does not close beyond the previous POC and does not close beyond the previous value area, the move is not acceptance but a fakeout; the market then accepts back inside, retests the POC (extreme inefficiency level) and resumes the direction, with 1 to 4 directional days afterwards (loose observation, no probability). Trigger: spike out of value, close back inside value and the previous POC. Entry, stop, target: NOT stated. Computable from klines/aggTrades (yes, daily VA and POC; spike and close tests are mechanical). Related: failed auction in `extract_qihraSSdI_M.md` V3.

> "ti Lancia questa Spike ecco quando voi Vedete questa spiking grigio Ok La vedi wearea contenuta e il poke che non fa accettazione" [0:28:57]
**Source GPS: 2h5TVfqtXXo | END**
(en) It throws this spike, here when you see this grey spike, the value area contained and the POC not making acceptance.

> "il mercato torna sotto fa tutta questa Spike ma non chiude sotto al precedente e neanche la velioria" [0:30:02]
**Source GPS: 2h5TVfqtXXo | END**
(en) The market goes back below, makes all this spike, but does not close below the previous one and not below the value area either.

> "perché il mercato è andato sotto e ha riassorbito perché la Spike funziona ragazzi perché la Spike ti comunica come il mercato ha raggiunto determinati livelli e quei livelli non sono stati accettati" [0:30:43]
**Source GPS: 2h5TVfqtXXo | END**
(en) Because the market went below and re-absorbed; the spike works because the spike tells you the market reached certain levels and those levels were not accepted.

> "e cosa fa torna a testare Pog un livello estremo su in efficienza questa non potenziale Trade e di nuovo riprende direzionalità si fa 1 2 3 4 giorni direzionali" [0:29:23]
**Source GPS: 2h5TVfqtXXo | END**
(en) And what does it do, it returns to test the POC, an extreme level of inefficiency, this is a potential trade, and again resumes direction, making 1 2 3 4 directional days (caption garbled).

### P7. Liquidity taken beyond the prior highs and re-entering the old range: balance exit done (SOURCED, direction unclear)

Rule: the market takes liquidity above the previous highs, re-enters the previous level and tests it, which means the exit from balance is done and a projection follows. Direction of the projection is NOT stated; his surrounding example was a short structure, so a bearish reading is OURS. Trigger is mechanical (sweep above prior high, close back inside the prior range, retest); no stop, no target. Computable (yes, klines).

> "il mercato per la giornata successiva nel momento in cui ti va a prendere liquidità sopra i massimi ok e ti rientra qua dentro ok all'interno del livello precedente e ti fa questo test che cosa ti sta comunicando Guarda che sono uscito dal Balance ho preso liquidità e vado in proiezione" [0:26:23]
**Source GPS: 2h5TVfqtXXo | END**
(en) The market, the next day, when it takes liquidity above the highs and comes back in here inside the previous level and makes this test, what is it telling you: look, I have left the balance, I took liquidity and I go into projection.

### P8. LVN gaps are inefficiencies: market tends to close them, so use them as targets (SOURCED)

Rule: low volume nodes are gaps in the profile, the places with the least liquidity inside a swing; the market tends to go and close these inefficiencies, so they are very good targets. Meaning of LVN: same as `extract_qihraSSdI_M.md` V1; the new element is use as take-profit. Parameters: LVN threshold (volume vs neighbours) NOT stated; no stop. Computable (yes): profile minima inside a swing, then first touch before the stop.

> "vedete come il mercato lascia dei Gap importanti Ok questi vengono chiamati lvn Ok lo voglio un nodo e dove abbiamo la minor parte di liquidità all'interno di uno swing" [0:27:12]
**Source GPS: 2h5TVfqtXXo | END**
(en) You see how the market leaves important gaps, these are called LVN, low volume node, where we have the least liquidity inside a swing.

> "le inefficienze viste oggettivamente da uno strumento quale questo ci sono e sono ottime per i target perché sono i livelli che il mercato tende a andare a chiudere" [0:32:39]
**Source GPS: 2h5TVfqtXXo | END**
(en) The inefficiencies seen objectively with a tool like this exist and are excellent for targets because they are the levels the market tends to go and close.

### P9. No longs while the visible-range profile shows strong sell pressure (SOURCED, what NOT to do)

Rule: if the profile over the visible horizon shows a non-balance phase of strong sell pressure (market not in consolidation, shape not a balanced bell), do not buy; he says it "removes the wish to take a long". Exact shape name is garbled in the caption (OURS: a one-sided profile with 70 percent of volume in a narrow band). Parameters for "strong" NOT stated; row size on TradingView set to 100 to 150 for the visible range (tool setting, OURS). Filter, not trigger; computable partly (profile skew and trend filter OURS).

> "perché il mercato Non è assolutamente in consolidamento questo già ti toglie la voglia di prenderti Long in una fase di pressione così bassa Ok di pressione Scusate così forte cell" [0:31:49]
**Source GPS: 2h5TVfqtXXo | END**
(en) Because the market is absolutely not in consolidation, this already takes away your wish to go long in a phase of such strong sell pressure (he corrects himself "so low... sorry, so strong").

## Not testable (one row per topic)

| Topic | Why not testable |
|---|---|
| Market profile vs volume profile vs TPO as visualisations (letters, 1980 Steve Mayer origin) | Display differences; the testable part is P1 |
| Auction market theory story: balance, aggression, new balance, real-estate and pandemic analogy | Narrative, no number |
| Volume Spread Analysis is the most precise volume technique on CFD and crypto without a feed | No trigger given; tick-volume caveat only (see `extract_qihraSSdI_M.md` V5) |
| Delta on CFD uses the broker's data, not real volume | Data caveat; not relevant to Binance aggTrades (real taker flow) |
| TradingView profile types (session, fixed range, visible range, periodic) and his preference | Tool menu |

Noticed: caption is full of misheard words (POC written boc/poke/pog, value area written "Venere"/"velioria"/"wearea", "mi reversal" for mean reversal), so quotes are verbatim but the reading of P3, P4 and P6 is partly inference; the caption never states a stop, a target distance or a hit rate in this lesson.
