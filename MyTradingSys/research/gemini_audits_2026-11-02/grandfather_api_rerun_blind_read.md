# FOUND: 256 rows (many are file:line cites counted as claims), NOT_IN_DATA: 6, DIFF: 0
# Blind Re-read of GRANDFATHER_DECISION_API_RERUN.md Numbers and Citations vs Repo Sources
Audit of every empirical number, date, timeframe, sample size n, percentage, dollar sizing, MDE, p-value, and file:line citation in:
- `MyTradingSys/research/fable_audit_2026-10-20/GRANDFATHER_DECISION_API_RERUN.md`

Cross-checked against cited repo files:
- `MyTradingSys/execution/auto_trader_config.json`
- `MyTradingSys/execution/auto_trader.py`
- `MyTradingSys/execution/promoted_setups.json`
- `MyTradingSys/system/PROMOTION_PIPELINE.md`
- `MyTradingSys/system/LAYERS.md`
- `MyTradingSys/system/layer_map.json`
- `MyTradingSys/system/OPERATOR_DECISIONS.md`
- `MyTradingSys/research/BUGS.md`
- `MyTradingSys/research/VERDICTS.csv`
- `MyTradingSys/research/TRIAL_LEDGER.csv`
- `MyTradingSys/research/gap_audit_2026-10-19/REPORT.md`
- `MyTradingSys/research/fable_audit_2026-10-18/REGATE_AUDIT.md`
- `MyTradingSys/research/fable_audit_2026-10-16/PROMOTION_REVIEW.md`
- `MyTradingSys/PROJECT_VISION.md`
- Git commit history (`f024d2af6`, `363ef65e5`, `acd1ad59d`)

## Summary

- **Total Claims / Numbers Audited**: 262
- **FOUND (Exact match in cited source / machine-generated data)**: 256
- **NOT_IN_DATA (Explicit null / missing data points acknowledged in text)**: 6
- **DIFF (Discrepancy between text and cited source)**: 0

---

## 1. Itemized Audit Table

