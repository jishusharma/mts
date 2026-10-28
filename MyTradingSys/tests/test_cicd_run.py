import sys; sys.dont_write_bytecode = True
"""test_cicd_run.py - one test per stage of scripts/dev/cicd_run.py (stages 2.1 to 2.9) plus runner mechanics.

Expected values come from the design, MyTradingSys/research/_archive/loose_2026-10/CICD_PIPELINE_2026-10-03.md, not from the code under test:
  - section 1 rule 2 and 4: no stage stops the run; exit code 0 all PASS/SKIP, 1 any WARN, 2 any FAIL/CRASH.
  - section 2.1: flags ID-ONLY-IN-ONE-SOURCE, STATUS-DISAGREE, STALE pipeline rows, PIPELINE-LOCAL rows are never orphans.
  - section 2.2: M3 Python compile + PowerShell parse of changed files, M4 T3 line, M5 gate map; dirty allowlist from 2.7.
  - section 2.3: pass = exit 0; test-count drop is a WARN; tool missing = SKIP, not FAIL.
  - section 2.4: BOM, Cyrillic, registry contract (CLOSED needs a receipt), file-index row per added file.
  - section 2.5: DRIFT-UNAPPROVED is a FAIL; NO-BASELINE is named; post-commit mode compares committed blobs.
  - section 2.6: gate L1-L8, only when a live-path file is in the change set; runtime state in a change set fails L8.
  - section 2.7: RELEASE line: READY | READY-WITH-WARN <n> | NOT-READY <stage ids>; explicit pathspec.
  - section 2.8: P1 drift, P3 receipt hash resolves, P6 tag lag; section 2.9: WARN.jsonl line per failure, CRASH row.
Every test uses a temp directory. No live-tree write, no maven invocation (maven calls are faked).
"""
import json
import subprocess
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import cicd_run as cr  # noqa: E402

SESSION = "S-TEST-1"


def G(repo, *args):
    p = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, (args, p.stderr)
    return p.stdout.strip()


def put(repo, rel, content):
    fp = Path(repo) / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return fp


