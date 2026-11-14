# Extract: Fabio Valentini (Fabervaale), "Analisi Volumetrica Pratica" (`ZrfwJBaI07Y`)

- **Video ID:** `ZrfwJBaI07Y`
- **Speaker:** Fabio Valentini (Fabervaale), order-flow scalper on NQ/ES futures; free live masterclass, 2024-02-28, Italian
- **Market in the video:** Nasdaq futures, M15 and M5 charts of the same day, footprint block view and an "imbalance tracker" tool (names a crypto platform family: Exocharts, TradingLite). Rules transfer to Binance aggTrades; the session context does not matter here ("the timeframe does not interest us").
- **Source:** `raw_transcripts_canonical/ZrfwJBaI07Y_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Overlap:** diagonal imbalance at 200 and 400 percent is already in `extract_KObUowoFiK0.md` K2 and `extract_h4emw9_2LU8.md` F2; here he gives a per-level ratio of 300 or 400 percent (Z2), stated as a threshold he does not fix. Sellers/buyers aggress with no result: see `extract_PEfkOliXaDc.md` P4 (Z6 is the same idea, same speaker).

## Rules

### Z1. Price-action proxy for imbalance: the candle body (SOURCED)

Rule: with only candles, imbalance is approximated by the one-directional candle body (impulse with no counter-wick); he calls this a deduction ("I assume the aggression happened somewhere in here"), not an observation. Parameters: body size and wick limit NOT stated. For BTC the exact order-flow version (Z2) replaces it; the proxy is computable from klines (partly, thresholds OURS).

> "negli anni si è andato a trovare un metodo di andare a individuare approssimativamente le imbalance utilizzando cosa utilizzando il corpo candela" [0:01:50]
**Source GPS: ZrfwJBaI07Y | BEGIN**
(en) Over the years a method was found to approximately identify imbalances, using what, using the candle body.

> "Quindi vado a supporre che all'interno di questa zona ci sia stata una imbalance importante anche dal punto di vista Order Flow" [0:02:35]
**Source GPS: ZrfwJBaI07Y | BEGIN**
(en) So I assume that inside this zone there was an important imbalance, also from the order flow point of view.

### Z2. Order-flow imbalance = ratio of short to long aggression at one price level above a threshold of 300 or 400 percent (SOURCED)

Rule: imbalance is a mathematical measurement, not the candle: at each price level compute the ratio between short aggression (taker sell) and long aggression (taker buy); when the ratio passes a threshold, the level is flagged as a barrier. Threshold SOURCED as "can be 300% or 400%" (he does not fix one); level size (tick or bucket), time frame of the bar, minimum volume: NOT stated. Computable from aggTrades binned by price (yes). Stop and target: NOT stated.

> "vai a vedere il rapporto Ok Fra l'aggressione short e l'aggressione Long quando questo rapporto supera un threshold il threshold sarebbe un limite che può essere del 300% o del 400 %" [0:09:15]
**Source GPS: ZrfwJBaI07Y | MIDDLE**
(en) You look at the ratio between short aggression and long aggression; when this ratio passes a threshold, the threshold being a limit that can be 300% or 400%.

> "L'unica cosa che può cambiare è il livello di threshold quindi il filtro che viene messo" [0:10:12]
**Source GPS: ZrfwJBaI07Y | MIDDLE**
(en) The only thing that can change is the threshold level, that is the filter that is applied.

### Z3. Why an imbalance level matters: the aggressors will defend or re-enter it (SOURCED)

Rule: a price level with an imbalance is a reaction level because the operators who aggressed there will have further interest in repositioning or protecting their position. Hypothesis of the speaker, stated as reasoning; no hit rate, no number of retests, no time limit given (all NOT stated). Test on BTC: first and later returns to an imbalance level versus random levels (OURS design).

> "perché cercate di ragionare gli operatori che hanno aggredito quel Price level Ok avranno ulteriore interesse a riposizionarsi o a proteggere la posizione" [0:09:46]
**Source GPS: ZrfwJBaI07Y | MIDDLE**
(en) Because try to reason: the operators who aggressed that price level will have further interest in repositioning or protecting the position.

### Z4. Filter: imbalance reacts best when aligned with the market structure; never an imbalance in a vacuum (SOURCED, what NOT to do)

Rule: in a supply/demand imbalance, the cases that react best are those aligned with market structure (break of the intermediate and the outer structure, then follow-up creating new bearish structures); a counter-structure imbalance gives only a reaction. An imbalance must also have minimum context. Structure definition (swing length) NOT stated; hit rate NOT stated. Partly computable (swing structure OURS).

> "quando ci troviamo in una condizione di squilibrio fra domanda e offerta le situazioni che reagiscono particolarmente bene sono quelle che sono Allineate alla struttura di mercato" [0:05:54]
**Source GPS: ZrfwJBaI07Y | BEGIN**
(en) When we are in a condition of imbalance between demand and supply, the situations that react particularly well are those aligned with the market structure.

> "perché non si può andare a considerare un imbalance all'interno del nulla No Abbiamo bisogno di un minimo di contestualizzazione" [0:14:00]
**Source GPS: ZrfwJBaI07Y | MIDDLE**
(en) Because you cannot consider an imbalance within nothing; we need a minimum of context.

### Z5. Refine the zone: the most intense aggression level inside the body that broke the structure (SOURCED)

Rule: take the candle body where price action broke the structure; inside it, the level with the strongest aggression (darkest block in his block view) is the refined reaction level; it replaces the broad discretionary zone. The tool also flags further imbalance levels that price then reacted to. Risk to reward: with the broad zone, entering at the far edge gives about 1:1 (a bit more than 1:1 on the projected high), while the refined level keeps a wide reaction area; the refined ratio is NOT stated as a number. Stop: NOT stated (zone break invalidates, implied only). Target: projection of the high, about 1:1 (SOURCED loosely from the caption). Computable from aggTrades (yes: max taker volume per price bucket inside the body candle).

> "se andiamo a prendere il corpo candela e quindi dove la Price Action ha fatto rottura e prendiamo il livello più acceso questo è il livello più acceso" [0:16:41]
**Source GPS: ZrfwJBaI07Y | END**
(en) If we take the candle body, that is where price action broke, and take the brightest level, this is the brightest level.

> "ora capite bene che il rischio rendimento cambia drasticamente se io mi devo mettere Cioè qua Faccio un 1-1 se io mi metto sulla proiezione del massimo faccio poco più dell'1 A1" [0:20:58]
**Source GPS: ZrfwJBaI07Y | END**
(en) Now you understand well that risk to reward changes drastically if I have to put myself, that is here I make a 1-1; if I put myself on the projection of the high I make a little more than 1 to 1.

> "aiutano molto nel rifinimento della zona nella qualificazione e più che il Wi rate Alzano il rischio rendimento Questi strumenti" [0:21:23]
**Source GPS: ZrfwJBaI07Y | END**
(en) They help a lot in refining the zone, in qualifying it, and more than the win rate they raise the risk to reward, these tools.

### Z6. Aggression with no result is a reversal warning (SOURCED)

Rule: green blocks (buyer aggression) with no price progress, because the market supplies weakness (limit sellers absorbing), means a wide probability of reversal. Same logic mirrored for sellers. No threshold for "no result" (NOT stated). Computable (yes): high taker-buy volume with a small close-to-close or high-to-low change; thresholds OURS. Same idea as `extract_Ni6quY00dcw.md` C3.

> "Quindi vedete il verde qua vedete aggressione da parte dei buyers senza un risultato perché il mercato sta fornendo delle weak quindi un'ampia probabilità di reversal" [0:15:55]
**Source GPS: ZrfwJBaI07Y | MIDDLE**
(en) So you see the green here, you see aggression by the buyers without a result because the market is providing weakness, so a wide probability of reversal.

## Not testable (one row per topic)

| Topic | Why not testable |
|---|---|
| Footprint only for scalping (never on H4), volume profile for positioning, swing and intraday, fixed range, volume profile footprint (delta profile) | Tool-to-horizon advice; horizon boundaries NOT stated |
| Order flow cannot make you profitable, needs capital, emotional control, do not raise risk because of the tool | Behaviour advice, no trigger |
| Footprint shows executed (market) orders, not limit orders; heatmap is the limit-order tool | Definition, same as `extract_C6PAcbpPYT8.md` M5 |
| Strategy families (volume profile, absorption/exhaustion on CVD, trapped buyers/traders, heatmap stop runs, icebergs, time zones such as NY open) | List only, no parameters |
| Platforms (Sierra, NinjaTrader, Volumetrica, ATAS, Quantower, Exocharts, TradingLite) and data feed analogy | Tooling |

Noticed: the examples (M5 and M15 buy and sell imbalance, Nasdaq of the same day) are shown on screen only; the caption gives no prices, no hit rate and no count of how many levels worked.
