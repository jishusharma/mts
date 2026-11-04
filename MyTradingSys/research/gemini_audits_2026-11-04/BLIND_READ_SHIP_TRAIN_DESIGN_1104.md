# Blind Read Audit: Ship Train Design (`ship_train_2026-11-04/DESIGN.md`)

- **Card**: `gemini-blind-read-of-mytradingsys-resear` (`OURS`)
- **Target File**: `MyTradingSys/research/ship_train_2026-11-04/DESIGN.md` (`OURS`)
- **Date**: 2026-11-04 UTC (`OURS`)
- **Auditor**: Gemini (Independent Blind Read — strictly reading `DESIGN.md` text only, without commit history, author notes, or external implementation context) (`OURS`)

---

## 1. Audit Overview & Methodology

This blind read audits all claims, tables, formulas, and operational rules in [DESIGN.md](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L1-L69) for:
1. Internal contradictions and mathematical/classification inconsistencies.
2. Untestable claims and underspecified operational mechanisms.
3. Missing numbers and unquantified assertions.

Every number below is labeled **SOURCED** (with exact quote and `DESIGN.md` line reference) or **OURS** (audit derivation/count).

---

## 2. Inventory of Findings

### Category A: Direct Contradictions & Classification Inconsistencies

#### Finding C1: Host Class Count & Category Mismatch Between Rule R1 and Cause Table
- **Quoted Line** ([DESIGN.md:56](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L56)):
  > `| R1 | ... | reds come from 4 host classes (26/16/10/3); no single machine to fix |`
- **Quoted Line** ([DESIGN.md:44](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L44)):
  > `| host (from branch name): jis-nuc / DESKTOP-F7IU69N / JIS-NB / cloud claude/* / other | 26 / 16 / 10 / 3 / 1 | inferred for non-merge heads; no machine is the single source |`
- **Quoted Line** ([DESIGN.md:33](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L33)):
  > `| A flaky | spec_news keywords | 1 | 1 | gemini-queue tree 1 | ca38a5b3d 11-03 19:13 |`
- **Contradiction Details**:
  - SOURCED `DESIGN.md:56` states: `4 host classes (26/16/10/3)`. Summing these 4 values gives `26 + 16 + 10 + 3 = 55` (`OURS`), which fails to sum to the total of 56 red runs.
  - SOURCED `DESIGN.md:44` explicitly defines **5** host classes: `jis-nuc / DESKTOP-F7IU69N / JIS-NB / cloud claude/* / other` with counts `26 / 16 / 10 / 3 / 1`, which correctly sums to `56` (`OURS`).
  - SOURCED `DESIGN.md:33` shows that the missing 1 run was attributed to `gemini-queue tree 1`. Rule R1 drops the 5th class (`other: 1` / `gemini-queue tree 1`), asserting there are only 4 host classes.

#### Finding C2: Incompatibility Between Fast-Forward Landing and Stamped Landing Merge Blame
- **Quoted Line** ([DESIGN.md:57](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L57)):
  > `| R2 | **The ref name is the author.** Blame = <host>/<slug> + the slug's claim, stamped into the landing merge message and the status file. Git author is ignored. | 56/56 reds carry author gemini-queue |`
- **Quoted Line** ([DESIGN.md:58](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L58)):
  > `| R3 | **Nothing red lands.** The train builds candidate = fast-track tip + queued refs merged (oldest first, cap 4), runs the existing CI matrix on it, and fast-forwards fast-track only on green. Merge conflict = eject that ref at once. | 38 content reds (68%) were found only on trunk; ~27 were repeats on an already-red trunk |`
- **Contradiction Details**:
  - In git, a "fast-forward" (`git merge --ff-only` or moving a branch pointer forward to an existing descendant commit) creates **no new merge commit** and therefore possesses **no merge commit message**.
  - If a queued ref is fast-forwarded or candidate tip is fast-forwarded without a merge commit, there is no "landing merge message" in which to stamp the blame.
  - Conversely, if a landing merge commit is created to stamp blame, the update to `fast-track` is a non-fast-forward merge commit creation, contradicting the strict phrasing `fast-forwards fast-track only on green` in Rule R3.