def commit_all(repo, msg="c"):
    G(repo, "add", "-A")
    G(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return G(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    G(r, "init", "-q")
    G(r, "config", "user.email", "t@example.invalid")
    G(r, "config", "user.name", "t")
    G(r, "config", "core.autocrlf", "false")
    put(r, "README.md", "seed\n")
    commit_all(r, "seed")
    return r


def make_ctx(repo, tmp_path, run=None, which=None, profile="desktop", session="", quick=False):
    out = []
    ctx = cr.Ctx(repo=repo, profile=profile, session=session, run=run, which=which or (lambda n: None),
                 out_dir=tmp_path / "out", quick=quick, emit=out.append)
    ctx.emitted = out
    return ctx


def fake_run(script):
    """Real git (inside the temp repo), scripted everything else. Records every non-git command."""
    calls = []

    def run(cmd, cwd=None, env=None):
        if cmd[0] == "git":
            return cr.default_run(cmd, cwd, env)
        calls.append(list(cmd))
        rc, out = script(cmd)
        return rc, out, 0.0
    run.calls = calls
    return run


def by_name(checks):
    return {c["check"]: c for c in checks}


BUGS_HEAD = ("# BUGS AND TASKS\n\n| ID | Opened | Status | Severity | Title | Evidence | Receipt |\n|---|---|---|---|---|---|---|\n")


# ------------------------------------------------------------------ 2.1 intake
def test_stage_2_1_intake_flags_disagreement_orphans_and_stale_rows(repo, tmp_path):
    put(repo, cr.BUGS_REL, BUGS_HEAD
        + "| B001 | 2026-01-01 | OPEN | MED | t | e | - |\n"
        + "| B002 | 2026-01-01 | CLOSED | MED | t | e | abc1234 |\n"
        + "| T003 | 2026-01-01 | OPEN | LOW | t | e | - |\n# END\n")
    put(repo, cr.INDEX_REL, "B001 | OPEN    | B001_x.md | s\nB002 | OPEN    | B002_x.md | s\nT009 | OPEN    | T009_x.md | s\n# END\n")
    put(repo, cr.PIPE_REL, "| # | ID | Slug | Status | Blocker | Next |\n|---|---|---|---|---|---|\n"
        "| 1.1 | B002 | slug | QUEUED | - | n |\n| 1.2 | R4-T1 | local | QUEUED | operator | n |\n")
    c = by_name(cr.stage_intake(make_ctx(repo, tmp_path)))
    assert c["intake/id-only-in-one-source"]["status"] == cr.WARN and "T009" in c["intake/id-only-in-one-source"]["detail"]
    assert c["intake/open-not-in-index"]["status"] == cr.WARN and "T003" in c["intake/open-not-in-index"]["detail"]
    assert c["intake/status-disagree"]["status"] == cr.WARN and "B002 BUGS=CLOSED INDEX=OPEN" in c["intake/status-disagree"]["detail"]
    assert c["intake/stale-pipeline"]["status"] == cr.WARN and "B002" in c["intake/stale-pipeline"]["detail"]
    assert "R4-T1" in c["intake/pipeline-local"]["detail"] and c["intake/pipeline-local"]["status"] == cr.PASS
    assert "R4-T1" in c["intake/blocked-on-operator"]["detail"]


def test_stage_2_1_intake_missing_sources_are_missed_rows_not_errors(repo, tmp_path):
    checks = cr.stage_intake(make_ctx(repo, tmp_path))
    assert checks and all(c["status"] == cr.SKIP and "MISSED" in c["detail"] for c in checks)


# ------------------------------------------------------------------ 2.2 pre-commit
def test_stage_2_2_precommit_compile_allowlist_and_gate_map(repo, tmp_path):
    put(repo, cr.BUILD_REPORT_REL, "STATUS: PASS\n")
    commit_all(repo, "report")
    put(repo, cr.BUILD_REPORT_REL, "STATUS: FAIL\n")          # allowlisted churn
    put(repo, "scripts/dev/bad.py", "def (:\n")
    put(repo, "scripts/dev/good.py", "x = 1\n")
    put(repo, "MyTradingSys/execution/auto_trader.py", "x = 1\n")
    put(repo, "MyTradingSys/system/sessions/%s.md" % SESSION, "status: open\n")
    c = by_name(cr.stage_precommit(make_ctx(repo, tmp_path, session=SESSION)))
    paths = c["precommit/change-set"]["paths"]
    assert cr.BUILD_REPORT_REL not in paths and "scripts/dev/bad.py" in paths
    assert c["precommit/python-compile"]["status"] == cr.FAIL and "bad.py" in c["precommit/python-compile"]["detail"]
    assert "good.py" not in c["precommit/python-compile"]["detail"]
    assert c["precommit/fail-before-line"]["status"] == cr.WARN          # record has no T3 line
    assert "livepath(2.6)=yes" in c["precommit/gate-map"]["detail"]
    put(repo, "MyTradingSys/system/sessions/%s.md" % SESSION, "status: open\nT3 fail-before: test_x failed on old code\n")
    c2 = by_name(cr.stage_precommit(make_ctx(repo, tmp_path, session=SESSION)))
    assert c2["precommit/fail-before-line"]["status"] == cr.PASS


def test_stage_2_2_precommit_powershell_parse_rows_use_the_shell_output(repo, tmp_path):
    put(repo, "scripts/dev/x.ps1", "Write-Output 1\n")
    seen = {}

    def script(cmd):
        seen["cmd"] = cmd
        return 0, "%s|2|Unexpected token\n" % cmd[-1]
    ctx = make_ctx(repo, tmp_path, run=fake_run(script), which=lambda n: "/fake/powershell" if n == "powershell" else None)
    c = by_name(cr.stage_precommit(ctx))
    assert c["precommit/powershell-parse"]["status"] == cr.FAIL and "Unexpected token" in c["precommit/powershell-parse"]["detail"]


# ------------------------------------------------------------------ 2.3 build
def _build_repo(repo):
    for rel in ("MyTradingSys/tests/t.py", "MyTradingSys/tests/docs/t.py", "tests/t.py", "scripts/dev/run_all_tests.py", "scripts/Build-Check.ps1"):
        put(repo, rel, "x = 1\n")


def _pass_script(cmd):
    joined = " ".join(cmd)
    if "run_all_tests" in joined:
        return 0, "ALL TESTS PASSED\n"
    if "Build-Check" in joined:
        return 0, "STATUS: PASS\n"
    if "pytest" in joined:
        return 0, "7 passed in 0.1s\n"
    return 0, ""


def test_stage_2_3_build_all_pass_and_commands_are_the_design_commands(repo, tmp_path):
    _build_repo(repo)
    run = fake_run(_pass_script)
    which = lambda n: "/fake/" + n if n in ("mvn", "powershell") else None  # noqa: E731
    checks = cr.stage_build(make_ctx(repo, tmp_path, run=run, which=which))
    assert [c["status"] for c in checks] == [cr.PASS] * 7
    joined = [" ".join(c) for c in run.calls]
    assert any("-DskipTests compile" in j for j in joined) and any(j.endswith("-q test") for j in joined)
    assert any("pytest MyTradingSys/tests --ignore=MyTradingSys/tests/docs" in j for j in joined)
    assert any("pytest MyTradingSys/tests/docs" in j for j in joined)
    assert not any("--quick" in j for j in joined if "run_all_tests" in j)
    assert (tmp_path / "out").exists()                                        # full output is kept, not tail only


def test_stage_2_3_build_failure_count_drop_missing_tool_and_quick(repo, tmp_path):
    _build_repo(repo)
    which = lambda n: "/fake/" + n if n in ("mvn", "powershell") else None  # noqa: E731

    def failing(cmd):
        if "MyTradingSys/tests" in cmd and "--ignore=MyTradingSys/tests/docs" in cmd:
            return 1, "a\nb\n1 failed, 3 passed\n"
        return _pass_script(cmd)
    c = by_name(cr.stage_build(make_ctx(repo, tmp_path, run=fake_run(failing), which=which)))
    assert c["build/pytest-math"]["status"] == cr.FAIL and "1 failed" in c["build/pytest-math"]["detail"]
    assert c["build/mvn-test"]["status"] == cr.PASS                           # a failure does not skip later stages

    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    (out / "cicd_run_2000-01-01.jsonl").write_text(json.dumps({"run": "old", "checks": [{"check": "build/pytest-math", "count": 10}]}) + "\n", encoding="utf-8")
    c = by_name(cr.stage_build(make_ctx(repo, tmp_path, run=fake_run(_pass_script), which=which)))
    assert c["build/pytest-math"]["status"] == cr.WARN and "10 -> 7" in c["build/pytest-math"]["detail"]

    c = by_name(cr.stage_build(make_ctx(repo, tmp_path, run=fake_run(_pass_script), which=lambda n: None)))
    assert c["build/mvn-compile"]["status"] == cr.SKIP and c["build/build-check"]["status"] == cr.SKIP
    run = fake_run(_pass_script)
    c = by_name(cr.stage_build(make_ctx(repo, tmp_path, run=run, which=which, quick=True)))
    assert c["build/mvn-test"]["status"] == cr.SKIP and not any("mvn" in x[0] for x in run.calls)
    assert any("--quick" in x for x in run.calls)


# ------------------------------------------------------------------ 2.4 contract
def test_stage_2_4_contract_bom_cyrillic_registry_and_file_index(repo, tmp_path):
    put(repo, "MyTradingSys/system/bom.md", b"\xef\xbb\xbfhello\n")
    put(repo, "MyTradingSys/research/cyr.md", "text " + chr(0x416) * 2 + "\n")
    put(repo, "MyTradingSys/system/newfile.md", "new\n")
    put(repo, cr.FILE_INDEX_REL, "| MyTradingSys/system/bom.md | doc | d | s | 2026-10-03 |\n")
    put(repo, cr.BUGS_REL, BUGS_HEAD + "| B001 | 2026-01-01 | CLOSED | MED | t | e | - |\n| B002 | 2026-01-01 | OPEN | MED | t | e | - |\n# END\n")
    put(repo, cr.INDEX_REL, "B002 | OPEN    | B002_x.md | s\nT077 | OPEN    | T077_x.md | s\n# END\n")
    c = by_name(cr.stage_contract(make_ctx(repo, tmp_path, session=SESSION)))
    assert c["contract/bom"]["status"] == cr.FAIL and "bom.md" in c["contract/bom"]["detail"]
    assert c["contract/cyrillic"]["status"] == cr.FAIL and "cyr.md:2" in c["contract/cyrillic"]["detail"]
    assert "cyr.md" in c["contract/non-ascii"]["detail"] and c["contract/non-ascii"]["status"] == cr.PASS
    reg = c["contract/registry"]
    assert reg["status"] == cr.FAIL
    for needle in ("B001 CLOSED with no receipt", "B002 OPEN with no items/ file", "T077 in INDEX but no BUGS row"):
        assert needle in reg["detail"]
    assert c["contract/file-index"]["status"] == cr.WARN and "newfile.md" in c["contract/file-index"]["detail"]
    assert c["contract/session-record"]["status"] == cr.WARN
    assert c["contract/rule-citations"]["status"] == cr.SKIP and c["contract/forbidden-phrases"]["status"] == cr.SKIP


def test_stage_2_4_contract_clean_change_set_passes(repo, tmp_path):
    put(repo, cr.BUGS_REL, BUGS_HEAD + "| B001 | 2026-01-01 | CLOSED | MED | t | e | abc1234 |\n# END\n")
    put(repo, cr.INDEX_REL, "# END\n")
    commit_all(repo, "registry")
    put(repo, "MyTradingSys/system/ok.md", "ok\n")
    put(repo, cr.FILE_INDEX_REL, "| MyTradingSys/system/ok.md | doc | d | s | 2026-10-03 |\n")
    put(repo, "MyTradingSys/system/sessions/%s.md" % SESSION, "status: open\nstarted: x\nmodel: m\n")
    c = by_name(cr.stage_contract(make_ctx(repo, tmp_path, session=SESSION)))
    assert [c[k]["status"] for k in ("contract/bom", "contract/cyrillic", "contract/registry", "contract/file-index", "contract/session-record")] == [cr.PASS] * 5


# ------------------------------------------------------------------ 2.5 artifact
def _artifact_repo(repo):
    put(repo, "DSA_SESSION_PROMPT.md", "prompt v1\n")
    put(repo, "scripts/core/mode.ps1", "mode v1\r\n")
    commit_all(repo, "critical")


def test_stage_2_5_artifact_match_no_baseline_and_drift(repo, tmp_path):
    _artifact_repo(repo)
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path)))
    assert c["artifact/baseline"]["status"] == cr.WARN and "NO-BASELINE" in c["artifact/baseline"]["detail"]

    cr.write_baseline(make_ctx(repo, tmp_path))
    commit_all(repo, "baseline")
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path)))
    assert c["artifact/DSA_SESSION_PROMPT.md"]["status"] == cr.PASS and "MATCH" in c["artifact/DSA_SESSION_PROMPT.md"]["detail"]
    assert c["artifact/scripts/core/mode.ps1"]["status"] == cr.PASS
    assert c["artifact/MyTradingSys/runtime/mts_math.py"]["status"] == cr.WARN       # critical path absent from this baseline

    put(repo, "DSA_SESSION_PROMPT.md", "prompt v2\n")
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path)))
    assert c["artifact/DSA_SESSION_PROMPT.md"]["status"] == cr.FAIL and "DRIFT-UNAPPROVED" in c["artifact/DSA_SESSION_PROMPT.md"]["detail"]
    # post-commit mode compares committed bytes: the uncommitted edit is not what HEAD holds
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path, profile="postclose")))
    assert c["artifact/DSA_SESSION_PROMPT.md"]["status"] == cr.PASS

    cr.write_baseline(make_ctx(repo, tmp_path))                                   # baseline updated in the same change set
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path)))
    assert c["artifact/DSA_SESSION_PROMPT.md"]["status"] == cr.PASS


