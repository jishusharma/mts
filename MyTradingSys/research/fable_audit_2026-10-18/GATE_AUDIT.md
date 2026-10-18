# Gate audit: prereg_gate.py, the Kurisko 0-of-8 freeze, and promote.py G4 (Fable run 1, 2026-10-18)

Auditor: Fable 5.1, worktree `peaceful-elion-cbb889`, branch `claude/fable-run-1-brief-f85eed`, base origin/fast-track be2d82f5.
Brief: `system/fable_run_1_brief.md`. Reads only: no backtest, no VALIDATION or HOLDOUT bar, no production code changed, no count re-run.
Every number is RE-DERIVED (arithmetic shown) or QUOTED (file:line). Parameters are labelled SOURCED or OURS.

## Verdict table

| Q | Verdict | One-line reason | Where |
|---|---|---|---|
| 1 Unit mix | **WRONG as labelled, BLOCK stands** | `--sd 1` makes MDE "1 SD" and adds it to a cost in R; 1 SD of per-event R is 1.4-4.5 R on this data, never 1. But 4 of 8 rows fail on cost alone and the other 4 would need sd <= 0.21 R to pass, so no realistic sd flips any row. | `prereg_gate.py:23,39`; `PRE_REG.md:33`; sd cross-check `VERDICTS.csv:57` |
| 2 Cost aggregation | **WRONG aggregator, lenient direction, BLOCK stands** | Mean fee-net R subtracts mean(14/stop_i), not 14/median(stop). The share of events with stop < 14 bp alone bounds mean cost at >= 0.31 R (row 5) and >= 0.38 R (row 6): above the 0.30 R ceiling with no distribution assumption. A min-stop filter is a new counted trial (PRE_REG s7 already says so). | `count_events.py:101`; `PRE_REG.md:22-31,44` |
| 3 Statistics | **CONFIRMED (conservative); one usage inconsistency** | z_holm = Phi^-1(1-0.05/(2m)) in prereg_gate equals promote's Phi^-1(1-0.025/m) for every m (z = 3.227 at m = 40 in both). n = event-days with a per-event sd is the rho = 1 upper bound on the clustered SE; correct direction for a gate. Inconsistency: m is study-local (8) here, repo-wide (42/62, 58) in the pit and bb-top gates. | `prereg_gate.py:18-23`; `promote.py:57-66`; `PRE_REG.md:33`; `pit_levels_2026-10-16/BLOCKED.md:7` |
| 4 Freeze overreach | **WRONG wording, no registry damage yet** | BLOCKED.md title says "no Quad Rotation cell can be frozen"; only 1m/5m x {stoch, RSI} x {long, short} with one stop definition and taker cost were counted. The VERDICTS.csv row is all UNPARSED (verdict, kill_scope), so `verdicts.py check` exits 0 today, but a FAIL added without a kill-scope sentence would block Kurisko on 15m/1h repo-wide. Kill-scope sentence given below. | `BLOCKED.md:1`; `VERDICTS.csv:39`; `verdicts.py:22-24,157-165,379` |
| 5 Count correctness | **CONFIRMED with one caveat** | Resample bucket drop has zero effect on DEV (912 x 1440 = 1,313,280 1m bars, no gap). The gate-deciding numbers are the 5m stochastic median stops (rows 5-6): a 2x wider stop definition (>= 46.7 bp) would lift the cost under 0.30 R. Event counts most sensitive to a rule: RSI rows (3-19 events, driven by the RSI-60 band) and the short rows (exist only by the NO-SOURCE mirror). Hand check below. | `counts/run_meta.txt:2`; `quad_rotation.py:33-47,71-93`; `FORMULAS.md` 24.4 |
| 6 Trial-ledger logic | **WRONG: KQ-T01 is written to no ledger any gate reads** | `TRIAL_LEDGER.csv` has 0 Kurisko rows (20 rows: wlow 8, wavetrend 9, krown 2 + header); the Kurisko entry sits only in `gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv:9`, which neither promote G5 nor `verdicts.py count` reads; the VERDICTS.csv row has split_read UNPARSED, so `count --split DEV` skips it. No double count found (wavetrend W01-W09 appear in TRIAL_LEDGER and VERDICTS, but each m reads one file). | `TRIAL_LEDGER.csv`; `EXPOSURE_LEDGER.csv:9`; `verdicts.py:401-409`; `promote.py:267-284` |