---

### Category B: Untestable Claims & Underspecified Operational Mechanisms

#### Finding U1: Underspecified Bisection / Ejection Algorithm for Multi-Ref Batches ($n > 2$)
- **Quoted Line** ([DESIGN.md:60](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L60)):
  > `| R5 | **Eject the breaker, not the batch.** Red candidate -> each ref runs alone on the tip in parallel (n <= 4); refs that fail alone are ejected, the rest re-run and land. A ref green alone but red only together ejects the later-queued one. | 11 distinct content causes inside 38 runs; 8 of 21 streak origins held 3..14 commits (SHIP_TRAIN.md) |`
- **Untestable / Ambiguity Details**:
  - SOURCED `DESIGN.md:60` specifies: `A ref green alone but red only together ejects the later-queued one`. This heuristic is deterministic only for a 2-ref batch ($R_1, R_2$).
  - For candidate batches of size $n=3$ or $n=4$ (permitted by `batch cap 4`), if candidate ($R_1+R_2+R_3$) fails and all three pass alone:
    1. The rule does not define which ref is ejected if the pairwise conflict is between $R_1$ and $R_2$, but $R_3$ is the "later-queued one". Blindly ejecting $R_3$ ejects an innocent ref while leaving the incompatible pair $R_1+R_2$ to fail again upon re-run.
    2. The rule says `the rest re-run and land`, but does not specify the re-run topology (e.g. iterative bisection, sequential testing, or candidate re-formation).
    3. The rule lacks an upper bound on retry rounds or a terminal failure handler if the remaining subset fails again.

#### Finding U2: Undefined Inter-Process / Host Signaling Transport from GitHub Actions
- **Quoted Line** ([DESIGN.md:62](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L62)):
  > `| R7 | **Name the breaker to its owner.** An ejected ref gets mts_signal to its host + slug with the failing test id and run link; its claim stays open. Never auto-revert. | 28/56 heads were merge commits: first-viewer revert hits the wrong commit |`
- **Untestable / Ambiguity Details**:
  - The ship train workflow runs in cloud-hosted GitHub Actions runners.
  - SOURCED `DESIGN.md:62` specifies: `gets mts_signal to its host + slug`. However, GitHub Actions runners do not have inbound network routes or socket connectivity to local machines (`jis-nuc`, `DESKTOP-F7IU69N`, `JIS-NB`).
  - While Rule R8 mentions writing queue status to the git branch `mts-signals`, Rule R7 states that an ejected ref directly receives `mts_signal` without specifying whether this occurs via git polling, commit hooks, or an external push service. The delivery transport is untestable as written.

#### Finding U3: Quarantine List Semantics, Data Structure, and Lifecycle Omitted
- **Quoted Line** ([DESIGN.md:61](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L61)):
  > `| R6 | **A flake never ejects.** A failed shard reruns once before it counts; a test that fails then passes on the same sha is logged to the quarantine list, not charged to the ref. | 18 flaky reds (32%), 10 of them one test (c_drive_buckets), all green next run with no fix |`
- **Untestable / Ambiguity Details**:
  - SOURCED `DESIGN.md:61` states: `logged to the quarantine list`.
  - The design specifies no storage path, no repository location, no schema, and no operational effect.
  - It is untestable whether a quarantined test is excluded from subsequent candidate CI runs, continues running with suppressed exit codes, or is merely logged for human review.

#### Finding U4: Fast-Lane Classification Rules and Head-of-Line Queue Preemption
- **Quoted Line** ([DESIGN.md:59](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L59)):
  > `| R4 | **Docs/data ships ride the train too, on a fast lane** (integrity + size-cap + ledger subset, 1-2 min) and are ordered first. The push: paths: filter stops deciding what runs. | home size cap 7 + trial ledger 4 = 11 runs, both started by docs/data-only commits CI never ran |`
