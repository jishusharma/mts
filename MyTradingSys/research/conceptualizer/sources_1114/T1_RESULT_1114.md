# RESULT t1_markdown_rally_rejection_short (2026-11-14)

**FAIL. Primary sample, VAL: n 2621, gross +0.004 R, fee-net -0.076 R at 12 bp, day-cluster CI [-0.181, +0.028], ex-best-5 -0.136 R, excess over same-phase random shorts +0.007 R (p 0.38). DEV failed the same way (net -0.063 R). Gate: BLOCK.**

`study.py val` was run once on the frozen code (frozen.json hashes checked, code unchanged). PRE_REG.md untouched.

## Context
- Phase: MARKDOWN days only, label from `phase_daily.csv` (lag 1). Idea: 1h push above daily P or R1 that closes back below, HM sell on 30m, close under VWAP; short to next pivot below; stop floor 1.2%, 24 h time exit; 12 bp round trip.
- Phase table sha256 at VAL time: b2cc2314324609fce7c1666912e0b7064e699dde275057456aa4ad311f867365 (audit item 3). Its MARKDOWN day counts equal the DEV-time mix (434 DEV, 198 VAL).

Regime mix: days per phase from the table, DEV / VAL: MARKDOWN 434 / 198, CAPITULATION 52 / 6, RELIEF 154 / 34, ACCUM-RANGE 333 / 156, MARKUP 605 / 321, DISTRIBUTION 248 / 333; total 1826 / 1048. Trades (primary, MARKDOWN, all filters): DEV 5320 on 407 signal days, VAL 2621 on 191 signal days. Filtered signals per phase (primary, VAL, before the one-position and 0.5R rules): MARKDOWN 4662, MARKUP 8472, DISTRIBUTION 8448, ACCUM-RANGE 3784, RELIEF 945, CAPITULATION 105.

## PASS bars vs result (primary sample, 12 bp)
| Bar | DEV | VAL |
|---|---|---|
| net R > 0 | -0.0631 FAIL | -0.0764 FAIL |
| day-cluster CI low > 0 | -0.1409 FAIL | -0.1806 FAIL |
| ex-best-5 > 0 | -0.0950 FAIL | -0.1364 FAIL |
| EXCESS > 0 and placebo p < 0.05 | -0.0103, p 0.728 FAIL | +0.0069, p 0.385 FAIL |
| n >= 150 and >= 40 signal days | 5320 / 407 ok | 2621 / 191 ok |
| Verdict | FAIL | FAIL |

Powered (not UNDERPOWERED): the failure is a flat-to-negative mean, not a lack of trades.

## Primary sample detail (20 fresh coins)
| Split | n | days | win % | break-even win % | gross R | cost R | net R | CI (net) | ex-best-5 | short-and-hold gross / net | stop / target / time |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV | 5320 | 407 | 43.7 | 46.4 | +0.0113 | 0.0744 | -0.0631 | [-0.141, +0.014] | -0.095 | +0.054 / -0.020 | 55 / 40 / 5 % |
| VAL | 2621 | 191 | 40.9 | 44.1 | +0.0039 | 0.0803 | -0.0764 | [-0.181, +0.028] | -0.136 | -0.024 / -0.104 | 58 / 37 / 5 % |

Placebo (1000 same-phase random shorts): DEV real -0.0631 vs placebo -0.0528, EXCESS -0.0103, p 0.728. VAL real -0.0764 vs placebo -0.0833, EXCESS +0.0069, p 0.385.

Short-and-hold baseline (24 h from the same entry bars, no stop/target): gross +0.054 DEV, -0.024 VAL; net negative in both. Being short did not work in VAL either.

## Control (same rule, non-MARKDOWN days), primary
| Split | n | gross R | net R | CI |
|---|---|---|---|---|
| DEV | 17443 | -0.026 | -0.094 | [-0.133, -0.053] |
| VAL | 11724 | +0.034 | -0.044 | [-0.096, +0.008] |

