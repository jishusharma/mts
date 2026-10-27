# CBP ultra task: finish the CBP module (D5 stage-4 exit)
Thinker, Sonnet LITE, 2026-10-23. Design only; nothing built, no session started. All numbers OURS unless marked.

## Facts checked this turn
- On origin/fast-track: ec54395ba, 6fd789b81, f787c15f4 (`git merge-base --is-ancestor`). CBP repo HEAD 50e71c3, 18fdfee (`git -C F:/CryptoScrapper log`).
- CBP repo is PRIVATE (`gh repo view jishusharma/cryptoscrapper`), 120 tracked files, 44 are inbox transcripts/cookies-pattern matches: transcripts are tracked there. Golden set must still use short excerpts (quote-sized), not full transcripts, so a later go-public does not leak.
- `MyTradingSys/queue/cbp_adapter.py:27` DEFAULT_TRANSCRIPTS = cbp_v2\inbox; `:64` own `quote_errors` (2nd checker next to `scripts/dev/verify_extract_quotes.py`).
- CBP has no tests/CI: `git ls-files` shows only `cbp_v2/tools/test_profile.py`; no `.github/`. `emit_mts.py` 82 lines, no gates. MTS `consumer.py` 105 lines.
- `~/.claude/scheduled-tasks/cbp-daily-workflow/SKILL.md` still exists (scheduler policy: none allowed).
- STATUS.md line 6: CI is RED (oldest ungreen commit 3.7 h). Per CLAUDE.md: fix CI first, before this run ships to MTS. Not this task's job; Phase 0 checks it and stops MTS-side shipping if still red.
- Budget (`traffic.py budget --no-fetch`): all logins NORMAL; C week 99% on pace (readings older than 6 h = stale).
- Open cards: cbp-routine-retire, cbp-adapter-read-raw, cbp-repo-commit-krown, cbp-quote-row-84, cbp-one-acked-row (est 8 turns).

## Options (differ in kind)
| # | Option | Cost (OURS) | ROI | Risk / undo |
|---|---|---|---|---|
| A | One ultra Workflow, 3 phases, 6 scoped agents + verifier, ends with D5 re-score | ~30-40 agent-turns, ~3 h wall | Closes all 7 audit gaps; S4 exit proven or killed with a number | Two repos touched; undo = revert 1 CBP + 1 MTS commit |
| B | Run the 5 raw cards as separate Sonnet sessions, no harness | ~25 turns but 5 sessions, serial claims | Gaps 1,2,5,6 closed; gaps 3,4,7 (producer gates, golden set, D5 amendment) never filed | Drift returns: no CI means nothing stops regression |
| C | Kill CBP: retire routine, freeze repo, keep adapter only | ~6 turns | Saves budget; loses the Krown/analyst signal source | Undo costs the whole rebuild |

RECOMMEND A: only A delivers the S4 exit (golden set green on CI + one acked row) and its kill criteria (below) give a cheap exit to C with evidence.

## (a) Phase plan (pipeline; no two writers on the same files)
Order: Phase 1 (parallel, disjoint files) -> Phase 2 (CBP commit) -> Phase 3 (MTS commit naming the CBP sha) -> Phase 4 verify.

| Agent | Phase | One outcome | Files it writes | Repo |
|---|---|---|---|---|
| P0 Preflight (Haiku) | 0 | Read-only: CI state, git cherry, claims, 429 status; stops if STOP/HOLD in ANNOUNCEMENTS | none | both |
| R Retire | 1 | Scheduled-task SKILL.md gone; `mcp scheduled-tasks` list shows no cbp job; SCHEDULING_POLICY mention if needed | `~/.claude/scheduled-tasks/cbp-daily-workflow/` (outside repos), MTS `system/SUPERVISOR_LOG.md` one line | outside |
| G Gates | 1 | `emit_mts.py` runs schema gate (reads MTS `cbp_contract_v1.schema.json` path from config, not a copy) + quote gate (imports/calls MTS `verify_extract_quotes.py`) before writing a row; idempotent on video_id+analyst | CBP `cbp_v2/tools/emit_mts.py`, `cbp_v2/tools/gates.py` (new, thin wrapper only, no checker logic) | CBP |
| H Harness | 1 | Golden set: 10-20 synthetic/short-excerpt cases + 3 known failures (2026-10-18 rows, rejected krown) + pytest + `.github/workflows/golden.yml` | CBP `tests/golden/*`, `tests/test_golden.py`, `.github/workflows/golden.yml` | CBP |
| F Fetch-429 | 1 | Row 84 (Jason bO88AeBojf8): retry fetch once; classify `ok|unavailable|blocked_429`; no loop | CBP `cbp_v2/processed.json` row only | CBP |
| T Tidy+Commit | 2 | After G,H,F finish: commit krown ack, tidy pending/analyst_feed (no runtime data beyond the one proof ack), rewrite README/PIPELINE/PLAN to the 1-fetcher/1-store/MTS-scheduled truth. ONE CBP commit; reports its sha | CBP docs + `mts_queue/acks/krown_*.json`, `pending.json`, `analyst_feed.json` | CBP |
| A Adapter | 3 | `cbp_adapter.py` reads `raw_transcripts_canonical`, deletes its `quote_errors` copy, calls `verify_extract_quotes`; 1 real Krown row -> queue -> consumer -> CANDIDATE_UNTESTED + ack, order_eligible false | MTS `queue/cbp_adapter.py`, `queue/test_cbp_adapter.py`, `queue/candidates/` | MTS |
| D D5-amend | 3 | D5 amended: CBP writes `raw_transcripts_canonical/` via MTS fetcher (named exception), CBP sha cited; D5 table added | `research/v1_plan_2026-10-20/D5_CBP_MODULE.md` | MTS |
| V Verify | 4 | Independent: see (d) | none (report to `research/thinker/` verdict file) | read-only |

