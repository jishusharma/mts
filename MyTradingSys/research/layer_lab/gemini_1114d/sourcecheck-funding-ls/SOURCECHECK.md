3 CONFIRMED / 1 CONTRADICTED / 9 NOT FETCHED

# Primary-Source Check: `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md`

Target: `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md` (read-only audit; rule book not modified).

## 1. Inventory of Rule Lines, Labels, and Cited Sources

| Line | Section / Item | Label in rule book | Cited source |
|---|---|---|---|
| 5 | Summary rule: use strictly as FLOW context / cascade gauge, never standalone entry | OURS (synthesis) | T055 (`T055_BT_RERUN_FULLFUNDING_2026-10-07.md`), FLOW |
| 11 | Formula pointer (`side_sign * rate`, funding percentile reversion) | OURS / code | `MyTradingSys/backtest/layers/FORMULAS.md` s13, s14; `live_aid.html`; `funding_cvd_fade.py`; `run_t055.py` |
| 16 | Who & Year (Funding rate): BitMEX May 2016 XBTUSD perpetual swap | SOURCED (no quote) | BM (`https://www.bitmex.com/app/perpetualContractsGuide`) |
| 17 | Mechanism & Purpose (Funding rate): periodic cash payments tethering perp to spot | SOURCED (no quote) | BM (`https://www.bitmex.com/app/perpetualContractsGuide`) |
| 18 | Exchange Formula (Binance funding): `F = P + clamp(I - P, -0.05%, +0.05%)` | SOURCED (no quote) | BIN_F (`https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031`) |
| 19 | Fee Calculation & Settlement: `Notional * Funding Rate` at 8h/4h/1h timestamps | SOURCED (no quote) | BIN_F (`https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031`) |
| 20 | Developer directional rule (Funding): no directional trading rules or entry signals | SOURCED (no quote) | BM, BIN_F |
| 21 | Binance Top Trader Ratios: top 20% by margin balance, account & position ratios | SOURCED (no quote) | BIN_LS (`https://binance-docs.github.io/apidocs/futures/en/#top-trader-long-short-ratio-positions`) |
| 22 | Ratio developer directional rule: no trading rules; informational data feed | SOURCED (no quote) | BIN_LS |
| 27 | Delta-neutral funding carry arbitrage yields stable risk-adjusted returns | SOURCED (no quote) | He, Manela, Ross, & von Wachter (2022/2026), `https://ideas.repec.org/p/nbr/nberwo/32936.html` |
| 28 | Extreme funding mean reversion; fees/liquidation spikes erode contrarian edges | SOURCED (no quote) | Ackerer, Hugonnier, & Jermann (2024), `https://www.nber.org/papers/w32936` |
| 29 | Retail crowding contrarian fade (Global vs Top Trader Position ratio) | SOURCED (no quote) | `https://www.coinglass.com/LongShortRatio` |
| 30 | High positive funding (>0.03% to 0.05% per 8h) -> overleveraged longs cascade | SOURCED (no quote) | `https://mudrex.com/blog/` |
| 31 | Funding rate Granger-causes spot price moves during sentiment extremes | SOURCED (no quote) | `https://aaltodoc.aalto.fi/` |
| 32 | Top-trader account ratio > 2.0 indicates extreme bullish consensus to fade | UNVERIFIED | Crypto Twitter / community consensus claims |
| 37 | Krown: funding as crowded boat thermometer; OI + hot funding = avalanche risk | SOURCED (quoted) | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:20,30,40,86` |
| 38 | Tom: no funding rate or long/short ratio usage | NO-SOURCE | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43` |
| 39 | Fabio: no funding rates or long/short account ratios | NO-SOURCE | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43` |
| 40 | CCU: no funding rate or long/short ratio usage | NO-SOURCE | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` |
| 41 | Malkan: strictly OHLC price bars for Wilder RSI(14) | NO-SOURCE | `MyTradingSys/research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:32-34` |
| 42-44 | NK (StockTalk), CryptoCred, Habib / CBP: no mention of funding/L-S ratios | NO-SOURCE | none found |
| 50 | T055 C1 `funding_cvd_fade`: IS 129 (+0.4113%), OOS 76 (-0.0453%, Sharpe -0.0346, FAIL) | OURS | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md` |
| 51 | Gross-effect screen (`FUNDING_RERUN`): T 40 (-0.05610%), INCONCLUSIVE | OURS | `MyTradingSys/research/gross_effect_screen_2026-10-15/FUNDING_RERUN.md` |
| 52 | Funding extreme event table: 2,736 prints, 726 extreme events, BUILT | OURS | `MyTradingSys/research/layer_lab/funding_extreme_event_table/REPORT.md` |
| 53 | Flow layers concepts: one-session observation, F10 `NOT_IN_DATA`, CONTEXT ONLY | OURS | `MyTradingSys/research/flow_layers_concepts_2026-10-28/README.md` |
| 54 | Ratio fade (`edge2-ratio-fade-wide-1113_RESULTS.md`) and DEV/VAL/RECENT split | NOT_MEASURED | noted absent in `FUNDING_LS.md` line 54 |
| 57-63 | Live Aid `#fund` and `#age-bc` panels | OURS / SOURCED | `MyTradingSys/tools/live_aid/live_aid.html` |
| 66-68 | Confluence role: FLOW; cascade risk veto and position sizing throttle | OURS | synthesis |
| 71-73 | Open tests (`edge2-ratio-fade-wide-1113`, `funding_extreme_cascade_veto`, `perpetual_basis_mean_reversion`) | OURS | open study proposals |

