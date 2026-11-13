# Extract: Fabio Valentini (Fabervaale), "Le differenze tra VSA e Orderflow" (`692OdHaZnRU`)

- **Video ID:** `692OdHaZnRU`
- **Speaker:** Fabio Valentini (Fabervaale), Italian professional trader (video published 2023-01-22; Italian caption)
- **Market in the video:** concept talk on Volume Spread Analysis (Wyckoff / VSA) versus order flow; mentions crypto, CFD/FX, index and commodity futures as markets with different volume quality. No entry, stop, target, timeframe or numeric threshold is given anywhere in this video.
- **Source:** `raw_transcripts_canonical/692OdHaZnRU_raw.txt` (Italian caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\; auto-caption, many mis-heard words kept verbatim in quotes)
- **Labels:** SOURCED = verbatim Italian quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading or parameter, no quote. English translation of each quote is on the `(en)` line after the GPS line.
- **Overlap:** effort versus result and absorption are the same concept as `extract_Ni6quY00dcw.md` C3 and C4 (not re-derived). Rules below are definitions and data-quality caveats, not trade triggers.

## Rules

### S1. VSA bar inputs: volume, range, body, close location (SOURCED)

Rule: VSA reads each candle from four numbers: volume in the candle, the range (high minus low, not the bid-ask spread), the body (open to close) and where the close sits in the range. Computable from Binance klines: yes (volume, high, low, open, close are all in a 1m or 5m kline). Thresholds for "high volume" or "small body" NOT stated (OURS/unknown).

> "va a guardare alla quantità di volume all'interno della candela al range dello Spread Non parliamo di spread classico Ma parliamo di differenza fra with to week e fra apertura e chiusura di candela" [0:07:05]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) It looks at the quantity of volume inside the candle, at the range of the spread; we are not talking about the classic spread but the difference between wick to wick and between open and close of the candle.

### S2. Effort without result: high volume and wide range but a tiny close body (SOURCED)

Rule: if volume is high and the excursion (high to low) is wide, but the candle closes with a very small body, the initial effort gave a large result that was not sustainable and price was pulled back to equilibrium, like a stretched rubber band; treat it as a signal to consider more carefully, not as a trade by itself. Computable from klines: yes (range / volume high, body / range low); percentile cut-offs would be OURS.

> "Quindi hai una relazione diretta importante fra prezzo e volumi però lo stesso tempo la chiusura della candela è piccolissima quindi la candela presenta un corpo piccolissimo" [0:04:39]
**Source GPS: 692OdHaZnRU | BEGIN**
(en) So you have an important direct relation between price and volumes but at the same time the close of the candle is tiny, so the candle has a tiny body.

> "e ha dato un risultato alto ma poi quel risultato alto non è stato sostenibile vedetelo come un elastico all'inizio Siete riusciti a tirare l'elastico poi la forza vi ha riportata un punto di equilibrio" [0:04:54]
**Source GPS: 692OdHaZnRU | BEGIN**
(en) And it gave a high result but then that high result was not sustainable; see it like a rubber band, at the start you managed to pull the band, then the force brought you back to a point of equilibrium.

### S3. Volume is only half of the information; price result of the effort decides absorption (SOURCED)

Rule: volume (effort) must be read together with the price result: the price shows whether the effort was absorbed. Never read volume alone. Same as `extract_Ni6quY00dcw.md` C3 for the footprint version (absorption divergence).

> "l'informazione che abbiamo sui volumi quindi l'informazione Recorder registrata dai volumi è metà perché l'altra parte risiede nel prezzo" [0:05:28]
**Source GPS: 692OdHaZnRU | BEGIN**
(en) The information we have on volumes, the recorded information from the volumes, is half, because the other half lies in the price.

> "perché il prezzo Fornisce poi la risultante di quello sforzo e quindi ci fa capire se stiamo avendo una condizione di assorbimento" [0:05:34]
**Source GPS: 692OdHaZnRU | BEGIN**
(en) Because the price then provides the result of that effort and so makes us understand if we are having an absorption condition.

### S4. Order flow shows exhaustion inside the bar; VSA only deduces it from bar data (SOURCED)

Rule: VSA works by deduction from the bar (where the force was exhausted, where the price response is no longer proportional to the volume); order flow works by visualisation inside the single candle, which needs a dedicated platform with a tick data feed. For us: the aggTrades tape can supply the inside-the-bar view, klines only the VSA view. Computable: yes for both (aggTrades for inside-bar delta, klines for VSA).