def test_stage_2_5_artifact_drift_with_stale_baseline_in_change_set_is_a_warn(repo, tmp_path):
    _artifact_repo(repo)
    cr.write_baseline(make_ctx(repo, tmp_path))
    commit_all(repo, "baseline")
    put(repo, "DSA_SESSION_PROMPT.md", "prompt v3\n")
    doc = json.loads((repo / cr.CRITICAL_REL).read_text(encoding="utf-8"))
    doc["updated_utc"] = "2026-10-03T06:00:00Z"                                   # baseline touched but blob not refreshed
    put(repo, cr.CRITICAL_REL, json.dumps(doc, indent=1) + "\n")
    c = by_name(cr.stage_artifact(make_ctx(repo, tmp_path)))
    assert c["artifact/DSA_SESSION_PROMPT.md"]["status"] == cr.WARN and "DRIFT:" in c["artifact/DSA_SESSION_PROMPT.md"]["detail"]


# ------------------------------------------------------------------ 2.6 live path
def test_stage_2_6_livepath_skips_when_no_live_file_changed(repo, tmp_path):
    put(repo, "MyTradingSys/research/note.md", "n\n")
    checks = cr.stage_livepath(make_ctx(repo, tmp_path))
    assert len(checks) == 1 and checks[0]["status"] == cr.SKIP


