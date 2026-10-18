# PRE-REGISTRATION V3: audit fixes 1-2 (stop comparability and Holm-z MDE rule) (2026-10-18, addendum to PRE_REG_V2.md)

Status: EXPLORATORY TRIAL, frozen before any outcome read. Addendum to PRE_REG_V2.md. No outcome column exists in this folder. DEV only (bar open 2022-01-01 .. 2024-06-30). One-run: not changed after the first outcome. Labels: SOURCED = quote + file:line; OURS = judgement. Applies AUDIT_BEFORE_RUN.md sections 1 and 2 verbatim so context-factors-one-run can run. PRE_REG.md and PRE_REG_V2.md remain frozen.

## 0. Scope and relationship to PRE_REG_V2.md
`AUDIT_BEFORE_RUN.md` (2026-10-17, commit 664cf00ab7a0) audited `PRE_REG_V2.md` and issued verdict **FIX-FIRST** on two items:
1. Item 1: Location-only control (relative median stop gap > 25 % on F3 and F5; requires stop comparability check and stratified E).
2. Item 2: MDE under day clustering (mismatch between planning z=2.8 and PASS z=3.337; non-trunk FAIL clause).
Items 3 (Holm k m=59, z=3.337), 4 (leakage clean), 5 (VERDICTS row clean), and 6 (frozen triggers) were judged OK.

This addendum supersedes sections 2 and 4 of `PRE_REG_V2.md` and inserts the count-only stop-comparability step. All other elements of `PRE_REG_V2.md` and `PRE_REG.md` remain strictly frozen and unchanged:
- Frozen trigger sha256 hashes (SOURCED: AUDIT_BEFORE_RUN.md:70-71):
  - `context_asof.py`: `51a2a247c06e97148bdf6177f60123236a64c276cf1dd9ce3d734cf079828976`
  - `PRE_REG_V2.md`: `cf44beacfe0f6f8bd58c6d0b6bcfbb9b0f5f84227d122e8e1fd633b7749be0e4`
- Episode definition (PRE_REG.md s.5: at_level, first_touch, ladder rung, stop >= 0.56 % floor).
- 14 contrasts (s.3, `episode_counts.py`).
- Outcome function (s.2: entry open[t+1], ladder stop, 1.5 R target, both touched = stop, gap fill min(open, stop), max hold 1440 bars, round-trip fees 0.14 %).
- Matching: `context_null` key (hour + vol tercile + trend) and K = 20 controls (kmin = 10).
- DEV only (bar open 2022-01-01 .. 2024-06-30); VALIDATION and HOLDOUT untouched. No price after T.

## 1. Power table and Holm-z formula (replaces PRE_REG_V2 s.2; audit fix 2a)
In PRE_REG_V2 s.2, n_needed used multiplier z = 2.8 (unadjusted alpha 0.05), whereas PASS requires |t| >= 3.337 (Holm m = 59). Under z = 3.337 and the old effects (0.15 R / 0.20 R), n was 1274 (own) / 983 (trunk-free) / 2775 (trunk-net) days, exceeding all cell day counts (max 700 days), meaning no cell was powered for the PASS gate.

Per AUDIT_BEFORE_RUN.md fix 2a, the planning formula is replaced by the Holm-z formula with a plausible effect of 0.30 R (OURS, set after counts) and 0.30 R sensitivity beside it:
$$n = \left\lceil \left( \frac{(z + z_\beta) \times \text{sd}}{\text{effect} - \text{cost}} \right)^2 \right\rceil$$

Formula parameters:
- $z = 3.337$ (SOURCED: AUDIT_BEFORE_RUN.md:56, two-sided Holm critical value for $m = 59$ tests at $\alpha = 0.05$, $\Phi^{-1}(1 - 0.05/118) = 3.3368$; PRE_REG_V2.md:48).
- $z_\beta = 0.8416$ (OURS: standard normal quantile for 80 % statistical power, $\Phi(0.8416) \approx 0.80$; AUDIT_BEFORE_RUN.md:44, mde_rule.py:6).
- $\text{effect} = 0.30\text{ R}$ (OURS, set after counts: plausible filter effect; AUDIT_BEFORE_RUN.md:51).
- $\text{cost} = 0.0\text{ R}$ (OURS: filter contrast pays no incremental execution fee; AUDIT_BEFORE_RUN.md:51, PRE_REG_V2.md:28).
- $\text{sd} = 1.5\text{ R}$ (OURS: trunk-free standard deviation estimate; AUDIT_BEFORE_RUN.md:51).
  $$n = \left\lceil \left( \frac{(3.337 + 0.8416) \times 1.5}{0.30 - 0.0} \right)^2 \right\rceil = \lceil 436.517 \rceil = 437\text{ days}$$
