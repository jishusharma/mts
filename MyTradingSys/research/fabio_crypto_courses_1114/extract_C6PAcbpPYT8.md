# Extract: Fabio Valentini (Fabervaale), "Meccanica di Mercato pt.2" (`C6PAcbpPYT8`)

- **Video ID:** `C6PAcbpPYT8`
- **Speaker:** Fabio Valentini (Fabervaale), order-flow scalper on NQ/ES futures; free live lesson, 2023-06-15, Italian
- **Market in the video:** futures and CFD in general (CME Group free education shown, 10,000-contract ES example); definitions only, no setup with entry, stop or target. Concepts transfer to Binance aggTrades (aggressor side is `isBuyerMaker`).
- **Source:** `raw_transcripts_canonical/C6PAcbpPYT8_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. Stop and target are NOT stated anywhere in this video.
- **Overlap:** the four-forces model is the definitional base for the aggression rules in `extract_Ni6quY00dcw.md` and `extract_h4emw9_2LU8.md`; no existing rule is a duplicate of M1 to M6.

## Rules

### M1. Four forces: only market orders move price, limit orders only block (SOURCED)

Rule: price is moved by aggressive market orders (buy market, sell market); resting limit orders (buy limit, sell limit) cannot move price, they can only stop it as a barrier. Definition for our code: aggressor side of each aggTrade = taker; limit liquidity = the maker side. No number given.

> "possiamo riassumere che le forze sono 4 nel pratico si dividono in due forze deboli i bye di mitorder e i sellimitorder e due forze aggressive quindi in grado di muovere il mercato i by Market Order esel Market Order" [0:31:19]
**Source GPS: C6PAcbpPYT8 | END**
(en) We can sum up that the forces are 4, in practice split into two weak forces, buy limit and sell limit orders, and two aggressive forces able to move the market, buy market and sell market orders.

> "ricordiamo che i Limit non possono muovere il prezzo ma possono fornire delle barriere quindi possono diventare una stop in forms" [0:33:04]
**Source GPS: C6PAcbpPYT8 | END**
(en) Remember that limit orders cannot move the price but can provide barriers, so they can become a stopping force.

### M2. Interaction up and interaction down (SOURCED)

Rule: price goes up when a buy market order hits a sell limit order, and down when a sell market order hits a buy limit order. So per bar: taker-buy volume = upward interaction, taker-sell volume = downward interaction. Computable from aggTrades (yes). No threshold given.

> "abbiamo un'interazione al rialzo Ok quando si scontra un by Market Order e un Selling storter Ok un'interazione a ribasso quindi interaction down quando si scontra un cell Market Order e un by Limit Order" [0:24:42]
**Source GPS: C6PAcbpPYT8 | MIDDLE**
(en) We have an upward interaction when a buy market order collides with a sell limit order (caption garbled), and a downward interaction when a sell market order collides with a buy limit order.

### M3. Count aggression, not the number of participants (SOURCED)

Rule: read the market by how aggressively one side buys or sells, not by how many operators are buying. For BTC: weight by taker volume (contracts), not by trade count. This is a definition, not a trigger; the numeric form (delta, delta percent) is in `extract_Ni6quY00dcw.md` C1.

> "la logica di aggressione e non di numero ok dalla logica di concetto di stando comprando più operatori alla logica di stanno comprando più aggressivamente" [0:32:49]
**Source GPS: C6PAcbpPYT8 | END**
(en) The logic of aggression and not of number: from the idea that more operators are buying to the idea that they are buying more aggressively.

### M4. Stop orders count as market orders (SOURCED)

Rule: a stop order is not a fifth force; it is an instruction to send a market order under a condition, so it is part of the aggressive flow. Consequence for the data: stop-triggered selling inside a down move shows up as taker-sell volume and cannot be separated from discretionary market orders in aggTrades (partly computable only).

> "sappiate che gli stop Order non possono essere considerati una forza Unica Ok una forza individuale ma sono sempre assimilabili ai Market Order" [0:32:05]
**Source GPS: C6PAcbpPYT8 | END**
(en) Know that stop orders cannot be considered a single force, an individual force, but are always assimilable to market orders.

### M5. Footprint shows executions only; hidden limit orders are called icebergs (SOURCED)

Rule: the footprint is a display of executed trades, not of resting orders; the resting book (heatmap, iceberg detection) is a separate data source we do not have from aggTrades. Hidden limit orders are called icebergs. For BTC from aggTrades only: executions at a price level are computable (yes), icebergs only indirectly as repeated absorption at one price (partly, OURS).

> "il futprint non è nient'altro che la visualizzazione degli eseguiti in un determinato modo" [0:09:27]
**Source GPS: C6PAcbpPYT8 | BEGIN**
(en) The footprint is nothing other than the display of executed trades in a certain way.

> "Ok limitorder nascosti prendono il nome di iceberg ok perché di iceberg" [0:28:37]
**Source GPS: C6PAcbpPYT8 | END**
(en) Hidden limit orders take the name of iceberg orders.

### M6. Imbalance is the inefficiency; the origin of an aggressive structure break is a demand zone with a probable reaction on return (SOURCED)

Rule: balance (equal supply and demand) is the efficient phase; an imbalance (price explosion that leaves a volume void) is the inefficient phase. The zone from which an aggressive move broke a structure is called demand (supply on the way down); when the market rebalances back to efficiency he expects a reaction in that zone, stated "in probabilistic terms". Parameters: zone boundaries NOT stated here (how to cut the zone is in `extract_ZrfwJBaI07Y.md` Z5); no stop, no target, no hit-rate number. Testable on klines/aggTrades as: break of a swing structure with high taker imbalance, then reaction on the first return to the origin zone (partly, zone cut OURS).

> "qui abbiamo un equilibrio fra la domanda e l'offerta e Qui invece abbiamo un un disequilibrio fra i due quindi questa è una situazione inefficiente" [0:05:05]
**Source GPS: C6PAcbpPYT8 | BEGIN**
(en) Here we have an equilibrium between demand and supply, and here instead a disequilibrium between the two, so this is an inefficient situation.

> "Qual è il punto dal quale si è generato un movimento aggressivo di prezzo Ok che ha portato una rottura di una determinata struttura Questa è Come si crea una demand" [0:07:02]
**Source GPS: C6PAcbpPYT8 | BEGIN**
(en) What is the point from which an aggressive price movement was generated that led to the break of a given structure: this is how a demand is created.

> "nel momento in cui il mercato ribilancia quindi cerca un ritorno all'efficienza Il mercato vede una potenziale reazione sempre in termini probabilistici all'interno di questa zona" [0:07:33]
**Source GPS: C6PAcbpPYT8 | BEGIN**
(en) When the market rebalances, that is it looks for a return to efficiency, the market sees a potential reaction, always in probabilistic terms, inside this zone.

## Not testable (one row per topic)

| Topic | Why not testable |
|---|---|
| Order flow is "a snapshot of the order flow", not an indicator; it is a way to display a data feed | Definition of the word, no trigger |
| Candle hides what happened inside it, fractal multi-timeframe analysis as the workaround | Motivation for the footprint; no number |
| AMT as efficient, inefficient, return to equilibrium; Wyckoff names mapped onto it | Framework; no threshold (the usable part is M6) |
| Data feeds and platforms (Rithmic, CQG, Sierra, Volumetrica, ATAS, Bookmap), liquid vs illiquid markets, CME free education and simulator | Tooling and advice, no rule |
| Large institutional order (10,000 ES contracts) "eats" the book and moves price | Illustration of M1, no number he tests |

Noticed: caption has many transcription errors ("by Market Order esel Market Order", "Selling storter", "futprint"); quotes are copied as-is. He says order flow is short-term and shows no live setup in this lesson.
