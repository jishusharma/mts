# GPT Fable economics recheck — 2026-10-16

**FIX-FIRST**

Independent recomputation from committed inputs. `recompute.py.txt` was written and run before opening `FABLE_RUNS_AUDIT.md`; the script records the input-based values and reproduces the arithmetic. No backtest, holdout, or production file was read or changed.

## Scope and method

- Audit claims: [FABLE_RUNS_AUDIT.md](MyTradingSys/research/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md:38), sections 1.2, 1.4, 1.5, 2.2 and 3.2.
- Inputs: [RESULT.md](MyTradingSys/research/gross_effect_screen_2026-10-15/RESULT.md:8), [PRE_REG.md](MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md:73), [decay.csv](MyTradingSys/research/gross_effect_screen_2026-10-15/decay.csv:1), [power_mde.py](MyTradingSys/backtest/power_mde.py:19), and [promote.py](MyTradingSys/backtest/layers/promotion/promote.py:185). Raw quote checks used `raw_transcripts_canonical/yRvMW6lgN1o_raw.txt`, `k0zm5NYn0IQ_raw.txt`, `hQ8sOq67x5o_raw.txt`; catalogue cross references were read only.
- Reproduction command: `python MyTradingSys/research/layer_lab/gpt-fable-economics-recheck/recompute.py.txt` (stdlib only).

## Claim audit