Gates on commits: CBP commit lands before the MTS commit; MTS commit body has `Result:` and `CBP sha: <sha>`; MTS ships via `sync.py ship` only.
Writers by phase: Phase 1 agents touch disjoint files (R outside repos, G emit_mts+gates, H tests+workflow, F one processed.json row). P2 T touches only CBP files G/H/F did not. P3 A and D touch disjoint MTS files; one MTS commit made by the orchestrator, not by agents racing.

## (b) Prompt skeletons (each starts: "You are <agent>. Sonnet. Do exactly this one outcome. Never read .secrets/.env. Testnet only. No scheduler. No chained cd+git (use git -C). Repo public rule: no transcripts/runtime data in MTS.")
- R: "Delete `~/.claude/scheduled-tasks/cbp-daily-workflow/` via the scheduled-tasks tool (delete) or file removal; list tasks after; confirm no job runs fetch_latest.ps1. Report the listing. Touch nothing else."
- G: "In F:/CryptoScrapper, edit `cbp_v2/tools/emit_mts.py` so a row is written only if (1) it validates against the MTS schema at the path in env `MTS_CONTRACT_SCHEMA` or the worktree default, (2) `verify_extract_quotes` accepts its quotes, (3) `(video_id, analyst)` is not already queued. Write the failing tests FIRST in `tests/test_emit_gates.py` (bad schema, fabricated quote, duplicate), see them fail on current code, then fix. No checker copy: call MTS's."
- H: "Create the golden set under `tests/golden/` from SHORT excerpts (<= 400 chars each, no full transcripts, no cookies). Expected extraction written by hand. pytest fails on: claim without quote, wrong direction, missing expires_at, duplicate row. Add `.github/workflows/golden.yml` running pytest on push. Show each test failing against a deliberately broken extractor once."
- F: "Retry the caption fetch for Jason bO88AeBojf8 ONCE via MTS `fetch_captions_timed`. On HTTP 429 record `blocked_429` and stop; no retry loop, no sleep loop. Update only that processed.json row."
- T: "Wait for G,H,F reports. Make ONE commit in F:/CryptoScrapper: krown ack, tidy pending/analyst_feed (keep only the proof row and the schema-valid state), docs rewrite. No transcripts beyond what is already tracked. Print `git -C F:/CryptoScrapper rev-parse HEAD`."
- A: "Given CBP sha <X>: change `MyTradingSys/queue/cbp_adapter.py` default transcript dir to `raw_transcripts_canonical`, remove `quote_errors`, call `verify_extract_quotes`. Test first (adapter rejects a fabricated quote, accepts the real Krown row), run `python MyTradingSys/queue/cbp_adapter.py --verify-quotes`."
- D: "Amend D5: replace 'No MTS path, no MTS write' with the named exception, add a status table (gate 1-5, harness, S4 exit) with MET/PARTIAL/NOT MET placeholders to be filled by V. Cite CBP sha."

## (c) Fail-first tests and done_when
| Agent | Fail-first test (must fail on pre-change code) | done_when |
|---|---|---|
| R | `scheduled-tasks list` shows cbp-daily-workflow before; none after | task absent; SKILL.md gone |
| G | 3 cases in test_emit_gates.py fail today (no gate) | pytest green; emit refuses bad schema/quote/dup |
| H | golden suite fails on a broken extractor stub; passes on the real profile | CI run on GitHub green (`gh run list`) |
| F | n/a (single action) | row 84 has a classification |
| T | `git -C F:/CryptoScrapper status --short` non-empty before | status clean; one commit; sha reported |
| A | adapter test rejects fabricated quote; today the copy checker is a different code path | `--verify-quotes` consumes the real Krown row; ack written; order_eligible false; grep shows 0 `def quote_errors` in MTS |
| D | grep "No MTS write" present before | amended text; table present |
| All | `git cherry origin/fast-track` empty (MTS); CBP `git status` clean and pushed | |

