# Spec-Derived Tests for traffic_report.py

**Date:** 2026-11-01 / 2026-11-02  
**Task ID:** `gpt-spec-tests-traffic-report`  
**Target:** `scripts/dev/traffic_report.py`  
**Test file:** `scripts/dev/test_traffic_report.py`  
**Registered in:** `scripts/dev/extra_tests.tsv`  

---

## 1. Branch Analysis of `traffic_report.py`

`traffic_report.py` has two main functions:

### A. `classify(subject, parents)`
1. **Branch 1 (Merge):** `parents > 1` -> returns `"merge"`.
   - Takes precedence even if the subject begins with `"claim"` or `"release"`.
2. **Branch 2 (Claim):** `parents <= 1` and `word in ("claim", "release")` where `word = subject.split(" ", 1)[0].lower() == "claim"` -> returns `"claim"`.
3. **Branch 3 (Release):** `parents <= 1` and `word == "release"` -> returns `"release"`.
4. **Branch 4 (Other):** `parents <= 1` and `word` not in `("claim", "release")` -> returns `"other"`.

### B. `report(hours=24, runner=subprocess.run)`
1. **Branch 5 (Log execution):** Calls `runner(["git", "log", TRUNK, f"--since={hours} hours ago", "--format=%P|%s"], capture_output=True, text=True)`.
2. **Branch 6 (Empty log):** If `total == 0`, percentage lambda returns `"0%"` (protects against `ZeroDivisionError`).
3. **Branch 7 (Aggregation & Overhead):** Counts `merge`, `claim`, `release`, and `other`; `overhead = merge + claim + release`.
4. **Branch 8 (Output format):** Returns formatted string:
   `f"last {hours} h on {TRUNK}: {total} commits | " + " | ".join(f"{k} {v} ({pct(v)})" for k, v in counts.items()) + f" | overhead {overhead} ({pct(overhead)})"`

---

## 2. Hand-Computed Expected Strings for Sample Inputs

### Input 1: Empty Log (0 commits)
- **Input lines:** `[]`
- **Counts:** `merge: 0, claim: 0, release: 0, other: 0, total: 0, overhead: 0`
- **Expected String:**
  `last 24 h on origin/fast-track: 0 commits | merge 0 (0%) | claim 0 (0%) | release 0 (0%) | other 0 (0%) | overhead 0 (0%)`

### Input 2: Merge with keyword "claim"
- **Input lines:** `["p1 p2|claim task-x"]`
- **Counts:** `merge: 1, claim: 0, release: 0, other: 0, total: 1, overhead: 1`
- **Expected String:**
  `last 24 h on origin/fast-track: 1 commits | merge 1 (100%) | claim 0 (0%) | release 0 (0%) | other 0 (0%) | overhead 1 (100%)`

### Input 3: Claim Commit
- **Input lines:** `["p1|claim ask-p0-12"]`
- **Counts:** `merge: 0, claim: 1, release: 0, other: 0, total: 1, overhead: 1`
- **Expected String:**
  `last 24 h on origin/fast-track: 1 commits | merge 0 (0%) | claim 1 (100%) | release 0 (0%) | other 0 (0%) | overhead 1 (100%)`

### Input 4: Release Commit
- **Input lines:** `["p1|release ask-p0-12"]`
- **Counts:** `merge: 0, claim: 0, release: 1, other: 0, total: 1, overhead: 1`
- **Expected String:**
  `last 24 h on origin/fast-track: 1 commits | merge 0 (0%) | claim 0 (0%) | release 1 (100%) | other 0 (0%) | overhead 1 (100%)`

### Input 5: Other Work Commit
- **Input lines:** `["p1|Result: add net_longs flags"]`
- **Counts:** `merge: 0, claim: 0, release: 0, other: 1, total: 1, overhead: 0`
- **Expected String:**
  `last 24 h on origin/fast-track: 1 commits | merge 0 (0%) | claim 0 (0%) | release 0 (0%) | other 1 (100%) | overhead 0 (0%)`

### Input 6: Mix of All Kinds with Custom Window (`hours=12`)
- **Input lines:**
  - `p1 p2|Merge remote-tracking branch` (merge)
  - `p1|Result: part 1` (other)
  - `p1|Result: part 2` (other)
- **Counts:** `merge: 1 (33%), claim: 0 (0%), release: 0 (0%), other: 2 (67%), total: 3, overhead: 1 (33%)`
- **Expected String:**
  `last 12 h on origin/fast-track: 3 commits | merge 1 (33%) | claim 0 (0%) | release 0 (0%) | other 2 (67%) | overhead 1 (33%)`

---

## 3. Test Suite Implementation

`scripts/dev/test_traffic_report.py` implements 9 offline unit tests (no real git subprocess):
1. `test_classify_merge_with_multiple_parents`: 2 or 3 parents classify as `"merge"`.
2. `test_classify_merge_takes_precedence_over_claim_or_release_keyword`: Multi-parent merge with `"claim"` or `"release"` remains `"merge"`.
3. `test_classify_claim_keyword`: Single-parent or root commit with `"claim"` / `"CLAIM"` classifies as `"claim"`.
4. `test_classify_release_keyword`: Single-parent commit with `"release"` / `"RELEASE"` classifies as `"release"`.
5. `test_classify_other_commit_subjects`: Regular work commits, `"claimed"`, `"releasing"`, or empty strings classify as `"other"`.
6. `test_report_empty_log_returns_zero_percent_and_no_division_by_zero`: Empty stdout returns valid 0% report without ZeroDivisionError.
7. `test_report_mix_of_all_kinds`: 4 commits (1 merge, 1 claim, 1 release, 1 other) match exact expected percentages and overhead.
8. `test_report_respects_custom_hours_argument_and_passes_to_git`: Injected runner receives `["git", "log", "origin/fast-track", "--since=72 hours ago", "--format=%P|%s"]`.
9. `test_report_rounding_and_counts`: 3 commits (1 merge, 2 other) verify integer rounding (33%, 67%).

---

## 4. Mutation Kill Verification

All 3 scratch mutations were executed and verified killed by the test suite:

1. **Mutation 1 (`parents > 1` changed to `parents >= 1`):**
   - *Result:* **KILLED** (5 test failures: `test_classify_claim_keyword`, `test_classify_other_commit_subjects`, `test_classify_release_keyword`, `test_report_mix_of_all_kinds`, `test_report_rounding_and_counts`).
2. **Mutation 2 (Drop `'release'` from keyword tuple):**
   - *Result:* **KILLED** (2 test failures: `test_classify_release_keyword`, `test_report_mix_of_all_kinds`).
3. **Mutation 3 (Zero division in `report` when `total == 0`):**
   - *Result:* **KILLED** (1 error: `ZeroDivisionError: division by zero` in `test_report_empty_log_returns_zero_percent_and_no_division_by_zero`).

---

## 5. Verification Commands

```bash
# Unit test run
python -m pytest scripts/dev/test_traffic_report.py -q
# 9 passed in 0.08s

# Task check
python scripts/dev/tasks.py check gpt-spec-tests-traffic-report
```