The phase gate adds nothing consistent: VAL control gross (+0.034) is above the MARKDOWN gross (+0.004); DEV MARKDOWN gross is about 0.04 R above control, reversed in VAL.

## Filter ablations (descriptive), primary
| Variant | DEV n / gross / net | VAL n / gross / net |
|---|---|---|
| main (HM + VWAP) | 5320 / +0.011 / -0.063 | 2621 / +0.004 / -0.076 |
| no HM | 6185 / +0.007 / -0.068 | 3058 / -0.015 / -0.094 |
| no VWAP | 6573 / +0.012 / -0.063 | 3329 / +0.007 / -0.074 |
| neither | 9558 / +0.023 / -0.053 | 4997 / +0.019 / -0.062 |

The filters do not help; the unfiltered trigger is the least bad in both halves and is still net negative.

## Maker row (6 bp, not pass-bearing; optimistic upper bound per audit item 2)
| Sample | Split | n | fill ratio | gross | net |
|---|---|---|---|---|---|
| primary | DEV | 5073 | 0.937 | -0.034 | -0.071 |
| primary | VAL | 2482 | 0.930 | -0.042 | -0.082 |

Net negative even at maker fees.

## Secondary (seen 20 coins) and pooled, VAL (information only)
| Sample | n | days | gross | net | CI | ex-best-5 | excess / p |
|---|---|---|---|---|---|---|---|
| secondary | 2671 | 189 | -0.036 | -0.120 | [-0.223, -0.016] | -0.176 | -0.027 / 0.880 |
| pooled | 5292 | 194 | -0.016 | -0.098 | [-0.200, +0.002] | -0.151 | -0.011 / 0.734 |

DEV secondary: n 4977, net -0.041, CI [-0.123, +0.038], excess +0.008 (p 0.33). DEV pooled: n 10297, net -0.052, excess -0.002 (p 0.56). Both FAIL the bar.

## By year, primary
| Year | n | days | gross | net |
|---|---|---|---|---|
| 2019 | 799 | 89 | -0.080 | -0.158 |
| 2020 | 335 | 28 | -0.117 | -0.188 |
| 2021 | 980 | 65 | +0.038 | -0.016 |
| 2022 | 2651 | 184 | +0.048 | -0.029 |
| 2023 | 555 | 41 | -0.001 | -0.097 |
| 2024 (VAL) | 295 | 23 | -0.247 | -0.332 |
| 2025 (VAL) | 1123 | 81 | +0.028 | -0.048 |
| 2026 (VAL) | 1203 | 87 | +0.043 | -0.041 |

No year is net positive. Only 2021, 2022, 2025, 2026 have positive gross, all below fee.

## By cycle state, primary
| Cycle | Split | n | days | gross | net |
|---|---|---|---|---|---|
| BEAR | DEV | 5320 | 407 | +0.011 | -0.063 |
| BEAR | VAL | 2349 | 173 | -0.006 | -0.088 |
| BULL | VAL | 272 | 18 | +0.091 | +0.020 |

DEV has no BULL-cycle MARKDOWN days. The only positive cell (VAL BULL, 18 days) is far below any power bar and is not a finding.

## By symbol, primary VAL (net R, n)
Positive net: NEO +0.087 (138), HBAR +0.075 (151), THETA +0.048 (137), MANA +0.005 (146). All other 16 negative; worst ZIL -0.246, XTZ -0.232, ICX -0.199, QTUM -0.176, IOTA -0.175, ONT -0.165, AAVE -0.147. 4 of 20 coins net positive, none distinguishable from noise over about 100 days each. Full tables: `val_by_symbol.csv`, `val_by_year.csv`, `val_by_cycle.csv`; trades `val_trades.csv`; summary `val_summary.txt`; `val_tables.json`.