## Q1. Unit mix: the arithmetic

QUOTED `prereg_gate.py:23`: MDE = (z_holm + 0.84) * sd / sqrt(n); `:39`: ok = MDE + cost <= max_gross (0.30 R, OURS). QUOTED `PRE_REG.md:33`: every row run with `--sd 1` ("SD units, OURS, since no outcome is read").

RE-DERIVED, m = 8: z_holm = Phi^-1(1 - 0.05/16) = Phi^-1(0.996875) = 2.734; z + 0.84 = 3.574.

| Row | event-days | MDE at sd = 1 (3.574/sqrt(days)) | cost R = 14/median stop | sd needed to pass = (0.30 - cost)/MDE | PRE_REG value |
|---|---|---|---|---|---|
| 1 1m stoch long | 912 | 0.118 | 14/6.671 = 2.099 | none (cost > 0.30) | 0.118 / 2.099 matches |
| 2 1m stoch short | 912 | 0.118 | 14/5.969 = 2.345 | none | matches |
| 3 1m rsi long | 18 | 0.842 | 14/114.28 = 0.123 | 0.211 | matches |
| 4 1m rsi short | 14 | 0.955 | 14/66.97 = 0.209 | 0.095 | matches |
| 5 5m stoch long | 678 | 0.137 | 14/23.43 = 0.597 | none | matches |
| 6 5m stoch short | 742 | 0.131 | 14/17.77 = 0.788 | none | matches |
| 7 5m rsi long | 3 | 2.064 | 14/452.2 = 0.031 | 0.130 | matches |
| 8 5m rsi short | 4 | 1.787 | 14/169.3 = 0.083 | 0.122 | matches |

All eight PRE_REG numbers reproduce. The gate's exit 1 is driven by `cost > max_gross` on rows 1, 2, 5, 6 (the script prints `n needed inf` there, `prereg_gate.py:38`) and by MDE >= 0.84 on rows 3, 4, 7, 8.

**Is "MDE(SD) + cost(R) <= 0.30 R" valid?** Only if 1 SD of per-event R equals 1 R. It does not; `--sd 1` is the favourable end, and the gate's docstring (`prereg_gate.py:3`) asks for "sd of R". Realistic sd of R per event (OURS, two outcome families):
- Time-exit gross return at a 12-bar 5m horizon, RE-DERIVED from a DEV read already on file: `VERDICTS.csv:57` W01 5m, n = 3,893, se = 0.0108 %, so sd = 0.0108 x sqrt(3893) = 0.674 % = 67 bp (W02: 62 bp, W03: 65 bp). Per R: 67/23.43 = **2.9 R** (row 5), 67/17.77 = **3.8 R** (row 6). Scaled to 1m (67/sqrt(5) = 30 bp over 12 1m bars): 30/6.67 = **4.5 R** (row 1).
- Two-point stop/target outcome (-1 R or +k R, zero mean): sd = sqrt(p k^2 + (1-p)) with p = 1/(1+k): k = 1 gives 1.00, k = 1.94 gives 1.39, k = 2 gives 1.41 R. The pit PRE_REG_V2 used 1.46 R at rr 1.94 (`pit_levels_2026-10-16/PRE_REG_V2.md:19`, OURS).

So sd is 1.0-1.5 R for a stop/target design and 2.9-4.5 R for a time exit. At sd = 1.4 the 5m stochastic MDE is 0.137 x 1.4 = 0.19 R (row 5) and 0.131 x 1.4 = 0.18 R (row 6); at sd = 2.9 it is 0.40 R. **The 5m stochastic BLOCK holds under every sd** because cost alone (0.60 / 0.79 R) exceeds 0.30 R; the RSI rows would need sd <= 0.21 R, which no outcome definition gives. Verdict: label WRONG (the PRE_REG table column "MDE (SD units)" is not an R and must not be added to an R), conclusion unchanged.

Side note: POWER_Z = 0.84 (`prereg_gate.py:15`) vs 0.8416 in `PRE_REG_V2.md:20`: MDE ratio 1.0004, immaterial.

## Q2. Cost aggregation

QUOTED `count_events.py:101`: `share_stop_ge_fee` = share of events with stop >= 14 bp; `PRE_REG.md:22`: Fee as R = 14 / median stop bp.