| Claim (audit file:line) | Inputs (file:line) | GPT value | Independent value | Result |
|---|---|---:|---:|---|
| Flow flag rate: 2.8%, 40 in 912 DEV days (1.2, 40–41) | RESULT.md:45; PRE_REG.md:77 | 2.8%; 40 / 912 | 40 / 1,440 eligible encounters = 2.7778%; 40 / 912 = 0.04386 per DEV day | MATCH |
| T-arm per-encounter SD: 0.1304 × √40 = 0.82% (1.2, 42–43) | RESULT.md:8,12; PRE_REG.md:74–76 | 0.82% | 0.1304 × √40 = 0.82472% | MATCH |
| At n=40, pass threshold 0.14 + 2 × 0.13 = 0.40% (1.2, 44) | RESULT.md:8; PRE_REG.md:73–78 | 0.40% gross mean | 0.14 + 2 × 0.1304 = 0.4008% (rounds 0.40%) | MATCH |
| If true mean equals cost, pass chance about 2% (1.2, 44–45) | PRE_REG.md:78; RESULT.md:8 | about 2% | P(Z>2) = 2.275% using the stated one-sided pass threshold | MATCH |
| At n=200, SE 0.058%; 80%-power mean 0.30%; 0.37 SD (1.2, 46–47) | RESULT.md:8; PRE_REG.md:76–78 | 0.058%; 0.30%; 0.37 SD | SD 0.82472%; SE=0.05832%; PRE_REG 2.8×SE gives gross threshold 0.30338%; 0.30338/0.82472=0.36786 SD | MATCH |
| C, ALL decay table, d=1: h=5 +0.019 (SE .011), h=15 +.015 (.016), h=60 −.007 (.025), h=240 −.076 (.052) (1.4, 62–64) | decay.csv:188–193 | As shown | +.01857 (.01142), +.01493 (.01636), −.00709 (.02458), −.07639 (.05184) | MATCH |
| C, ALL decay table, d=5: h=5 −.002 (.010), h=15 −.009 (.013), h=60 −.030 (.023), h=240 −.103 (.051), gross t≈−2.0 (1.4, 65) | decay.csv:200–205 | As shown; −.103/.051≈−2.0 | −.00168 (.01010), −.00897 (.01303), −.02966 (.02298), −.10322 (.05059); last gross/SE=−2.0403 | MATCH |
| Fresh extreme reversal about 2 bp, then continuation about 10 bp; follow-the-extreme is 4 bp below 14 bp cost (1.4, 67–70) | decay.csv:188,193,200,205; PRE_REG.md:32 | ≈+2 bp; ≈−10 bp; ≈4 bp short | +1.857 bp at d1/h5; −10.322 bp at d5/h240; 14−10.322=3.678 bp | MATCH |
| C-arm encounter SD at h=60: .0246×√1,439=.93%; at h=240: .0518×√1,439=1.97% (1.5, 73) | decay.csv:191,193 | .93%; 1.97% | .02458×√1439=.9327%; .05184×√1439=1.9666% | MATCH |
| Required mean/SD ratios .15 at 1h and .07 at 4h (1.5, 74) | PRE_REG.md:32; decay.csv:191,193 | .15; .07 | .14/.9327=.1501; .14/1.9666=.0712 | MATCH |
| Daily-hold ratio about .05 (1.5, 74) | decay.csv grid ends at h=240 (four hours): decay.csv:1 | ≈.05 | No daily horizon or daily-hold SD in the cited input grid | NOT_IN_DATA |
| Fixed h=60 continuity rationale (1.5, 75) | PRE_REG.md:68 | 60 minutes, continuity with study.py prior horizon | PRE_REG says primary h=60 and cites continuity with study.py:25 | MATCH |
| TOM_ON_BTC stop floor >=.40% (1.5, 76) | No TOM_ON_BTC input in this card’s permitted source set | .40% floor | Could not independently verify from the committed inputs read for this card | NOT_IN_DATA |
| Promotion gate: net_r>0, ci_low>0, n_trades>=30 (2.2, 98–99) | promote.py:36,185–192 | 30-trade floor; positive fee-net result and CI low | Exact gate reproduced: `MIN_TRADES=30`; net_r>0; ci_low>0 | MATCH |
| Ten 95% tests yield 1−.975^10=22%, about 1 in 5 (2.2, 100–102) | promote.py:194–211; standard arithmetic | 22% | 22.3670% under independence; rounds to 22%, about 1 in 5. `promote.py` verifies ledger count matches variants but does not adjust CI level | MATCH |
| “30 trades see only a very large effect” (2.2, 107) | power_mde.py:19–50; CATALOGUE_AUDIT.md:64; raw hQ8sOq67x5o_raw.txt | Qualitative claim; no numerical MDE printed there | At p=.35, RR=4, n=30, and cost_R=0 (stop size unavailable in committed inputs), the function’s MDE is 1.2198 R. Cost-adjusted MDE cannot be independently specified without stop size | MATCH (directional); adjusted value NOT_IN_DATA |
| TOM-3: “risk of 12 ticks”; 6,768 target; stop 3 points; cost 3.2R maker 2.0R (3.2, 139–142) | raw yRvMW6lgN1o: transcript contains “risk of 12 ticks” and “6,768”; CATALOGUE_AUDIT.md:34–35; PRE_REG.md:32–33 | 3 pts / 6768 = .044%; 3.2R taker, 2.0R maker | Conditional on ES tick=.25: 12×.25=3 pts; stop=.044326%; .14/.044326=3.1584R; .09/.044326=2.0304R | MATCH conditional; ES tick=.25 is NOT_IN_DATA in the checked quote/source set |
| TOM-1: “stop-loss of 20 points”; DAX level 15,000–24,000; .08–.13%; cost 1.1–1.7R (3.2, 143) | raw k0zm5NYn0IQ: transcript states “stop-loss of 20 points in the DAX”; price band not found in that transcript | 20 points; .08–.13%; 1.1–1.7R | For assumed 15k–24k price band, stop=.08333–.13333%; .14% cost=1.05–1.68R, rounds 1.1–1.7R | Arithmetic MATCH; price-band premise NOT_IN_DATA in cited raw quote |
| T-3: 35% wins and 4R winners imply +.75R expectancy (3.2, 144–146) | raw hQ8sOq67x5o: 35% win rate and reward four times risk; CATALOGUE_AUDIT.md:64 | +.75R | .35×4−.65×1=.75R | MATCH |
| .14/.75=.19% stop threshold; slippage excluded (3.2, 146–147) | PRE_REG.md:32; preceding +.75R | .19% | .14/.75=.18667%, rounds .19%; this does not include any additional slippage beyond the 14bp cost already defined | MATCH |

## “Loses on Binance by construction” sentence

**OVERSTATED.** Within the table, the two priced intraday Tom examples exceed the reused +0.75R swing expectancy: TOM-3 costs 3.16R (conditional on the unverified ES .25 tick), and TOM-1 costs 1.05–1.68R for the assumed price band. The table has no priced Fabio intraday row, so it cannot support “every … Tom/Fabio row.” The +0.75R is also a sourced swing statistic applied across different setups as an explicit conditional assumption, not a demonstrated Tom/Fabio expectancy for those intraday rows. The numerical proposition for the two listed Tom rows holds under those assumptions; the universal sentence is broader than its table evidence.

## Verdict and follow-ups

**FIX-FIRST** — arithmetic is sound for the priced examples, but clarify the universal “every Tom/Fabio” sentence and label the ES tick and DAX price-band assumptions as assumptions (or source them). The section’s cost-before-G3 recommendation remains supported for the two listed Tom rows. There is no recommendation-changing numerical mismatch, so no follow-up card was retained.

Recompute script: [recompute.py.txt](MyTradingSys/research/layer_lab/gpt-fable-economics-recheck/recompute.py.txt).
