# RESCORE: fabio_of 09-30 with plan stops (card fee-stop-rescore-fabio-habib-1106)

**Verdict: cost killed the old result, and the plan stop makes it worse.** Gross R is about 0 to +0.15 either way; the plan stop (1 tick beyond the trigger extreme, median 5-9 bp of price) is about half the retired 0.15 % floor, so the 10 bp taker round trip costs more than 1 R per trade. 0 of 16 variants per cell are net positive OOS with n >= 30 under either stop.

Method: same 90 days (2026-07-01..09-28, OOS = last 28 days), same events, management and true-flow grid (16 variants per cell: tf 5/15 x p99/p99.9 x k 1.5/2.5 x plain/trail) as FABIO_OF_REPORT.md, re-run with current `fees.py` Deribit costs (taker 5 bp, maker 0; the old report used legacy fees). OLD = 0.15 % minimum stop (OURS, retired by d-stops-follow-trade-1106). PLAN = the spec's stop 1 tick beyond the trigger extreme or broken level (OURS where inferred; the level stop is the spec's, the 1-tick buffer is OURS). Skip rule: stop tighter than 0.02 % of price is untradeable (OURS, kept). Entry mkt = regime A (taker in, taker stops, maker target); limit = regime B (maker in at the level, fades only; imb_break has no limit cell with a distinct result). Driver: `rescore_fabio.py` (reuses the archived driver code); R maths: `rescore.py` / `test_rescore.py`.

Each cell pools the 16 variants (they share events), so n per variant = pooled n / 16. Gross and net R are the mean over pooled trades. All numbers are candidates for testnet at most, never forecasts.

| setup | scope | entry | stop | n/variant (all 90d) | gross R | net R | n/variant OOS | OOS gross R | OOS net R | median stop bp | variants net>0 (OOS n>=30) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| balance_fade | all | mkt | OLD 0.15 % floor | 2567 | +0.011 | -0.561 | 764 | +0.030 | -0.545 | 15.0 | 0 of 16 |
| balance_fade | all | mkt | PLAN tight | 2306 | +0.079 | -1.423 | 690 | +0.107 | -1.381 | 7.3 | 0 of 16 |
| balance_fade | all | limit | OLD 0.15 % floor | 1734 | -0.064 | -0.339 | 500 | -0.079 | -0.357 | 15.0 | 0 of 16 |
| balance_fade | all | limit | PLAN tight | 775 | -0.099 | -1.031 | 217 | +0.029 | -0.897 | 5.3 | 0 of 16 |
| balance_fade | ny | mkt | OLD 0.15 % floor | 724 | +0.012 | -0.548 | 225 | +0.026 | -0.541 | 15.0 | 0 of 16 |
| balance_fade | ny | mkt | PLAN tight | 655 | +0.037 | -1.324 | 204 | +0.155 | -1.163 | 8.4 | 0 of 16 |
| balance_fade | ny | limit | OLD 0.15 % floor | 506 | -0.026 | -0.299 | 147 | -0.014 | -0.284 | 15.0 | 0 of 16 |
| balance_fade | ny | limit | PLAN tight | 238 | -0.065 | -0.952 | 68 | -0.129 | -1.058 | 5.6 | 0 of 16 |
| imb_break | all | mkt | OLD 0.15 % floor | 764 | +0.045 | -0.413 | 227 | +0.018 | -0.448 | 17.2 | 0 of 16 |
| imb_break | all | mkt | PLAN tight | 794 | +0.027 | -0.758 | 232 | -0.022 | -0.784 | 17.0 | 0 of 16 |
| imb_break | ny | mkt | OLD 0.15 % floor | 284 | +0.090 | -0.322 | 77 | -0.084 | -0.520 | 21.4 | 0 of 16 |
| imb_break | ny | mkt | PLAN tight | 290 | +0.085 | -0.549 | 77 | -0.097 | -0.693 | 21.2 | 0 of 16 |

Reading: gross R barely moves between stops (OLD +0.01..+0.09, PLAN +0.03..+0.09 for market entries), so the stop did not create or destroy a gross edge. Net R falls from about -0.55 (OLD) to -1.4 (PLAN) for balance fades at market because fees scale with 1 / stop width. Maker-in limit fades cost less (-0.34 vs -1.03) but the stop exit is still taker. No setup is net positive, so there is no testnet watch card from this study (Next: END).
Checks: OLD market balance_fade OOS net -0.545 is in line with the old report's floor rows (-0.39 to -0.58) given the fee correction (maker 0 not 2 bp, taker 5 bp).