## 2. Local Source Quote & Number Verification

### Cited Local Quotes Not Found Verbatim or Mis-Lined
1. **Krown (`FUNDING_LS.md` line 37 -> cites `extract_P3rDSh187TE.md` lines `20,30,40,86`):**
   - `loaded mountain of snow` (quoted in `FUNDING_LS.md` line 37): **NOT FOUND verbatim** in `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md`. Actual text is "it tells you the mountain is loaded with snow and that avalanche has a potential to come now" at `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:44`.
   - "thermometer for how crowded one side of the boat has become" is at `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:32` (not line 30, and without trailing period).
   - "check the weather before you size funding and open interest are free" is at `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:78` (not in cited lines 20, 30, 40, 86).
   - `do not multiply by zero` (paraphrase in `FUNDING_LS.md` line 37) corresponds to "if you get liquidated you lose everything you lose everything so we don t want to multiply by zero here" at `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:80` (not in cited lines 20, 30, 40, 86).
2. **Tom & Fabio (`FUNDING_LS.md` lines 38-39 -> cites `SOURCED_RULES.md` line 43):**
   - Line 43 of `SOURCED_RULES.md` is Bollinger bands; the actual funding/long-short NO-SOURCE row ("Open interest, long/short ratio, funding | NO-SOURCE. 0 hits for") is at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:45`.

### Other Local Citations Checked (Found)
- `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`: 0 matches for `funding|long.?short|ratio` (confirms NO-SOURCE).
- `MyTradingSys/research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:32-34`: confirms Indian equities + "14-period RSI charts" only.
- `MyTradingSys/backtest/layers/FORMULAS.md:350-377`: confirms s13 (`side_sign * rate`) and s14 (`funding_cvd_fade.py`).
- `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:14,27,33-34`: confirms IS 129 (+0.4113%), OOS 76 (-0.0453%, Sharpe -0.0346), 108 variants, PBO 0.1385, FAIL.
- `MyTradingSys/research/gross_effect_screen_2026-10-15/FUNDING_RERUN.md:8-16`: confirms d=1 h=60, T 40 (-0.05610), notF 1399 (-0.00548), C 1439 (-0.00688), +0.0013 pp, INCONCLUSIVE.
- `MyTradingSys/research/layer_lab/funding_extreme_event_table/REPORT.md:1,11-14`: confirms 2,736 prints, 726 extreme events (695 short fades, 31 long fades), BUILT.
- `MyTradingSys/research/flow_layers_concepts_2026-10-28/README.md:46,80`: confirms F10 `NOT_IN_DATA` and slow/opposite move of top-trader ratios vs hours-long price swing.
- `MyTradingSys/tools/live_aid/live_aid.html:280,375,391,662,1302`: confirms `#fund`, `#age-bc`, `about zero` (<0.001%), `high` (>=0.03%), `rate x 3 x 365`, and `topLongShortPositionRatio` / `topLongShortAccountRatio` (flat under 0.2%).
- Note on `FUNDING_LS.md` line 54: `edge2-ratio-fade-wide-1113_RESULTS.md` exists under `MyTradingSys/research/layer_lab/gemini_edge_1113/` in this branch, though `FUNDING_LS.md` line 54 marks it `NOT_MEASURED`.

## 3. Primary-Source Verification (Unquoted & `UNVERIFIED` Lines)