With per-event risk sizing (each stop = 1 R, the only sizing under which "R" means anything), the fee-net mean over events is mean(gross_R_i) - mean(14/stop_i). The median-of-stop cost 14/median(stop) is not mean(14/stop_i): 1/x is convex, and 17-38 % of events have stop < 14 bp, where each event's cost is > 1 R. RE-DERIVED lower bound on the mean cost from the share column alone (events with stop < 14 bp cost > 1 R each; the rest cost > 0):

| Row | share stop < 14 bp = 1 - share_stop_ge_fee | mean cost lower bound (R) | vs 0.30 R |
|---|---|---|---|
| 1 | 1 - 0.2206 = 0.779 | > 0.78 | above |
| 2 | 1 - 0.1732 = 0.827 | > 0.83 | above |
| 5 | 1 - 0.6883 = 0.312 | > 0.31 | above, from this bound alone |
| 6 | 1 - 0.6172 = 0.383 | > 0.38 | above |
| 3 | 0.105 | > 0.11 | not decided by this bound (row fails on power) |
| 4, 7, 8 | 0 | - | not decided (rows fail on power) |

So the median-of-stop input is the lenient choice; the correct mean-of-cost input makes rows 1, 2, 5, 6 fail harder. The one-number gate is right to take one cost, but that number should be mean(14/stop_i) (or, if a stop floor is part of the design, the mean over the filtered sample). `counts.csv` does not carry the mean, so the exact value is UNDECIDABLE from the committed files; the bound above suffices for the verdict.

**Minimum-stop filter (PRE_REG s7).** Filtering to stop >= 14 bp keeps 68.8 % / 61.7 % of 5m events; the filtered median is not in `counts.csv`, so whether the filtered cost drops under 0.30 R (needs filtered median >= 14/0.30 = 46.7 bp) is UNDECIDABLE here. It is a selection on a pre-outcome variable (the stop is known at the event bar, `count_events.py:85-89`, no look-ahead), so it is a legitimate design, but it is a different sample chosen after seeing the stop distribution: a new trial, counted in m, with its own count pass. `PRE_REG.md:44` already states this correctly. Note that a tick-based stop as in the sources (`PRE_REG.md:47`) is tighter, not wider, so it cannot rescue the gate either.

## Q3. Statistics

- **Holm z.** `prereg_gate.py:19`: Phi^-1(1 - 0.05/(2m)). `promote.py:59`: Phi^-1(1 - 0.025/max(1, variants)). 0.05/(2m) = 0.025/m: identical for every m. RE-DERIVED m = 40: both give 3.227 (card `fable-audit-e4-promotion-variants` result line quotes 3.227; `test_promote.py:95-99` tests it). m = 1: 1.960 both. CONFIRMED consistent. Both apply the strictest Holm step (= Bonferroni) to one number; for a gate that is the conservative choice.
- **One-sided vs two-sided.** Both use a two-sided critical value and then test one side (promote: net_r - z se > 0, `promote.py:259`; prereg: MDE above zero). Same convention, so the two gates agree for the same m. The MDE formula (z_alpha/2 + z_beta) sd/sqrt(n) is the standard normal approximation for a two-sided test at 80 % power; CONFIRMED.
- **Day clustering.** The gate takes n = event-days and sd = per-event sd (`prereg_gate.py:7`). For a day-clustered mean the true SE of the per-event mean is sd x sqrt(1 + (k - 1) rho) / sqrt(N_events), k = events per day, rho = within-day correlation. With n = days and the per-event sd the gate uses the rho = 1 bound: on 1m stochastic (k = 15.7, `counts.csv:2`) the MDE is 0.118 vs 0.030 at rho = 0 (3.574/sqrt(14317)), a factor sqrt(15.7) = 4. For 5m (k = 2.4-2.7) the factor is at most 1.6. Direction: conservative (a gate may never understate MDE), so CONFIRMED; but the gate cannot express an intermediate rho, and the correct per-day unit is the daily mean of R with its own sd, which `counts.csv` does not carry. If a later count pass records the daily-mean sd, the gate can take it directly with n = days and no clustering assumption.
- **Which m.** QUOTED `PRE_REG.md:33`: m = 8 (study-local). QUOTED `pit_levels_2026-10-16/BLOCKED.md:7`: m = 42 and 62 from `verdicts.py count --split DEV`; `bb_top_reversal_2026-10-18/BLOCKED.md:5`: m = 58; `eur_low_us_sweep_followups_2026-10-18/PRE_REG.md:16`: m = 3. `TASK_REFINEMENT.md:80` says `verdicts.py count --split DEV` "is the m". Today the count prints 57 (run here, lower bound). RE-DERIVED at m = 57 + 8 = 65: z_holm = 3.364, 5m long MDE = 4.204/sqrt(678) = 0.161 sd (vs 0.137). No row flips, but the convention is inconsistent across the four PRE_REGs that used the gate, and the smaller m is the lenient side.
- **promote.py MDE floor.** `promote.py:62-66`: n >= max(30, 4 ((z + 0.84) sd / net_r)^2), sd = se sqrt(n). Same formula as prereg's `need` (`prereg_gate.py:38`) with the observed net_r in place of (plausible - cost). That is post-hoc power on the observed effect: a lucky large net_r lowers its own floor. The 4x safety factor (OURS) blunts but does not remove this. A floor computed from the PRE_REG's pre-registered (plausible - cost) would be consistent with E1 and not circular. Flagged as a fix, not a defect in the arithmetic.