def test_stage_2_6_livepath_gate_checks_l1_to_l8(repo, tmp_path):
    put(repo, "MyTradingSys/execution/auto_trader.py", "x = 1\n")
    commit_all(repo, "live module")
    put(repo, "MyTradingSys/execution/auto_trader.py", "x = 2\n")                  # in-place edit of a tracked live file
    put(repo, "MyTradingSys/execution/journal/j.json", "{}\n")                    # runtime state in the change set
    c = by_name(cr.stage_livepath(make_ctx(repo, tmp_path)))
    assert c["livepath/gate"]["status"] == cr.PASS and "auto_trader.py" in c["livepath/gate"]["detail"]
    assert c["livepath/L1-one-writer"]["status"] == cr.WARN
    assert c["livepath/L2-staging"]["status"] == cr.WARN                          # no process list: staging cannot be proven
    assert c["livepath/L4-tests"]["status"] == cr.WARN and c["livepath/L5-review"]["status"] == cr.WARN
    assert c["livepath/L7-restart"]["status"] == cr.SKIP
    assert c["livepath/L8-touch-list"]["status"] == cr.FAIL and "journal" in c["livepath/L8-touch-list"]["detail"]


def test_stage_2_6_livepath_evidence_present_passes(repo, tmp_path):
    put(repo, "MyTradingSys/execution/auto_trader.py", "x = 1\n")
    commit_all(repo, "live module")
    put(repo, "MyTradingSys/execution/auto_trader.py", "x = 2\n")
    put(repo, "MyTradingSys/execution/test_auto_trader.py", "# auto_trader: restart reset, deposit transfer, URLError\n")
    put(repo, "MyTradingSys/system/sessions/%s.md" % SESSION,
        "status: open\nno running process imports auto_trader.py\nhash before/after and diff read\nreview: S-OPUS-1\n")
    put(repo, cr.SUPERVISOR_LOG_REL, "%s owns execution/\n" % SESSION)
    c = by_name(cr.stage_livepath(make_ctx(repo, tmp_path, session=SESSION)))
    for k in ("L1-one-writer", "L2-staging", "L3-proof", "L4-tests", "L5-review", "L6-auto-pause", "L8-touch-list"):
        assert c["livepath/" + k]["status"] == cr.PASS, (k, c["livepath/" + k])


