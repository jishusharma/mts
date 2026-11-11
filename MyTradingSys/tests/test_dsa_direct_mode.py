import sys; sys.dont_write_bytecode = True
"""test_dsa_direct_mode.py - guards DSA direct mode (operator 2026-10-08) and the two processes that feed every DSA boot.

Expected values come from the operator's request of 2026-10-08, not from the code under test:
  - DSA runs commands itself through AIBridge, inside the project working tree, and may delete there.
  - A 100 KB to 250 KB session paste must work: no split rule, no size alarm below that.
  - The session paste (Dumps/SESSION_PASTE.txt) and the news path (sync.py news) are never lost.
MTS_REPO_ROOT points the checks at another tree (used to prove the tests fail on the pre-change files).
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
PROMPT = ROOT / "DSA_SESSION_PROMPT.md"
START = ROOT / "scripts" / "start-session.ps1"
MANIFEST = ROOT / "MyTradingSys" / "runtime" / "SESSION_MANIFEST.json"
LANE = ROOT / "MyTradingSys" / "system" / "AIBRIDGE_LANE.md"
SYNC_DIR = ROOT / "scripts" / "dev"


def text(p):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


# ------------------------------------------------------------------ the prompt
def test_prompt_has_direct_mode_section_first():
    s = text(PROMPT)
    assert "## 0. DIRECT MODE" in s
    assert s.index("## 0. DIRECT MODE") < s.index("## 1. ROLE")
    for needle in ("0.2 Reach", "0.3 The floor", "0.4 Delete is allowed", "0.8 PROTECTED PROCESSES"):
        assert needle in s, needle


def test_prompt_lets_dsa_run_commands_and_delete_inside_the_tree():
    s = text(PROMPT)
    assert "You run commands yourself" in s
    assert "Never ask the operator to run, paste or read back" in s
    assert "read, write, create, move, copy, delete and run anything" in s
    assert "Outside the roots you have nothing" in s       # permission = the project working tree only


def test_prompt_drops_the_old_restrictions():
    s = text(PROMPT)
    assert "The user runs all commands. The AI issues them" not in s
    assert "A paste over roughly 150 KB should be split" not in s
    assert "Paste size is not a limit" in s


def test_prompt_keeps_numbered_sections_other_docs_cite():
    s = text(PROMPT)
    for n in range(1, 14):
        assert re.search(r"^## %d[a-z]?\. " % n, s, re.M), "section %d missing" % n
    assert "Critical files:" in s                          # critical_files.json cites this list
    assert "## 11. CURRENT STATE" in s and "## 5d. DSA DOES THIS DIRECTLY" in s


def test_prompt_names_both_protected_processes():
    s = text(PROMPT)
    assert "scripts\\start-session.ps1" in s and "Dumps\\SESSION_PASTE.txt" in s
    assert "python scripts/dev/sync.py news" in s
    boot = s[s.index("## 3. BOOT PROCEDURE"):s.index("## 4. READING LARGE FILES")]
    assert "sync.py news" in boot                          # boot step 12 still reads the news


# ------------------------------------------------------------------ the session paste
def test_start_session_header_matches_prompt_v2():
    # 2026-10-14: the paste header said "one block per reply", "writes run only on the operator's click",
    # "stop if build is not PASS" and claimed to win over the prompt; v2 (bridge v0.7) says the opposite.
    s = text(START)
    for old in ("COORDINATOR or WORKER", "If build status is not PASS", "this block wins",
                "run only on the operator's click", "One block per reply", "ask for one at a time",
                "One decision per turn", "act on them, then write yours"):
        assert old not in s, old
    for new in ("section 0 wins", "task=mts-boot", "dsa.py boot", "Up to 6 blocks per reply", "counts only for the host"):
        assert new in s, new


def test_start_session_still_writes_the_paste_from_the_manifest():
    s = text(START)
    assert "Dumps\\SESSION_PASTE.txt" in s
    assert "SESSION_MANIFEST.json" in s
    assert "boot_files" in s and "boot_supplemental" in s


def test_start_session_points_at_the_news_instead_of_pasting_it():
    # operator 2026-10-10: the pasted 72 h news was 61 KB of a 189 KB paste; DSA runs sync.py news itself (0.8b)
    s = text(START)
    assert "### news: NOT PASTED" in s and "sync.py news 72" in s
    assert "news unavailable" in s                         # the pointer says what to report if the command fails
    assert "sync.py') news" not in s                       # the paste builder no longer runs it
    assert "Select-Object -First 30" in s                  # dirty-file list is capped


def test_supervisor_inbox_is_a_pointer_in_the_manifest():
    import json
    m = json.loads(text(ROOT / "MyTradingSys" / "runtime" / "SESSION_MANIFEST.json"))
    rows = [f for f in m["boot_supplemental"] if f["path"].endswith("SUPERVISOR_INBOX.md")]
    assert rows and rows[0]["read"] == "pointer"


def test_paste_size_alarms_sit_above_250_kb():
    ps = text(START)
    m = re.search(r"\$sizeKb -gt (\d+)", ps)
    assert m and int(m.group(1)) >= 250
    sched = text(ROOT / "scripts" / "sched" / "check_paste_size.py")
    m = re.search(r"LIMIT = (\d+) \* 1024", sched)
    assert m and int(m.group(1)) >= 250


def test_manifest_boots_the_prompt_and_every_repo_file_it_lists_exists():
    m = json.loads(text(MANIFEST))
    paths = [f["path"] for f in m["boot_files"] + m["boot_supplemental"]]
    assert "DSA_SESSION_PROMPT.md" in paths and "USER.md" in paths
    # Dumps/ and runtime_data/ are gitignored: they exist on the live machine only.
    missing = [p for p in paths if not p.startswith(("Dumps/", "runtime_data/")) and not (ROOT / p).exists()
               and p not in ("MyTradingSys/runtime/BUILD_REPORT.md", "MyTradingSys/runtime/session_state.json",
                             "MyTradingSys/runtime/current_market_state.md", "MyTradingSys/runtime/state_code.json",
                             "MyTradingSys/runtime/NEXT_SESSION_HANDOFF.md")]
    assert missing == []


@pytest.mark.skipif(not shutil.which("powershell"), reason="needs Windows PowerShell to parse")
@pytest.mark.parametrize("rel", ["scripts/start-session.ps1", "scripts/dev/bridge_selftest.ps1"])
def test_ps1_files_parse(rel):
    cmd = ("$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$t,[ref]$e);"
           "exit $e.Count" % str(ROOT / rel).replace("'", "''"))
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# ------------------------------------------------------------------ news works in the live tree
def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def test_sync_news_runs_inside_a_live_tree_and_shows_the_result_line(monkeypatch):
    sys.path.insert(0, str(SYNC_DIR))
    import sync
    tmp = Path(tempfile.mkdtemp())
    try:
        origin = tmp / "origin.git"
        sh(tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        live = tmp / "live"
        sh(tmp, "clone", "-q", str(origin), str(live))
        sh(live, "config", "user.email", "t@t")
        sh(live, "config", "user.name", "t")
        (live / "a.md").write_text("a\n", newline="\n")
        sh(live, "add", "a.md")
        sh(live, "commit", "-q", "-m", "feature one", "-m", "Result: the number is 7")
        sh(live, "push", "-q", "origin", "HEAD:fast-track")
        (live / sync.LIVE_MARKER).write_text("x\n")            # this checkout is now a live tree
        monkeypatch.chdir(live)                                # sync.main resolves the repo from cwd
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = sync.main(["news", "1"])
        assert rc == 0
        assert "feature one" in buf.getvalue() and "Result: the number is 7" in buf.getvalue()
        with pytest.raises(sync.SyncError):                    # ship stays refused there
            sync.refuse_live(live)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ the bridge side
def test_lane_doc_states_the_direct_mode_contract():
    s = text(LANE)
    assert "delete" in s.lower() and "Roots:" in s
    assert "262144 bytes" in s and "# AIRUN" in s
    assert "bridge_selftest.ps1" in s and (ROOT / "scripts" / "dev" / "bridge_selftest.ps1").exists()
    assert "allowlist" not in s.lower().split("## what mts never asks")[0].split("## direct mode")[1]


def test_prompt_matches_the_bridge_call_format_and_refusals():
    s = text(PROMPT)
    assert "# AIRUN cwd=" in s and "no result seen" in s
    assert "262144 bytes" in s
    assert "Start-Process" in s and "$env:" in s            # named as refused, not recommended
    assert "starts with Start-Process" not in s
    assert "$env:" not in text(ROOT / "scripts" / "dev" / "bridge_selftest.ps1").replace("No $env: use", "")


def test_prompt_carries_the_bridge_0_7_4_rules():
    # dsabr-c5 (FIX_PLAN section 2): async queue, final-answer-only fences, exit codes, wake-up notice
    raw = text(PROMPT)
    assert raw.splitlines()[0].startswith("# SESSION PROMPT - DSA (DeepSeek + AIBridge)")
    s = " ".join(raw.split())   # line wraps do not matter
    for sentence in (
        "Write AIRUN fences only in your final answer, never while thinking.",
        "the bridge ignores fences inside the thinking panel",
        'NOT RUN: duplicate of block K',
        "append a `Write-Output 'again'` line",
        "The bridge is a queue.",
        "your next input is their [AIRUN RESULT] (or BATCH) message",
        "Never send a status-check block while a task runs; never put two gate or ship tasks in one reply",
        "Per chain the bridge runs 200 blocks, then hands-free turns off and says so.",
        "A step passes on its own exit code.",
        "`; exit $LASTEXITCODE`",
        'Never add `Write-Output "EXIT_CODE=$LASTEXITCODE"` as the last line',
        "Never run the gate yourself: the ship runs it",
        "`TASK RESULT: PASS|FAIL` plus the ship step's own output; a docs-only ship runs no gate, and that is normal",
        "PowerShell keeps going after a non-terminating error",
        "`$ErrorActionPreference='Stop'` as line 2",
        "[AIRUN NOTICE] your last reply ended without a final answer",
        "A second notice in a row turns hands-free off",
        "non-zero exit of ANY command, a read included",
        "A search that may find nothing (rg, findstr) ends with `; exit 0`",
    ):
        assert sentence in s, sentence


# ------------------------------------------------------------------ how DSA works (operator 2026-11-03): FIRST section, one test flow
SHIP_LINES = ['{"steps":[',
              '{"name":"ship","cmd":"python scripts/dev/sync.py ship --release <slug>","cwd":"<WORKTREE>","timeout_s":1100,"show":12},',
              '{"name":"where","cmd":"python scripts/dev/sync.py where","cwd":"<WORKTREE>","timeout_s":120,"show":4}',
              ']}']
SHIP_BLOCK = "\n".join(SHIP_LINES)


def test_prompt_top_holds_sections_a_to_f_and_the_ship_block():
    s = text(PROMPT)
    head = "## FIRST: HOW YOU WORK (read this before anything else)"
    assert head in s and s.index(head) < s.index("## 00. SAME LEVEL"), "FIRST must sit before section 00"
    assert s.startswith("# SESSION PROMPT")
    assert s.index(head) < 400, "FIRST must be directly under the title line"
    first = s[s.index(head):s.index("## 00. SAME LEVEL")]
    for letter, title in (("A", "ACT THROUGH BLOCKS"), ("B", "MAX WORK PER REPLY"), ("C", "NO REPEATS"), ("D", "THE TEST FLOW, ONE WAY ONLY"),
                          ("E", "TRUNK CI RED IS NOT YOUR TREE"), ("F", "THE OPERATOR ASKS MID-TASK")):
        assert "\n%s. %s" % (letter, title) in first, letter
    assert "# AIRUN task=inline timeout=1200\n" + SHIP_BLOCK in first
    for needle in ("python scripts/dev/ci_fail.py", "mts_signal.py read", "--fix-ci", "TASK: <id> | SLUG: <claim slug> | WT: <worktree> | STEP: <n> | NEXT: <next action>",
                   "NEVER run run_all_tests.py, task=mts-gate or task=mts-ship yourself", "Up to 6 blocks per reply"):
        assert needle in first, needle


def test_prompt_and_paste_never_tell_dsa_to_run_the_gate_as_a_step():
    for name, body in (("prompt", text(PROMPT)), ("paste header", text(START))):
        for ln in body.splitlines():
            if "task=mts-gate" in ln or "task=mts-ship" in ln:
                assert re.search(r"NEVER|Never", ln), "%s instructs a gate task: %s" % (name, ln)
    s = text(PROMPT)
    assert "One gate per task, always before a ship" not in s
    assert "(mts-ship runs it)" not in s


def test_mts_ship_playbook_is_one_ship_step_without_the_gate():
    spec = json.loads(text(ROOT / "scripts" / "aibridge" / "tasks" / "mts-ship.json"))
    cmds = [st["cmd"] for st in spec["steps"]]
    assert sum(c.startswith("python scripts/dev/sync.py ship") for c in cmds) == 1
    assert "python scripts/dev/sync.py ship --release {release}" in cmds
    assert not any("run_all_tests" in c for c in cmds) and "gate" not in [st["name"] for st in spec["steps"]]
    assert spec["params"]["release"] is None            # required: no release slug, no ship


def test_start_session_paste_header_carries_a_to_f_and_the_ship_block():
    s = text(START)
    for tag in ("- A. Act through blocks", "- B. Up to 6 blocks", "- C. No repeats", "- D. One test flow", "- E. Trunk CI red", "- F. Operator asks mid-task"):
        assert tag in s, tag
    assert all(ln in s for ln in SHIP_LINES[1:3]), "plan lines"
    assert "ci_fail.py" in s and "Prompt source:" in s


@pytest.mark.skipif(not shutil.which("powershell"), reason="needs Windows PowerShell")
def test_paste_takes_the_prompt_from_origin_fast_track_not_the_stale_tree(tmp_path):
    m = re.search(r"^function Get-PromptFromTrunk \{.*?^\}\n", text(START), re.S | re.M)
    assert m, "Get-PromptFromTrunk missing"
    origin, tree = tmp_path / "origin.git", tmp_path / "tree"
    sh(tmp_path, "init", "-q", "--bare", str(origin))
    sh(tmp_path, "init", "-q", str(tree)); sh(tree, "checkout", "-q", "-b", "fast-track")
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        sh(tree, "config", k, v)
    (tree / "DSA_SESSION_PROMPT.md").write_text("TRUNK PROMPT v2\n", encoding="utf-8", newline="\n")
    sh(tree, "add", "."); sh(tree, "commit", "-q", "-m", "x")
    sh(tree, "remote", "add", "origin", str(origin)); sh(tree, "push", "-q", "origin", "fast-track")
    (tree / "DSA_SESSION_PROMPT.md").write_text("STALE PROMPT v1\n", encoding="utf-8", newline="\n")   # the lagging working file
    outp = tmp_path / "out.json"
    ps = ("$root='%s'; %s; $r = Get-PromptFromTrunk -Path 'DSA_SESSION_PROMPT.md'; "
          "[IO.File]::WriteAllText('%s', (ConvertTo-Json $r), (New-Object Text.UTF8Encoding($false)))") % (tree, m.group(0), outp)
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    got = json.loads(outp.read_text(encoding="utf-8"))
    assert got["Text"] == "TRUNK PROMPT v2" and got["Source"].startswith("origin/fast-track @ "), got
    # no remote ref at all: the working file is used and the line says so
    sh(tree, "remote", "remove", "origin"); sh(tree, "update-ref", "-d", "refs/remotes/origin/fast-track")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    got = json.loads(outp.read_text(encoding="utf-8"))
    assert got["Text"] is None and got["Source"].startswith("WORKING FILE"), got


def test_inline_plan_in_prompt_is_multiline_short_valid_json_with_doubled_backslashes():
    # operator audit 2026-11-03: bad_task_spec (plans cut mid-string, Set-Location in the body, single backslashes in cwd)
    first = text(PROMPT)
    block = first[first.index("# AIRUN task=inline timeout=1200\n") + len("# AIRUN task=inline timeout=1200\n"):]
    plan = block[:block.index("\n```")]
    lines = plan.split("\n")
    assert len(lines) >= 4 and all(len(ln) < 200 for ln in lines), [len(ln) for ln in lines]
    assert not any("Set-Location" in ln for ln in lines)
    wt = "C:\\Users\\E-ngineers\\IdeaProjects\\mts-dsa-host-1103-1200"          # the path as the model must write it in JSON: doubled
    doc = json.loads(plan.replace("<WORKTREE>", wt.replace("\\", "\\\\")).replace("<slug>", "my-slug"))
    assert [st["name"] for st in doc["steps"]] == ["ship", "where"]
    assert doc["steps"][0]["cwd"] == wt and doc["steps"][0]["cmd"].endswith("--release my-slug")
    with pytest.raises(ValueError):                                            # single backslashes are invalid JSON
        json.loads(plan.replace("<WORKTREE>", wt).replace("<slug>", "s"))
    flat = " ".join(first.split())
    for needle in ("every backslash in <WORKTREE> is doubled", "The body is JSON only, no Set-Location line",
                   "bad_task_spec means the plan arrived cut or malformed: it ran nothing"):
        assert needle in flat, needle
    assert "a task=inline body is JSON only" in flat                              # 9a says its Set-Location rule is for plain blocks


def test_5a_closes_the_source_before_the_one_ship():
    s = " ".join(text(PROMPT).split())
    a, c, b = s.index("7. Close the source BEFORE the ship"), s.index("8. `python scripts/dev/dsa.py commit"), s.index("9. The inline ship block")
    assert a < c < b and "--files <exact paths> <card file>" in s and '--next "<card-id | stage | END: reason>"' in s and "A second ship within 10 minutes is allowed" in s and "ships itself" in s


def test_prompt_boots_then_waits_for_the_order():
    # operator 2026-11-07: one-command start (dsa.py start seed), quick init, then wait; DSA did too much on its own
    s = PROMPT.read_text(encoding="utf-8")
    first = s[: s.index("## 00.")]
    assert "G. BOOT, THEN WAIT FOR THE ORDER" in first
    assert "python scripts/dev/dsa.py start" in first
    assert "Pick the first task by section 5 and start" not in s
    assert "0.9 BRIDGE KNOW-HOW" in s and s.index("0.9 BRIDGE KNOW-HOW") < s.index("## 1. ROLE")
    assert "dsa.py start, paste the seed" in s                 # section 12 names the new start


# ------------------------------------------------------------------ self-consistency (operator 2026-11-11: "check everything")
# The prompt broke its own rules: 0b said line 2 of every block is the UTF-8 line while every example lacked it, two
# sections gave opposite ship-frequency rules, and boot step 4 parked a JAVA_HOME-only fix. These keep it consistent.
UTF8 = "$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'"


def _plain_blocks(s):
    out = []
    for m in re.finditer(r"```powershell\n(.*?)\n```", s, re.S):
        lines = m.group(1).split("\n")
        if lines[0].startswith("# AIRUN cwd="):
            out.append(lines)
    return out


def test_every_plain_block_in_the_prompt_follows_its_own_9a_order():
    blocks = _plain_blocks(text(PROMPT))
    assert len(blocks) >= 3
    for lines in blocks:
        cwd = re.match(r"# AIRUN cwd=(\S+)", lines[0]).group(1)
        body = lines[1:]
        if body and body[0] == "$ErrorActionPreference='Stop'":
            body = body[1:]
        assert body[0] == UTF8, lines
        assert body[1] == "Set-Location '%s'" % cwd, lines
        assert not any(ln.startswith("#") for ln in lines[1:]), lines
        assert all(len(ln) < 200 for ln in lines), lines


def test_prompt_states_each_contested_rule_once():
    s = " ".join(text(PROMPT).split())
    assert s.count("10 minutes") == 1, "ship frequency must be stated once (0b rule 4)"
    assert "once per 10 minutes" not in s
    assert "Take work only through" not in s           # 0b defers to the section 5 queue order


def test_prompt_boot_claims_match_the_seed():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dsa_for_prompt", ROOT / "scripts" / "dev" / "dsa.py")
    dsa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dsa)
    seed = dsa.seed_text("HOST")
    boot = text(PROMPT)
    boot = boot[boot.index("## 3. BOOT PROCEDURE"):boot.index("## 4. READING LARGE FILES")]
    assert "made the worktree, printed this file and ran `dsa.py boot`" in boot
    for needle in ("git worktree add", "Get-Content DSA_SESSION_PROMPT.md", "python scripts/dev/dsa.py boot"):
        assert needle in seed, needle
    if UTF8.replace("'", "") not in seed.replace("'", "").replace(" ", "").replace(";", "; "):
        assert "the seed's boot block, may lack line 3" in " ".join(text(PROMPT).split())


def test_prompt_fixes_java_from_java_home_instead_of_parking_it():
    boot = text(PROMPT)
    boot = " ".join(boot[boot.index("## 3. BOOT PROCEDURE"):boot.index("## 4. READING LARGE FILES")].split())
    assert r'$env:Path = "$env:JAVA_HOME\bin;" + $env:Path' in boot
    assert r'Test-Path "$env:JAVA_HOME\bin\java.exe"' in boot


def test_prompt_says_how_deepseek_thinking_works():
    s = " ".join(text(PROMPT).split())
    assert "Your thinking is NOT carried into the next turn" in s
    assert "Keep DeepThink on" in s and "think step by step" in s     # named as scaffolding not to add


def test_prompt_size_and_no_stale_state():
    raw = PROMPT.read_bytes()
    assert 20_000 <= len(raw) <= 50_000, len(raw)      # operator 2026-11-11: 25-50 KB is fine; rules first
    s = text(PROMPT)
    assert "Last DSA boot" not in s and "not yet recorded" not in s
    assert raw.decode("ascii")                          # ASCII only (PowerShell 5.1 pipes)


def test_review_fixes_1111_hold():
    # Haiku + Sonnet review of 47b513a2: hash line vs 9a, session end order, H vs the PATH post, flake defined
    s = " ".join(text(PROMPT).split())
    assert "add a `# again` line" not in s
    assert s.index("NEXT_SESSION.md overwritten and shipped (5e D) from your worktree") < s.index("Last, `python scripts/dev/dsa.py end`")
    assert "a fix outside the roots (a user PATH, an install)" in s
    assert "a failing test your change does not touch" in s and "is no flake" in s
    assert "the first line after Set-Location: `$OutputEncoding" in s
    assert "## 14. KEEP IN VIEW" in s