| Rule line | Claim summary | Verdict | Primary source & verbatim quote / reason |
|---|---|---|---|
| `FUNDING_LS.md` line 16 | Who & Year (Funding rate): BitMEX May 2016 XBTUSD perpetual swap | NOT FETCHED | `https://www.bitmex.com/app/perpetualContractsGuide` returned a JS/login sign-in page (`Sign-in Sign in to your account...`); BitMEX ceased trading 2026-09-23 (`https://blog.bitmex.com/tag/perpetual-swap/`). |
| `FUNDING_LS.md` line 17 | Mechanism & Purpose (Funding rate): periodic payments tethering perp to spot | NOT FETCHED | `https://www.bitmex.com/app/perpetualContractsGuide` unreachable without JS/login (sign-in shell returned). |
| `FUNDING_LS.md` line 18 | Binance funding formula (`F = P + clamp(I - P, -0.05%, +0.05%)`) | NOT FETCHED | `https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031` returned HTTP 202 with 0 bytes (JS/WAF challenge). |
| `FUNDING_LS.md` line 19 | Binance fee calculation & discrete settlement (8h/4h/1h) | NOT FETCHED | `https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031` returned HTTP 202 with 0 bytes (JS/WAF challenge). |
| `FUNDING_LS.md` line 20 | Developer directional rule (Funding): no directional trading rules | NOT FETCHED | Both `BM` and `BIN_F` unreachable without JS/WAF/login. |
| `FUNDING_LS.md` line 21 | Binance Top Trader Ratios (`topLongShortAccountRatio`, `topLongShortPositionRatio`, top 20%) | NOT FETCHED | `https://binance-docs.github.io/apidocs/futures/en/` redirects to `https://developers.binance.com/docs/derivatives`, which returned HTTP 202 with 0 bytes (JS/WAF challenge). (Secondary vendor CoinGlass `https://www.coinglass.com/LongShortRatio` states: `"Top traders are typically defined as users ranked in the top 20% by margin balance."`) |
| `FUNDING_LS.md` line 22 | Ratio developer directional rule: no trading rules; informational feed | NOT FETCHED | `https://developers.binance.com/docs/derivatives` returned HTTP 202 with 0 bytes (JS/WAF challenge). |
| `FUNDING_LS.md` line 27 | Delta-neutral funding carry arbitrage yields stable risk-adjusted returns (He, Manela, Ross, & von Wachter) | CONFIRMED | Primary source `https://arxiv.org/abs/2212.06888` (HTTP 200; note: `FUNDING_LS.md` line 27 mis-cited `https://ideas.repec.org/p/nbr/nberwo/32936.html`, which is Ackerer et al.): `"To minimize the gap between perpetual and spot prices, long investors periodically pay shorts a funding rate proportional to this difference. We derive no-arbitrage prices for perpetual futures in frictionless markets and bounds in markets with trading costs. ... An implied arbitrage strategy yields high Sharpe ratios."` |
| `FUNDING_LS.md` line 28 | Extreme funding mean reversion; fees & liquidation spikes erode simple contrarian directional edges (Ackerer, Hugonnier, & Jermann, NBER WP 32936) | CONTRADICTED | `https://ideas.repec.org/p/nbr/nberwo/32936.html` (HTTP 200) is a theoretical no-arbitrage pricing paper, not an empirical study of fees and liquidation spikes eroding contrarian directional edges: `"Perpetual futures are contracts without expiration date in which the anchoring of the futures price to the spot price is ensured by periodic funding payments from long to short. We derive explicit expressions for the no-arbitrage price of various perpetual contracts, including linear, inverse, and quantos futures in both discrete and continuous-time. In particular, we show that the futures price is given by the risk-neutral expectation of the spot sampled at a random time that reflects the intensity of the price anchoring."` |
| `FUNDING_LS.md` line 29 | Retail crowding contrarian fade when long/short ratio is excessively high | CONFIRMED | `https://www.coinglass.com/LongShortRatio` (HTTP 200): `"For example, when the long-to-short account ratio becomes excessively high and long participation is overcrowded, the market may experience a contrarian move, leading to price declines."` (Note: specific divergence between Global Account vs Top Trader Position ratio is not stated as a rule on that page.) |
| `FUNDING_LS.md` line 30 | High positive funding rate indicates overleveraged longs / overheated market | CONFIRMED | `https://mudrex.com/blog/mudrex-funding-rate/` (HTTP 200): `"Funding rates can rise sharply—sometimes even beyond 0.2%—due to: Extreme one-sided sentiment (e.g., everyone going long) ... These spikes act as signals: the market may be overheated or unstable."` (Note: the specific `>0.03% to 0.05% per 8h` threshold in `FUNDING_LS.md` line 30 is not in this post.) |
| `FUNDING_LS.md` line 31 | Funding rate Granger-causes spot price moves during sentiment extremes (Aalto University) | NOT FETCHED | `https://aaltodoc.aalto.fi/` returned an empty SPA shell; permanent thesis link `https://urn.fi/URN:NBN:fi:aalto-202301221391` returned HTTP 403 Forbidden. |
| `FUNDING_LS.md` line 32 | Top-trader account ratio > 2.0 indicates extreme bullish consensus that should be faded (`UNVERIFIED`) | NOT FETCHED | No public primary source fetched establishing or testing a `> 2.0` top-trader account ratio fade rule (`https://www.coinglass.com/LongShortRatio` discusses `"excessively high"` ratios qualitatively without a `2.0` cutoff). |