## Q4. Freeze scope

QUOTED `BLOCKED.md:1`: "no Quad Rotation cell can be frozen". QUOTED `PRE_REG.md:3`: "Every TF x arm x side is fee-dominated or underpowered". What was counted: TF {1m, 5m}, arm {stoch, RSI}, side {long, short}, one stop definition (pattern low from episode start, OURS), taker cost 14 bp (`PRE_REG.md:16,19,47,50`). Not counted: 15m, 1h, any maker entry, any tick stop, the (44,x) band, D9-cross turn rule.

Registry state: `VERDICTS.csv:39` has verdict UNPARSED and kill_scope UNPARSED (no RESULT.md, PRE_REG has no "FAIL means stop" sentence; `verdicts.py:157-165` reads only PRE_REG.md and RESULT.md, not BLOCKED.md). `verdicts.py check` run here exits 0. Risk: `verdicts.py:379` blocks any family match when verdict == FAIL and kill_scope != "none"; the docstring (`verdicts.py:22-24`) treats UNPARSED kill_scope on a FAIL as family-wide. Writing "FAIL" or "NEGATIVE" for this study without a scope sentence would kill Kurisko on 15m/1h repo-wide. The verdict word for this study is BLOCKED (count-only, nothing tested), which `verdicts.py:44` does not know; the row should carry verdict INCONCLUSIVE with an explicit scope, or a new BLOCKED word.

**Kill-scope sentence to write into PRE_REG.md s7 (matches `verdicts.py:162`):**
"FAIL/INCONCLUSIVE: stop; this BLOCK (count-only, no outcome read) covers only Quad Rotation on BTCUSDT 1m and 5m with bands (9,3),(14,3),(40,4),(60,10) D-line, the pattern-low stop and a 14 bp taker round trip; 15m and 1h, a minimum-stop filter, a maker entry or a tick stop are untested and need their own PRE_REG and gate."

With that sentence the 0-of-8 stands as written for the eight cells, and higher-TF Kurisko is not dead.

## Q5. Count correctness (reasoning from FORMULAS 24.4; module not re-run)