def test_stage_2_6_livepath_in_place_edit_of_a_running_file_fails(repo, tmp_path):
    put(repo, "MyTradingSys/execution/position_manager.py", "x = 1\n")
    commit_all(repo, "live module")
    put(repo, "MyTradingSys/execution/position_manager.py", "x = 2\n")
    run = fake_run(lambda cmd: (0, "4242|2026-10-03T01:00:00Z|python MyTradingSys/execution/position_manager.py\n"))
    ctx = make_ctx(repo, tmp_path, run=run, which=lambda n: "/fake/powershell" if n == "powershell" else None)
    c = by_name(cr.stage_livepath(ctx))
    assert c["livepath/L2-staging"]["status"] == cr.FAIL and "position_manager.py" in c["livepath/L2-staging"]["detail"]


# ------------------------------------------------------------------ 2.7 release
def _row(stage, status, checks=()):
    return {"stage": stage, "status": status, "checks": list(checks)}


def test_stage_2_7_release_verdict_lines_and_pathspec(repo, tmp_path):
    assert cr.release_verdict([_row("2.3", cr.PASS)]) == "RELEASE: READY"
    warn = _row("2.4", cr.WARN, [cr.ck("a", cr.WARN, "x"), cr.ck("b", cr.WARN, "y")])
    assert cr.release_verdict([warn]) == "RELEASE: READY-WITH-WARN 2"
    assert cr.release_verdict([_row("2.5", cr.FAIL), _row("2.3", cr.CRASH), warn]) == "RELEASE: NOT-READY 2.3 2.5"
    assert cr.release_verdict([_row("2.1", cr.FAIL)]) == "RELEASE: READY"          # intake is advisory, not a gate

    put(repo, "MyTradingSys/system/a.md", "a\n")
    put(repo, cr.BUILD_REPORT_REL, "dirty\n")                                      # allowlisted, never in a pathspec
    ctx = make_ctx(repo, tmp_path, session=SESSION)
    ctx.rows = [_row("2.3", cr.PASS)]
    c = by_name(cr.stage_release(ctx))
    assert "RELEASE: READY" in ctx.emitted
    ps = c["release/pathspec"]
    assert ps["pathspec"] == ["MyTradingSys/system/a.md"] and "-A" not in ps["detail"].replace("never add -A", "")
    assert "MTS-Session: " + SESSION in ps["detail"]