> "dove effettivamente la forza sia esaurita dove abbiamo il patto blister esistence dove la risposta sviluppo del prezzo non è più commisurata ai volumi" [0:12:47]
**Source GPS: 692OdHaZnRU | END**
(en) Where the force is actually exhausted, where we have effort versus resistance, where the response and development of the price is no longer commensurate with the volumes.

### S5. Delta bars differ from VSA volume bars: bar colour and volume colour can disagree (SOURCED)

Rule: in VSA the volume colour follows the candle close (a candle closing red never has a green volume bar); in order flow the bars are delta bars and that changes the situation completely, so the two volume series must not be mixed. For BTC build volume bars as total volume (klines) and delta bars (aggTrades taker side) as separate series. Computable: yes (aggTrades has the taker-side flag).

> "Quindi se la candela chiude rossa non capiterà mai che avrete un volume qua sotto verde parlo di usa ok" [0:07:56]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) So if the candle closes red you will never have a green volume underneath, I am talking about VSA, ok.

> "perché se andiamo a parlare di volumi Order flowers andiamo a parlare di barre a delta lì cambia completamente la situazione" [0:08:06]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) Because if we talk about order flow volumes we talk about delta bars, there the situation changes completely.

### S6. Tick volume tracks real volume at swing points but is not a substitute (SOURCED, observation not a study)

Rule: at the swing low and swing high pivots the maximum-volume bar appears in both the tick-volume chart and the real-volume platform, and volume grows when price takes direction; but levels differ and one does not replace the other. He cites an old study (about 2011 to 2012) of high correlation, not re-done since (OURS: unverified, no number given). For BTC, kline volume is real traded volume on one exchange, so this caveat is about CFD tick volume, not Binance klines.

> "Cosa vediamo nello precedente che effettivamente abbiamo un Massimo volumetrico stessa identica cosa noi l'abbiamo all'interno di questa visualizzazione qua" [0:09:19]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) What do we see in the previous one: that we effectively have a volume maximum, and the very same thing we have inside this visualisation here.

> "e poi quando prende direzionalità i volumi crescono esponenzialmente quindi c'è da dire che c'è una relazione fra i due ma diciamo che non sono sostituibili" [0:10:16]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) And then when it takes direction the volumes grow exponentially, so it must be said that there is a relation between the two but let us say they are not interchangeable.

### S7. Crypto volume is fragmented across venues: single-exchange order flow is unreliable, aggregate or use VSA (SOURCED, what NOT to do)

Rule: crypto trades on many exchanges (he names Binance futures, FTX, KuCoin, Bybit, OKX), so there is no central data feed; pure order flow needs an aggregate of all exchanges to be reliable, otherwise VSA (price and volume per bar) has more validity. He says futures order flow is most reliable in indices and commodities. Directly relevant to us: our aggTrades come from Binance only, so any delta or absorption rule on BTC is a one-venue read and must be tested for that limit (OURS: no share-of-volume figure is given). Computable: partly (single-venue yes; aggregate across venues not from Binance data).

> "non puoi attaccare un data Feed che va condividere tutti gli scambi perché perché ci sarà chi scambia su binance il futures ci sarà chi scambia Una volta su FTX" [0:10:50]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) You cannot attach a data feed that shares all the trades because there will be those who trade Binance futures, there will be those who trade on FTX.

> "allora in quel caso assume molta validità o fare un'aggregazione dei dati fra tutti i vari Exchange oppure utilizzare la usa" [0:11:25]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) Then in that case it gains a lot of validity either to aggregate the data across all the various exchanges or to use VSA.

> "il futures trova la sua massima applicazione la sua massima affidabilità nel mercato degli indici e delle materie prime" [0:11:59]
**Source GPS: 692OdHaZnRU | END**
(en) Futures finds its maximum application, its maximum reliability, in the market of indices and commodities.

### S8. Always put the signal in context and test it against your own checklist (SOURCED)

Rule: no volume signal stands alone; place it in context with other analysis, and judge each method only by whether it gives an edge inside your own checklist and strategy. Fits our rule that nothing trades without an out-of-sample, fee-net test.

> "va a spiegare come tutta questa tipologia analitica deve essere sempre posta in contesto ok" [0:06:23]
**Source GPS: 692OdHaZnRU | MIDDLE**
(en) He explains how this whole type of analysis must always be put in context, ok.

> "la cosa migliore è sempre vedere se vi forniscono un vantaggio in base alla vostra checklist e alla vostra strategia" [0:14:36]
**Source GPS: 692OdHaZnRU | END**
(en) The best thing is always to see if they give you an edge based on your checklist and your strategy.