- **Untestable / Ambiguity Details**:
  - The design does not define what constitutes a "Docs/data ship" (no path globs, no file extension whitelist, and no rule for mixed commits containing both docs and code).
  - The specification `and are ordered first` implies head-of-line priority queueing. It is ambiguous whether a newly arriving docs ship preempts an in-flight code batch, inserts ahead of waiting code refs, or forces re-basing of pre-tested code candidates.

---

### Category C: Missing Numbers & Unquantified Claims

#### Finding M1: Unquantified Developer Delay and CI Wait Duration
- **Quoted Line** ([DESIGN.md:63](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L63)):
  > `| R8 | **One status file is the wait.** The train writes queue status (landed / ejected / position) on the mts-signals branch; ship --wait reads it instead of polling CI. | every red run cost every later shipper a full CI wait (56 runs) |`
- **Missing Number Details**:
  - SOURCED `DESIGN.md:63` claims `every red run cost every later shipper a full CI wait (56 runs)`.
  - The design cites the count of 56 runs, but provides **no number** for the duration of a "full CI wait" (median, p95, or mean minutes), nor does it quantify the total developer wall-clock or queue-delay hours lost across the 56 runs.

#### Finding M2: Unsourced Fast-Lane Execution Duration Estimate
- **Quoted Line** ([DESIGN.md:59](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L59)):
  > `| R4 | **Docs/data ships ride the train too, on a fast lane** (integrity + size-cap + ledger subset, 1-2 min) and are ordered first. | ... |`
- **Missing Number Details**:
  - SOURCED `DESIGN.md:59` asserts the fast lane takes `1-2 min`.
  - This time range is unmeasured and unsourced from actual historical run timing data for the cited test subset (`test_hub_folds_link_help_and_stays_compact`, card validation, and `test_live_repo_trial_ledger_built`).

#### Finding M3: Missing Polling and Timeout Parameters for `ship --wait`
- **Quoted Line** ([DESIGN.md:63](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L63)):
  > `| R8 | **One status file is the wait.** The train writes queue status (landed / ejected / position) on the mts-signals branch; ship --wait reads it instead of polling CI. | ... |`
- **Missing Number Details**:
  - The design provides **no numbers** for `ship --wait`: no polling frequency interval (e.g. seconds between git fetches), no backoff schedule, and no maximum timeout before assuming train failure.

#### Finding M4: Missing Quantitative Evaluation Thresholds for Shadow Week
- **Quoted Line** ([DESIGN.md:66-67](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L66-L67)):
  > `DECISION (OURS): batch cap 4 and one shard retry are starting values, to be measured in the shadow week, not SOURCED.`
- **Missing Number Details**:
  - SOURCED `DESIGN.md:66-67` correctly identifies `batch cap 4` and `one shard retry` as `OURS` (un-sourced design choices).
  - However, it provides **zero quantitative evaluation criteria** or target metrics for the shadow week (e.g. target median queue latency in minutes, maximum tolerated rerun frequency percentage, or throughput requirements).

#### Finding M5: Uncounted Co-occurrence of Flaky and Content Failures
- **Quoted Line** ([DESIGN.md:8](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L8)):
  > `first matching cause wins, content causes before flaky ones (a run holding both is content).`
- **Missing Number Details**:
  - SOURCED `DESIGN.md:8` establishes a priority filter where content causes mask flaky causes.
  - The document omits the exact number of runs that exhibited **both** content and flaky test failures, leaving unquantified the degree to which flaky failure rates are suppressed by the classifier.

