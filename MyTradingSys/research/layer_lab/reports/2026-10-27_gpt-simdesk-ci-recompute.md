# GPT sim desk CI recomputation — Krown

**FIX-FIRST** — mean and sample-SD MDE match after rounding; the requested t interval does not match the published band, and the band cannot be independently reproduced from this cumulative curve alone.

## What I checked

- Read the complete result artifact [desk-krown-634f1a37.json](../../sim_desk/results/desk-krown-634f1a37.json), especially its study declaration (lines 6–25), reported verdict and KPIs (26–57), and cumulative curve (59–105).
- Before opening `desk.py`, recovered trade R by first-differencing the 35 four-decimal cumulative R values, retaining the first cumulative value as trade 1. Command: Python `json` + `statistics` calculation over `examples[0].r`. The differenced values sum to 9.7458 R, mean 0.2784514 R, sample SD 1.350951 R, SE 0.228352 R.
- Compared the mean, conventional two-sided 95% one-sample Student t interval (df=34; t*=2.0322), and conventional normal-approximation MDE for 80% power, `(1.96 + 0.8416) * s / sqrt(n)`, against the artifact. T interval from the rounded curve is [-0.1856, +0.7425] R; MDE is +0.6409 R.
- Then read `desk.py` and its cited interval/MDE implementation, `MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py`. The desk uses a seeded day-cluster bootstrap interval, not a Student t interval. Its bootstrap requires per-trade day assignments and the full calendar-day set, absent from the artifact. The curve therefore cannot verify the published bootstrap endpoints.
- Backtest readiness: this artifact explicitly labels the run exploratory and NO-RECALL-CLEARANCE (JSON line 10), so it is not a ready/pre-registered backtest. PRE_REG_TEMPLATE items 1–12 are consequently not established by this artifact; specifically source ledger/recall (1–3), proof inputs/profile/cost/fills/exits/null (4–9), prospective power/holdout/trial accounting/stratification (10–12) lack supporting evidence here. No market data or post-DEV data was read; no backtest was run.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/research/sim_desk/results/desk-krown-634f1a37.json:47-48`; `MyTradingSys/research/sim_desk/desk.py:60-72`; `MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py:153-170` | The requested claim calls [-0.161, +0.750] a 95% t-range, but that is not the t interval derivable from the displayed curve. The desk implementation identifies its interval as a day-bootstrap CI. | Independent first differences yield mean +0.278451 and SD 1.350951; t(34) interval [-0.1856, +0.7425], not [-0.161, +0.750]. Code uses `Boot.ci` over days (seeded resampling), so the result's endpoints may be valid bootstrap outputs, but cannot be independently checked from rounded cumulative R alone. The artifact lacks trade days and `all_days`. | Label the displayed interval as day-bootstrap, not t; publish/recover the exact net-trade/day inputs and bootstrap settings for reproducibility. Do not substitute the t interval for the desk's intended estimator. |
| LOW | `MyTradingSys/research/sim_desk/results/desk-krown-634f1a37.json:43-44, 55-56`; `MyTradingSys/research/sim_desk/desk.py:99-104, 304-312`; `MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py:193-196` | The +0.64 R figure matches the sample-SD 80%-power MDE calculation, but is not a t interval bound and is distinct from the desk's multi-try luck adjustment. | From curve: `(1.96 + 0.8416)*1.350951/sqrt(35)=0.6409 R`. `ladder_run.cell` uses this same formula (`Z975 + Z80`); desk `luck()` uses `sd*sqrt(2 ln tries)/sqrt(n)` and yields zero for one try. | Name it “sample-SD MDE (80% power, normal approximation)” and keep it separate from any “best-of-tries luck” number. |
| LOW | `MyTradingSys/research/sim_desk/results/desk-krown-634f1a37.json:6, 10, 24-25`; `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:1-3, 1-12` | The exploratory run is explicitly marked NO-RECALL-CLEARANCE and does not carry evidence for the 12 readiness items; the performance numbers must not be read as cleared source fit or a pre-registered study. | Artifact's own study declaration says exploratory/NO-RECALL-CLEARANCE. The result artifact contains no cited trade ledger, timestamps, source frames, or itemized pre-registration evidence. | Preserve the exploratory and no-recall labels; complete and evidence the readiness template in a separately scoped study before making source-fit or edge claims. |

## Follow-up cards

None. No HIGH findings.

## Verdict

**FIX-FIRST** — mean MATCH (+0.278 R); conventional t interval MISMATCH (-0.186..+0.743 R vs published -0.161..+0.750 R), though the desk's actual interval is a day-bootstrap whose inputs are NOT_IN_DATA in this artifact; sample-SD MDE MATCH (+0.641 R vs +0.64 R). The desk's procedure matches its code description, but the report label/reproducibility gap should be fixed before treating the endpoints as independently recomputed.