# ------------------------------------------------------------------ 2.8 post-close
def test_stage_2_8_postclose_drift_receipts_trailer_and_tag(repo, tmp_path):
    put(repo, cr.BUGS_REL, BUGS_HEAD + "| B001 | 2026-01-01 | OPEN | MED | t | e | - |\n# END\n")
    first = commit_all(repo, "open")
    G(repo, "tag", "-f", "last-snapshot")
    put(repo, cr.BUGS_REL, BUGS_HEAD + "| B001 | 2026-01-01 | CLOSED | MED | t | e | %s and d3adbe3 |\n# END\n" % first[:7])
    put(repo, "MyTradingSys/system/sessions/%s.md" % SESSION, "status: closed\ncommits: abc\n")
    put(repo, "MyTradingSys/system/added.md", "a\n")
    G(repo, "add", "-A")
    G(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "close B001\n\nMTS-Session: %s" % SESSION)
    put(repo, "forgotten.txt", "left behind\n")
    c = by_name(cr.stage_postclose(make_ctx(repo, tmp_path, profile="postclose")))
    assert c["postclose/P1-drift"]["status"] == cr.WARN and "forgotten.txt" in c["postclose/P1-drift"]["detail"]
    assert c["postclose/P3-registry"]["status"] == cr.WARN and "d3adbe3" in c["postclose/P3-registry"]["detail"]
    assert first[:7] not in c["postclose/P3-registry"]["detail"]                   # the resolvable hash is not flagged
    assert c["postclose/P4-session"]["status"] == cr.PASS
    assert c["postclose/P5-file-index"]["status"] == cr.SKIP                        # no 03_FILE_INDEX in this temp repo
    assert c["postclose/P6-tag"]["status"] == cr.WARN and "1 commit" in c["postclose/P6-tag"]["detail"]
    assert c["postclose/P7-live-import"]["status"] == cr.SKIP
    assert c["postclose/L7-restart"]["status"] == cr.SKIP
    G(repo, "tag", "-f", "last-snapshot")
    c = by_name(cr.stage_postclose(make_ctx(repo, tmp_path, profile="postclose")))
    assert c["postclose/P6-tag"]["status"] == cr.PASS


