FOUND: 20, NOT_IN_DATA: 13, DIFF: 1  (rows group several numbers; every number counted once in a row)

# Blind re-read: ci_audit REPORT_FIRST_RED.md and mts_doctor REPORT_2026-11-01.md (independent, DSA direct 2026-11-02)

Method: every number/reference in the two reports checked against git objects (`git cat-file -s/-t`, `git ls-files`, `git log --since/--until` on origin/fast-track), file reads, and arithmetic. The `gh` CLI is not installed here and no CI run data is committed, so run-level numbers are NOT_IN_DATA, not guessed. The earlier Gemini file (ci_doctor_blind_read.md, FOUND 167 / NOT_IN_DATA 35 / DIFF 0) was not used; it reported zero DIFF, this recount finds one (LAYERS.md size, file regenerated after the report date).

| source | number / reference | status | evidence |
|---|---|---|---|
| FIRST_RED | 300 pushes; 6 in-flight/cancelled excluded; 213+81+2+4 | NOT_IN_DATA | gh run list data (runs.json) not in repo; gh CLI not installed here. Arithmetic 213+81+2+4=300 and 2+4=6: FOUND (computed) |
| FIRST_RED | red streak lengths 1x12,2x5,3x2,4x2,5x1,6x1,7x2,9x1,11x1 = 27 streaks | FOUND | sum of counts=27 (12+5+2+2+1+1+2+1+1) and sum length*count=81 = failure count; computed |
| FIRST_RED | pushes blocked MIN_STREAK=1 (74) vs =2 (37): 74-37=37 = gained 18 + false 19 | FOUND | 18+19=37 arithmetic; underlying 74/37/68 counts N/A |
| FIRST_RED | 68 pushes created inside red CI window; 74; 37; 18; 19 | NOT_IN_DATA | needs the runs.json scratchpad data, not in repo |
| FIRST_RED | "12 single-red episodes cleared by the next green" vs 19 false blocks | FOUND | streak table shows 12 length-1 streaks (consistent; 19 counts pushes, 12 counts episodes) |
| FIRST_RED | card window 10-30 21:31Z..10-31 08:10Z reproduces 26 reds | FOUND | CI_RED_ROOT_CAUSES.md:1,3 states the same window and "26 failure" |
| FIRST_RED | card says 17 innocent pushes; measured 18 | FOUND | CI_RED_ROOT_CAUSES.md:30 "17 of the 26"; 18 itself NOT_IN_DATA |
| DOCTOR | CLAUDE.md 7164/7168 B | FOUND | git cat-file -s HEAD:CLAUDE.md = 7164; cap 7168 at MyTradingSys/tests/docs/test_integrity.py:14 |
| DOCTOR | SURFACE_POLICY.md 3997/4096 | FOUND | git cat-file -s = 3997; cap test_integrity.py:15 |
| DOCTOR | roles builder 1475/1500, eagle_eyes 7098/7100, supervisor 7496/7500 | FOUND | wc -c = 1475, 7098, 7496; caps test_role_budget.py:14-15 (1500, 7100, 7500) |
| DOCTOR | headroom percents 0.1, 2.4, 1.7, 0.0, 0.1 | FOUND | (7168-7164)/7168=0.06->0.1; (4096-3997)/4096=2.4; (1500-1475)/1500=1.7; (7100-7098)/7100=0.03->0.0; (7500-7496)/7500=0.05->0.1 |
| DOCTOR | CI-REVERT reds 2b61ed46, 82734786, 38780f6d, 9eb34b9e exist | FOUND | git cat-file -t = commit for all four |
| DOCTOR | 18 / 26 / 13 / 22 min to green | NOT_IN_DATA | CI run timestamps not in repo |
| DOCTOR | ship_wall n=21 median 12s p90 30s; gate n=5 | NOT_IN_DATA | timing log not in repo (runtime data) |
| DOCTOR | HOOK-REG main checkout 2142 commits behind (limit 50) | NOT_IN_DATA | machine state at report time; boot line today reads 124 behind, differs |
| DOCTOR | DISK 401 GB; CONTEXT-GAP 1 row; BROADCAST; OF-RESTARTS | NOT_IN_DATA | host state, not in repo |
| DOCTOR | WAITING-ON-OPERATOR 3 cards: cost-checkup-doctor-section, fable-run7-forward-test, opus-o3-overhead-cut | FOUND | all three card files exist; waiting state itself time-varying (boot line today shows 2) |
| DOCTOR | STALE-CLAIMS 44 over 24h, limit 5; claim ages | NOT_IN_DATA | claims are live state; snapshot not in repo |
| DOCTOR | ASK-GAPS 80 open items; SUPERVISOR-IDLE A 182 min, C 164 min, 52 READY | NOT_IN_DATA | live state |
| DOCTOR | 115 guidance files checked | NOT_IN_DATA | doctor run state |
| DOCTOR | largest files WHERE_IS 216415, OPERATOR_DECISIONS 159387, 03_FILE_INDEX 79735, LESSONS_LEARNED 41996 | FOUND | git cat-file -s HEAD: 216415, 159387, 79735, 41996 exact |
| DOCTOR | LAYERS.md 37391 | DIFF | git cat-file -s HEAD:MyTradingSys/system/LAYERS.md = 36806 (file regenerated since report) |
| DOCTOR | 9 DEAD-REF paths "not tracked" | FOUND | git ls-files returns 0 for each of the 9 paths (count 9 listed = 9) |
| DOCTOR | 9 CARD stale-scope rows (listed 9) and 20 DUP-CARD | FOUND | listing counts: CARD rows 9, DUP-CARD rows 20 (line count of report) |
| DOCTOR | commit mix 1890 commits, merge 666 (35%), other 1222, overhead 668 | FOUND | git log origin/fast-track --since=2026-10-29T20:00Z --until=2026-11-01T19:58Z: 1891 commits, 667 merges (+1, window edge); 666/1890=35.2%, 668/1890=35.3%, 1222/1890=64.7% |
| DOCTOR | non-merge 1224; gate bookkeeping 38 of 1224 (3%) | FOUND | 1891-667=1224 non-merge; 38/1224=3.1% |
| DOCTOR | Part 2 CI: 30 runs, 22 success, 8 failure; reds a0423fbe, ea231d65, 9432fbac | FOUND | 22+8=30; all 3 shas are commits (git cat-file); ea231d65 subject is "Revert QUICK_PARTS sharding (1aaf5db65)..." as quoted; run statuses N/A |
| DOCTOR | named bookkeeping commits 6db6e0433, af34821d8, 4a26cac5f, 201d47c73, 5273a6f23, d6cc31796 | FOUND | all exist; subjects match the quoted text (AIBridge 0.7.8, Lab_Guy promote dsabr-c1..c8, G5 Holm 6db6e0433) |
| DOCTOR | CI red audit 26 red runs, 3 classes, fixes 201d47c73 5273a6f23 d6cc31796 | FOUND | commit 251063ae7 subject says exactly this; root-cause doc says 26 failure of 100 runs |
| DOCTOR | workflow-file commits 181; newest 10 shas | FOUND | all 10 shas exist (26ff2273e..29a98af4e); 181 count NOT_IN_DATA |
| DOCTOR | overhead 34->35, b4 20->0, stale 29->44; B4 0% <50%; standalone release 2, folded 0 | NOT_IN_DATA | previous report values not recomputed; "release 2" matches claim line count N/A |
| DOCTOR | Cost: Week 28/30/58%, 5h 17/18%, Fable 11/12%; reset times | NOT_IN_DATA | mts_signal budget readings are account state, not in repo files checked |
| DOCTOR | cost row e: 11 OPUS cards of 240 active; 72% non-research commits | NOT_IN_DATA | card worker field holds only session/agent (35/9 on ready cards today); no opus marker and no 240-card definition found; state counts today: ready 44, refined 63, blocked 113, active 1 |
| DOCTOR | cost rows a-d,f-i (745 MB, 15-20%, 4 waves, ~59k, 10 skills) | NOT_IN_DATA | host measurements |