## (d) Verification stage (agent V, fresh context, read-only)
Gets only the repos and this table, not the builders' reports. Must: (1) run `git cherry origin/fast-track` in MTS (empty) and `git -C F:/CryptoScrapper status` (clean, pushed); (2) run pytest in CBP and `python scripts/dev/run_all_tests.py --quick` itself, paste last lines; (3) `gh run list` shows golden CI green on the CBP sha; (4) grep proves one checker (`quote_errors` gone) and no scheduled task; (5) re-score D5 table per row MET / PARTIAL / NOT MET with evidence; (6) check no transcript or runtime data in the MTS diff; (7) emit the verdict file `research/thinker/2026-10-23_cbp_ultra_verdict.md`. A claim without command output = NOT MET.

## (e) Cost estimate (OURS, agent-turns)
P0 3, R 3, G 8, H 10, F 3, T 5, A 8, D 3, V 8, orchestration 4 = ~55 ceiling; expected 35-40. Wall ~3 h. Budget: all logins NORMAL (stale readings); run on one login; stop at 60 turns.

## (f) Kill criteria (OURS numbers; PENDING OPERATOR to adopt)
Stop and recommend option C if, after the one real Krown row, any of:
- Gate-5 value: of the last 6 actionable-profile analysts' rows in `analyst_feed.json`, fewer than 3 are unique tradable (entry+target+invalidation present, quote verified) across the last 30 days -> nothing tradable.
- Dedupe value: duplicates removed by the single-store dedupe < 5% of rows extracted (count from processed.json) AND extraction cost > 0 -> dedupe adds nothing.
- Golden set: pass rate < 80% after 2 prompt/profile fixes (OURS).
- V finds more than 2 NOT MET rows after a single repair pass.
Note: 56 scored calls per analyst is the existing SOURCED-by-D5 scorecard bar; not touched.

## DECISIONS (defaults taken, OURS; no operator quote exists for any)
- DEFAULT: CBP golden CI lives in the CBP repo workflow (private repo), MTS CI runs the adapter tests only (avoids cross-repo token).
- DEFAULT: golden fixtures are excerpts, never full transcripts.
- DEFAULT: Phase 1 may run while MTS CI is RED; nothing MTS-side ships until CI is green or the orchestrator's CI-fix card is claimed first (CLAUDE.md "fix CI first").
- PENDING OPERATOR: adopt kill numbers above; model for V (Sonnet default; Opus only on his word).

## (g) Launch prompt (paste into a Sonnet session in the Code tab)
```
You are the CBP Orchestrator. Sonnet. Run ONE Workflow (user opts in: "use a workflow") that finishes the CBP module per
MyTradingSys/research/thinker/2026-10-23_cbp_ultra_task.md (read it first; follow section (a) order, (b) prompts, (c) tests, (d) verify).
Boot: python scripts/dev/sync.py start cbp-ultra; read STATUS.md and ACTIVE ANNOUNCEMENTS; if CI line is RED, claim the CI-fix first.
Pipeline: P0 preflight -> Phase 1 parallel (R, G, H, F) -> Phase 2 T (one CBP commit, report sha) -> Phase 3 A + D (one MTS commit with
"CBP sha: <sha>" and "Result:") -> Phase 4 V (independent verify, re-score D5 MET/PARTIAL/NOT MET, write verdict file).
Rules: no schedulers, no transcripts or runtime data in the MTS repo, never read .secrets or .env, testnet only, git -C never chained cd.
Stop at 60 agent-turns or on any kill criterion in section (f) and report the number. Finish with sync.py ship, git cherry empty,
then a plain status: done / not done / what V scored. Do not ask to proceed; take the defaults in the note.
```

## (h) Pre-run checklist (added after the operator asked to "prepare", 2026-10-23; run before pasting (g))
Found this turn: `sync.py claims` shows `cbp-one-acked-row-through-queue-consumer` claimed by JIS-NB/jishusharma, 14 h old. That card is the same outcome as phase A (same file `queue/cbp_adapter.py`): two writers. Also this tree was 87 commits behind trunk, and the STATUS CI line on origin/fast-track still reads RED.
1. Before launch: ask the claim owner (JIS-NB) to ship or release that claim (`sync.py release`); the ultra run then SUPERSEDES the 5 cbp-* cards (retire, adapter, repo-commit, row-84, acked-row): mark them done by reference to the verdict file, not dispatched in parallel.
2. Before launch: `python scripts/dev/sync.py start cbp-ultra` (merges trunk); then read the CI line. RED = the orchestrator claims the CI fix first; Phase 1 (CBP-repo only) may run meanwhile.
3. Idle linked session `cbp-ship-fetcher-store-l` (local_8a9a8501-6771-42b8-ae96-893bef25b80a): confirm it holds no uncommitted CBP edits (`git -C F:/CryptoScrapper status`); the dirty CBP files today are exactly phase T's input.
4. To watch the run: `/workflows`; after it ends read `research/thinker/2026-10-23_cbp_ultra_verdict.md` and the MET/PARTIAL/NOT MET table. Check: verdict has pasted command output; `git cherry origin/fast-track` empty; kill criteria numbers stated.
5. PENDING OPERATOR still: kill numbers in (f).
