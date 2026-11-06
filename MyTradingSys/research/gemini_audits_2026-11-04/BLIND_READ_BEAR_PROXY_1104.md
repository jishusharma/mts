# Blind read: bear_proxy_context_tuning_2026-11-04

Method: CSVs (A_dev, A_val, A_count, B_dev, B_val, B_count) read and recomputed first; RESULT.md read only after. The study has no raw trade file, so "recompute" means: (a) internal arithmetic of every CSV row (net = gross - 0.14, t = net/se, CI = net +/- 1.96 se, p from normal t within 0.02), (b) re-derive the picks (best in-gate net, n >= 30, >= 20 days, baseline excluded) and counts from the rows, (c) count CSV vs result CSV agreement.

## Row checks

| Check | Result |
|---|---|
| A_dev in-gate rows (76), out rows (120); A_val in/out (4/4); B_dev (20); B_val (8): cost 0.14, t, p, CI arithmetic | 0 bad of 232 |
| A_count in_n/setting equals A_dev; B_count n/fakeout_rate equals B_dev | identical |
| Rows with n >= 30 and >= 20 days (Part A DEV) | 69 of 168; 0 with CI lo > 0 (RESULT: 69 of 168, 0) |
| Regime mix (regime_mix_dev.txt): 73/222/65/0 of 360 = 20/62/18/0 % | matches; 57 proxy-on weeks matches |

## Per-number table (RESULT.md vs recomputed)

| Number | RESULT.md | Recomputed | |
|---|---|---|---|
| A ALL pick | rsi21<=35 1d SMA on, n 238/88 d, +0.003 [-0.281,+0.287] BLOCK | same | FOUND |
| A ALL baseline | n 823, -0.166 [-0.272,-0.059] | same | FOUND |
| A ALL VAL | n 46/17 d, -0.463 [-1.147,+0.221] | same | FOUND |
| A bull/mature pick / VAL | n 60/27 d -0.127 [-0.650,+0.397]; VAL n 6 -0.113 [-0.327,+0.100] | same | FOUND |
| A range/fresh pick / baseline / VAL | n 200/88 d -0.140 [-0.419,+0.138]; base n 128 -0.230 [-0.632,+0.171]; VAL n 77/39 d -0.117 [-0.306,+0.072] | same | FOUND |
| A range/mature pick / baseline / VAL | n 122/47 d +0.250 [-0.017,+0.518]; base n 695 -0.154 [-0.255,-0.053]; VAL n 5/3 d -2.770 [-5.595,+0.054] | same | FOUND |
| bull/fresh, bear/fresh, bear/mature: no setting n >= 30 | none | none | FOUND |
| Gate hit rate ALL baseline | 0.376 over 109 gated weeks vs 0.423 over 584 | 0.3761 / 109 / 0.4229 / 584 | FOUND |
| Gate hit rate picked ALL | 0.21 over 28 weeks vs 0.42 | 0.2143 / 28 / 0.4229 | FOUND |
| Gate hit rate range/mature | 0.394 vs 0.449 | 0.3936 vs 0.4489 | FOUND |
| Inside vs outside gate ALL | -0.166 vs -0.194, diff +0.028, t 0.48 | -0.1656 / -0.1939 / +0.0282 / 0.476 | FOUND |
| Inside vs outside range/mature, range/fresh | +0.022 t 0.36; -0.017 t -0.08 | 0.0222 / 0.357; -0.0175 / -0.083 | FOUND |
| B 15m none/confirm1/htf_rsi/volume/retest DEV net | -0.139 / -0.198 / -0.207 / -0.110 / -0.172 | -0.1394 / -0.1984 / -0.2066 / -0.1098 / -0.1717 | FOUND |
| B 15m volume DEV n, CI, fake-out | 3943, [-0.164,-0.055], 45.6 -> 44.1 % | 3943, [-0.1642,-0.0553], 45.60 -> 44.13 % | FOUND |
| B 15m VAL | fake-out 49.2 -> 48.6; net -0.203 -> -0.183 [-0.312,-0.053], n 642; raw p 0.006 | 49.17 -> 48.60; -0.2029 -> -0.1828 [-0.312,-0.053]; 1751/642; p 0.00568 | FOUND |
| B 1h DEV / VAL | -0.244 -> -0.223 [-0.420,-0.025] n 1097; fake-out 49.4 -> 49.8; VAL -0.295 -> -0.384 [-0.831,+0.062] n 169, 52.0 -> 53.3 | same | FOUND |
| B 4h DEV / VAL | -0.476 -> +0.203 [-0.611,+1.018] n 170; fake-out 46.6 -> 51.2; VAL +0.090 -> +0.747 [-0.283,+1.777] n 27, 39.0 -> 18.5 | same | FOUND |
| B 1d DEV / VAL | -1.123 -> -0.921 [-3.369,+1.527] n 137; 50.0 -> 47.4; VAL -3.213 -> -3.301 [-7.397,+0.796] n 18, 65.2 -> 72.2 | same | FOUND |
| B DEV: 20 of 20 cells negative or zero-spanning, none CI > 0; 15m is the only PASS TF | as stated | 20 cells, CI hi < 0 or lo < 0 < hi; only 15m rows PASS (5) | FOUND |
| Holm 15m 0.063; all verdicts | FAIL (0.063); others underpowered | verdicts_val.json: 0.0625, FAIL; rest underpowered | FOUND |
| Trials 188 DEV | 188 | 168 A rows + 20 B rows | FOUND |
| Trials 11 VALIDATION / Holm m = 11 | 11 | 7 A cells + 4 B TFs = 11 family; only 8 CSV rows (4 A + 4 B picks) carry data | FOUND (family size not recomputable from rows) |

Counts: FOUND 22, DIFF 0, not verifiable from files: 1 (the 18-test pytest claim, not run here).

Note: the claim "only threshold-45 settings pass the count gate (ALL cell)" in Honest limits is true of the 12 PASS rows in A_dev only in the sense that all PASS rows contain "45" in the setting; the headline verdict does not depend on it.

VERDICT: MATCH
