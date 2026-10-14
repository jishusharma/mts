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
