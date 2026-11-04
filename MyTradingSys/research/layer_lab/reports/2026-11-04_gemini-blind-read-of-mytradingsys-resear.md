# Layer Lab Report: `gemini-blind-read-of-mytradingsys-resear`

- **Card**: `gemini-blind-read-of-mytradingsys-resear` (`OURS`)
- **Date**: 2026-11-04 UTC (`OURS`)
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_SHIP_TRAIN_DESIGN_1104.md` (`OURS`)
- **Headline Counts**: `FINDINGS: 12 (2 CONTRADICTIONS, 4 UNTESTABLE/AMBIGUOUS, 6 MISSING NUMBERS)` (`OURS`)
- **Audit Outcome**: `VERDICT: FINDINGS` (`OURS`)

## Findings

1. **Host Class Count & Category Mismatch (`CONTRADICTION`)**:
   - `DESIGN.md:56` (Rule R1) cites `reds come from 4 host classes (26/16/10/3); no single machine to fix`.
   - `DESIGN.md:44` defines **5** host classes: `jis-nuc / DESKTOP-F7IU69N / JIS-NB / cloud claude/* / other` with counts `26 / 16 / 10 / 3 / 1`.
   - `DESIGN.md:33` lists row 33 with host `gemini-queue tree 1`.
   - Sum of the 4 classes in R1 is `26 + 16 + 10 + 3 = 55` (`OURS`), which drops the 5th class (`other: 1`) and fails to equal the total of 56 red runs (`OURS`).

2. **Fast-Forward Landing vs Landing Merge Blame Stamping (`CONTRADICTION`)**:
   - `DESIGN.md:57` (Rule R2) specifies: `Blame = <host>/<slug> + the slug's claim, stamped into the landing merge message and the status file`.
   - `DESIGN.md:58` (Rule R3) specifies: `The train builds candidate = fast-track tip + queued refs merged (oldest first, cap 4), runs the existing CI matrix on it, and fast-forwards fast-track only on green`.
   - In git, a fast-forward (`git merge --ff-only`) creates no merge commit and has no merge commit message to stamp blame into.

3. **Underspecified Bisection Algorithm for Multi-Ref Batches (`UNTESTABLE / AMBIGUOUS`)**:
   - `DESIGN.md:60` (Rule R5): `A ref green alone but red only together ejects the later-queued one`.
   - For batch sizes $n=3$ or $n=4$ (permitted by `batch cap 4`), if candidate fails and all pass alone, ejecting the later-queued ref falsely penalizes later innocent refs when the semantic conflict is between earlier refs. The re-run loop termination and subset resolution rules are omitted.

4. **Missing GitHub Actions to Local Host Signal Transport (`UNTESTABLE`)**:
   - `DESIGN.md:62` (Rule R7): `An ejected ref gets mts_signal to its host + slug with the failing test id and run link`.
   - Cloud GitHub Actions runners lack socket connectivity or network routing to local machines (`jis-nuc`, `DESKTOP-F7IU69N`, `JIS-NB`). The physical delivery mechanism is unstated.

5. **Quarantine List Operational Semantics Omitted (`UNTESTABLE`)**:
   - `DESIGN.md:61` (Rule R6): `logged to the quarantine list, not charged to the ref`.
   - Storage path, persistence schema, and runtime behavior (whether future failures are skipped, ignored, or converted to warnings) are omitted.

6. **Docs/Data Fast-Lane Classification & Queue Preemption (`UNTESTABLE / AMBIGUOUS`)**:
   - `DESIGN.md:59` (Rule R4): `Docs/data ships ride the train too, on a fast lane ... and are ordered first`.
   - No path globs or file type criteria are specified to classify a ref, and head-of-line preemption behavior vs ongoing batches is undefined.

7. **Missing Number: CI Wait Duration & Aggregate Lost Time (`MISSING NUMBER`)**:
   - `DESIGN.md:63` (Rule R8): `every red run cost every later shipper a full CI wait (56 runs)`.
   - The document omits numbers for median/mean CI run duration and aggregate developer wait hours.

8. **Missing Number: Fast-Lane Execution Duration Estimate (`MISSING NUMBER`)**:
   - `DESIGN.md:59` (Rule R4): asserts `1-2 min` without empirical timing data for the required check subset.

9. **Missing Number: Polling Frequency and Timeout for `ship --wait` (`MISSING NUMBER`)**:
   - `DESIGN.md:63` (Rule R8): specifies no polling interval or timeout limit for `ship --wait`.

10. **Missing Number: Shadow Week Quantitative Targets (`MISSING NUMBER`)**:
    - `DESIGN.md:66-67`: labels `batch cap 4 and one shard retry` as `OURS`, but defines no target evaluation thresholds.

11. **Missing Number: Dual Flaky & Content Failures Masked (`MISSING NUMBER`)**:
    - `DESIGN.md:8`: `first matching cause wins, content causes before flaky ones (a run holding both is content)`.
    - Omits the count of runs having both flaky and content failures.

12. **Approximation in Repeat Run Count (`MISSING NUMBER / AMBIGUITY`)**:
    - `DESIGN.md:46`: cites `~27 runs re-reported a break already on trunk` without streak breakdown or verifying overlapping breakage windows.

## Test Verification
- Executed: `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_SHIP_TRAIN_DESIGN_1104.md'); assert p.exists() and 'VERDICT' in p.read_text()"` -> Exit Code 0 (`OURS`).