- **Resample bucket drop:** zero effect on DEV. RE-DERIVED: 2022 (365) + 2023 (365) + 2024-01..06 (182) = 912 days; 912 x 1440 = 1,313,280 = `run_meta.txt:2` bars_1m; 1,313,280 / 5 = 262,656 = bars_5m. Every 5m bucket is complete, none dropped, and `quad_rotation._segments` (`:33-47`) never splits. On VALIDATION this will not hold if a gap exists: a dropped bucket splits the series, restarts all four lines as NaN for up to 60 + 10 bars, and ends any open episode (one lost event per gap at most, plus the warm-up). Low sensitivity.
- **Strict "< 20" and NaN on HH == LL:** measure-zero on BTC 1m/5m; low sensitivity.
- **Turn rule (fast[t] > fast[t-1], one event per episode):** on 1m stochastic the first uptick of the (9,3) D line after entry fires; events = episodes with an uptick. A stricter turn (D9 crosses 20) cuts events but event-days are already saturated at 912 (every DEV day), so the gate input n does not move; the **median stop** moves (a later fire from the same episode start widens close - min low). Rows 1-2 cannot be rescued (6.7 bp vs 46.7 bp needed).
- **Stop definition (OURS):** the gate-deciding number. Rows 5-6 need median stop >= 14/0.30 = 46.7 bp to clear cost alone, i.e. 2.0x (long) / 2.6x (short) the pattern-low stop. Anchoring the stop at the lowest low of the 60-bar lookback, or a prior swing low, is the one rule choice that could change the 5m verdict, and each such definition is a new ledger trial.
- **Short mirror (NO-SOURCE):** rows 2, 6, 4, 8 exist only by it; sensitivity 100 %, but they are reported apart (`PRE_REG.md:16`) and decide nothing on their own.
- **RSI-60 band:** rows 3, 4, 7, 8 (3-19 events in 912 days) are controlled by requiring Wilder RSI(60) < 20, which needs a 60-bar average loss >= 4x the average gain. Dropping the 60 band or using 44 would multiply these counts; a one-event change on row 7 is 33 %. Most rule-sensitive counts, but they only decide "underpowered" and would remain so unless the count rises ~100x (n needed for MDE 0.30 at sd 1.4, m 8: (3.574 x 1.4 / 0.30)^2 = 278 days at zero cost).

**Hand check the operator can run (one DEV month, no module import, no outcome):** row 5 (5m stochastic long) on `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2024-06.csv` (DEV; the loader cutoff is 2024-07-01 so this file is the last allowed one). Pandas: read columns open_time, high, low, close; `t5 = open_time // 300000 * 300000`; group by t5 with high max, low min, close last, keep groups of size 5; for each (k, d) in (9,3), (14,3), (40,4), (60,10): raw = 100 (close - low.rolling(k).min()) / (high.rolling(k).max() - low.rolling(k).min()) with the division-by-zero as NaN, D = raw.rolling(d).mean(); scan bars in order: inside = all four D < 20; episode starts at the first inside bar s; fire once at the first t > s with inside on s..t-1 and D9[t] > D9[t-1]; stop_bp = 1e4 (close[t] - low[s..t].min()) / close[t]. Compare the event list (t, s) and median stop with `python count_events.py` restricted to that month (patch `dev_files()` to the one file, keep the sha check). Expected: identical event rows and median; a difference points at the warm-up (the module restarts lines per segment; a single month starts at NaN for the first 69 5m bars either way). Expected magnitude for the month, RE-DERIVED from `counts.csv:6`: 1646 events / 30 months = about 55 events on about 23 event-days.

## Q6. Trial-ledger logic

- `TRIAL_LEDGER.csv` (20 data rows): wlow_bounce 8, wavetrend 9, krown_recall 2, **Kurisko 0**. Grep for kurisko, quad, KQ: none.
- `gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv:9`: the one Kurisko row ("which Quad Rotation cells enter a PRE_REG (0 of 8 ...)"). The pit PRE_REG also calls this file its trial ledger (`pit_levels_2026-10-16/PRE_REG.md:80`).
- `VERDICTS.csv:39`: Kurisko row, split_read UNPARSED, so `verdicts.py count --split DEV` (`:401-409`) skips it (it is one of the 7 skipped rows the count reports).
- `promote.py:267-284` (G5): reads the CSV named in the manifest, counts rows whose `study` equals `entry_id`, and requires that count to equal `variants`; G4 (`:255-262`) uses that `variants` for the Holm z. So E4's m is per manifest and per ledger file, never repo-wide, and a Kurisko manifest pointing at TRIAL_LEDGER.csv would find 0 rows (G5 REJECT: "no rows for study"), while one pointing at EXPOSURE_LEDGER.csv has no `study` column match for KQ-T01 either (its study field is `kurisko_2026-10-18/count_events.py`, one row, not eight).

