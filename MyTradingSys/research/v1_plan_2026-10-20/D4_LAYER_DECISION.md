# D4. Which layers go into v1 (decision basis from numbers on disk)

Rule applied: WIP = 2 research layers. A layer earns a slot by (a) having a pre-registration or a KEEP rule on disk, (b) no
FAIL verdict on the same hypothesis, (c) a data path that already works. Layers with a FAIL or closed verdict leave the trade
flow at the 2026-10-23 review. Everything else is PARKED with its files intact.

## 1. The evidence table (RESULT, LAYERS.md and research folders, read 2026-10-20)
| Family | Best number on disk | Verdict on disk | Slot |
|---|---|---|---|
| Levels Confluence (session levels, VAH/VAL/POC/VWAP holds) | KEEP rule written: a level is kept when the lower CI of hold rate > 0 (levels_hold.md); LC1 and LC2 done, LC3 `lc-ladder-dev` ready, LC4 `lc-validation` refined | no verdict yet; funnel built | SLOT 1 |
| CryptoCred HTF (4h/1d) | pre-reg filed and counted (`cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md`, COUNT_POWER.md); card done dc745272; numbers OURS-UNREPRODUCED | 15m and 1h FAIL earlier; 4h/1d untested | SLOT 2 |
| Tom (Fade, Trend-Healthy, Balance) | 7 backtest rows, all negative net of fees; TOM-CORE-1007 net -2.91 R; holdout -2.80 R | negative; v2 chain blocked on operator eye-read | THIRD IN LINE (park) |
| RSI deep-buy (operator study 2026-10-19) | spec only, 8 raw cards | none | park; operator may swap for slot 2 |
| Fabio v3 | OOS FAIL, 79 trades, mean -0.1038 R; ledger audit FIX-FIRST | FAIL | park (v2 spec waits) |
| Guidance Q33 | no cell survives | FAIL | closed |
| RSI divergence MTF | no edge on any TF | FAIL | closed |
| Positioning C1 (T055) | FAIL | FAIL | close cards |
| Session C2/C3, T087 | FAIL | FAIL | close cards |
| Volume / candles | no edge | FAIL | closed |
| WaveTrend | W01-W03, W09 FAIL; W04-W08 INCONCLUSIVE | mixed, no pass | park |
| Krown | not built; 4 of 19 videos blocked | none | park |
| Kurisko | module landed (dd001f2a7); 0 of 8 prereg cells have power | none | park |
| Pitchfork | detector only | none | park |
| Callers scorecard | needs 56 scored calls for 80 % power (analysts/SCORECARD.md) | none | CBP module (D5) |
| Gross-effect screen 2026-10-15 | INCONCLUSIVE | none | closed |

## 2. Why these two
- Both are higher-timeframe (4h/1d), so fees (< 0.25 R per PROJECT_VISION economics) are a smaller share of each trade.
  Every intraday family on disk failed fee-net.
- Both already have their next card written; no spec work is needed to start.
- They do not share a hypothesis, so a FAIL on one says nothing about the other.
- EXPECT (stated before any run): LC ladder DEV gives a fee-net mean R per trade above 0 with the lower CI above 0 on at
  least one level class; CryptoCred 4h/1d DEV gives at least 40 trades per cell (COUNT_POWER.md) and a fee-net mean R > 0.
  RESULT goes into each layer's report, not here.

## 3. What happens to the rest
- PARKED families keep their folders, cards and branches; nothing is deleted. A parked layer enters only when a slot frees:
  a slot frees on PASS (promotion) or FAIL (VALIDATION read negative, or DEV below the pre-reg floor).
- Order of entry after the two slots: Tom v2 (operator asked for it most, and the eye-read is already a card), then RSI
  deep-buy, then Kurisko when a cell reaches power. The operator can reorder this in q-v1-layers.
- Closed families (Q33, RSI divergence, positioning, session, volume/candles, gross-effect) are not re-opened in v1 without a
  new hypothesis and a new pre-registration.

## 4. The 2026-10-23 review of `auto_trader_config.json` (separate operator decision, q-v1-config-1023)
27 `pre_pipeline_sources` trade on testnet today with no backtest ticket. Proposal: at the review, keep only sources whose
family is in a slot or has a KEEP rule (levels, cryptocred 4h/1d); move every FAIL family to `trade_blocklist`; leave the
rest in `trade_blocklist_parked`. EXPECT: testnet trade count drops sharply and the time-exit share falls from 97 %, since the
Tom-flow exits (T085) leave the flow. This is a config decision the operator signs, not a builder change.