- $\text{sd} = 1.281\text{ R}$ (OURS: own standard deviation estimate $1.25 \times \sqrt{1 + 1/20} = 1.2806\text{ R}$; AUDIT_BEFORE_RUN.md:41, PRE_REG_V2.md:26).
  $$n = \left\lceil \left( \frac{(3.337 + 0.8416) \times 1.281}{0.30 - 0.0} \right)^2 \right\rceil = \lceil 318.359 \rceil = 319\text{ days}$$

### Power table (DEV distinct UTC days; recomputed by hand):

| cell | long n | long days | powered (>= 437 d) | powered (>= 319 d) | short n | short days | powered (>= 437 d) | powered (>= 319 d) |
|---|---|---|---|---|---|---|---|---|
| F1 at a side-aware level (every episode) | 1636 | 694 | YES | YES | 1651 | 700 | YES | YES |
| F2 confluence n_layers >= 2 | 1305 | 654 | YES | YES | 1307 | 657 | YES | YES |
| F3 operator condition (ladder_cond) | 965 | 448 | YES | YES | 965 | 452 | YES | YES |
| F4 4h pattern in the trade direction | 261 | 161 | NO | NO | 287 | 177 | NO | NO |
| F5 band state (long re-entry / short walk veto) | 36 | 27 | NO | NO | 40 | 27 | NO | NO |
| F6 phase A with the trade | 578 | 247 | NO | NO | 382 | 162 | NO | NO |
| F7 HTF alignment | 885 | 376 | NO | YES | 667 | 299 | NO | NO |

(Episode counts and distinct day counts SOURCED: PRE_REG_V2.md:33-39, EPISODE_COUNTS.md:22-35, AUDIT_BEFORE_RUN.md:42).

### Powered cell list:
- Powered by design at primary threshold 437 days (sd 1.5 R): **F1 long (694 d), F1 short (700 d), F2 long (654 d), F2 short (657 d), F3 long (448 d), F3 short (452 d)** (6 cells).
- Note on F3: although F3 is powered by day count (448 / 452 days >= 437 days), its stop-width relative gap (+43 % / +45 %) exceeds 25 %, so per Section 2 / audit fix 1b, F3 cannot reach FAIL and receives INCONCLUSIVE ("R units not comparable") with no kill scope.
- Note on own sd 1.281 R (319 days): under 319 days, F7 long (376 d) would have met 319 days, but F7 short (299 d) does not; F1, F2, F3 long and short are powered under both thresholds.
- Unpowered cells: **F4 long/short, F5 long/short, F6 long/short, F7 long/short** (8 cells).
- Unpowered cells can only be INCONCLUSIVE, as PRE_REG_V2 already specifies (audit fix 2d).

## 2. Stop-width comparability step and stratified E (audit fix 1a-c)
The `context_null` matching key (hour + vol tercile + trend) contains no stop term. While both arms share the ladder stop rule, the stop width determines the R unit. In AUDIT_BEFORE_RUN.md section 1, F3 (+43 % / +45 %) and F5 (+44 % / +130 %) exhibited large stop-width gaps against the at-level control pool.

The executor must execute the following count-only stop-comparability step before reading outcomes:
1. **Count-only diagnostics before read (audit fix 1a):**
   For each of the 14 cells, print:
   - Median and p90 `stop_pct` for the cell episodes.
   - Median and p90 `stop_pct` for its matched control pool.
   - Shares of `ladder_rung` (`f3_stop_tf`: D, 12h, 8h, 6h, 4h) for both cell and control pool.
   `stop_pct` is the ladder stop percentage as known at decision time T. No post-T price or outcome data is loaded or used.
2. **Relative stop-width gap rule (audit fix 1b):**
   Let $\text{gap}_{\text{median}} = \frac{|\text{median}(\text{stop\_pct}_{\text{cell}}) - \text{median}(\text{stop\_pct}_{\text{ctrl}})|}{\text{median}(\text{stop\_pct}_{\text{ctrl}})}$.
   A cell whose relative median stop gap exceeds 25 % relative ($> 0.25$, OURS) gets the verdict word **INCONCLUSIVE** ("R units not comparable"), never FAIL, and carries NO kill scope.