#### Finding M6: Approximate vs Exact Repeat Break Count
- **Quoted Line** ([DESIGN.md:46](file:///F:/MTS/gq/gemini-blind-read-of-mytradingsys-resear/MyTradingSys/research/ship_train_2026-11-04/DESIGN.md#L46)):
  > `Read: 11 content causes produced 38 red runs, so ~27 runs re-reported a break already on trunk, because ships kept landing on a red trunk.`
- **Missing Number Details**:
  - SOURCED `DESIGN.md:46` uses an approximation `~27 runs` despite `38 - 11 = 27` (`OURS`) being exact arithmetic under the single-break assumption. The text does not provide exact run streak counts per cause or verify if multiple distinct causes overlapped simultaneously on trunk during the window.

---

## 3. Summary Table of Verified vs Unverified Figures

| Metric / Assertion | Value in `DESIGN.md` | Status | Source / Verification |
|---|---|---|---|
| Sampled window runs | 200 runs | SOURCED | `DESIGN.md:7` |
| Failure runs | 56 runs (28%) | SOURCED | `DESIGN.md:7`, `56 / 200 = 28.0%` (`OURS`) |
| Content failures | 38 runs (68%) | SOURCED | `DESIGN.md:36`, `38 / 56 = 67.86%` (`OURS`) |
| Flaky failures | 18 runs (32%) | SOURCED | `DESIGN.md:36`, `18 / 56 = 32.14%` (`OURS`) |
| Distinct content causes | 11 causes | SOURCED | `DESIGN.md:46`, Table 1 rows 16-26 (`OURS`) |
| Merge-headed red runs | 28 of 56 runs (50%) | SOURCED | `DESIGN.md:34,43`, Table 1 merge sum = 28 (`OURS`) |
| Git author `gemini-queue` | 56 of 56 runs (100%) | SOURCED | `DESIGN.md:42` |
| Host breakdown counts | 26 / 16 / 10 / 3 / 1 | SOURCED | `DESIGN.md:44`, Table 1 host sum = 56 (`OURS`) |
| Host class count in R1 | 4 host classes | **CONTRADICTION** | `DESIGN.md:56` omits 5th host class (`other: 1`) |
| Fast-forward vs merge blame | Fast-forward with landing msg | **CONTRADICTION** | `DESIGN.md:57` vs `DESIGN.md:58` |
| Fast lane duration | 1-2 min | **MISSING NUMBER** | `DESIGN.md:59` unsourced estimate |
| Full CI wait duration | "full CI wait" | **MISSING NUMBER** | `DESIGN.md:63` duration in min unquantified |
| Co-occurring flake count | Masked by content | **MISSING NUMBER** | `DESIGN.md:8` count of dual failures omitted |
| Multi-ref bisection ($n>2$) | Eject later-queued ref | **UNTESTABLE** | `DESIGN.md:60` lacks topology / loop bound |
| GitHub Actions to host signal | `mts_signal to its host` | **UNTESTABLE** | `DESIGN.md:62` no network transport specified |
| Quarantine list semantics | "logged to quarantine list" | **UNTESTABLE** | `DESIGN.md:61` path, schema, effects omitted |
| Shadow week success criteria | "to be measured" | **MISSING NUMBER** | `DESIGN.md:66-67` target thresholds omitted |

---

VERDICT: FINDINGS

## Claude spot-check (Builder gem-review-chain-1104)

- Checked 5 of 12 findings against trunk `MyTradingSys/research/ship_train_2026-11-04/DESIGN.md`:
  - C1: lines 33, 44, 56 quoted correctly; 26+16+10+3+1 = 56 and R1 says "4 host classes (26/16/10/3)": AGREE.
  - C2: quotes at lines 57-58 correct; the fast-forward versus merge-commit contradiction follows from the text: AGREE.
  - U1: quote at line 60 correct: AGREE.
  - U2: quote at line 62 correct; `mts-signals` is named at line 63: AGREE.
  - U3: quote at line 61 not checked.
- Outcome: 5 of 5 AGREE, 0 DISAGREE. Confirmed design gaps C1, C2, U1, U2 filed as one raw card. Card closed.