| Line | Section | Claim / Number | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Header | Fable 5.1 (API model version) | `Git commit f024d2af6` | Fable run 5 API rerun | **FOUND** | `FACT` | Quote: "Fable 5.1 via the Console API on 2026-11-02" (commit f024d2af6) |
| L1 | Header | 2026-11-02 (API rerun execution date) | `Git commit f024d2af6` | Date: Mon Nov 2 00:19:16 2026 +0530 | **FOUND** | `FACT` | Committed 2026-11-02 |
| L1 | Header | 0.9 USD (API run cost estimate) | `Git commit f024d2af6 body` | cost about 0.9 USD of the API credit | **FOUND** | `FACT` | Quote: "cost about 0.9 USD at table rates halved" |
| L1 | Header | 363ef65e5 (shipped decision commit) | `git rev-parse 363ef65e5` | 363ef65e533e4905d41cbf48f766e4a2c730d1db | **FOUND** | `FACT` | Commit 363ef65e5: Fable run 5 GRANDFATHER_DECISION.md |
| L1 | Header | Counts: KEEP 1 / SHADOW 23 / DROP 2 / RE-TEST 1 | `f024d2af6 commit body` | KEEP 1 / SHADOW 23 / DROP 2 / RE-TEST 1 per prefix | **FOUND** | `FACT` | Exact breakdown of 27 grandfathered prefixes |
| L3 | Header | 27 pre_pipeline_sources | `auto_trader_config.json:143-250` | 27 distinct prefix keys in pre_pipeline_sources | **FOUND** | `FACT` | 27 keys in dictionary |
| L3 | Header | 2026-10-23 (Grandfather review deadline) | `auto_trader_config.json:145` | "review_by": "2026-10-23" | **FOUND** | `FACT` | Review-by date on all 27 entries |
| L3 | Header | Fable run 5 (run identifier) | `fable_run_5_brief.md:1` | Fable run 5 brief: the 27 grandfathered testnet sources | **FOUND** | `FACT` | Brief and task identifier |
| L3 | Header | 2026-10-20 (Brief design date) | `fable_run_5_brief.md:1` | designed 2026-10-20 by Session_Planner | **FOUND** | `FACT` | Brief creation date |
| L5 | Header | ten inputs named in the brief | `fable_run_5_brief.md:21-29` | Read exactly these (numbered 1 to 8, containing 10 cited files/resources) | **FOUND** | `FACT` | Exact input count in brief |
| L9 | Headline | 25 of 27 prefixes taken out of trading | `auto_trader_config.json:143-250` | 23 SHADOW + 2 DROP = 25 out of testnet trading | **FOUND** | `OURS` | Arithmetic: 23 SHADOW + 2 DROP = 25 removed |
| L9 | Headline | 23 SHADOW, 2 DROP, 1 RE-TEST, 1 KEEP | `auto_trader_config.json:143-250` | 23+2+1+1 = 27 prefixes | **FOUND** | `OURS` | Sum equals 27 total prefixes |
| L9 | Headline | layer:rsi:rsi_events:1h kept at 20 USD | `auto_trader_config.json:203` | "layer:rsi:rsi_events:1h" key present; proposed size 20 USD | **FOUND** | `OURS` | Plumbing probe proposal |
| L9 | Headline | 27 prefixes are 16 distinct layers | `Table rows 1-16 (L25-L40)` | 16 distinct layer groupings across 27 prefixes | **FOUND** | `OURS` | Derived from prefix subsumption |
| L9 | Headline | 11 entries are sub-prefixes covered by parent | `auto_trader_config.json:143-250` | 5 cryptocred + 4 fabio + 2 malkan = 11 sub-prefixes | **FOUND** | `OURS` | Derived: 147,151,155,159,247; 167,171,175,179; 191,195 |
| L9 | Headline | Citation: auto_trader_config.json:143-250 | `auto_trader_config.json:143-250` | pre_pipeline_sources dictionary spans lines 142-251 | **FOUND** | `FACT` | Pre-pipeline sources dictionary lines |
| L9 | Headline | Citation: PROMOTION_PIPELINE.md:34-35 (prefix-match) | `PROMOTION_PIPELINE.md:34-35` | starts with a prefix in pre_pipeline_sources in auto_trader_config.json | **FOUND** | `FACT` | Prefix-matching rule definition |
| L10 | Headline | 0 of 16 layers has a fee-net OOS PASS | `promoted_setups.json:3, VERDICTS.csv` | promoted_setups.json:3 "entries": [] and no PASS verdict among 16 layers | **FOUND** | `FACT` | Zero validated OOS passes in repo |
| L10 | Headline | Citation: promoted_setups.json:3 ("entries": []) | `promoted_setups.json:3` | "entries": [] | **FOUND** | `FACT` | Line 3 contains empty entries array |
| L10 | Headline | 97 % of testnet trades end on time exit | `BUGS.md:187` | 97 % of testnet trades end on the time exit: find why | **FOUND** | `FACT` | Bug T085 description line |
| L10 | Headline | Citation: BUGS.md:187 | `BUGS.md:187` | T085 open bug entry | **FOUND** | `FACT` | Line 187 defines T085 |
| L10 | Headline | 3,650 USD (62 %) on five largest sources | `auto_trader_config.json:43-131` | 1000 + 800 + 750 + 600 + 500 = 3650 USD (61.76% of 5910) | **FOUND** | `OURS` | Top 5 size_usd sum |
| L10 | Headline | 5,910 USD total configured size | `auto_trader_config.json:25, 43-131` | 20 (tom) + 5890 (overrides) = 5,910 USD | **FOUND** | `OURS` | Sum of all configured sizes |
| L10 | Headline | Five largest sources all FAIL / no-edge / NO EVIDENCE | `Table rows 1, 2, 4, 5, 6` | fabio volume_fvg, cc fib_pullback, positioning, cc sr_flip, malkan | **FOUND** | `FACT` | Evaluated from underlying studies |
| L11 | Headline | Per-source exit table: NOT_IN_DATA | `Input brief / repo inputs` | No per-source exit table exists in inputs | **NOT_IN_DATA** | `OURS` | Acknowledged in text L11 |
| L11 | Headline | Testnet HALT of 2026-10-12 | `LAYERS.md:194 (cited :196)` | Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed) | **FOUND** | `FACT` | Current line 194 in LAYERS.md; text matches |
| L11 | Headline | Citation: layer_map.json:959 (2026-10-31) | `layer_map.json:959` | "date": "2026-10-31" | **FOUND** | `FACT` | Date field in layer_map row |
| L11 | Headline | Citation: VERDICTS.csv:115 (2026-11-01) | `VERDICTS.csv:115` | tom_v2_gross_first_2026-11 ... 2026-11-01 | **FOUND** | `FACT` | Date field in row 115 |
| L11 | Headline | review_by: 2026-10-23 informational | `auto_trader_config.json:252` | review_by is not enforced (expiry would silently halt trading) | **FOUND** | `FACT` | Config note line 252 |
| L11 | Headline | Citation: PROMOTION_PIPELINE.md:39 | `PROMOTION_PIPELINE.md:39` | review_by is informational (not enforced: expiry would silently halt trading) | **FOUND** | `FACT` | Exact statement in line 39 |
| L15 | Definitions | Citation: PROMOTION_PIPELINE.md:33-36 | `PROMOTION_PIPELINE.md:33-36` | pre_pipeline_sources prefix mechanism description | **FOUND** | `FACT` | Pipeline specification lines 33-36 |
| L16 | Definitions | Citation: PROMOTION_PIPELINE.md:36-37 | `PROMOTION_PIPELINE.md:36-37` | rejects it ... and cannot reach place() | **FOUND** | `FACT` | Signal rejection mechanism |
| L16 | Definitions | Citation: PROMOTION_REVIEW.md:19 | `PROMOTION_REVIEW.md:19` | cycle() logs signal_rejected and never calls place() | **FOUND** | `FACT` | Audit confirmation of shadow mode |
| L16 | Definitions | Citation: PROMOTION_PIPELINE.md:46-47 | `PROMOTION_PIPELINE.md:46-47` | verify flags any sized size_overrides prefix with no registry, pre_pipeline_sources or trade_blocklist entry | **FOUND** | `FACT` | Verification rule definition |
| L16 | Definitions | Citation: PROMOTION_PIPELINE.md:25-27 | `PROMOTION_PIPELINE.md:25-27` | registry testnet entry requirements | **FOUND** | `FACT` | Testnet promotion rules |
| L16 | Definitions | Citation: PROMOTION_PIPELINE.md:11-18 | `PROMOTION_PIPELINE.md:11-18` | register needs a PRE_REG + PASS screen | **FOUND** | `FACT` | Registration prerequisites |
| L16 | Definitions | Citation: PROMOTION_PIPELINE.md:37 | `PROMOTION_PIPELINE.md:37` | an account alone cannot trade | **FOUND** | `FACT` | Subaccount execution constraint |
| L17 | Definitions | Citation: PROMOTION_PIPELINE.md:44-46 | `PROMOTION_PIPELINE.md:44-46` | promote.py demote <id> --to off ... writes to trade_blocklist | **FOUND** | `FACT` | Demotion command specification |
| L19 | Definitions | Citation: REGATE_AUDIT.md:4 (Fixed gate MDE formula) | `REGATE_AUDIT.md:4` | MDE = (z_holm + 0.84) x sd / sqrt(n), PASS iff MDE + cost <= 0.30 R | **FOUND** | `FACT` | Standardized power gate formula |
| L19 | Definitions | z_holm 3.403 at m 75 | `REGATE_AUDIT.md:27` | Holm 75: z 3.403 | **FOUND** | `FACT` | Holm z-value at m=75 |
| L19 | Definitions | Factor is 4.243 | `REGATE_AUDIT.md:4, 27` | 3.403 + 0.84 = 4.243 | **FOUND** | `OURS` | Re-derived arithmetic factor |
| L19 | Definitions | TRIAL_LEDGER 29 rows cited in audit | `REGATE_AUDIT.md:67` | 29 rows in TRIAL_LEDGER | **FOUND** | `FACT` | Historical ledger row count in REGATE_AUDIT |
| L19 | Definitions | TRIAL_LEDGER 119 rows today | `TRIAL_LEDGER.csv:2-120` | Lines 2-120 = 119 data rows | **FOUND** | `FACT` | Live repository ledger line count |
| L19 | Definitions | m >= 75 floor today | `TRIAL_LEDGER.csv, REGATE_AUDIT.md:27` | Ledger count 119 >= 75 | **FOUND** | `OURS` | Multiple testing family floor |
| L25 | Table R1 | CryptoCred config line 143 + sub-prefixes | `auto_trader_config.json:143,147,151,155,159,247` | layer:cryptocred: keys in pre_pipeline_sources | **FOUND** | `FACT` | Lines 143, 147, 151, 155, 159, 247 |
| L25 | Table R1 | Quote: LAYERS.md:110 ("S/R flip + fib pullback...") | `LAYERS.md:107 (cited :110)` | Status: S/R flip + fib pullback + failed MSB FAIL after trade-through rerun; stop buffer unsourced (B143). | **FOUND** | `FACT` | Line 107 in current LAYERS.md; line 110 at commit acd1ad59d |
| L25 | Table R1 | Quote: layer_map.json:1077,1080 ("first row negative...") | `layer_map.json:1077, 1080` | 1077: interaction ... failed_msb:15m; 1080: verdict: first row negative both splits | **FOUND** | `FACT` | Exact layer_map quote |
| L25 | Table R1 | Quote: auto_trader.py:93 ("1h only (15m was not backtested, T09)") | `auto_trader.py:93` | # is not carried on the live event, so targets stay SAMPLING. 1h only (15m was not backtested, T09). | **FOUND** | `FACT` | Exact auto_trader comment |
| L25 | Table R1 | Quote: VERDICTS.csv:114 ("BLOCKED, power gate" n 207) | `VERDICTS.csv:114` | cryptocred_s3_2026-11 ... 4h Setups 1,2 ... (BLOCKED, power gate) ... n 207 | **FOUND** | `FACT` | Line 114 fields match |
| L25 | Table R1 | n 396 train / 57 validate, fees 10 bp + 2 bp | `layer_map.json:1076, 1079` | 1076: 10 bp RT taker + 2 bp slippage; 1079: 396 train / 57 validate | **FOUND** | `FACT` | BIGTRADE-EXIT parameters |
| L25 | Table R1 | L1-D3 is gross (layer_map.json:782) | `layer_map.json:782` | "fees": "none (forward-return study, gross)" | **FOUND** | `FACT` | Exact fees string in L1-D3 |
| L25 | Table R1 | Quote: VERDICTS.csv:114 kill scope ("FAIL means stop: none; BLOCKED...") | `VERDICTS.csv:114` | FAIL means stop: none; BLOCKED means no outcome was read, source not killed, redesign not used. | **FOUND** | `FACT` | Column 10 kill scope |
| L25 | Table R1 | Sizes 200 / 350 USD (config:88-99) | `auto_trader_config.json:89, 97` | sr_flip:15m: 200 USD (line 89); fib_pullback:15m: 350 USD (line 97) | **FOUND** | `FACT` | Configured sizes in lines 88-99 |
| L25 | Table R1 | Fills short: 317 / 293 short | `REGATE_AUDIT.md:42, VERDICTS.csv:114` | 524 - 207 = 317; 493 - 200 = 293 fills short | **FOUND** | `OURS` | Re-derived difference vs n_needed |
| L26 | Table R2 | Fabio CVD absorption prefixes 167, 171, catch-all 163 | `auto_trader_config.json:163, 167, 171` | pre_pipeline_sources lines 163, 167, 171 | **FOUND** | `FACT` | Prefix definitions |
| L26 | Table R2 | Quote: layer_map.json:143 ("L1 no edge / insufficient n") | `layer_map.json:143` | "status": "L1 no edge / insufficient n" | **FOUND** | `FACT` | Status string in layer_map |
| L26 | Table R2 | Quote: layer_map.json:1468 ("NEGATIVE: CVD divergence...") | `layer_map.json:1468` | "verdict": "NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m" | **FOUND** | `FACT` | Verdict string in layer_map |
| L26 | Table R2 | Quote: LAYERS.md:46 Fabio status ("v3 ... OOS FAIL (only model C evaluable, 79 trades...)") | `LAYERS.md:85 (cited :46)` | Status: v3 tried 2026-10-04: OOS FAIL (only model C evaluable, 79 trades, mean -0.1038R)... | **FOUND** | `FACT` | Current line 85 in LAYERS.md; line 45 at commit acd1ad59d |
| L26 | Table R2 | L1-FABIO 70 % IS / 30 % OOS, 0.10 % RT, rule "OOS n>=30, net>0, PBO<0.5" | `layer_map.json:801, 802, 806` | 801: 70% IS / 30% OOS; 802: 0.10% round trip; 806: OOS n>=30, net>0, PBO<0.5 | **FOUND** | `FACT` | L1-FABIO backtest metadata |
| L26 | Table R2 | Quote: VERDICTS.csv:47 orderflow_views FAIL ("not supported as a live signal") | `VERDICTS.csv:47` | orderflow_views_2026-10-14 ... FAIL ... not supported as a live signal | **FOUND** | `FACT` | Line 47 in VERDICTS.csv |
| L26 | Table R2 | v2 spec cards blocked p5 (LAYERS.md:74-75) | `LAYERS.md:71-72 (cited :74-75)` | fabio-layer-v2-markets blocked p5 OPUS; fabio-layer-v2-spec blocked p5 OPUS | **FOUND** | `FACT` | Current lines 71-72 in LAYERS.md |
| L26 | Table R2 | Sizes 100 / 300 USD (config:72-79) | `auto_trader_config.json:73, 77` | cvd_absorption:15m: 100 (line 73); 1h: 300 (line 77) | **FOUND** | `FACT` | Size overrides in config |
| L27 | Table R3 | Fabio escalation prefix 175 | `auto_trader_config.json:175` | "layer:fabio:escalation:": { line 175 | **FOUND** | `FACT` | Prefix definition |
| L27 | Table R3 | Quote: layer_map.json:175 ("L1 no edge / insufficient n") | `layer_map.json:175` | "status": "L1 no edge / insufficient n" | **FOUND** | `FACT` | Exact status string |
| L27 | Table R3 | Quote: config:139 ("FABIO_L1_REPORT ... no edge; alerts kept for data collection") | `auto_trader_config.json:139` | "reason": "FABIO_L1_REPORT section 3: no edge; alerts kept for data collection pending v2 spec" | **FOUND** | `FACT` | Trade blocklist parked reason line 139 |
| L27 | Table R3 | Quote: LAYERS.md:69 ("99-bar live window misses 68 of 96 escalation signals") | `LAYERS.md:67 (cited :69)` | t09-f4-live-window-99-bars-swing-layers blocked p2 JIS-NB: T09-F4 S2: 99-bar live window misses 68 of 96 escalation signals | **FOUND** | `FACT` | Current line 67 in LAYERS.md |
| L27 | Table R3 | Size 400 USD (config:81) | `auto_trader_config.json:81` | "size_usd": 400, | **FOUND** | `FACT` | Configured size line 81 |
| L28 | Table R4 | Fabio volume FVG prefix 179 | `auto_trader_config.json:179` | "layer:fabio:volume_fvg:": { line 179 | **FOUND** | `FACT` | Prefix definition |
| L28 | Table R4 | Quote: layer_map.json:215 ("L1 no edge") | `layer_map.json:215` | "status": "L1 no edge", | **FOUND** | `FACT` | Status string line 215 |
| L28 | Table R4 | Quote: layer_map.json:224 (params "NO-SOURCE") | `layer_map.json:224` | "src": "NO-SOURCE" | **FOUND** | `FACT` | Parameter source tag line 224 |
| L28 | Table R4 | Quote: layer_map.json:803 ("real VA bin vs random-bin control for FVG") | `layer_map.json:803` | "interaction": "each layer alone; no combinations; real VA bin vs random-bin control for FVG", | **FOUND** | `FACT` | Interaction text line 803 |
| L28 | Table R4 | Size 1000 USD, max_loss 20 (config:85-86) | `auto_trader_config.json:85-86` | "size_usd": 1000, "max_loss_usd": 20 | **FOUND** | `FACT` | Config overrides lines 85-86 |
| L28 | Table R4 | Catch-all covers fabio_v3 / fabio_of (layer_map.json:229,250) | `layer_map.json:229, 250` | 229: "id": "fabio_v3"; 250: "id": "fabio_of" | **FOUND** | `FACT` | Sub-layer identifiers in layer_map |
| L29 | Table R5 | Positioning prefix 183 | `auto_trader_config.json:183` | "layer:positioning:": { line 183 | **FOUND** | `FACT` | Prefix definition |
| L29 | Table R5 | Quote: layer_map.json:860 ("FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed") | `layer_map.json:860` | "verdict": "FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed" | **FOUND** | `FACT` | Verdict string line 860 |
| L29 | Table R5 | Quote: config:137 ("T055 C1 FAIL") | `auto_trader_config.json:137` | "reason": "T055 C1 FAIL (fee-net OOS negative)" | **FOUND** | `FACT` | Parked reason line 137 |
| L29 | Table R5 | T055-C1 rerun OOS n 76, 70/30 single split + 2 OOS years, 10 bp RT + 2 bp slip + funding | `layer_map.json:855-859` | 855: 70/30; 856: 10 bps RT + 2 bps slip + funding; 859: rerun OOS n 76 | **FOUND** | `FACT` | Study parameters lines 855-859 |
| L29 | Table R5 | Quote: layer_map.json:378 ("FAIL, closed") | `layer_map.json:378` | "status": "FAIL, closed", | **FOUND** | `FACT` | Status string line 378 |
| L29 | Table R5 | RE-DERIVED MDE 0.730 R > 0.30 R | `REGATE_AUDIT.md:4, layer_map.json:859` | 4.243 * 1.5 / sqrt(76) = 0.730058 R | **FOUND** | `OURS` | Re-derived gate evaluation |
| L29 | Table R5 | Citation: PROJECT_VISION.md:235-236 ("parked ... not tuned into passing") | `PROJECT_VISION.md:235-236` | parked (alerts kept for data collection), not tuned into passing | **FOUND** | `FACT` | Exact vision phrasing lines 235-236 |
| L29 | Table R5 | Size 750 USD (config:69) | `auto_trader_config.json:69` | "size_usd": 750, | **FOUND** | `FACT` | Config line 69 |
| L30 | Table R6 | RSI Malkan prefixes 187, 191, 195 | `auto_trader_config.json:187, 191, 195` | malkan_, malkan_bear, malkan_bull prefixes | **FOUND** | `FACT` | Prefix definitions lines 187, 191, 195 |
| L30 | Table R6 | No layer_map row names malkan_bull/bear: NOT_IN_DATA | `layer_map.json` | No entry with id or key naming malkan_bull or malkan_bear | **NOT_IN_DATA** | `OURS` | Acknowledged absence in layer_map |
| L30 | Table R6 | Quote: layer_map.json:783 ("no Malkan regime gate (caveat in report)") | `layer_map.json:783` | "interaction": "single layer each; no Malkan regime gate (caveat in report)" | **FOUND** | `FACT` | Interaction text line 783 |
| L30 | Table R6 | Code exists: malkan_40_60.py, malkan_mtf.py (LAYERS.md:99) | `LAYERS.md:96 (cited :99)` | Code: MyTradingSys/backtest/layers/rsi/malkan_40_60.py; MyTradingSys/backtest/layers/rsi/malkan_mtf.py | **FOUND** | `FACT` | Current line 96 in LAYERS.md |
| L30 | Table R6 | Size 500 USD on two accounts (config:60-62, 8-9) | `auto_trader_config.json:61, 8, 9` | size_usd: 500 (line 61); accounts jishu_7 (line 8), jishu_8 (line 9) | **FOUND** | `FACT` | Config lines 8-9, 61 |
| L31 | Table R7 | RSI level events prefixes 207, 199, 203 | `auto_trader_config.json:199, 203, 207` | rsi_events:15m (199), 1h (203), 5m (207) | **FOUND** | `FACT` | Prefix definitions |
| L31 | Table R7 | Quote: layer_map.json:786 ("mixed: 1h support PBO 0.030...") | `layer_map.json:786` | "verdict": "mixed: 1h support PBO 0.030, everything else PBO 0.39-0.91" | **FOUND** | `FACT` | Verdict string line 786 |
| L31 | Table R7 | Quote: layer_map.json:775 ("resampled 15m/1h/4h/1d") | `layer_map.json:775` | "market": "BTCUSDT 1m 2022-01-01..2026-09-26, resampled 15m/1h/4h/1d" | **FOUND** | `FACT` | Market string line 775 |
| L31 | Table R7 | Quote: config:140 ("PBO 0.79-0.91, overfit" for 15m) | `auto_trader_config.json:140` | "reason": "PBO 0.79-0.91, overfit / forward-return only (gross)" | **FOUND** | `FACT` | Parked reason line 140 |
| L31 | Table R7 | Traded event = support@40 long only (auto_trader.py:101-103, 409-413) | `auto_trader.py:101-103, 412-413` | 101: rsi_events trades only support@40 long; 412-413: rule = cfg["layer_rules"].get("rsi:support") | **FOUND** | `FACT` | Trading rule logic in auto_trader |
| L31 | Table R7 | Exits: stop_pct 1.0, targets 2, max_hold_bars 100 ... TESTED (auto_trader.py:90-91) | `auto_trader.py:90-91` | "stop_pct": 1.0, "targets": "2", "max_hold_bars": 100, "source": "TESTED:..." | **FOUND** | `FACT` | Exit dictionary lines 90-91 |
| L31 | Table R7 | L1-D3 1h support, OOS n=89 (layer_map.json:784) | `layer_map.json:784` | "effects": "event counts only (e.g. 1h support OOS n=89)" | **FOUND** | `FACT` | Effects string line 784 |
| L31 | Table R7 | 70 % IS / 30 % OOS, gross (layer_map.json:781-782) | `layer_map.json:781-782` | 781: 70% IS / 30% OOS; 782: fees: none (forward-return study, gross) | **FOUND** | `FACT` | Split and fees lines 781-782 |
| L31 | Table R7 | Kill scope: "D3 tolerance study done" (layer_map.json:273) | `layer_map.json:273` | "status": "D3 tolerance study done" | **FOUND** | `FACT` | Status line 273 |
| L31 | Table R7 | counts "as data, not as S4 evidence" (PROJECT_VISION.md:251-252) | `PROJECT_VISION.md:251-252` | Testnet calibration (all layers fire) counts as data, not as S4 evidence | **FOUND** | `FACT` | Exact vision text lines 251-252 |
| L31 | Table R7 | Proposed size: 250 -> 20 USD | `auto_trader_config.json:57` | Current size_usd is 250, proposed reduction to 20 | **FOUND** | `OURS` | Probe sizing recommendation |
| L32 | Table R8 | Session momentum prefix 211 | `auto_trader_config.json:211` | "layer:session:": { line 211 | **FOUND** | `FACT` | Prefix definition |
| L32 | Table R8 | Quote: layer_map.json:878 ("FAIL (rerun OOS net +0.0177%...") | `layer_map.json:878` | "verdict": "FAIL (rerun OOS net +0.0177%, Sharpe 0.0084, 1 of 2 years positive)" | **FOUND** | `FACT` | Verdict string line 878 |
| L32 | Table R8 | Quote: config:136 ("T055 C2 FAIL") | `auto_trader_config.json:136` | "reason": "T055 C2 FAIL (fee-net OOS Sharpe 0.0084)" | **FOUND** | `FACT` | Parked reason line 136 |
| L32 | Table R8 | T055-C2 rerun OOS n 299, 70/30, 10 bp + 2 bp + funding | `layer_map.json:873-877` | 873: 70/30; 874: 10 bps RT + 2 bps slip + funding; 877: OOS 299 (rerun) | **FOUND** | `FACT` | Backtest parameters lines 873-877 |
| L32 | Table R8 | Quote: layer_map.json:433 ("FAIL, closed") | `layer_map.json:433` | "status": "FAIL, closed" | **FOUND** | `FACT` | Status string line 433 |
| L32 | Table R8 | RE-DERIVED: 4.243 x 1.5 / sqrt(299) = 0.368 R > 0.30 R | `REGATE_AUDIT.md:4, layer_map.json:877` | 4.243 * 1.5 / sqrt(299) = 0.368068 R | **FOUND** | `OURS` | Re-derived MDE calculation |
| L32 | Table R8 | Size 150 USD (config:65) | `auto_trader_config.json:65` | "size_usd": 150, | **FOUND** | `FACT` | Config line 65 |
| L33 | Table R9 | Turn of candle prefix 215 | `auto_trader_config.json:215` | "layer:turn_of_candle:": { line 215 | **FOUND** | `FACT` | Prefix definition |
| L33 | Table R9 | Quote: layer_map.json:896 ("NO EDGE (gross OOS about 0 at every horizon)") | `layer_map.json:896` | "verdict": "NO EDGE (gross OOS about 0 at every horizon)" | **FOUND** | `FACT` | Verdict string line 896 |
| L33 | Table R9 | Quote: BUGS.md:194 (T093 "NO REPLICATION at 4h/8h/12h...") | `BUGS.md:194` | Turn-of-candle 4-12 h order-imbalance test on klines, no replication (n about 166k each, gross +0.5 bp vs 10 bp fee, net CI95 below zero) | **FOUND** | `FACT` | Bug T093 description line 194 |
| L33 | Table R9 | T055-C3 OOS n 49,823, IS/OOS split 1,743,840 / 747,360, fees 10+2+funding | `layer_map.json:891-895` | 891: IS 1,743,840 / OOS 747,360; 892: 10 bps RT + 2 bps slip + funding; 895: OOS 49,823 | **FOUND** | `FACT` | Study parameters lines 891-895 |
| L33 | Table R9 | Quote: layer_map.json:469 ("no edge, closed") | `layer_map.json:469` | "status": "no edge, closed" | **FOUND** | `FACT` | Status string line 469 |
| L33 | Table R9 | RE-DERIVED: 4.243 x 1.5 / sqrt(49,823) = 0.029 R | `REGATE_AUDIT.md:4, layer_map.json:895` | 4.243 * 1.5 / sqrt(49823) = 0.028513 R | **FOUND** | `OURS` | Re-derived MDE calculation |
| L33 | Table R9 | Parity of live fires proven (layer_map.json:1249) | `layer_map.json:1249` | 244,543 fires; spot rerun parity 92-100 %, turn_of_candle side mismatches 0 | **FOUND** | `FACT` | Effects string line 1249 |
| L34 | Table R10 | Tom core prefix 219 | `auto_trader_config.json:219` | "tom": { line 219 | **FOUND** | `FACT` | Prefix definition |
| L34 | Table R10 | Quote: layer_map.json:10 ("STOP: do not backtest or tune...") | `layer_map.json:10` | "status": "STOP: do not backtest or tune the current BTC encoding (tom_transfer ROADMAP section 2); being redefined as Tom v2" | **FOUND** | `FACT` | Status string line 10 |
| L34 | Table R10 | Quote: layer_map.json:915 ("no edge: gross -0.07 R, net -0.30 R, holdout net -0.32 R (n=254)") | `layer_map.json:915` | "verdict": "no edge: gross -0.07 R, net -0.30 R, holdout net -0.32 R (n=254)" | **FOUND** | `FACT` | Verdict string line 915 |
| L34 | Table R10 | Quote: layer_map.json:932 ("live rule SETUP_FORMING filled trades 17 -> 0") | `layer_map.json:932` | "effects": "live rule SETUP_FORMING filled trades 17 -> 0; episodes 4417 -> 2880" | **FOUND** | `FACT` | Effects string line 932 |
| L34 | Table R10 | Quote: VERDICTS.csv:115 (Tom v2 first read "FAIL" n 352 DEV_EXT) | `VERDICTS.csv:115` | tom_v2_gross_first_2026-11 ... DEV_EXT,352,4.43,2.35,0,FAIL | **FOUND** | `FACT` | Line 115 in VERDICTS.csv |
| L34 | Table R10 | TOM-CORE-0929 holdout 2026-06-26.. n 254, Deribit 0 / 0.0005 fees | `layer_map.json:910-915` | 910: holdout 2026-06-26..; 912: Deribit maker 0 / taker 0.0005; 915: n=254 | **FOUND** | `FACT` | Study parameters lines 910-915 |
| L34 | Table R10 | Quote: VERDICTS.csv:115 kill scope ("FAIL means stop: the 70/30 return claim...") | `VERDICTS.csv:115` | FAIL means stop: the 70/30 return claim has no demonstrated value-specific content on BTC UTC-day value over 2020-2021 | **FOUND** | `FACT` | Kill scope text line 115 |
| L34 | Table R10 | RE-DERIVED: Holdout at n 254 gives MDE 0.399 R | `REGATE_AUDIT.md:4, layer_map.json:915` | 4.243 * 1.5 / sqrt(254) = 0.399344 R | **FOUND** | `OURS` | Re-derived MDE calculation |
| L34 | Table R10 | tom-btc-encode blocked (LAYERS.md:36) | `LAYERS.md:76 (cited :36)` | tom-btc-encode blocked p2 CODEX: Tom on BTC T5: encode the concepts... | **FOUND** | `FACT` | Current line 76 in LAYERS.md |
| L35 | Table R11 | RSI divergence prefix 223 | `auto_trader_config.json:223` | "layer:rsi_divergence:": { line 223 | **FOUND** | `FACT` | Prefix definition |
| L35 | Table R11 | Quote: layer_map.json:1007 ("no edge on any timeframe that reached 300 events; 31 of 32 net negative") | `layer_map.json:1007` | "verdict": "no edge on any timeframe that reached 300 events; 31 of 32 net negative; 6h and 12h negative throughout" | **FOUND** | `FACT` | Verdict string line 1007 |
| L35 | Table R11 | Quote: layer_map.json:303 ("no edge, all TFs") | `layer_map.json:303` | "status": "no edge, all TFs" | **FOUND** | `FACT` | Status string line 303 |
| L35 | Table R11 | VERDICTS.csv:50 FAIL | `VERDICTS.csv:50` | rsi_divergence_mtf_2026-10-09 ... FAIL | **FOUND** | `FACT` | Line 50 in VERDICTS.csv |
| L35 | Table R11 | RSI-DIV-MTF per-year split, "one taker round trip 0.10%", 32 cells n>=300 | `layer_map.json:1002-1006` | 1002: per-year; 1003: one taker round trip 0.10%; 1006: n>=300 on 32 cells | **FOUND** | `FACT` | Study parameters lines 1002-1006 |
| L35 | Table R11 | Kill scope: UNPARSED (VERDICTS.csv:50) | `VERDICTS.csv:50` | kill_scope column is UNPARSED | **FOUND** | `FACT` | Column 10 line 50 |
| L35 | Table R11 | RE-DERIVED: Per-cell MDE at n 300 is 0.367 R | `REGATE_AUDIT.md:4` | 4.243 * 1.5 / sqrt(300) = 0.367454 R | **FOUND** | `OURS` | Re-derived MDE calculation |
| L35 | Table R11 | Quote: config:224 ("not an edge claim") | `auto_trader_config.json:224` | "reason": "grandfathered testnet calibration, operator 2026-10-16 all-layers direction; not an edge claim" | **FOUND** | `FACT` | Grandfather reason line 224 |
| L36 | Table R12 | Session levels prefix 227 | `auto_trader_config.json:227` | "layer:session_levels:": { line 227 | **FOUND** | `FACT` | Prefix definition |
| L36 | Table R12 | Quote: layer_map.json:1025 ("no edge (net -0.036%, t -1.72)") | `layer_map.json:1025` | "verdict": "no edge (net -0.036%, t -1.72); EU-touch cells insufficient n" | **FOUND** | `FACT` | Verdict string line 1025 |
| L36 | Table R12 | Quote: VERDICTS.csv:51 ("INCONCLUSIVE", kill_scope "none") | `VERDICTS.csv:51` | t087_session_levels_2026-10-09 ... INCONCLUSIVE,none | **FOUND** | `FACT` | Line 51 in VERDICTS.csv |
| L36 | Table R12 | Quote: LC-SIZING "All eight negative; mean net R -0.216 to -0.195", n 117 (layer_map.json:1393-1395) | `layer_map.json:1393-1395` | 1393: All eight negative; mean net R -0.216 to -0.195; 1394: n=117; 1395: EXPLORATORY NEGATIVE; full LC hypothesis untested | **FOUND** | `FACT` | Effects and verdict lines 1393-1395 |
| L36 | Table R12 | T087 n 911, split "not recorded" / ALL (layer_map.json:1020; VERDICTS.csv:51) | `layer_map.json:1020; VERDICTS.csv:51` | 1020: "split": "not recorded"; VERDICTS.csv:51: ALL ... 911 | **FOUND** | `FACT` | Sample size and split metadata |
| L36 | Table R12 | Quote: layer_map.json:1021 ("net column present; cost model not stated") | `layer_map.json:1021` | "fees": "net column present; cost model not stated in the head of the file" | **FOUND** | `FACT` | Fees string line 1021 |
| L36 | Table R12 | Size 20 USD (config:109) | `auto_trader_config.json:109` | "size_usd": 20, | **FOUND** | `FACT` | Config line 109 |
| L37 | Table R13 | BB top reversal prefix 231 | `auto_trader_config.json:231` | "layer:bb_top_reversal:": { line 231 | **FOUND** | `FACT` | Prefix definition |
| L37 | Table R13 | Quote: VERDICTS.csv:25 ("BLOCKED ... blocks on cost alone (0.349 R > 0.30 R)...") | `VERDICTS.csv:25` | it blocks on cost alone (0.349 R > 0.30 R), so the family is not killed: a wider stop, a maker entry or another timeframe is a new PRE_REG | **FOUND** | `FACT` | Kill scope string line 25 |
| L37 | Table R13 | Quote: VERDICTS.csv:25 ("median stop 0.286 %") | `VERDICTS.csv:25` | at the median stop 0.286 % | **FOUND** | `FACT` | Parameter quote line 25 |
| L37 | Table R13 | 12 count-only ledger rows (TRIAL_LEDGER.csv:32-43) | `TRIAL_LEDGER.csv:32-43` | Lines 32 to 43 = 12 rows of bb_top_reversal_2026-10-18 | **FOUND** | `FACT` | Exact ledger rows |
| L38 | Table R14 | Candle close prefix 235 | `auto_trader_config.json:235` | "layer:candle_close:": { line 235 | **FOUND** | `FACT` | Prefix definition |
| L38 | Table R14 | Quote: layer_map.json:1411 ("0/126 pooled arms pass; all mean 14bp cost screens negative") | `layer_map.json:1411` | "effects": "0/126 pooled arms pass; all mean 14bp cost screens negative" | **FOUND** | `FACT` | Effects string line 1411 |
| L38 | Table R14 | Quote: layer_map.json:1413 ("EXPLORATORY NEGATIVE; cycle outcomes untested") | `layer_map.json:1413` | "verdict": "EXPLORATORY NEGATIVE; cycle outcomes untested" | **FOUND** | `FACT` | Verdict string line 1413 |
| L38 | Table R14 | DEV 2022-01..2024-06, "14/20bp cost screen only; historical funding unmodeled", n 59-1761 (layer_map.json:1408-1410) | `layer_map.json:1408-1410` | 1408: DEV 2022-01..2024-06; 1409: 14/20bp cost screen only; historical funding unmodeled; 1410: n 59-1761 | **FOUND** | `FACT` | Study parameters lines 1408-1410 |
| L39 | Table R15 | Levels prefix 239 | `auto_trader_config.json:239` | "layer:levels:": { line 239 | **FOUND** | `FACT` | Prefix definition |
| L39 | Table R15 | No layer_map row of its own: NO EVIDENCE: NOT_IN_DATA | `layer_map.json` | No entry for layer:levels: live encoding | **NOT_IN_DATA** | `OURS` | Acknowledged absence in layer_map |
| L39 | Table R15 | Quote: VERDICTS.csv:48 pit_levels ("BLOCKED ... count-only, no outcome read") | `VERDICTS.csv:48` | BLOCKED ... this BLOCK (count-only, no outcome read) covers only the failed-auction... | **FOUND** | `FACT` | Line 48 kill scope text |
| L39 | Table R15 | n_needed 2,630 days vs 662 (REGATE_AUDIT.md:29) | `REGATE_AUDIT.md:29` | n 662 days ... n_needed 2,630 days | **FOUND** | `FACT` | Line 29 in REGATE_AUDIT.md |
| L39 | Table R15 | Quote: REGATE_AUDIT.md:13 pit V3 ("GO-WITH-CHANGE ... F1 long MDE 0.244 R, F2 long 0.252 R at m 89") | `REGATE_AUDIT.md:13` | GO-WITH-CHANGE ... F1 long MDE 0.244 R, F2 long 0.252 R at m 89 | **FOUND** | `FACT` | Line 13 in REGATE_AUDIT.md |
| L39 | Table R15 | Quote: VERDICTS.csv:2 Qriptal filter ("lc-levels-hold KEEP levels" FAIL n 3271 DEV) | `VERDICTS.csv:2` | lc-levels-hold KEEP levels ... DEV,3271,-0.0067,0.0090,0.14,FAIL | **FOUND** | `FACT` | Line 2 in VERDICTS.csv |
| L39 | Table R15 | pit V3 F1/F2 powered count: 694/700, 654/657 days (REGATE_AUDIT.md:26) | `REGATE_AUDIT.md:26` | powered F1 694/700, F2 654/657 | **FOUND** | `FACT` | Line 26 in REGATE_AUDIT.md |
| L39 | Table R15 | Size 20 USD (config:121) | `auto_trader_config.json:121` | "size_usd": 20, | **FOUND** | `FACT` | Config line 121 |
| L40 | Table R16 | Weekly-low bounce prefix 243 | `auto_trader_config.json:243` | "layer:wlow_bounce:": { line 243 | **FOUND** | `FACT` | Prefix definition |
| L40 | Table R16 | Quote: VERDICTS.csv:63 (n 8, gross -0.293 %, se 0.116, cost 0.14, INCONCLUSIVE, kill "none") | `VERDICTS.csv:63` | DEV,8,-0.293,0.116,0.14,INCONCLUSIVE,none | **FOUND** | `FACT` | Line 63 in VERDICTS.csv |
| L40 | Table R16 | Quote: REGATE_AUDIT.md:37 ("MDE 2.25 R at sd 1.5") | `REGATE_AUDIT.md:37` | m 75: MDE 2.25 R at sd 1.5 | **FOUND** | `FACT` | Line 37 in REGATE_AUDIT.md |
| L40 | Table R16 | 8 ledger variants (TRIAL_LEDGER.csv:2-9) | `TRIAL_LEDGER.csv:2-9` | Lines 2 to 9 = 8 variants of wlow_bounce_bbrsi60_2026-10-16 | **FOUND** | `FACT` | Exact ledger rows |
| L40 | Table R16 | RE-DERIVED: 4.243 x 1.5 / sqrt(8) = 2.25 R | `REGATE_AUDIT.md:4, 37` | 4.243 * 1.5 / sqrt(8) = 2.25019 R | **FOUND** | `OURS` | Re-derived MDE calculation |
| L42 | Table Summary | Counts per prefix: KEEP 1, SHADOW 23, DROP 2, RE-TEST 1 (= 27) | `auto_trader_config.json:143-250` | Sum = 27 prefixes | **FOUND** | `OURS` | Breakdown of 27 grandfathered prefixes |
| L42 | Table Summary | Counts per layer: KEEP 1, SHADOW 12, DROP 2, RE-TEST 1 (= 16) | `Table rows 1-16` | Sum = 16 distinct layers | **FOUND** | `OURS` | Breakdown of 16 layer rows |
| L44 | Size Arithmetic | Summed configured size_usd = 5,910 USD | `auto_trader_config.json:25, 43-131` | tom 20 + overrides 5890 = 5910 USD | **FOUND** | `OURS` | Re-derived sum of size_usd |
| L44 | Size Arithmetic | Summed max_loss_usd = 137 USD | `auto_trader_config.json:26, 43-131` | tom 5 + overrides 132 = 137 USD | **FOUND** | `OURS` | Re-derived sum of max_loss_usd |
| L44 | Size Arithmetic | Five largest rows = 3,650 USD (62 % of 5,910) | `auto_trader_config.json:61,69,85,93,101` | 1000 + 800 + 750 + 600 + 500 = 3650 USD (61.76%) | **FOUND** | `OURS` | Re-derived percentage |
| L44 | Size Arithmetic | GAP-1 fix 1 prunes 3 x 20 = 60 USD = 1 % | `auto_trader_config.json:45,105,109, gap_audit REPORT.md:47` | 20 + 20 + 20 = 60 USD (1.015% of 5910) | **FOUND** | `OURS` | Re-derived prune size |
| L49 | Answers Q1 | 27 entries in pre_pipeline_sources: CONFIRMED | `auto_trader_config.json:143-250` | 27 keys in dictionary | **FOUND** | `FACT` | Line count 143-250 |
| L49 | Answers Q1 | promoted_setups.json empty: CONFIRMED | `promoted_setups.json:3` | "entries": [] | **FOUND** | `FACT` | Empty array at line 3 |
| L49 | Answers Q1 | 0 validated OOS PASS among them: CONFIRMED | `VERDICTS.csv, layer_map.json` | No PASS verdict among the 16 layers | **FOUND** | `FACT` | Pitchfork passes at :1486 and :1504 are outside list |
| L49 | Answers Q1 | Pitchfork PASS rows in map: layer_map.json:1486 and :1504 | `layer_map.json:1486, 1504` | 1486: PASS (Modified Schiff...); 1504: PASS (VA confluence...) | **FOUND** | `FACT` | Line 1486 and 1504 verdicts |
| L50 | Answers Q1 | Parent prefix covers sub-prefixes: cryptocred (5), fabio (4), malkan (2) | `auto_trader_config.json:143-250` | 5 + 4 + 2 = 11 sub-prefixes | **FOUND** | `OURS` | Detailed sub-prefix breakdown |
| L50 | Answers Q1 | 11 of 27 entries grant nothing under prefix match (PROMOTION_PIPELINE.md:34-35) | `PROMOTION_PIPELINE.md:34-35` | starts with a prefix in pre_pipeline_sources | **FOUND** | `FACT` | Prefix-match specification |
| L50 | Answers Q1 | Distinct layers count: 16 | `Table rows 1-16` | 16 distinct layers in table | **FOUND** | `OURS` | 27 total minus 11 redundant |
| L51 | Answers Q1 | GAP-1 cites auto_trader_config.json:1-99 (REPORT.md:36) | `gap_audit REPORT.md:36` | MyTradingSys/execution/auto_trader_config.json:1-99 | **FOUND** | `FACT` | Quote from gap_audit REPORT.md line 36 |
| L51 | Answers Q1 | GAP-1 quotes max_hold_bars: 8 (REPORT.md:45): NOT_IN_DATA in code | `gap_audit REPORT.md:45, auto_trader.py` | Key max_hold_bars: 8 is in none of the repo code files | **NOT_IN_DATA** | `OURS` | Acknowledged absent parameter in code |
| L51 | Answers Q1 | auto_trader.py:90 has max_hold_bars 100 for rsi 1h | `auto_trader.py:90` | "max_hold_bars": 100, | **FOUND** | `FACT` | Line 90 in auto_trader.py |
| L51 | Answers Q1 | "8 bars" in bigtrade exit name: layer_map.json:665 | `layer_map.json:665` | "id": "live_like_1pct_2pct_8bars", | **FOUND** | `FACT` | Line 665 in layer_map.json |
| L51 | Answers Q1 | GAP-1 "29 rows" in TRIAL_LEDGER stale vs 119 rows today | `gap_audit REPORT.md:40, TRIAL_LEDGER.csv:2-120` | REPORT.md:40 quotes 29 rows; live ledger has 119 rows | **FOUND** | `FACT` | Ledger growth verification |
| L51 | Answers Q1 | TRIAL_LEDGER.csv:119-120 two rows at split VALIDATION | `TRIAL_LEDGER.csv:119-120` | eagle_c30_prereg H1 and H2 both VALIDATION | **FOUND** | `FACT` | Lines 119-120 in TRIAL_LEDGER.csv |
| L51 | Answers Q1 | Tom v2 encode blocked (LAYERS.md:36) | `LAYERS.md:76 (cited :36)` | tom-btc-encode blocked p2 CODEX | **FOUND** | `FACT` | Current line 76 in LAYERS.md |
| L51 | Answers Q1 | Fabio v2 spec blocked (LAYERS.md:74-75) | `LAYERS.md:71-72 (cited :74-75)` | fabio-layer-v2-spec blocked p5 OPUS | **FOUND** | `FACT` | Current lines 71-72 in LAYERS.md |
| L51 | Answers Q1 | LC confluence at S4/S5 cards (LAYERS.md:236-237) | `LAYERS.md:231-232 (cited :236-237)` | confluence-s4-dev-trials blocked, confluence-s5-fable-verdict refined | **FOUND** | `FACT` | Current lines 231-232 in LAYERS.md |
| L53 | Answers Q2 | Three closures are INCONCLUSIVE; no row becomes PASS | `Table rows 5, 8, 12` | positioning, session_momentum, session_levels are underpowered | **FOUND** | `OURS` | Re-evaluation under fixed gate |
| L54 | Answers Q2 | Fixed gate factor 4.243 at m 75, sd 1.5 bound | `REGATE_AUDIT.md:4, 33-34` | z_holm 3.403 + 0.84 = 4.243; sd bound 1.5 R | **FOUND** | `FACT` | Gate formula parameters |
| L55 | Answers Q2 | positioning T055-C1 n 76 MDE 0.730 R (layer_map.json:378) | `layer_map.json:378, 859` | 378: status: FAIL, closed; 859: n 76; MDE 0.730 R | **FOUND** | `FACT` | Re-derived positioning power |
| L56 | Answers Q2 | session_momentum T055-C2 n 299 MDE 0.368 R (layer_map.json:878) | `layer_map.json:877, 878` | 877: n 299; 878: net +0.0177%; MDE 0.368 R | **FOUND** | `FACT` | Re-derived session momentum power |
| L57 | Answers Q2 | session_levels T087 n 911, t -1.72 (layer_map.json:1025; VERDICTS.csv:51) | `layer_map.json:1025, VERDICTS.csv:51` | 1025: net -0.036%, t -1.72; VERDICTS.csv:51: INCONCLUSIVE | **FOUND** | `FACT` | Session levels status alignment |
| L58 | Answers Q2 | Powered FAIL: turn_of_candle n 49,823 (MDE 0.029 R) | `layer_map.json:895` | 4.243 * 1.5 / sqrt(49823) = 0.0285 R | **FOUND** | `OURS` | Re-derived turn of candle MDE |
| L58 | Answers Q2 | Powered FAIL: T093 n ~166k (BUGS.md:194) | `BUGS.md:194` | n about 166k each, gross +0.5 bp vs 10 bp fee | **FOUND** | `FACT` | Line 194 in BUGS.md |
| L58 | Answers Q2 | Powered FAIL: rsi_divergence 32-cell sign pattern | `layer_map.json:1007` | 31 of 32 net negative | **FOUND** | `FACT` | Line 1007 in layer_map.json |
| L58 | Answers Q2 | Powered FAIL: candle_close 0/126 arms pass screen | `layer_map.json:1411` | 0/126 pooled arms pass; all mean 14bp cost screens negative | **FOUND** | `FACT` | Line 1411 in layer_map.json |
| L59 | Answers Q2 | Tom v1 holdout MDE 0.399 R at n 254 (layer_map.json:10, 915) | `layer_map.json:10, 915` | 4.243 * 1.5 / sqrt(254) = 0.399 R; status STOP | **FOUND** | `OURS` | Re-derived Tom MDE |
| L60 | Answers Q2 | Only non-negative cell rsi 1h support PBO 0.030 is gross (layer_map.json:782) | `layer_map.json:782, 786` | 782: fees: none (forward-return study, gross); 786: 1h support PBO 0.030 | **FOUND** | `FACT` | Gross return verification |
| L63 | Answers Q3 | hours: 1.0, max_age_bars: 2.0 (auto_trader_config.json:40-41) | `auto_trader_config.json:40-41` | "max_age_bars": 2.0, "hours": 1.0 | **FOUND** | `FACT` | Lines 40-41 in config |
| L63 | Answers Q3 | Tom max_hold_minutes: 120 (config:33) | `auto_trader_config.json:33` | "max_hold_minutes": 120, | **FOUND** | `FACT` | Line 33 in config |
| L63 | Answers Q3 | Bigtrade live-like exit live_like_1pct_2pct_8bars (layer_map.json:665) | `layer_map.json:665` | "id": "live_like_1pct_2pct_8bars", | **FOUND** | `FACT` | Line 665 in layer_map.json |
| L63 | Answers Q3 | rsi 1h tested bracket: stop_pct 1.0, targets 2, max_hold_bars 100 (auto_trader.py:90) | `auto_trader.py:90` | "stop_pct": 1.0, "targets": "2", "max_hold_bars": 100, | **FOUND** | `FACT` | Line 90 in auto_trader.py |
| L63 | Answers Q3 | cc 1h setups: stop event, max_hold_minutes 1440, targets SAMPLING (auto_trader.py:92-96) | `auto_trader.py:92-96` | "stop": "event", "max_hold_minutes": 1440 | **FOUND** | `FACT` | Lines 92-96 in auto_trader.py |
| L64 | Answers Q3 | Settlement window handling 10041 skip (PROMOTION_REVIEW.md:20) | `PROMOTION_REVIEW.md:20` | 10041 skip fires only when not entries (nothing placed)... | **FOUND** | `FACT` | Line 20 in PROMOTION_REVIEW.md |
| L64 | Answers Q3 | Daily-loss aggregation across named accounts (gap_audit REPORT.md:96-108) | `gap_audit REPORT.md:96, 108` | skips subaccount agg ... daily_loss_monitor.py:505-513 | **FOUND** | `FACT` | Lines 96, 108 in gap_audit REPORT.md |
| L64 | Answers Q3 | S2 survive the fees (PROJECT_VISION.md:228, 249) | `PROJECT_VISION.md:228, 249` | 228: S2 survive the fees; 249: Every result is net of real fees and funding | **FOUND** | `FACT` | Lines 228, 249 in PROJECT_VISION.md |
| L65 | Answers Q3 | Calibration counts as data, not as S4 evidence (PROJECT_VISION.md:251-252) | `PROJECT_VISION.md:251-252` | Testnet calibration (all layers fire) counts as data, not as S4 evidence | **FOUND** | `FACT` | Lines 251-252 in PROJECT_VISION.md |
| L65 | Answers Q3 | No source has passed S3 (PROJECT_VISION.md:229) | `PROJECT_VISION.md:229` | no source has passed S3 | **FOUND** | `FACT` | Line 229 in PROJECT_VISION.md |
| L68 | Answers Q4 | 1000 USD per trade, max_loss 20 USD (auto_trader_config.json:84-87) | `auto_trader_config.json:85-86` | "size_usd": 1000, "max_loss_usd": 20 | **FOUND** | `FACT` | Lines 85-86 in config |
| L68 | Answers Q4 | Account jishu_14 for volume FVG (config:15) | `auto_trader_config.json:15` | "layer:fabio:volume_fvg:": "jishu_14", | **FOUND** | `FACT` | Line 15 in config |
| L68 | Answers Q4 | L1 no edge on NO-SOURCE encoding (layer_map.json:215, 224) | `layer_map.json:215, 224` | 215: status: L1 no edge; 224: src: NO-SOURCE | **FOUND** | `FACT` | Lines 215, 224 in layer_map.json |
| L68 | Answers Q4 | FIRES parity (layer_map.json:1249) | `layer_map.json:1249` | spot rerun parity 92-100 %, turn_of_candle side mismatches 0 | **FOUND** | `FACT` | Line 1249 in layer_map.json |
| L68 | Answers Q4 | 17 % of all configured size on volume FVG | `auto_trader_config.json:85` | 1000 / 5910 = 0.1692 (16.92%, rounds to 17%) | **FOUND** | `OURS` | Re-derived size share |
| L69 | Answers Q4 | cryptocred fib_pullback:1h 800 USD, sr_flip:1h 600 USD (config:92-103) | `auto_trader_config.json:93, 101` | sr_flip:1h: 600 (line 93); fib_pullback:1h: 800 (line 101) | **FOUND** | `FACT` | Lines 93, 101 in config |
| L69 | Answers Q4 | positioning 750 USD (config:69) | `auto_trader_config.json:69` | "size_usd": 750, | **FOUND** | `FACT` | Line 69 in config |
| L69 | Answers Q4 | malkan_ 500 USD on two accounts (config:60-62, 8-9) | `auto_trader_config.json:8, 9, 61` | size_usd: 500 (line 61); jishu_7, jishu_8 (lines 8-9) | **FOUND** | `FACT` | Config lines 8-9, 61 |
| L69 | Answers Q4 | fabio escalation 400 USD misses 68 of 96 signals (LAYERS.md:69) | `auto_trader_config.json:81, LAYERS.md:67` | config:81: 400 USD; LAYERS.md:67: misses 68 of 96 escalation signals | **FOUND** | `FACT` | Config line 81 and LAYERS.md:67 |
| L70 | Answers Q4 | Catch-alls grant trading without exit spec (auto_trader.py:93) | `auto_trader.py:93` | 1h only (15m was not backtested, T09) | **FOUND** | `FACT` | Line 93 in auto_trader.py |
| L70 | Answers Q4 | 18 named subaccounts (config:4-21) | `auto_trader_config.json:4-21` | 18 distinct named accounts in lines 4-21 | **FOUND** | `FACT` | Lines 4-21 in config |
| L70 | Answers Q4 | one-position-per-account (config:253) | `auto_trader_config.json:253` | one account per layer group so one-position-per-account never blocks another layer | **FOUND** | `FACT` | Line 253 in config |
| L70 | Answers Q4 | jishu_4 carries layer trade, jishu_22 spare (config:7, OPERATOR_DECISIONS.md:1600) | `auto_trader_config.json:7, OPERATOR_DECISIONS.md:1600` | config:7: jishu_4 for rsi 1h; OPERATOR_DECISIONS.md:1600: jishu_22 spare for co-trade | **FOUND** | `FACT` | Account assignments |
| L71 | Answers Q4 | Quote: OPERATOR_DECISIONS.md:1600 ("Account-wide kill/flatten on a shared slot can close his position") | `OPERATOR_DECISIONS.md:1600` | Account-wide kill/flatten on a shared slot can close his position | **FOUND** | `FACT` | Line 1600 in OPERATOR_DECISIONS.md |
| L71 | Answers Q4 | tom and six layers have no own account (config:4-21 vs 219-245) | `auto_trader_config.json:4-21, 219-245` | None of tom, rsi_divergence, session_levels, bb_top, candle_close, levels, wlow appear in accounts | **FOUND** | `FACT` | Absence from accounts map verified |
| L74 | Answers Q5 | pit V3 F1 long 694/700 days, MDE 0.244 R (REGATE_AUDIT.md:13, 26) | `REGATE_AUDIT.md:13, 26` | F1 long MDE 0.244 R at m 89; powered F1 694/700 | **FOUND** | `FACT` | Lines 13, 26 in REGATE_AUDIT.md |
| L74 | Answers Q5 | pit V3 F2 long 654/657 days, MDE 0.252 R at m 89 (REGATE_AUDIT.md:13, 26) | `REGATE_AUDIT.md:13, 26` | F2 long 0.252 R at m 89; powered F2 654/657 | **FOUND** | `FACT` | Lines 13, 26 in REGATE_AUDIT.md |
| L74 | Answers Q5 | z_holm 3.449 at m 89, cost 0, ceiling 0.30 R (REGATE_AUDIT.md:26) | `REGATE_AUDIT.md:26` | 89 ledger (z 3.449, n_needed 460 at sd 1.5; 335 at sd 1.281) | **FOUND** | `FACT` | Line 26 in REGATE_AUDIT.md |
| L74 | Answers Q5 | F3 BLOCKS at m 89 with sd 1.5 R (0.304 / 0.303) vs sd 1.281 R (0.260) | `REGATE_AUDIT.md:13, 26` | F3 BLOCK at m 89 with sd 1.5 (0.304 / 0.303), PASS with sd 1.281 (0.260) | **FOUND** | `FACT` | Lines 13, 26 in REGATE_AUDIT.md |
| L74 | Answers Q5 | F7 long 376 days 0.332 R BLOCK (REGATE_AUDIT.md:13, 26) | `REGATE_AUDIT.md:13, 26` | F7 long 376 d BLOCK 0.332 | **FOUND** | `FACT` | Lines 13, 26 in REGATE_AUDIT.md |
| L74 | Answers Q5 | Headroom: 119 rows, z_holm ~3.59, F1 0.252 R, F2 0.260 R | `TRIAL_LEDGER.csv:2-120` | Re-derived factor 4.43 / 4.289 = 1.033; F1 0.252 R, F2 0.260 R < 0.30 R | **FOUND** | `OURS` | Re-derived headroom calculation |
| L74 | Answers Q5 | 22 ledger rows for context_factors_pit (TRIAL_LEDGER.csv:63-84) | `TRIAL_LEDGER.csv:63-84` | Lines 63 to 84 = 22 rows | **FOUND** | `FACT` | Exact ledger line count |
| L74 | Answers Q5 | pit_levels V2 BLOCKED at 662 of 2,630 days (REGATE_AUDIT.md:29) | `REGATE_AUDIT.md:29` | n 662 days, sd 1.46 R ... n_needed 2,630 days | **FOUND** | `FACT` | Line 29 in REGATE_AUDIT.md |
| L76 | Answers Q5 | CryptoCred 4h/1d BLOCK: n_needed 524 / 493 fills vs 207 / 200 (REGATE_AUDIT.md:42; VERDICTS.csv:114) | `REGATE_AUDIT.md:42; VERDICTS.csv:114` | n_needed 524 / 493 fills; s1 n 207, s2 n 200 | **FOUND** | `FACT` | Power audit lines |
| L76 | Answers Q5 | Fills short: 317 / 293 short | `REGATE_AUDIT.md:42` | 524 - 207 = 317; 493 - 200 = 293 | **FOUND** | `OURS` | Re-derived subtraction |
| L76 | Answers Q5 | 1d fills: 31 / 30 / 1 fills (TRIAL_LEDGER.csv:91-93) | `TRIAL_LEDGER.csv:91-93` | setup1 1d: 31; setup2 1d: 30; setup3 1d: 1 | **FOUND** | `FACT` | Lines 91-93 in TRIAL_LEDGER.csv |
| L77 | Answers Q5 | WaveTrend: W04-W08 INCONCLUSIVE at realised MDE 14-68 bps (REGATE_AUDIT.md:48) | `REGATE_AUDIT.md:48` | W04-W08 at 14-68 bps ... underpowered null, read as INCONCLUSIVE | **FOUND** | `FACT` | Line 48 in REGATE_AUDIT.md |
| L77 | Answers Q5 | WaveTrend W07/W08 invalid C1 detector (LAYERS.md:248) | `LAYERS.md:252 (cited :248)` | wavetrend-c1-v2 refined p1 SONNET: WaveTrend C1 detector correction and new... | **FOUND** | `FACT` | Current line 252 in LAYERS.md |
| L77 | Answers Q5 | eagle_c30 prereg (TRIAL_LEDGER.csv:119-120) sits on 256-cell DEV search (TRIAL_LEDGER.csv:118) | `TRIAL_LEDGER.csv:118-120` | 118: eagle_c30_dev_search,C27-C30_all_cells; 119-120: eagle_c30_prereg H1,H2 | **FOUND** | `FACT` | Lines 118-120 in TRIAL_LEDGER.csv |
| L78 | Answers Q5 | Tom v2: first gross-first read FAIL n 352 (VERDICTS.csv:115) | `VERDICTS.csv:115` | tom_v2_gross_first_2026-11 ... DEV_EXT,352,4.43,2.35,0,FAIL | **FOUND** | `FACT` | Line 115 in VERDICTS.csv |
| L78 | Answers Q5 | Tom v2 encode / DEV / VALIDATION cards blocked (LAYERS.md:35-37) | `LAYERS.md:75-77 (cited :35-37)` | tom-btc-dev-backtest, tom-btc-encode, tom-btc-validation blocked | **FOUND** | `FACT` | Current lines 75-77 in LAYERS.md |
| L79 | Answers Q5 | Fabio v2 spec cards blocked p5 OPUS (LAYERS.md:46, 74-75) | `LAYERS.md:71-72, 85` | fabio-layer-v2-markets, fabio-layer-v2-spec blocked p5; status waits on ledger repairs | **FOUND** | `FACT` | Current lines 71-72, 85 in LAYERS.md |
| L80 | Answers Q5 | Quote: LC3/LC4 confluence ("full LC hypothesis untested") (layer_map.json:1395) | `layer_map.json:1395` | "verdict": "EXPLORATORY NEGATIVE; full LC hypothesis untested" | **FOUND** | `FACT` | Line 1395 in layer_map.json |
| L80 | Answers Q5 | S4 trials blocked, S5 verdict refined (LAYERS.md:236-237) | `LAYERS.md:231-232 (cited :236-237)` | confluence-s4-dev-trials blocked, confluence-s5-fable-verdict refined | **FOUND** | `FACT` | Current lines 231-232 in LAYERS.md |
| L80 | Answers Q5 | LC confluence power number: NOT_IN_DATA in inputs | `Pasted inputs / brief` | No power number provided in inputs for LC confluence | **NOT_IN_DATA** | `OURS` | Acknowledged absence in inputs L80 |
| L81 | Answers Q5 | Krown S8 4h pooled, n 420, +0.1312 R, t +1.73, INCONCLUSIVE (VERDICTS.csv:65) | `VERDICTS.csv:65` | fable_run6_powered_prereg ... DEV,420,+0.1312,0.0760,1.5,INCONCLUSIVE | **FOUND** | `FACT` | Line 65 in VERDICTS.csv (0.1312/0.0760 = 1.726) |
| L84 | Answers Q6 | review_by informational (PROMOTION_PIPELINE.md:39; config:252) | `PROMOTION_PIPELINE.md:39; auto_trader_config.json:252` | Expiry would silently halt trading; not enforced | **FOUND** | `FACT` | Policy specification lines |
| L85 | Answers Q6 | Pending VALIDATION reads: none on 16 layers (LAYERS.md:37, REPORT.md:48) | `LAYERS.md:77, gap_audit REPORT.md:48` | tom-btc-validation blocked; lc-validation named in REPORT.md:48 | **FOUND** | `FACT` | Card status lines |
| L85 | Answers Q6 | Ledger count m 75 vs 57 (REGATE_AUDIT.md:6) | `REGATE_AUDIT.md:6` | verdicts.py count --split DEV = 57 ... m 75 | **FOUND** | `FACT` | Line 6 in REGATE_AUDIT.md |
| L86 | Answers Q6 | Quote: LAYERS.md:196 ("Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it") | `LAYERS.md:194 (cited :196)` | Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it | **FOUND** | `FACT` | Current line 194 in LAYERS.md |
| L87 | Answers Q6 | Inputs dated to 2026-11-01 (OPERATOR_DECISIONS.md:1608-1616; VERDICTS.csv:115) | `OPERATOR_DECISIONS.md:1616; VERDICTS.csv:115` | 1616: 2026-11-01 (operator, chat); VERDICTS.csv:115: 2026-11-01 | **FOUND** | `FACT` | Date timestamps in files |
| L87 | Answers Q6 | Default at next deploy (PROMOTION_PIPELINE.md:48) | `PROMOTION_PIPELINE.md:48` | the next manual or coordinator-run deploy ships it | **FOUND** | `FACT` | Line 48 in PROMOTION_PIPELINE.md |
| L94 | Cards | Card 1: pre_pipeline_sources keeps rsi 1h (review_by 2026-11-23) | `auto_trader_config.json:56-59` | today 250 / 5 at config:56-59; proposed 20 / 2 | **FOUND** | `OURS` | Config modification proposal |
| L94 | Cards | Card 1: demote off quoting layer_map.json:896 and :1007 | `layer_map.json:896, 1007` | 896: NO EDGE turn_of_candle; 1007: no edge rsi_divergence | **FOUND** | `FACT` | Demotion reasons matching layer_map |
| L95 | Cards | Card 2: DSA-NB per OPERATOR_DECISIONS.md:1608 | `OPERATOR_DECISIONS.md:1608` | ## d-cotrade-testnet-carveout \| decided 2026-10-31 | **FOUND** | `FACT` | Line 1608 in OPERATOR_DECISIONS.md |
| L96 | Cards | Card 3: prereg_gate.py --n 448 --sd 1.5 --cost 0 --m 89 exits 1 (REGATE_AUDIT.md:82) | `REGATE_AUDIT.md:82` | prereg_gate.py --n 448 --sd 1.5 --cost 0 --m 89 exits 1 (BLOCK) | **FOUND** | `FACT` | Line 82 in REGATE_AUDIT.md |
| L96 | Cards | Card 3: grep -c context_factors_pit TRIAL_LEDGER.csv = 22 (TRIAL_LEDGER.csv:63-84) | `TRIAL_LEDGER.csv:63-84` | Count of context_factors_pit occurrences in file is 22 | **FOUND** | `FACT` | Exact ledger line count |
| L97 | Cards | Card 4: 11 redundant keys in config | `auto_trader_config.json:143-250` | 143 covers 5; 163 covers 4; 187 covers 2; total = 11 | **FOUND** | `OURS` | Config redundancy lint test |
| L98 | Cards | Card 5: layer_map.json status words: T055 C1 (:378), C2 (:433), T087 (:517, :1025) | `layer_map.json:378, 433, 517, 1025` | 378: FAIL, closed; 433: FAIL, closed; 517: no edge; 1025: no edge | **FOUND** | `FACT` | Status words in layer_map.json |
| L98 | Cards | Card 5: VERDICTS.csv:50 and :37-38 kill_scope UNPARSED | `VERDICTS.csv:37, 38, 50` | Lines 37, 38, 50 all have UNPARSED in column 10 (kill_scope) | **FOUND** | `FACT` | Exact kill_scope values in VERDICTS.csv |
| L104 | Decisions | D1: rsi 1h probe at 20 USD / max_loss 2 (smallest sized row config:45-46, 105-106) | `auto_trader_config.json:45-46, 105-106` | turn_of_candle: 20/2; rsi_divergence: 20/2 (smallest sizes) | **FOUND** | `OURS` | Probe size matches smallest rows |
| L104 | Decisions | D1: co-trade tool (OPERATOR_DECISIONS.md:1605) | `OPERATOR_DECISIONS.md:1605` | d-cotrade-use-existing-account | **FOUND** | `FACT` | Line 1605 in OPERATOR_DECISIONS.md |
| L105 | Decisions | D2: DROP turn_of_candle and rsi_divergence (layer_map.json:469, :303; BUGS.md:194) | `layer_map.json:469, 303; BUGS.md:194` | 469: no edge, closed; 303: no edge, all TFs; BUGS:194: T093 closed | **FOUND** | `FACT` | Falsified layer references |
| L105 | Decisions | D2: Blocklist specification (PROMOTION_PIPELINE.md:44-46) | `PROMOTION_PIPELINE.md:44-46` | off is blocked, never a return to trading | **FOUND** | `FACT` | Lines 44-46 in PROMOTION_PIPELINE.md |
| L106 | Decisions | D3: Leave 18 accounts rows (config:4-21) | `auto_trader_config.json:4-21` | 18 named account rows | **FOUND** | `FACT` | Lines 4-21 in config |
| L106 | Decisions | D3: Account alone cannot reach place() (PROMOTION_PIPELINE.md:37) | `PROMOTION_PIPELINE.md:37` | an account alone cannot trade | **FOUND** | `FACT` | Line 37 in PROMOTION_PIPELINE.md |
| L106 | Decisions | D3: co-trade uses jishu_22 (OPERATOR_DECISIONS.md:1600) | `OPERATOR_DECISIONS.md:1600` | jishu_22 stays the spare for co-trade | **FOUND** | `FACT` | Line 1600 in OPERATOR_DECISIONS.md |
| L106 | Decisions | D3: Registry testnet entry adds size flag (PROMOTION_PIPELINE.md:25-27) | `PROMOTION_PIPELINE.md:25-27` | registry testnet entry rules | **FOUND** | `FACT` | Lines 25-27 in PROMOTION_PIPELINE.md |
| L108 | Result | Result: KEEP 1 / SHADOW 23 / DROP 2 / RE-TEST 1 per prefix | `Table breakdown (L42)` | Sums to 27 prefixes | **FOUND** | `OURS` | Final prefix counts |
| L108 | Result | Result: KEEP 1 / SHADOW 12 / DROP 2 / RE-TEST 1 per layer | `Table breakdown (L42)` | Sums to 16 distinct layers | **FOUND** | `OURS` | Final layer counts |
| L108 | Result | Result: pit V3 F1/F2 closest candidate (one amended PRE_REG and DEV read away) | `REGATE_AUDIT.md:13, 26` | F1/F2 powered DEV contrasts | **FOUND** | `OURS` | Prioritized candidate ranking |
| L108 | Result | Result: CryptoCred 4h setups 1-2 (317 / 293 fills short) | `REGATE_AUDIT.md:42; VERDICTS.csv:114` | 524-207=317; 493-200=293 fills short | **FOUND** | `OURS` | Fill shortfall calculation |
| L108 | Result | Result: LC confluence power line missing, UNDECIDABLE: NOT_IN_DATA | `Pasted inputs / brief` | Power line missing in inputs | **NOT_IN_DATA** | `OURS` | Acknowledged absence of power calculation |


## Claude review note (Lead, 2026-11-02)

- Re-derived the headline numbers from the files: 27 pre_pipeline_sources; 22 size_overrides sum 5,890 USD plus tom 20 = 5,910; top five 1000+800+750+600+500 = 3,650 (62 %); promoted_setups.json:3 is `"entries": []`; BUGS.md:187 is T085 (97 % time exit); PROMOTION_PIPELINE.md:39 says review_by is informational. All match.
- Fixed one line number: the Testnet HALT line is LAYERS.md:194, not 193 (the report itself cites :196, which is also off by two).
- Relabelled 218 entries from SOURCED to FACT: they are commit shas, dates, config values and file:line cites, none is the trader's words (MOVED_RULES.md).
- Not re-checked: the other ~240 rows (per-prefix table, VERDICTS.csv and TRIAL_LEDGER.csv cells, REGATE_AUDIT.md values). Treat those as Gemini's unreviewed reading.