## Coins used / dropped
- Primary: all 20 (EOS NEO IOTA ZEC DASH ZIL VET BAT ICX QTUM ONT ENJ MANA SAND THETA XTZ HBAR AAVE GRT CHZ). Dropped for under 730 days or missing: none.
- EOS data ends 2025-05-26, so its VAL is partial (29 trades).
- Secondary: 20 coins in `binance_spot`; TRX has few VAL trades (63).
- 8 primary coins (AAVE ENJ GRT HBAR MANA SAND THETA XTZ) overlap nk5-nyasia (different rule), disclosed in PRE_REG.

## Gate output (prereg_gate.py, run on DEV before freeze)
```
n 434 sd 1.2103 m 249 z_holm 3.718 MDE 0.265 R + cost 0.0744 = 0.339 vs max plausible gross 0.3; n needed 598
BLOCK: do not freeze (write BLOCKED.md with these numbers)
```
BLOCK. The run continued per the PRE_REG (operator order); no bar was lowered. In VAL, sd is 1.275 and cost 0.080 R, so the BLOCK holds a fortiori.

## Data limits
- Phase is BTC-only; all coins share one tape, so the effective n is days (191 VAL signal days, 407 DEV), not trades. Trades within a day are correlated; the CI is bootstrapped over days.
- MARKDOWN is 3 episodes in this data (2019, 2022, 2025-26); a pass would not have been a law.
- No funding, no slippage; spot-priced bars. With 57% of trades stopped out, slippage would only worsen the net.
- A day with any missing 15m bar gives no pivot the next day (audit item 4); 14-23 gaps per coin.
- The freeze does not hash the phase table or caches; the table hash is recorded above.

## Independent recomputations (INDEPENDENT_RECOMPUTE.md)
Three DEV EOS trades (stop 2019-01-04, target 2019-01-03, time exit 2019-10-12) recomputed from raw 15m bars and FORMULAS s1/s4/s5/s12 without reading study code: 0 diffs on entry, level, D, target, exit type, gross, fee, net and hold24 R; day labels MARKDOWN/BEAR match. Limits: all three are level P; ATR was never the binding term.

## Adversarial audit (ADVERSARIAL_AUDIT.md): no blocking issue
Poked with truncated and randomly perturbed future bars (0 differences in causal arrays), re-simulated all 5320 DEV primary trades independently (5320 match, 9 rounding flags on 4e-5-priced coins), 0 position overlaps, 250-trade filter sample 0 mismatches, freeze check and PHASE_LAG/STUDY_BUG test failures confirmed. Five low items, none edited (code frozen), disclosed here:
1. Placebo pool uses the ENTRY bar's UTC day while trades are gated on the SIGNAL bar's day: differs only for 23:00 UTC signals (1/24).
2. Maker row is optimistic (a target touched before the fill inside the bar is credited).
3. The freeze does not hash the phase table or caches (hash recorded above).
4. Days with a missing 15m bar yield no signals the next day.
5. Cost is on entry notional only; sub-basis-point effect on gap stops.
Nothing found or fixed changed a number.

## Deviations (DEVIATIONS.md)
Items 1-9 are readings of text the spec leaves open, fixed before VAL (exit-bar convention, one-position timing, DEV cut at the split, bucket completeness, warm-up, phase label as written, placebo pool, maker row, statistics definitions). Item 10 is CI wiring (extra_tests.tsv and look-ahead allowlists, Context-lint allowlist instead of editing the frozen spec). Item 11 is the gate BLOCK. No frozen parameter was changed.

## Next variant most worth testing (FAIL)
Unfiltered trigger with the 1.2% floor stop, but a trailing exit (under the 1h EMA(20), no pivot target) on MARKDOWN days. Reason: the entry has gross about +0.02 R in both halves (neither-filter row) and short-and-hold gross was +0.15 R in DEV with no stop, so the loss sits in the 57% stop-outs and the pivot target, not the entry; a stop-and-target rule cannot pay 12 bp from a +0.02 R entry. Caveat: this reading uses VAL as well as DEV, so it needs its own PRE_REG and fresh coins; the honest alternative is to drop the rally-rejection family.