Verdict: WRONG. KQ-T01 is named (`PRE_REG.md:44`) but recorded in no ledger that any gate reads, so the 8 counted cells enter neither E4's `variants` nor `verdicts.py count`. Whether count-only cells *should* consume Holm alpha is a policy point (no outcome was tested, so strictly they do not), but the repo's own rule (`TASK_REFINEMENT.md:80`, "append your row") and the PRE_REG's own trial id say they are trials; today the three registries (TRIAL_LEDGER, EXPOSURE_LEDGER, VERDICTS) disagree on what a trial row is. Double counting: none found. Wavetrend W01-W09 are in both TRIAL_LEDGER (`:10-18`) and VERDICTS (`:57-65`), but each m reads only one file, so no m counts them twice. Omission: Kurisko (8 cells), and pit (0 rows in TRIAL_LEDGER; counted in VERDICTS only through its PRE_REG row).

## Fix list (max 6; card title + the test that must fail on current code)

1. **prereg_gate: sd in R, refuse sd < 1 without a label.** `--sd` must be the sd of per-event R; print "MDE 0.137 R at sd 1.00 R" and exit 2 when `--sd < 1` unless `--sd-source <file:line>` names a measured or two-point value. Test: `run("--n","678","--sd","1","--cost","0.597","--m","8")` returns 2 (today 1); `--sd 1 --sd-source x` returns 1.
2. **count pass writes the cost column the gate needs.** `count_events.py` (and the PRE_REG template line) record `mean_cost_R = mean(14/stop_i)` and `sd_daily_mean_R` (or "n/a: no outcome") beside the median; the PRE_REG table uses the mean. Test: `summarise()` on the four-row fixture of `test_count_events.py:48-54` returns `mean_cost_R` = (14/5 + 14/7 + 14/9)/3 = 2.118 (today: KeyError).
3. **One m: prereg_gate takes `--m` from verdicts.py count + new cells.** Add `prereg_gate.py --m auto --new-cells 8` that runs `verdicts.py count --split DEV` and uses count + new cells; document in `TASK_REFINEMENT.md:80`. Test: with a VERDICTS.csv fixture of 3 DEV rows, `--m auto --new-cells 2` prints `m 5` (today: argparse error on "auto").
4. **verdicts.py: BLOCKED verdict word + kill_scope from BLOCKED.md.** `VERDICTS` gains "BLOCKED" (never family-wide), `kill_scope_of` also reads BLOCKED.md, and Kurisko's PRE_REG s7 gets the sentence in Q4. Test: a study dir with PRE_REG.md + BLOCKED.md (no RESULT) parses to verdict BLOCKED, kill_scope = the sentence (today: UNPARSED, UNPARSED); `check "kurisko quad rotation"` still exits 0.
5. **Trial ledger: one file, count-only rows included.** Append 8 `kurisko_2026-10-18,KQ-T01_<cell>,...,status=count-only-blocked` rows to `TRIAL_LEDGER.csv`; pit's row too; `verdicts.py count` gains `--ledger` that unions TRIAL_LEDGER (study, variant) with VERDICTS (study, arm). Test: `count --split DEV --ledger` >= 57 + 8 + 8 (today the flag does not exist; the plain count stays 57).
6. **promote.py G4 floor from the pre-registered effect, not net_r.** Manifest gains `pre_reg.plausible_net_r` (= plausible gross - cost from the PRE_REG gate line); `mde_floor` uses it; net_r stays only for the Holm CI test. Test: the good manifest with `net_r` doubled and `plausible_net_r` fixed keeps the same floor (today the floor falls 4x); a manifest without `plausible_net_r` REJECTs.

## Does 0-of-8 stand?

**Yes, as a verdict on the eight counted cells; no, as written.** All eight PRE_REG numbers reproduce, and every unit or aggregation choice the session made (sd = 1, median-of-stop cost, m = 8, n = event-days) sits on the lenient side, so the correct choices (sd 1.4-4.5 R, mean cost >= 0.31-0.83 R, m >= 57, clustered n) make each row fail by more, never less. What must change: the BLOCKED.md and PRE_REG s0 wording from "every Quad Rotation cell" to the eight counted cells with the kill-scope sentence of Q4 placed in PRE_REG.md, the "MDE (SD units)" column relabelled so nobody adds it to an R again, and KQ-T01's eight cells written into the ledger that `verdicts.py count` reads. Kurisko on 15m/1h, with a wider or sourced stop or a maker entry, is untested, not dead; each such route is a new counted trial with its own count pass before any outcome is read.

Fable weekly meter: 23 % before this session (get_usage at start); the end value is in the session's last message.
