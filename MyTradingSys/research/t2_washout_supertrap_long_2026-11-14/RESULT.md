# VERDICT T2 (read this first)

**Verdict cell BULL+BASE: FAIL (bars 2 and 5 miss: mean +0.089 R, CI low -0.041; DEV +0.156 but VAL -0.012). Registered prediction REFUTED. Control cell BEAR: passes all 6 pre-registered bars at 12 bp (n 87 episodes, 5,129 trades, gross +0.283 R, fee-net +0.210 R, CI [0.029, 0.414], ex-best-5 +0.062, Holm-adj p 0.018, DEV +0.243 / VAL +0.135).** Read the BEAR pass with care: it was the control, its CI low is only +0.03 R, ex-best-5 is +0.06 R, the mean percent return per trade is slightly negative (-0.08%; the R mean is positive because tight-stop trades give large R, so it only pays if sized by risk), the power gate said BLOCK, and BEAR days are 39% of the calendar but include 2022 (32 of 87 episodes). A pass here needs the blind review and the operator's go before any testnet-forward card.

## Disclosed conventions and caveats (not in PRE_REG text; logged in NOTES.md, audited)
- Missing 1h/4h bars (exchange outages): BTC 4h RSI and the coin's ATR/BB re-seed after a gap; a trade is dropped only if a gap is met before its stop or exit resolves (64 mid-data unresolved signals dropped plus those at data end, clustered on 2021-04-19, 2020-06-27, 2021-04-24, 2021-09-28, 2019-08-14, 2019-11-24). A first version dropped 146 (also stop-resolved ones); both audits flagged it, fixed before stats (Bug log in NOTES.md).
- Placebo cycle matching uses each trade's own trap-day cycle; 21 episodes are mixed-cycle. Holm alpha 0.025 one-sided OURS.
- Audits: independent recompute of 6 dated trades (DOT, DOGE, MANA, LINK, XRP, THETA) plus whole-coin re-simulation of 6 coins (ETH, ALGO, AAVE, DOT, DOGE, MANA, LINK, XRP, THETA): all match to 1e-9. Adversarial audit: no look-ahead (phase_daily close_used equals the prior day's BTC close on 100% of 2,830 days), fee 12 bp charged once, 35 unit tests, 16 of 16 mutants caught.
- Power gate BLOCK recorded in PRE_REG (overruled by the operator's order). History starts 2019-01; 2018 absent.
- Not run by decision: any variant (e.g. BASE only: +0.169 R, CI low -0.014; BULL +0.002 R) after seeing these numbers.

# RESULT: T2 washout Supertrap LONG by cycle state

Seed 1114; 12 bp fee-net R primary; episode = unit of verdict; 13044 trades, 224 episodes.

Regime mix: calendar days BULL 28%, BASE 33%, BEAR 39% | signals BULL 28%, BASE 26%, BEAR 46% | episodes DEV {'BULL': 20, 'BASE': 62, 'BEAR': 60}, VAL {'BULL': 46, 'BASE': 9, 'BEAR': 27}

## Verdict (family m = 2, Holm)
### BULL+BASE: FAIL  (raw p 0.0975, Holm-adj p 0.0975, alpha 0.025 one-sided)
| Bar | Result | Detail |
|---|---|---|
| 1 >=30 episodes | PASS | n=137 |
| 2 mean>0 and CI low>0 | FAIL | mean=0.089 CI=[-0.041,0.215] |
| 3 ex-best-5 mean>0 | PASS | 0.007 |
| 4 beats placebo p97.5, excess>0 | PASS | real=0.089 placebo mean=-0.039 p97.5=0.075 excess=0.128 |
| 5 DEV>0 and VAL>0 | FAIL | DEV n=82 mean=0.156; VAL n=55 mean=-0.012 |
| 6 fresh-8 mean>0 (if >=10 ep) | PASS | n_ep=132 mean=0.132 |

### BEAR: PASS  (raw p 0.0090, Holm-adj p 0.0180, alpha 0.025 one-sided)
| Bar | Result | Detail |
|---|---|---|
| 1 >=30 episodes | PASS | n=87 |
| 2 mean>0 and CI low>0 | PASS | mean=0.210 CI=[0.029,0.414] |
| 3 ex-best-5 mean>0 | PASS | 0.062 |
| 4 beats placebo p97.5, excess>0 | PASS | real=0.210 placebo mean=-0.057 p97.5=0.060 excess=0.267 |
| 5 DEV>0 and VAL>0 | PASS | DEV n=60 mean=0.243; VAL n=27 mean=0.135 |
| 6 fresh-8 mean>0 (if >=10 ep) | PASS | n_ep=83 mean=0.056 |

Registered prediction (BULL+BASE mean > 0 and BEAR mean <= 0): REFUTED
BEAR passed bars 1-6: reported as the tradable result, labelled by itself (m = 2).

## Cells in detail
| Cell | Ep | Trades | Mean R12 | CI | Gross | 6bp | sd trade | sd ep | Mean pct net/trade | Hold h |
|---|---|---|---|---|---|---|---|---|---|---|
| BULL+BASE | 137 | 7915 | 0.089 | [-0.041,0.215] | 0.153 | 0.121 | 1.603 | 0.779 | -0.0013 | 12.6 |
| BEAR | 87 | 5129 | 0.210 | [0.029,0.414] | 0.283 | 0.246 | 1.670 | 0.919 | -0.0008 | 12.6 |

## Each state separately (descriptive)
| State | Ep | Mean R12 | CI |
|---|---|---|---|
| BULL | 66 | 0.002 | [-0.167,0.186] |
| BASE | 71 | 0.169 | [-0.014,0.369] |
| BEAR | 87 | 0.210 | [0.029,0.414] |

## BULL+BASE: cuts
Top-coin removal (SAND, largest summed R): mean after 0.085; not fragile
By year (episodes): 2019: n=14 mean -0.138; 2020: n=18 mean 0.011; 2021: n=24 mean 0.219; 2023: n=26 mean 0.356; 2024: n=23 mean -0.147; 2025: n=25 mean 0.015; 2026: n=7 mean 0.335
By phase label (trades, descriptive): ACCUM-RANGE: n=1529 mean -0.134; CAPITULATION: n=132 mean -0.050; DISTRIBUTION: n=2894 mean -0.069; MARKDOWN: n=569 mean -0.405; MARKUP: n=2736 mean -0.100; RELIEF: n=55 mean 0.866
By symbol (trades): AAVE: n=215 mean 0.071; ADA: n=345 mean -0.266; ALGO: n=286 mean -0.111; ATOM: n=305 mean -0.033; AVAX: n=233 mean -0.073; BCH: n=305 mean -0.183; BNB: n=317 mean -0.175; BTC: n=356 mean -0.217; DOGE: n=325 mean -0.097; DOT: n=247 mean -0.093; ENJ: n=271 mean -0.032; ETC: n=344 mean -0.107; ETH: n=345 mean -0.058; FIL: n=256 mean -0.181; GRT: n=234 mean -0.141; HBAR: n=253 mean -0.189; LINK: n=312 mean -0.166; LTC: n=324 mean -0.219; MANA: n=254 mean 0.008; NEAR: n=206 mean -0.073; SAND: n=239 mean 0.096; SOL: n=245 mean -0.036; THETA: n=281 mean -0.181; TRX: n=245 mean 0.074; UNI: n=229 mean 0.070; XLM: n=304 mean -0.130; XRP: n=352 mean -0.184; XTZ: n=287 mean -0.182

## BEAR: cuts
Top-coin removal (TRX, largest summed R): mean after 0.212; not fragile
By year (episodes): 2019: n=13 mean 0.471; 2020: n=4 mean 0.682; 2021: n=7 mean -0.011; 2022: n=32 mean 0.230; 2023: n=4 mean -0.386; 2025: n=5 mean 0.507; 2026: n=22 mean 0.051
By phase label (trades, descriptive): ACCUM-RANGE: n=1140 mean -0.150; CAPITULATION: n=220 mean 0.245; DISTRIBUTION: n=612 mean 0.118; MARKDOWN: n=2886 mean -0.141; RELIEF: n=271 mean -0.139
By symbol (trades): AAVE: n=162 mean -0.050; ADA: n=218 mean -0.192; ALGO: n=185 mean -0.021; ATOM: n=189 mean -0.202; AVAX: n=183 mean -0.110; BCH: n=162 mean 0.042; BNB: n=216 mean -0.132; BTC: n=212 mean 0.041; DOGE: n=188 mean -0.090; DOT: n=179 mean -0.151; ENJ: n=170 mean -0.222; ETC: n=222 mean -0.111; ETH: n=220 mean -0.096; FIL: n=167 mean -0.107; GRT: n=160 mean -0.065; HBAR: n=160 mean -0.274; LINK: n=197 mean 0.054; LTC: n=216 mean -0.035; MANA: n=164 mean -0.363; NEAR: n=146 mean -0.178; SAND: n=165 mean -0.141; SOL: n=172 mean -0.274; THETA: n=168 mean -0.054; TRX: n=167 mean 0.188; UNI: n=161 mean 0.007; XLM: n=196 mean 0.002; XRP: n=202 mean -0.089; XTZ: n=182 mean -0.092

## Buy-and-hold equal-weight basket (reported, not a gate)
| Year | Basket return (first to last close in year) | Coins |
|---|---|---|
| 2019 | 4.1% | 18 |
| 2020 | 197.9% | 27 |
| 2021 | 1658.4% | 28 |
| 2022 | -76.1% | 28 |
| 2023 | 126.7% | 28 |
| 2024 | 66.0% | 28 |
| 2025 | -48.3% | 28 |
| 2026 | -29.1% | 28 |

| State | Basket mean 24h log return | Mean per-coin cumulative return in state days | Coin-hours | Strategy share of coin-hours in position |
|---|---|---|---|---|
| BULL | 0.00120 | 3.895 | 537424 | 0.0807 |
| BASE | 0.00028 | 1.435 | 521000 | 0.0855 |
| BEAR | -0.00081 | -0.169 | 682247 | 0.1122 |

Notes: bar 4 placebo episodes reuse the real trade's episode structure; Holm alpha 0.025 one-sided matches the 95% two-sided CI (OURS). See NOTES.md for reading choices.
