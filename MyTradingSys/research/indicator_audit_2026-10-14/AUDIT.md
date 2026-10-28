# Indicator values multi-model audit (card indicator-values-multi-model-audit)

Trust tag: **MACHINE-OK** (not VERIFIED: no non-Claude column is filled yet).
Run: 2026-10-20, session indicator-audit-1020 (MTS_Doctor). Definitions: `MyTradingSys/backtest/layers/FORMULAS.md` s1 (RSI), s22 (Bollinger), s23 (StochRSI); read-only, none added.

## Result

21 values (42 numbers: 7 RSI, 7 x 3 Bollinger, 7 x 2 StochRSI K/D) recomputed blind by Haiku and Sonnet from the packet alone: **0 mismatches each** (Haiku 0/42, Sonnet 0/42), largest absolute difference 0.0 (bit-identical). The two engine copies of Bollinger that layers read (`chart_verify.bollinger`, `live_bb_top_reversal.bollinger`) agree on all 7 BB packets. No defect in the sampled engine route (`rsi_core`, `chart_verify.bollinger`/`stochrsi`).

## Seed, pool, tolerance (OURS, written in `TOLERANCE.md` 2026-10-19T23:01Z before any reply)

- Seed 20261020 (OURS: run date); `scripts/dev/indicator_audit_sample.py draw --pool klines_pool.json --seed 20261020 --out packets`. Same seed gives an identical sample; another seed differs (test).
- Pool (OURS): public Binance USDT-M klines, BTCUSDT and ETHUSDT x 5m/15m/1h, 1499 closed bars each (`klines_pool.json`). Packet = 500 consecutive closes ending at the sampled bar + FORMULAS.md definition text + question; never our value, never engine code (test). Wilder seed truncation at 500 bars costs below 1e-9.
- Tolerance: RSI and StochRSI K, D absolute 0.01 points; Bollinger mid/upper/lower relative 1e-6 (population sd). Missing or non-finite reply = mismatch. Compared in code (`scripts/dev/indicator_audit_compare.py`), never by asking a model.

## Sample count by indicator x timeframe (>= 6 each, 3 timeframes)

| Indicator | 5m | 15m | 1h | total |
|---|---|---|---|---|
| RSI | 2 | 3 | 2 | 7 |
| BB | 3 | 2 | 2 | 7 |
| STOCHRSI | 2 | 3 | 2 | 7 |

## Table value x reviewer

Reviewer scripts written by the reviewers from the packet text alone: `replies/reviewer_haiku_compute.py`, `replies/reviewer_sonnet_compute.py`; replies in `replies/replies_haiku.json`, `replies/replies_sonnet.json`. GPT and DSA are desk rows to the NUC (posted with `desk.py post --target DSA`, never run here).

| packet | indicator | symbol tf | window sha256 | Haiku | Sonnet | GPT | DSA |
|---|---|---|---|---|---|---|---|
| bb-01-ethusdt-5m | BB | ETHUSDT 5m | 65bec05a343fdee39423a2f3f1b1b12f1e6084efddb6ba24aa97a8bfec1b9ff4 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-02-ethusdt-1h | BB | ETHUSDT 1h | ad2c2beb24e194faf775dcf933936b2ae06505fc574ed2a8c3998975d79723c7 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-03-btcusdt-5m | BB | BTCUSDT 5m | d632ffaefb38006da176cddc839ecdbac436bc7949e1d82d80c432300a43b937 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-04-btcusdt-15m | BB | BTCUSDT 15m | 41e5a82de7c4a7da9f5e8199ab90b4a7cb6c793520926104800f3196f340d545 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-05-ethusdt-15m | BB | ETHUSDT 15m | 126b21be91a607ceeb30273a919206c0fb552bbac203b1e8026fe1522ab83ca8 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-06-btcusdt-1h | BB | BTCUSDT 1h | 732e2657856e8d97ffec24c18eb5dd9810585b9c99e9a0da7169d18a9ad8b1e3 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| bb-07-ethusdt-5m | BB | ETHUSDT 5m | 8e0c15897dcc7a892352fa565d262cba256ec8185e5e82cce238cfc9fe8c1866 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-01-ethusdt-15m | RSI | ETHUSDT 15m | 3fbb3d5bbcc09f2d32619cda394991aa027eb7ec586a0ce172cd43cd3d722741 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-02-btcusdt-5m | RSI | BTCUSDT 5m | 1c096302d8a8f67a657cad05b4d2fe361a1c723fd529473b94312aa95257e08b | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-03-ethusdt-1h | RSI | ETHUSDT 1h | 6307ce92110bbfe2072cd3e72ee4a0970e4001e3bf8cc9809e01abc7091c5e1d | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-04-btcusdt-15m | RSI | BTCUSDT 15m | 4db5ef245b7a835981d84aecd8c6b24117a5ac2908de90da0ad930782573ce44 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-05-btcusdt-1h | RSI | BTCUSDT 1h | 29e625c79d9ef056d98840345ff755cce44e7995b3b21db1e6e9bfa4fad87e80 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-06-ethusdt-5m | RSI | ETHUSDT 5m | b94a8f04b68b7cbdb8a0d8e5be83b3dbc64b5ba1e573a66d632551fc33d8e3c9 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| rsi-07-ethusdt-15m | RSI | ETHUSDT 15m | 80bec57fdc78f12a106badc2d1210dbf4f34520817ead6e2a2a01d3ef4e85bf7 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-01-ethusdt-15m | STOCHRSI | ETHUSDT 15m | 1b991768b21b4a7c99b8387889b010a3250ebefc5e741c26abea6264e2d1669b | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-02-btcusdt-1h | STOCHRSI | BTCUSDT 1h | a3d56f63de42b80c51bf35a46926dd076ebc0a7f6b44fc840843a44ea08bb51e | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-03-ethusdt-5m | STOCHRSI | ETHUSDT 5m | 8db69b7c0f174ad4f852a3cef8a9259a448a973df99e294db5c8358a3e67bcaa | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-04-btcusdt-5m | STOCHRSI | BTCUSDT 5m | a4f965a32536d278863ee8a368257e9f6effca8ee2972777372f4ffe211fd4ba | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-05-ethusdt-1h | STOCHRSI | ETHUSDT 1h | 203104e2444f66e38121f5c85cf20206acda7c3f5782a2f24313cf0770cd621f | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-06-btcusdt-15m | STOCHRSI | BTCUSDT 15m | 01a15a15065d27317d8da34cea7c03ccc121e2ed9758cc5af679537727320794 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |
| stochrsi-07-ethusdt-15m | STOCHRSI | ETHUSDT 15m | 7e1813aca7339cfd5ad25fd61d377af9469e892f7cbabd5693e47191c7d09de2 | match | match | PENDING(20261019-230129-indicator-audit-gpt-blind-packet-run) | PENDING(20261019-230131-indicator-audit-dsa-deepseek-blind-packe) |