3. **Stratified E requirement for PASS (audit fix 1c):**
   During the read, E is additionally computed within each `ladder_rung` stratum (same matching key plus rung, with $k_{\text{min}} = 10$ matched controls per stratum, OURS) and printed beside the pooled verdict.
   Strata with fewer than 10 controls are ineligible ($E = \text{null}$).
   **PASS** requires that stratified $E > 0$ holds across strata that together contain at least 80 % ($\ge 0.80$, OURS) of matched cell events.

## 3. Verdict rule (replaces PRE_REG_V2 s.4; audit fixes 2b-d, 1b-c, and item 5)
Let $E$ = mean $\text{net\_R}$ of matched episodes in the cell minus mean $\text{net\_R}$ of their matched controls ($K = 20, k_{\text{min}} = 10$).
Let $\text{SE}_{\text{day}}$ and $\text{SE}_{\text{week}}$ be the day- and week-clustered standard errors.
Let $\text{MDE}_{\text{real}} = 2.8 \times \text{SE}_{\text{day}}$ (multiplier 2.8 is OURS; PRE_REG_V2.md:52, AUDIT_BEFORE_RUN.md:48).

- **PASS** (audit fix 2c, unchanged from V2 except for stratified E requirement):
  PASS iff:
  1. The cell is powered by design (Section 1: $\text{days} \ge 437$).
  2. Relative median stop gap $\le 25\ \% $.
  3. $E > 0$ (filter helps).
  4. $|E| / \text{SE}_{\text{day}} \ge 3.337$ (Holm threshold $z = 3.337$).
  5. $|E| / \text{SE}_{\text{week}} \ge 3.337$.
  6. Sign of $E$ is positive ($E > 0$) in each sub-period: 2022, 2023, and 2024H1 (matched episodes only).
  7. Stratified $E > 0$ on `ladder_rung` strata holding $\ge 80\ \% $ of matched events (Section 2).

- **FAIL** (audit fix 2b and item 5):
  FAIL iff:
  1. $E \le 0$.
  2. $2.8 \times \text{SE}_{\text{day}} \le 0.30\text{ R}$ ($\text{cost} = 0\text{ R}$ for filter contrast; sensitivity 0.30 R is OURS; AUDIT_BEFORE_RUN.md:52).
  3. Relative median stop gap $\le 25\ \% $ (audit fix 1b: a cell with median gap $> 25\ \% $ is INCONCLUSIVE, never FAIL).
  
  Kill scope: FAIL means stop: this contrast's definition at this engine sha only; never a trader, a setup family or a layer.

- **INCONCLUSIVE** (audit fix 2b, 2d, 1b):
  All other outcomes are INCONCLUSIVE. Specifically:
  - If $E > 0$ but $|E| / \text{SE}_{\text{day}} < 3.337$ (below $z$), verdict is INCONCLUSIVE (not FAIL, correcting V2 defect 2).
  - If $E \le 0$ but $2.8 \times \text{SE}_{\text{day}} > 0.30\text{ R}$, verdict is INCONCLUSIVE (insufficient precision to rule out the 0.30 R effect).
  - If relative median stop gap $> 25\ \% $, verdict is INCONCLUSIVE ("R units not comparable") and no kill scope is applied.
  - If unpowered by design ($\text{days} < 437$), verdict can only be INCONCLUSIVE (audit fix 2d; unpowered cells never PASS or FAIL).
  - $\text{MDE}_{\text{real}}$ is printed beside every verdict; never relabelled.
  - Cross-engine agreement: a cell with cross-engine Cohen's kappa $< 0.4$ carries suffix "(definition-fragile)" on its verdict word in RESULT.md and VERDICTS.csv.

## 4. Parameter classification (SOURCED vs OURS)
In accordance with repo policy (CLAUDE.md:33), every number is explicitly labeled:

### SOURCED:
- $z = 3.337$: SOURCED: AUDIT_BEFORE_RUN.md:56, two-sided Holm critical value for $m = 59$ at $\alpha = 0.05$, $\Phi^{-1}(1 - 0.05/118) = 3.3368$; PRE_REG_V2.md:48.
- $m = 59$: SOURCED: AUDIT_BEFORE_RUN.md:56, PRE_REG_V2.md:47-48 (37 DEV variants from 12 studies + 8 trials.csv rows + 14 cells).
- $\alpha = 0.05$: SOURCED: AUDIT_BEFORE_RUN.md:44, AUDIT_BEFORE_RUN.md:56.
- Distinct UTC days per cell: SOURCED: PRE_REG_V2.md:33-39, EPISODE_COUNTS.md:22-35, AUDIT_BEFORE_RUN.md:42 (F1 long 694, short 700; F2 long 654, short 657; F3 long 448, short 452; F4 long 161, short 177; F5 long 27, short 27; F6 long 247, short 162; F7 long 376, short 299).
- Episode counts per cell: SOURCED: PRE_REG_V2.md:33-39, EPISODE_COUNTS.md:22-35 (F1 long 1636, short 1651; F2 long 1305, short 1307; F3 long 965, short 965; F4 long 261, short 287; F5 long 36, short 40; F6 long 578, short 382; F7 long 885, short 667).
- Frozen engine blob SHA-256: `context_asof.py` = `51a2a247c06e97148bdf6177f60123236a64c276cf1dd9ce3d734cf079828976` (SOURCED: AUDIT_BEFORE_RUN.md:70).
- Frozen pre-registration blob SHA-256: `PRE_REG_V2.md` = `cf44beacfe0f6f8bd58c6d0b6bcfbb9b0f5f84227d122e8e1fd633b7749be0e4` (SOURCED: AUDIT_BEFORE_RUN.md:71).

### OURS:
- $z_\beta = 0.8416$: OURS, standard normal quantile for 80 % statistical power ($\Phi(0.8416) \approx 0.80$; AUDIT_BEFORE_RUN.md:44).
- Plausible effect $= 0.30\text{ R}$: OURS, set after counts (AUDIT_BEFORE_RUN.md:51).
- Incremental cost $= 0.0\text{ R}$: OURS, filter contrast pays no extra trading fee (AUDIT_BEFORE_RUN.md:51, PRE_REG_V2.md:28).
- Trunk-free standard deviation $\text{sd} = 1.5\text{ R}$: OURS (AUDIT_BEFORE_RUN.md:51).
- Own standard deviation $\text{sd} = 1.281\text{ R}$: OURS, $1.25 \times \sqrt{1 + 1/20} = 1.2806\text{ R}$ (PRE_REG_V2.md:26, AUDIT_BEFORE_RUN.md:41).
- $n = 437\text{ days}$: OURS, recomputed by hand formula $\lceil ((3.337 + 0.8416) \times 1.5 / 0.30)^2 \rceil = 437$ (AUDIT_BEFORE_RUN.md:51).
- $n = 319\text{ days}$: OURS, recomputed by hand formula $\lceil ((3.337 + 0.8416) \times 1.281 / 0.30)^2 \rceil = 319$ (AUDIT_BEFORE_RUN.md:52).
- Realised MDE multiplier $= 2.8$: OURS, multiplier for day-clustered SE $2.8 \times \text{SE}_{\text{day}}$ (AUDIT_BEFORE_RUN.md:48, PRE_REG_V2.md:52).
- Sensitivity bound $= 0.30\text{ R}$: OURS, threshold for FAIL condition $2.8 \times \text{SE}_{\text{day}} \le 0.30\text{ R}$ (AUDIT_BEFORE_RUN.md:51-52).
- Stop-width relative gap threshold $= 25\ \% $: OURS, maximum allowable relative median stop_pct difference between cell and control pool (AUDIT_BEFORE_RUN.md:36).
- Stratified E coverage requirement $= 80\ \% $: OURS, minimum proportion of matched cell events in strata with $E > 0$ for PASS (AUDIT_BEFORE_RUN.md:37).
- Minimum controls per stratum $k_{\text{min}} = 10$: OURS (AUDIT_BEFORE_RUN.md:37).
- Matched controls $K = 20$: OURS (PRE_REG_V2.md:52, PRE_REG.md:104).
- Minimum matched controls $k_{\text{min}} = 10$: OURS (PRE_REG_V2.md:52).
- Minimum stop floor $= 0.56\ \% $: OURS (PRE_REG.md:55).
- Cross-engine kappa threshold $= 0.4$: OURS (PRE_REG_V2.md:59).