def test_stage_2_8_postclose_missing_trailer_warns(repo, tmp_path):
    c = by_name(cr.stage_postclose(make_ctx(repo, tmp_path, profile="postclose")))
    assert c["postclose/P4-session"]["status"] == cr.WARN and "trailer" in c["postclose/P4-session"]["detail"]


# ------------------------------------------------------------------ 2.9 failure handling and runner
def test_stage_2_9_failures_append_one_warn_line_per_failure(repo, tmp_path):
    ctx = make_ctx(repo, tmp_path)
    ctx.rows = [_row("2.4", cr.FAIL, [cr.ck("contract/bom", cr.FAIL, "x.md"), cr.ck("contract/ok", cr.PASS, "fine")]),
                _row("2.3", cr.WARN, [cr.ck("build/pytest-math", cr.WARN, "count dropped")])]
    checks = cr.stage_failures(ctx)
    lines = (tmp_path / "out" / "cicd_warn.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert set(first) == {"utc", "run", "stage", "check", "severity", "detail", "path"} and first["severity"] == cr.FAIL
    assert "1 FAIL/CRASH, 1 WARN" in checks[0]["detail"]
    clean = make_ctx(repo, tmp_path)
    clean.rows = [_row("2.3", cr.PASS, [cr.ck("a", cr.PASS)])]
    assert cr.stage_failures(clean)[0]["status"] == cr.PASS
    assert len((tmp_path / "out" / "cicd_warn.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_stage_2_9_a_crashing_stage_is_a_row_and_the_run_continues(repo, tmp_path):
    ctx = make_ctx(repo, tmp_path)

    def boom(c):
        raise RuntimeError("stage exploded")
    cr.run_stage(ctx, "2.1", "intake", boom)
    cr.run_stage(ctx, "2.4", "contract", lambda c: [cr.ck("contract/x", cr.PASS, "fine")])
    assert [r["status"] for r in ctx.rows] == [cr.CRASH, cr.PASS]
    assert "stage exploded" in ctx.rows[0]["evidence"] and "Traceback" in ctx.rows[0]["checks"][0]["detail"]
    rows = [json.loads(l) for l in ctx.day_file("jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["stage"] for r in rows] == ["2.1", "2.4"]                              # one JSONL row per stage
    assert set(rows[0]) >= {"utc", "run", "profile", "stage", "name", "status", "evidence", "checks", "seconds"}
    assert any(line.startswith("CRASH|2.1") for line in ctx.emitted)
    assert cr.exit_code(ctx.rows) == 2


def test_exit_code_is_data_0_pass_1_warn_2_fail():
    assert cr.exit_code([_row("2.1", cr.PASS, [cr.ck("a", cr.PASS)]), _row("2.2", cr.SKIP, [cr.ck("b", cr.SKIP)])]) == 0
    assert cr.exit_code([_row("2.1", cr.WARN, [cr.ck("a", cr.WARN)])]) == 1
    assert cr.exit_code([_row("2.1", cr.WARN, [cr.ck("a", cr.WARN)]), _row("2.2", cr.FAIL, [cr.ck("b", cr.FAIL)])]) == 2


def test_unwritable_receipt_prints_the_row_and_continues(repo, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a directory\n", encoding="utf-8")
    ctx = cr.Ctx(repo=repo, out_dir=blocker / "sub", which=lambda n: None, emit=lambda s: None)
    out = []
    ctx.emit = out.append
    cr.run_stage(ctx, "2.4", "contract", lambda c: [cr.ck("contract/x", cr.PASS, "fine")])
    assert ctx.rows[0]["status"] == cr.PASS
    assert any("RECEIPT-WRITE-FAILED" in s for s in out) and any('"stage": "2.4"' in s for s in out)


def test_run_profile_runs_profile_stages_in_order_and_never_raises(repo, tmp_path):
    ctx = make_ctx(repo, tmp_path, profile="postclose")
    code = cr.run_profile(ctx)
    assert [r["stage"] for r in ctx.rows] == ["2.8", "2.9"] and code in (0, 1, 2)
    assert cr.PROFILES["desktop"] == ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.9"]
    assert [s[0] for s in cr.STAGES] == ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9"]


# ------------------------------------------------------------------ baseline (critical_files.json)
def test_baseline_records_git_blob_ids_not_raw_sha256_and_eol(repo, tmp_path):
    put(repo, "DSA_SESSION_PROMPT.md", b"line one\r\nline two\r\n")
    put(repo, "scripts/core/mode.ps1", b"a\nb\n")
    put(repo, "scripts/core/stop-day.ps1", b"a\r\nb\n")
    doc = cr.build_baseline(make_ctx(repo, tmp_path, session=SESSION))
    files = {f["path"]: f for f in doc["files"]}
    assert set(files) == {"DSA_SESSION_PROMPT.md", "scripts/core/mode.ps1", "scripts/core/stop-day.ps1"}
    for rel, f in files.items():
        assert f["blob"] == G(repo, "hash-object", "--", rel) and len(f["blob"]) == 40
        assert len(f["sha256_8"]) == 8 and f["approved_commit"] == "pending"
    assert files["DSA_SESSION_PROMPT.md"]["eol"] == "CRLF" and files["scripts/core/mode.ps1"]["eol"] == "LF"
    assert files["scripts/core/stop-day.ps1"]["eol"] == "MIXED"
    assert doc["observed_by"] == SESSION and doc["updated_utc"].endswith("Z")


def test_critical_paths_match_the_nine_files_in_the_dsa_prompt():
    assert len(cr.CRITICAL_PATHS) == 9
    dsa = (Path(__file__).resolve().parents[2] / "DSA_SESSION_PROMPT.md")
    if dsa.exists():
        text = dsa.read_text(encoding="utf-8", errors="replace")
        for p in cr.CRITICAL_PATHS:
            assert p in text


def test_seeded_baseline_file_shape_if_present():
    fp = Path(__file__).resolve().parents[2] / cr.CRITICAL_REL
    if not fp.exists():
        pytest.skip("baseline not seeded in this checkout")
    doc = json.loads(fp.read_text(encoding="utf-8"))
    assert doc["updated_utc"].endswith("Z") and [f["path"] for f in doc["files"]] == cr.CRITICAL_PATHS
    for f in doc["files"]:
        assert set(f) == {"path", "blob", "sha256_8", "eol", "approved_by", "approved_commit"}
        assert len(f["blob"]) == 40 and int(f["blob"], 16) >= 0 and f["eol"] in ("CRLF", "LF", "MIXED")