## Triage per mismatch above tolerance

None: 0 mismatches for Haiku, 0 for Sonnet. Both reviewers reported the definitions unambiguous (Haiku noted `delta[0:period]` is read as the first `period` changes; the worked example settles it). No B-item from the sampled values.

## Findings outside the sampled route (engine copies and docs)

- **B-item (hand-confirmed)**: `MyTradingSys/backtest/layers/krown/krown_core.py:300-301` `val()` returns 100.0 whenever avg_loss == 0, so a perfectly flat window gives RSI 100; FORMULAS s1 step 4 says 50 (flat) and `rsi_core.py` gives 50. Hand: closes [5]*15, period 14, avg_gain = avg_loss = 0, so 50. Reachable only on a flat window; on the 21 sampled windows krown_core.rsi and wlow_bounce.bollinger_upper agree with the main route (`other_routes` check, 0 disagreements). Card `b-item-krown-core-rsi-returns-100-on-a-f` (raw).
- Doc only: `rsi_core.py:10` words the seed as "mean of the positive/negative deltas" (reads like the divide-by-count bug named in FORMULAS s1; the code at rsi_core.py:29-30 divides by `period`, correct). `live_bb_top_reversal.py:14` says "FORMULAS.md has no BB section"; s22 exists. Both listed in the same card.
- Not sampled, no FORMULAS entry: snapshot VWAP (+-1s/2s bands), session CVD, trade-flow deltas (the numbers in `data/snapshots/*.json` that every layer reads). Audit step 1 samples only indicators with an entry; card `formulas-md-definitions-for-snapshot-vwa` (raw) files the definition entry as its own C2 card.
- Not sampled (separate maths copies): `kurisko/stoch_core.py` (FORMULAS s24), `wavetrend` (s20), ATR (s12), Java-side values. StochRSI exists only in `chart_verify.py` (a label tool), no live layer reads it.

## Limit (stated, not hidden)

20 clean values bound the engine mismatch rate only to about 14 percent at 95 percent confidence (rule of three, 3/21 = 14.3 percent). Both reviewers are Claude models and the engine and the reviewers share one author lineage and one definition text; a clean table is **MACHINE-OK, not VERIFIED**, until at least one non-Claude column is filled and matches. Upgrade to VERIFIED-C1 only then.

## Left for the NUC (GPT and DSA columns)

Two desk rows target DSA, shown PENDING in the table: `20261019-230129-indicator-audit-gpt-blind-packet-run` and `20261019-230131-indicator-audit-dsa-deepseek-blind-packe`. Each gives the packet folder, the reply format, and the compare command; the reviewer gets packets only, never our value.

## Decisions (OURS)

- Sample drawn from public klines through the engine functions (live snapshots hold no RSI/BB/StochRSI values, so a snapshot sample is not possible); engine value computed at compare time from the same 500 closes.
- 7 values per indicator over 6 symbol x timeframe pools; 5m/15m/1h (card needs >= 2 timeframes).
- Two Claude reviewers run as sub-Agents with the packet folder only; their scripts are kept for audit.
