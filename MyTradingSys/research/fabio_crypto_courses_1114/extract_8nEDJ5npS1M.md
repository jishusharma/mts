# Extract: Fabio Valentini (Fabervaale), "Orderflow Series 2025" (`8nEDJ5npS1M`)

- **Video ID:** `8nEDJ5npS1M`
- **Speaker:** Fabio Valentini (Fabervaale), Italian-language live lecture on his own channel (113 min, published 2025-06-09). Parts: auction market theory with volume-profile bias reading, then a live Nasdaq session with profile, CVD, footprint and VWAP. Language: Italian; every quote is the verbatim Italian caption, translations follow each Source GPS line as `(en)`.
- **Market in the video:** CME Nasdaq futures (M1/M5/M15 charts, profile, footprint, CVD on a futures platform) plus daily/weekly Bitcoin charts for the cycle and zone logic. Session clocks (New York open, Friday close) do not transfer to BTC; the balance/imbalance, value area and delta logic does.
- **Source:** `raw_transcripts_canonical/8nEDJ5npS1M_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. He narrates charts, so levels are pointed at ("this level") and his thresholds are mostly NOT stated; every number below is a speaker claim with no data shown. The caption mishears some words ("view app" = VWAP, "CPD" = CVD, "value area I" = value area high, "aria" = area).
- **Duplicate check (against `orderflow_extracts_1112/ORDERFLOW_RULES.md` and `fabio_crypto_courses_1114/`):** the following ideas are already extracted and are only referenced here, not repeated: value area = 70% of volume (`BB3c8visnkI` R6); POC as maximum-interest area (`DyS79Eb92Ug` R4); acceptance versus wick (`BB3c8visnkI` R4, `ridY2Z0hSQA` R3); finished/unfinished auction (`oa8kxSLLkAo` R1-R2); absorption in general (`usho6UVLqkE` R8, `rFPCtOcfUMI` R1); two-phase strategy choice (`VOiy8mAALWA` R1, R3; `VHhvg96W6lc` V1-V2); delta peak plus value-area low as buy zone (`VHhvg96W6lc` V11). Rules below add his numbers, trigger wording or stop/target placement that those files do not carry (R1 is the same family as VOiy8mAALWA R1 and VHhvg96W6lc V1 but adds the 20% figure and the 8-of-10 compression filter).

## Rules

### R1. Trend phases are about 20% of the time; a trend model in balance gets stopped on both sides (SOURCED)

Rule: the market is either in balance (accumulation/distribution) or in imbalance (directional). He claims trend phases are about 20% of the time and balance is the main state; a trend-following model is not broken, it is used in the wrong phase and gets stopped on both sides inside large ranges. The 20% figure is his claim, no study shown (OURS: measurable on BTC with a range/trend classifier). Phase classifier parameters: NOT stated.

> "se andate a vedere i mercati le fasi di trend sono un 20% del tempo. La parte principale è di accumulo e distribuzione." [0:17:30]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "if you look at the markets, trend phases are 20% of the time. The main part is accumulation and distribution."

> "il modello che avete creato funziona, il problema è che non funziona in quella condizione di mercato" [0:04:11]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "the model you built works, the problem is that it does not work in that market condition."

### R2. Volatility filter after a run of compression sessions (SOURCED, index-futures-only wording, idea transfers)

Rule: when 8 of 10 New York sessions were compressed and his Nasdaq model performed badly, he built a volatility filter and only trades when the session shows expansion. The 8-of-10 count is one anecdote (March 2024); the filter's definition and threshold are NOT stated (OURS/unknown). For BTC: gate entries by a realized-range regime, threshold to be fitted.

> "otto sessioni New York su 10 erano in compressione. In questi casi la cosa migliore che mi è venuta in mente da fare è creare un filtro. creare un filtro di volatilità" [0:42:49]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "eight New York sessions out of 10 were in compression. In these cases the best thing I could think of was to create a filter, a volatility filter."

### R3. Opening-range breakout gives direction; breakout-and-re-entry days hurt (SOURCED, index-futures-only)

Rule: breaking the range of the first hours of the New York session has a high probability of showing the day's direction, same logic as leaving the value area. The days that hurt are breakout-and-re-entry days where direction is not clear. Range length (hours) and probability number: NOT stated. BTC equivalent session open is OURS.

> "il range che viene creato dalle prime ore della sessione di New York, il breakout di quel range dà una ehm probabilità di identificare la direzionalità molto alta" [0:43:15]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "the range created by the first hours of the New York session, the breakout of that range gives a very high probability of identifying the direction."

> "quando beccate condizioni di breakout e rientro, breakout e rientro, quindi quando la direzionalità di giornata non è chiara" [0:43:55]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "when you catch breakout-and-re-entry conditions, breakout and re-entry, that is, when the direction of the day is not clear."

### R4. A shifted fair value (POC/value area) is the direction of pressure, no personal opinion needed (SOURCED)

Rule: if the session's fair value moved clearly from the prior session's level, the pressure of operators is up or down accordingly; he reads direction from where value moved, not from price. How big a shift counts ("not by a little"): NOT stated.

> "il fair value è passato da questo livello a questo livello, il che vuol dire che la pressione degli operatori è rialzista o ribassista. Qua non c'è interpretazione personale" [0:22:12]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "the fair value went from this level to this level, which means the pressure of operators is bullish or bearish. Here there is no personal interpretation."

### R5. POC shift plus value-area shift in the same direction: next-day continuation bias (SOURCED)

Rule: when a day closes with both the POC and the value area shifted down, volume analysis says "continuation short", and the next day he looks for a return into the prior session's zones to redistribute; when both value area and POC rise, he says there is a very high probability of long continuation the next day. Daily profile on session basis. Stop/target: NOT stated here. "Very high probability" is a verbal claim, no number (OURS: test next-day continuation after double shift). Same family as VOiy8mAALWA R6; this adds the next-day return-to-prior-zone entry idea.

> "Chiudiamo la nostra giornata, nello specifico il 15 di aprile, con uno shift del POC a ribasso e un cambio della value area a ribasso, il che vuol dire che l'analisi volumetrica ci sta gridando. Continuazione short." [0:22:51]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "We close our day, specifically April 15, with a POC shift down and a value area change down, which means volume analysis is shouting continuation short."

> "la value area mi si alza, mi si alza anche il POC e mi comunica che il giorno successivo c'è un'altissima probabilità di continuazione long" [0:31:23]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "the value area rises on me, the POC rises too, and it tells me that the next day there is a very high probability of long continuation."

> "Nella giornata successiva quello che noi andremo a cercare è potenzialmente un ritorno all'interno delle zone della sessione precedente e una ridistribuzione" [0:23:08]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "On the next day what we will look for is potentially a return inside the zones of the previous session and a redistribution."

### R6. Value area up but POC down is still accumulation: stay long, do not short the new high (SOURCED, what NOT to do)

Rule: a day that makes a new high, closes with the value area higher but the POC lower (most volume traded lower inside the day) looks confusing; a beginner says short, he says long because the value area shift shows accumulation orders. Rule is VA-shift over POC-shift when they disagree. Day count/threshold: NOT stated. Computable from daily profiles.

> "che ci chiude con la value area al di sopra, ma il po al di sotto questa, ecco, può essere confusionaria" [0:32:56]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "that closes us with the value area above but the POC below, this one can be confusing."

> "No, sei long. Sei long perché questi sono ordini di accumulo e lo vedi dallo shift della value area." [0:33:13]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "No, you are long. You are long because these are accumulation orders and you see it from the shift of the value area."

### R7. Trade with the value bias: short above the value area when bearish, buy at a discount when bullish (SOURCED)

Rule: when the value-migration bias is down, short above the area holding 70% of volume ("premium"); when bias is up, buy at a discount in the direction of the bias, accumulating below value. Entry trigger inside the premium zone beyond "price arrives there": NOT stated (he adds an orderflow trigger of his choice). Stop/target: see R14.

> "se io so che il mercato ha una tendenza ribassista, voglio shortare al di sopra della presenza del 70% dei volumi, sì o no? Assolutamente sì." [0:24:17]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "if I know the market has a bearish tendency, I want to short above the presence of 70% of the volumes, yes or no? Absolutely yes."

> "comprare a favore della direzionalità, quindi se venite da sotto sarete direzionalità long, comprare discount a favore della direzionalità" [0:32:27]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "buy in favour of the direction, so if you come from below you will be directionally long, buy at a discount in favour of the direction."

### R8. Inside-value day is neutral; buy below the prior value area; merge overlapping days into one composite profile (SOURCED)

Rule: a session whose whole value area sits inside the prior area is neutral; in that balance, longs taken below the prior value area are valid when the bias is long. When several days overlap, merge them with a fixed-range volume profile (composite) and trade discount-side in the direction of bias. Overlap threshold: NOT stated.

> "Perché neutrale? Perché siamo contenuti comunque all'interno della tutta la l'area precedente." [0:29:38]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "Why neutral? Because we are contained anyway inside the whole previous area."

> "Quello che si può fare senza dubbio di nuovo è prendersi long quando siamo al di sotto della value area precedente perché siamo in una condizione di bilanciamento, quindi tutti questi sono long validi." [0:29:52]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "What you can do without doubt again is take longs when we are below the previous value area because we are in a balance condition, so all these are valid longs."

> "potete creare un singolo volume profile, cioè le accorpate tutte, andate su fixed range volume profile, dall'inizio alla fine le accorpate tutte quante" [0:32:09]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "you can create a single volume profile, that is, you merge them all, go to fixed range volume profile, from start to end you merge them all."

### R9. Range fade: buy the value-area edge in a long bias, target the opposite level (SOURCED)

Rule: in a balance with 70% of volume inside and a long bias, put buys at the value level (value area low, on rejection) with the target at the opposite level; he calls it the best way to trade ranges because balanced markets tend to return to fair value (elastic effect). Entry is a limit at the level or on a rejection test; stop beyond the extreme: NOT stated numerically; target = opposite edge (SOURCED).

> "si possono mettere direttamente dei buy sul livello della value con il target livello opposto" [0:39:47]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "you can put buys directly on the value level with the target the opposite level."

> "Questo è il miglior modo di tradare range, ragazzi, perché il mercato quando è bilanciato ha una probabilità altissima di tornare al fair value, quindi al valore centrale." [0:40:52]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "This is the best way to trade ranges, guys, because when the market is balanced it has a very high probability of returning to fair value, that is, the central value."

> "noi sappiamo che il 70% dei volumi è contenuto qui all'interno e che la direzionalità dell'asset è long" [0:39:28]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "we know that 70% of the volumes is contained in here and that the direction of the asset is long."

### R10. Outliers beyond the range ("outline") re-enter with very high probability (SOURCED)

Rule: price outside the balance range (beyond the value area edges, "outline") has a very high probability of re-entering; the range-bound trade is the re-entry. Probability: NOT stated (verbal "altissima"). Must be applied only when the phase is balance (see R1). Same family as 9IliXww64uM R10.

> "queste qua prendono il nome di outline, cioè quando il mercato va al di fuori dei range, questa operatività range bound ha una probabilità altissima di rientrare dentro." [0:41:04]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "these are called outlines, that is, when the market goes outside the ranges, this range-bound trading has a very high probability of re-entering."

### R11. Only take the range target if reward-to-risk is worth it: 3.45 yes, 1.79 less, 1.5 seen (SOURCED)

Rule: for value-edge range trades he reports example reward-to-risk of 3.45 ("worth it"), 1.79 ("less"), and about 1.5 on a retest entry; the target is not always worth it, so measure R:R before taking the range trade. Minimum R:R cut-off: NOT stated (OURS: sweep 1.5 / 1.8 / 3.5 as thresholds; note the three numbers are examples read off charts, not a tested rule).

> "È che il target non sempre ne vale la pena, cioè rischio rendimento 1 a 3,45 ne vale la pena. 1 a 1,79 meno." [0:40:16]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "It is that the target is not always worth it, that is, risk-reward 1 to 3.45 is worth it. 1 to 1.79 less."

> "Anche in questa casistica, o meglio, rientrava qua dentro, quindi eseguivate qua su test, qua era un 1 a 1,5." [0:40:36]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "Also in this case, or rather, it re-entered in here, so you executed here on the test, here it was 1 to 1.5."

### R12. Leaving the value area creates new value; the old edges become the pivot (SOURCED)

Rule: when price exits the value area it is creating new value; the odds favour continuation if the retest of the value area is rejected, and very often the market uses the old value-area levels as a pivot and takes direction. This is the entry for the trend case: wait for the exit, then the test of the edge. Number of bars outside / acceptance filter: NOT stated. Stop/target: NOT stated here.

> "quando noi usciamo dalla value area I stiamo creando nuovo valore, quindi stiamo andando nella parte superiore del della distribuzione, quindi possiamo avere una maggiore probabilità che se testa la value area rigetta abbiamo una continuation" [0:38:10]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "when we exit the value area high we are creating new value, so we are going into the upper part of the distribution, so we can have a higher probability that if it tests the value area [and] rejects we have a continuation."

> "molto spesso vedrete che quando il mercato esce dalla value area usa quei livelli come perno e prende direzionalità." [0:38:26]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "very often you will see that when the market leaves the value area it uses those levels as a pivot and takes direction."

### R13. After breaking out of balance and accepting lower, the return to the broken value-area low is rejected (SOURCED)

Rule: if the market left a balance down and accepted lower prices (low volume at the break), then when it later returns to the old value area low from below, the main probability is rejection; a short from that retest. Stop/target: NOT stated here; he says in the example the opposite balance is where to exit (R15). Acceptance window: NOT stated. Same family as BB3c8visnkI R9.

> "Il mercato mi ha accettato valori inferiori di volume, ok? Di rottura. Il che vuol dire che quando il mercato tornerà a validare quei livelli, la probabilità principale è che venga rifiutato." [0:54:18]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "The market accepted lower volume values for me, ok? Of breakout. Which means that when the market comes back to validate those levels, the main probability is that it will be rejected."

### R14. Stop behind the hardest zone, target in the easiest zone: target inside the 70% value area, stop outside it (SOURCED)

Rule: place the stop behind the zones the market finds hardest to break and the target in the zones easiest for the market to reach; concretely the target goes where the 70% value area is and the stop outside the value area ("path of least resistance"). Tick/ATR buffer beyond the area: NOT stated.

> "noi cercheremo di coprire lo stop loss dietro le zone più difficili dal mercato per il mercato da rompere e mettere il target nelle zone più facili per il mercato da raggiungere." [1:03:17]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "we will try to cover the stop loss behind the zones that are hardest for the market to break and put the target in the zones easiest for the market to reach."

> "ci piazziamo il target dove sta il 70% dell'area di valore e ci copriamo lo stop loss al di fuori della value area." [1:03:32]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "we place the target where the 70% of the value area is and we cover the stop loss outside the value area."

### R15. Take the short profit just before the value-area low, the most sensitive level (SOURCED)

Rule: a short aiming down into value should be closed slightly before the value area low because it is the most sensitive level and price can bounce there; a short taken from a low zone near the VAL is not a premium setup, a better short starts from a higher zone. Buffer ("poco prima"): NOT stated.

> "Perché poco prima della zona? Perché il rischio è che vi rimbalzi sulla value area low, che è il livello più sensibile." [1:00:37]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "Why shortly before the zone? Because the risk is that it bounces on you at the value area low, which is the most sensitive level."

> "Questa zona premium deriva proprio dal fatto che la value area low, che è la zona più sensibile di giornata, come ha reagito qua sotto, sta poco sopra." [0:59:48]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "This premium zone comes precisely from the fact that the value area low, which is the most sensitive zone of the day, as it reacted down here, is just above."

### R16. Do not trade into the Friday close: range compression with volatility bursts (SOURCED, index-futures-only)

Rule: late on Friday toward the close the market compresses into a range and throws volatility bursts; it is harder to trade, so he does not trade those hours. The CME Friday close does not exist for BTC spot; a BTC analogue (late-Friday UTC / weekend low-liquidity) is OURS/untested. Clock: NOT stated.

> "Perché andiamo verso la chiusura del venerdì, il mercato si comprime a livello di range, si tira delle botte di volatilità, ma è più complicato tradare a queste ore" [1:04:53]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "Because we are heading toward the Friday close, the market compresses in range, throws volatility blows, but it is harder to trade at these hours."

### R17. The volume-profile peak of the prior distribution is the protection level for stops (SOURCED)

Rule: the biggest volume peak (most aggressive level) of the preceding distribution is a protection level; use it to cover the stop and as the sensitive zone to load a short from, and the overshoot past it was about half an M1 candle in his example. Peak = highest-volume price bin of the swing's fixed-range profile (1 example overshoot only, not a tested tolerance). Stop buffer: NOT stated.

> "Il prezzo ci dà un livello uno di informazione e il profile ci dà l'aggressione più importante della distribuzione precedente." [1:31:54]
**Source GPS: 8nEDJ5npS1M | END**
(en) "Price gives us a level one of information and the profile gives us the most important aggression of the previous distribution."

> "Questo è un livello di protezione, ok? Che cosa vuol dire? Che se io devo coprirmi il mio stop loss" [1:30:17]
**Source GPS: 8nEDJ5npS1M | END**
(en) "This is a protection level, ok? What does it mean? That if I have to cover my stop loss."

> "Anzi, in realtà meno. Questo è stato quanto ha sporcato la zona. Metà candela M1." [1:34:18]
**Source GPS: 8nEDJ5npS1M | END**
(en) "Actually, in reality less. This is how much it dirtied the zone. Half an M1 candle."

### R18. Inside the value area, pick the discount-side volume peak as target; the premium-side peak is ignored (SOURCED)

Rule: within the value area of the swing there can be several volume peaks; for a short, the premium peak (above) is not of interest and the discount peak is; the first target is the nearest peak and the second the next one, with a few ticks of tolerance. Peak detection method and tick tolerance: NOT stated.

> "Questa è situazione premium, quindi non ci interessa. Questa è situazione discount, ci può interessare." [1:35:13]
**Source GPS: 8nEDJ5npS1M | END**
(en) "This is a premium situation, so it does not interest us. This is a discount situation, it may interest us."

> "Quindi io so già, se sono short, che il mio primo target deve essere questo qua sopra e il mio secondo è questo qua sotto." [1:35:39]
**Source GPS: 8nEDJ5npS1M | END**
(en) "So I already know, if I am short, that my first target must be this one up here and my second is this one down here."

> "il mercato può protrarre, parliamo di pochi tic di differenza, eh, ma il mercato può protrarre o in zona 1 o in zona due." [1:35:29]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the market can extend, we are talking about a few ticks of difference, but the market can extend either in zone 1 or in zone two."

### R19. CVD is a pressure summary and leads price: the flip comes before the setup (SOURCED)

Rule: CVD (cumulative volume delta) is the summary of market pressure; in his example it switched at 20:55 and the price setup only came after the aggression had already started, because price takes time to discount the information. A volume divergence while price still falls can prepare the explosion in the other direction. Delta resolution/divergence threshold: NOT stated (visual). Computable: CVD sign change time versus swing time.

> "il CDD è il cumulative Volume Delta e è un riassunto di pressione di mercato" [1:15:48]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the CVD is the cumulative volume delta and it is a summary of market pressure."

> "Il mercato ha iniziato ad accelerare a livello di volume, cioè la pressione cambiata. Il prezzo ha messo del tempo a scontare questa informazione perché perché era un mercato rialzista, stava accelerando a rialzo." [1:37:12]
**Source GPS: 8nEDJ5npS1M | END**
(en) "The market started to accelerate in terms of volume, that is, the pressure changed. Price took time to discount this information because it was a rising market, it was accelerating up."

> "il mercato può fare una riaccumulazione mentre scende, prepara il movimento successivo, come può fare una divergenza di volumi da qua dentro e prepara l'esplosione ribassista" [1:24:31]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the market can do a re-accumulation while it falls, prepares the next move, as it can make a volume divergence from in here and prepares the bearish explosion."

### R20. Momentum trades follow the CVD direction; opposite-side aggression starts while price is still stationary (SOURCED)

Rule: for a momentum trade, position with the CVD direction (short when CVD is in sell dominance); but the opposite aggression can already begin while price is stationary, which is the delay between the pressure and price. Sets "do not fight CVD for a momentum trade". Dominance threshold: NOT stated. Stop/target: NOT stated.

> "Quindi se io voglio andare a fare operatività momentum sicuramente mi vado a posizionare con un'operatività momentum che segue il CPD short" [1:39:14]
**Source GPS: 8nEDJ5npS1M | END**
(en) "So if I want to do momentum trading I will certainly position myself with a momentum trade that follows the CVD short."

> "L'aggressione buy inizia mentre siamo in una condizione di stazionamento." [1:39:45]
**Source GPS: 8nEDJ5npS1M | END**
(en) "The buy aggression starts while we are in a stationary condition."

### R21. After a structural break with CVD collapsing, short with the stop above the sell aggression; first buyer support is the next volume level (SOURCED)

Rule: after a distribution and a structural break, if CVD collapses in full sell dominance, the first potential buyer support is the next profile level below (target); the stop goes above the sell aggression / the protection level or the aggressive-buyer level already passed. Stop distance beyond that level: NOT stated; he calls it a "statistical advantage" with no data shown.

> "vediamo che il CVD al di sotto sta collassando, cioè il CVD sta crollando ed è in dominio sell completo e vediamo che il primo livello di potenziale supporto buyers magari sta qua sotto" [1:41:33]
**Source GPS: 8nEDJ5npS1M | END**
(en) "we see that the CVD underneath is collapsing, that is, the CVD is crashing and is in complete sell dominance and we see that the first level of potential buyer support is maybe down here."

> "concordate sul fatto che questo delta a livello di posizionamento con uno stop loss che magari mi posso mettere sopra l'aggressione cell è un bel vantaggio statistico" [1:41:52]
**Source GPS: 8nEDJ5npS1M | END**
(en) "do you agree that this delta in terms of positioning, with a stop loss that I can maybe put above the sell aggression, is a nice statistical advantage."

> "questo era un easy short con lo stop loss sopra il livello di protezione per arrivare o sul livello buyers aggressivo che già abbiamo superato" [1:48:08]
**Source GPS: 8nEDJ5npS1M | END**
(en) "this was an easy short with the stop loss above the protection level, to arrive either on the aggressive buyers level that we already passed."

### R22. "Punch into the wall": a cluster of aggressive buyers at the candle top with zero response is absorption (SOURCED)

Rule: on a delta footprint, if the top of a bar shows a conglomerate of aggressive buyers that got zero response (only a wick), passive orders absorbed everything: absorption, and the bar's top becomes a protection level for sellers. Footprint form: delta footprint with profile display. Cluster size, delta threshold, number of price levels: NOT stated (visual).

> "il top di questa candela ha un conglomerato di Bayers aggressivi che hanno avuto zero risposta" [1:44:37]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the top of this candle has a conglomerate of aggressive buyers who had zero response."

> "Perché? Perché gli ordini passivi qui hanno, aggred, scusa, hanno assorbito tutto quanto. Quindi questa è una condizione di assorbimento." [1:45:07]
**Source GPS: 8nEDJ5npS1M | END**
(en) "Why? Because the passive orders here have, aggre, sorry, absorbed everything. So this is an absorption condition."

> "Dovreste capire quando i buyers sono in una condizione di zero risultato." [1:45:20]
**Source GPS: 8nEDJ5npS1M | END**
(en) "You should understand when the buyers are in a zero-result condition."

### R23. Sellers' "lock" at the top rejects everything and marks a protection level to retest (SOURCED)

Rule: a bar top where buyers cluster and the sellers "lock" (hit back and reject all of it) is a protection level; the market may come back, revalidate it and test whether it still interests them, then decide to redistribute above. Entry on the retest; stop/target: NOT stated.

> "il top della candela qua vede un conglomerato di buyers e un lucchetto sellers. Cosa vuol dire un lucchetto? Che qui hanno aggredire i sellers e hanno rigettato tutto quanto." [1:45:31]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the top of the candle here sees a conglomerate of buyers and a seller lock. What does a lock mean? That here the sellers aggressed and rejected everything."

> "hanno creato un altro livello di protezione, quindi il mercato potrebbe tornar su, rivalidarlo, testare se questo livello è di loro interesse" [1:48:26]
**Source GPS: 8nEDJ5npS1M | END**
(en) "they created another protection level, so the market could come back up, revalidate it, test whether this level is of interest to them."

### R24. Sellers still hitting the lows means sellers are alive; sellers hitting the bottom without result is crucial (SOURCED)

Rule: in the developing bar, aggressive selling into the lows means aggressive sellers are still present (do not buy yet); when sellers keep hitting the bottom of a bar and no longer get a result, he calls it crucial information that cannot be read without order flow (selling absorption/exhaustion at the low). Reading is bar-by-bar on the footprint; thresholds: NOT stated.

> "se un seller mi vende i minimi, vuol dire che abbiamo ancora sellers aggressivi qua dentro" [1:46:14]
**Source GPS: 8nEDJ5npS1M | END**
(en) "if a seller sells me the lows, it means we still have aggressive sellers in here."

> "i sellers aggrediscono sul bottom della candela, ma non riescono più ad ottenere un un risultato. Ok? E questo è, ragazzi, è cruciale." [1:49:37]
**Source GPS: 8nEDJ5npS1M | END**
(en) "the sellers aggress on the bottom of the candle, but can no longer obtain a result. Ok? And this is, guys, crucial."

### R25. Aggressive buyers being absorbed at the top level: expect the level to be attacked and broken (SOURCED, numbers are a viewer's)

Rule: when aggressive buyers are absorbed at the top price level, the probability is high that the market fires against the level, attacks it and moves to the next level (a short bias). The numbers 104 delta at the top and 75 at the second level were read out from a viewer's chat, not his threshold; his own threshold: NOT stated (OURS: per-price-level delta from aggTrades at the bar high versus the next level).

> "Al top ci sono stati 104 di delta buy sul top 75 sul secondo. Bello." [1:07:57]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "At the top there were 104 of buy delta on the top, 75 on the second. Nice."

> "la probabilità che sparano contro questo livello, aggrediscono e vanno al secondo è è molto alta perché perché i buyers aggressivi stanno venendo assorbiti" [1:08:21]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "the probability that they fire against this level, attack and go to the second is very high because the aggressive buyers are being absorbed."

### R26. Anchored VWAP from the swing pivots: heavy short capital redistributes at VWAP (SOURCED)

Rule: take the pivot high and pivot low of the swing, draw the profile of the dealing range and the VWAP of the move; in a short move heavy-capital sellers cannot short from the low, so they wait for better prices to add, and he says the redistribution happened exactly at the VWAP. VWAP is an institutional bias line. Anchor = swing pivot; entry on a test of VWAP from below in a downswing is the implied trade; stop/target: NOT stated. Computable from klines/aggTrades.

> "volume weighted average price e questa è fondamentale perché è un'indicazione di bias tipicamente istituzionale" [1:19:57]
**Source GPS: 8nEDJ5npS1M | END**
(en) "volume weighted average price and this is fundamental because it is a typically institutional bias indication."

> "vi prendete i profili del range, del dealing range che è stato generato, ok? E vi prendete il view app. Guardate dove stanno ridistribuendo." [1:51:46]
**Source GPS: 8nEDJ5npS1M | END**
(en) "you take the profiles of the range, of the dealing range that was generated, ok? And you take the VWAP. Look where they are redistributing."

> "questi operatori che shortano capitali pesanti non possono shortare dal minimo, quindi aspettano dei dei livelli di prezzo migliorativi per aggiungere posizioni se vogliono andare a fare una continuation" [1:52:20]
**Source GPS: 8nEDJ5npS1M | END**
(en) "these operators who short heavy capital cannot short from the low, so they wait for better price levels to add positions if they want to go for a continuation."

### R27. Expansion after a balance is about twice the balance range: project and exit at 2x (SOURCED, speaker claim)

Rule: the imbalance (explosive) phase is about two times the amplitude of the preceding balance phase; for a longer-term position after a failed breakout inside accumulation, take two times the dealing-range expansion as the exit (first and second projection). He says "statistically" with no data shown; for BTC dealing ranges on weekly/daily. Stop: he buys and holds without a tight stop (investor mode); stop for the speculative version: NOT stated here (see R28).

> "la fase di inbalance, quindi la fase esplosiva, ha due volte l'ampiezza della fase di bilanciamento" [0:49:33]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "the imbalance phase, so the explosive phase, has twice the amplitude of the balance phase."

> "Come lo faccio a capire la fase di esplosione? Se sono lungo termine sul settimanale, mi vado a prendere due volte l'espansione del dealing range." [0:50:25]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "How do I understand the explosion phase? If I am long-term on the weekly, I take two times the expansion of the dealing range."

> "Questi punti di acquisto, a livello di liquidazione, per me, se sono un investitore, hanno mediamente a livello statistico, due volte l'espansione della fase accumulatoria." [0:51:04]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "These buy points, in terms of liquidation, for me, if I am an investor, have on average, statistically, twice the expansion of the accumulation phase."

### R28. Trend entry on the breakout-origin candle: stop under the initiating candle, target the upper dealing range (SOURCED)

Rule: after an exit from weekly accumulation (BTC cycle bias up), trade the daily zone of the candle that originated the breakout: stop below the initiating candle, target the upper dealing range; he reports about 1:2 on one example and 4.67 on another daily example. The volumes that caused the aggression are the same that protect the zone on return and re-accumulate. Entry on the retest of the origin candle zone (acceptance of the candle); stop distance: NOT stated beyond "under the candle". The R:R figures are read off two chart examples.

> "Questi modelli trend following possono essere attuati con lo stop loss sotto la candela di iniziazione del movimento." [0:46:00]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "These trend-following models can be implemented with the stop loss under the initiating candle of the move."

> "i volumi che hanno provocato questa aggressione sono gli stessi volumi che hanno protetto la zona al rientro e qua hanno rigenerato una nuova condizione di accumulo" [0:44:51]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "the volumes that caused this aggression are the same volumes that protected the zone on the return and here they regenerated a new accumulation condition."

> "Qua il target potrebbe essere il dealing range superiore, un a 4,67" [0:48:04]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "Here the target could be the upper dealing range, a 4.67."

> "Perché queste metodologie funzionano in questo caso? Perché stiamo lavorando allineati al ciclo di lungo termine." [0:48:00]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "Why do these methodologies work in this case? Because we are working aligned with the long-term cycle."

### R29. Acceptance is value built outside the area, not a wick; a failed auction is an attack with no result (SOURCED)

Rule: he does not want a wick beyond the area, he wants to see the market build value beyond it (acceptance); a failed auction is an attack on a level that gets no result. Acceptance window (bars/time) NOT stated. Same family as BB3c8visnkI R4 and oa8kxSLLkAo; kept for the exact wording and its link to the profile.

> "io non voglio che mi faccia una wiek, ma voglio vedere il mercato che costruisca valore al di sopra dell'aria." [0:37:19]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "I do not want it to make a wick for me, I want to see the market build value above the area."

> "vuol dire che il mercato effettivamente non riesce ad avere un riscontro da quello che sta provando a rompere, quindi aggredisce un livello ma non ha un risultato" [0:36:55]
**Source GPS: 8nEDJ5npS1M | BEGIN**
(en) "it means the market effectively does not get a response from what it is trying to break, so it attacks a level but gets no result."

### R30. Order flow is used to qualify the zone and the timing, not as a stand-alone signal (SOURCED)

Rule: three uses: profile for the grey situations (where the aggression was largest), footprint as the zone qualifier and trigger refiner, CVD for timing; he prefers the delta footprint with profile display. Never replaces price/structure context (R1, R4-R7). All thresholds: NOT stated.

> "Il timing, le situazioni grigge, quindi andare a usarlo come linea di demarcazione su setup premium e non premium e soprattutto quando lo andate a utilizzare come qualificatore di zona." [1:11:51]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "The timing, the grey situations, so using it as a line of demarcation between premium and non-premium setups and above all when you use it as a zone qualifier."

> "Il profilo volume è molto utile per andare a capire dove c'è stata più aggressione, almeno questo è come lo utilizzo io." [1:14:20]
**Source GPS: 8nEDJ5npS1M | MIDDLE**
(en) "The volume profile is very useful for understanding where there was more aggression, at least this is how I use it."

> "quello che prediliggo io è il footprint a delta con visualizzazione a profilo" [1:44:04]
**Source GPS: 8nEDJ5npS1M | END**
(en) "what I prefer is the delta footprint with profile display."
