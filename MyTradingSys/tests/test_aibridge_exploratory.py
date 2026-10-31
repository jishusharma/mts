import sys; sys.dont_write_bytecode = True
"""test_aibridge_exploratory.py - regression tests from the 2026-10-31 exploratory pass on the DSA bridge path.

Findings: MyTradingSys/research/dsa_bridge_exploratory_2026-10-31/FINDINGS.md. Every test marked xfail(strict=True) FAILS on the current
code (bridge 0.7.3) and names its finding; the fix cards are NOT shipped yet (a planning agent writes the plan in parallel). When a fix
ships the test XPASSes, strict mode turns that into a failure, and the fix author deletes the xfail mark. Tests without the mark are
guards for behaviour that already works (6 blocks once each, CRLF, per-occurrence duplicates).

Agent side: a scratch agent from the repo payload (aibridge_scratch.py) or run-task.ps1 directly. Extension side: the real loop.js and
content.js in headless Edge/Chrome against a fake chat page (aibridge_dom.py), virtual time. Windows only; skipped without the tools.
"""
import json
import os
import shutil
import subprocess
import tempfile

import pytest

from aibridge_dom import find_browser, run_page

IS_WIN = os.name == "nt" and shutil.which("powershell.exe") is not None
needs_ps = pytest.mark.skipif(not IS_WIN, reason="needs Windows PowerShell")
needs_browser = pytest.mark.skipif(not IS_WIN or not find_browser(), reason="needs Edge/Chrome headless on Windows")
FIX_PENDING = "fix card not shipped yet (2026-10-31); delete this mark when the fix lands"

ARM = "setTimeout(function(){ document.querySelector('.aibridge-ctl input').click(); }, 500);\n"
SAMPLE = ("window.extra = {st: []}; setInterval(function(){ var s=document.querySelector('.aibridge-ctl .st');"
          " window.extra.st.push([Math.round((Date.now()-window.T0)/1000), s?s.textContent:null]); }, 5000);\n")


# ---------------------------------------------------------------- agent side (exit codes)

@pytest.fixture
def tmp_path():
    """Own scratch dir: pytest's tmp_path root (Temp, pytest-of-user) is not writable on some hosts."""
    d = tempfile.mkdtemp(prefix="aib_exp_")
    try:
        yield __import__("pathlib").Path(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def agent():
    from aibridge_scratch import Scratch
    s = Scratch()
    yield s
    s.close()


@needs_ps
def test_E1_direct_block_native_exit_code_is_reported(agent):
    """A block whose last command is a native program that exits 3 must report exit=3 (today: exit=0, silent PASS)."""
    st, r = agent.run("cmd /c exit 3")
    assert st == 200 and r["exit"] == 3, r


@needs_ps
def test_E1_python_sys_exit_1_is_reported(agent):
    st, r = agent.run('python -c "import sys; sys.exit(1)"')
    assert st == 200 and r["exit"] == 1, r


def _run_task(tmp_path, name, steps=None, params=None, files=None):
    """run-task.ps1 in a scratch layout (base\\scripts, base\\tasks) the way agent.ps1 calls it."""
    from aibridge_scratch import PAYLOAD
    base = tmp_path / "bridge"
    (base / "scripts").mkdir(parents=True)
    (base / "tasks").mkdir()
    shutil.copy2(PAYLOAD / "scripts" / "run-task.ps1", base / "scripts" / "run-task.ps1")
    for f in (PAYLOAD / "tasks").glob("*.json"):
        shutil.copy2(f, base / "tasks" / f.name)
    for rel, text in (files or {}).items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    spec = {"name": name, "params": params or {}}
    if steps:
        spec["spec"] = {"steps": steps}
    sf = tmp_path / "spec.json"
    sf.write_text(json.dumps(spec), encoding="utf-8")
    ps = shutil.which("powershell.exe")
    p = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(base / "scripts" / "run-task.ps1"), str(sf)],
                       capture_output=True, text=True, timeout=180)
    return p.returncode, p.stdout


@needs_ps
def test_E2_task_inline_native_exit_1_is_FAIL(tmp_path):
    """task=inline, a step that is one native command exiting 1: result must be FAIL (today: PASS)."""
    rc, out = _run_task(tmp_path, "inline", steps=[{"name": "s", "cmd": 'python -c "import sys; sys.exit(1)"', "cwd": str(tmp_path)}])
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out, out
    assert rc == 1


@needs_ps
def test_E2_guard_task_inline_explicit_exit_1_is_FAIL(tmp_path):
    """Guard (works today): an explicit 'exit 1' step fails the task."""
    rc, out = _run_task(tmp_path, "inline", steps=[{"name": "s", "cmd": "exit 1", "cwd": str(tmp_path)}])
    assert "TASK RESULT: FAIL" in out and rc == 1, out


@needs_ps
def test_E3_mts_gate_crash_without_FAILED_line_is_FAIL(tmp_path):
    """The real mts-gate playbook (one step: python scripts/dev/run_all_tests.py --quick). A gate that crashes (traceback, exit 1,
    no 'FAILED: N step(s)' line) must be FAIL. Today: 'TASK RESULT: PASS', so DSA ships on a broken gate."""
    files = {"repo/scripts/dev/run_all_tests.py": "import sys\nprint('Traceback (most recent call last): boom')\nsys.exit(1)\n"}
    rc, out = _run_task(tmp_path, "mts-gate", params={"repo": str(tmp_path / "repo")}, files=files)
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out, out
    assert rc == 1


@needs_ps
def test_E3_mts_ship_does_not_ship_after_crashed_gate(tmp_path):
    """mts-ship = status, gate, ship, where. A crashed gate (exit 1) must stop the playbook before the ship step runs."""
    ship = tmp_path / "ship_ran.txt"
    files = {"repo/scripts/dev/run_all_tests.py": "import sys\nprint('Traceback boom')\nsys.exit(1)\n",
             "repo/scripts/dev/sync.py": "open(r'%s', 'w').write('shipped')\n" % ship}
    subprocess.run(["git", "init", "-q", str(tmp_path / "repo")], check=False)
    _run_task(tmp_path, "mts-ship", params={"repo": str(tmp_path / "repo")}, files=files)
    assert not ship.exists(), "ship step ran after the gate crashed"


# ---------------------------------------------------------------- extension side (real content.js in headless Edge)

def _ps_blocks(n):
    return [("# AIRUN cwd=C:\\x\nWrite-Output b%d" % i) for i in range(1, n + 1)]


@needs_browser
def test_guard_six_blocks_run_once_each_seventh_not_run():
    js = ARM + "setTimeout(function(){ window.dsaReply('go', %s); }, 8000); setTimeout(window.finish, 60000);" % json.dumps(_ps_blocks(7))
    r = run_page(js, 70000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun"]
    assert runs == ["Write-Output b%d" % i for i in range(1, 7)], runs
    # the fake chat never answers, so 0.7.4 adds a wake-up notice after 45 s: the BATCH is the first post and the only one
    assert sum(1 for p in r["posted"] if "[AIRUN BATCH]" in p["text"]) == 1 and "blocks_seen=7 blocks_run=6 not_run=1" in r["posted"][0]["text"]
    assert "NOT RUN: over the per-reply cap" in r["posted"][0]["text"]


@needs_browser
def test_guard_crlf_block_lines_survive_and_a_duplicate_in_one_reply_is_not_run():
    js = ARM + r"""
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\r\nWrite-Output C1\r\nWrite-Output C2\r\n', '# AIRUN cwd=C:\\x\nWrite-Output DUP', '# AIRUN cwd=C:\\x\nWrite-Output DUP']); }, 8000);
setTimeout(window.finish, 40000);
"""
    r = run_page(js, 50000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun"]
    # 0.7.4 (dsabr-c1): a second identical block in ONE reply gets "NOT RUN: duplicate of block K" (was: ran twice)
    assert runs == ["Write-Output C1\nWrite-Output C2", "Write-Output DUP"], runs
    assert "NOT RUN: duplicate of block 2" in r["posted"][0]["text"], r["posted"][0]["text"][:900]


@needs_browser
def test_E4_block_inside_thinking_section_is_ignored():
    """A fenced AIRUN block in the model's thinking/thought section is not an instruction. Today all three variants run."""
    js = ARM + r"""
setTimeout(function(){
  var d = document.createElement('div'); d.className='dsa';
  var th = document.createElement('div'); th.className = 'ds-think-content thinking'; window.codeBlock(th, '# AIRUN cwd=C:\\x\nWrite-Output FROM_THINKING'); d.appendChild(th);
  var t2 = document.createElement('thought'); window.codeBlock(t2, '# AIRUN cwd=C:\\x\nWrite-Output FROM_THOUGHT_TAG'); d.appendChild(t2);
  var dt = document.createElement('details'); var sm = document.createElement('summary'); sm.textContent='Thought for 5 seconds'; dt.appendChild(sm); window.codeBlock(dt, '# AIRUN cwd=C:\\x\nWrite-Output FROM_DETAILS'); d.appendChild(dt);
  document.getElementById('log').appendChild(d);
}, 8000); setTimeout(window.finish, 40000);
"""
    r = run_page(js, 50000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun"]
    assert runs == [], runs


@needs_browser
@pytest.mark.xfail(strict=True, reason="E5 MINOR/BLOCKER: " + FIX_PENDING)
def test_E5_failed_read_kind_command_stops_the_dependent_block():
    """exit=128 on a kind=read command (git fetch) must stop the batch like any other failure; today block 2 still runs."""
    js = ARM + r"""
window.agent = function(msg){ if (String(msg.cmd).indexOf('FAILME')>=0) return {body:{exit:128, kind:'read', out:'fatal: unable to access'}}; return {body:{out:'ok'}}; };
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\ngit fetch FAILME', '# AIRUN cwd=C:\\x\nWrite-Output DEPENDENT']); }, 8000);
setTimeout(window.finish, 40000);
"""
    r = run_page(js, 50000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun"]
    assert runs == ["git fetch FAILME"], runs


@needs_browser
@pytest.mark.xfail(strict=True, reason="E6 STOPPER/BLOCKER (B210 gap): " + FIX_PENDING)
def test_E6_task_without_timeout_keeps_its_lock_for_the_agent_default():
    """task=mts-gate without timeout= runs under the agent's 600 s task default; the extension released the lock at 240 s with
    LOCK_EXPIRED while the gate was still running (agent running=1), losing the real result and inviting a duplicate run."""
    js = ARM + r"""
window.agent = function(msg){ return {delay_ms: 400000, body:{kind:'task', out:'TASK RESULT: PASS 1 steps'}}; };
window.agentRunning = 1;
setTimeout(function(){ window.dsaReply('go', ['# AIRUN task=mts-gate repo=C:\\x']); }, 8000); setTimeout(window.finish, 500000);
"""
    r = run_page(js, 510000)
    text = "\n".join(p["text"] for p in r["posted"])
    assert "LOCK_EXPIRED" not in text and "TASK RESULT: PASS" in text, text[:400]


@needs_browser
def test_E7_no_final_message_after_result_is_not_silently_abandoned():
    """After a result is posted DSA's generation drops (the chat only shows a thinking spinner, no final message, no new block).
    Within ~60 s the bridge must post an error or a wake-up message to the chat, or show a stop banner. Today it posts nothing:
    the panel reads 'waiting for DSA after #N' for 30 s to ~3.5 min (spinner text keeps changing), then 'armed: waiting for the
    next DSA block' forever, and DSA never resumes without the operator."""
    js = ARM + SAMPLE + r"""
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output ONE']); }, 8000);
setTimeout(function(){ var d=document.createElement('div'); document.getElementById('log').appendChild(d); var n=0; setInterval(function(){ n++; d.textContent='Thinking '+('.'.repeat(n%5))+' '+n; }, 700); }, 12000);
setTimeout(window.finish, 120000);
"""
    r = run_page(js, 130000)
    assert len(r["posted"]) >= 2 or r["banner"], (r["status"], [p["text"][:80] for p in r["posted"]])


@needs_browser
def test_E8_consecutive_blocks_without_wrapper_text_are_separate_blocks():
    """Three AIRUN blocks as bare <pre> siblings (no prose or header text between) were merged into one command: one receipt, the
    2nd and 3rd '# AIRUN' lines became comments, their cwd/timeout/task ignored."""
    js = ARM + r"""
setTimeout(function(){ var d=document.createElement('div'); d.className='dsa';
 ['one','two','three'].forEach(function(n){ var pre=document.createElement('pre'); var c=document.createElement('code'); c.textContent='# AIRUN cwd=C:\\x\nWrite-Output '+n; pre.appendChild(c); d.appendChild(pre); });
 document.getElementById('log').appendChild(d); }, 8000);
setTimeout(window.finish, 40000);
"""
    r = run_page(js, 50000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun"]
    assert runs == ["Write-Output one", "Write-Output two", "Write-Output three"], runs


@needs_browser
def test_E7_quiet_dropped_generation_gets_one_notice_then_a_stop_banner():
    """0.7.4 (dsabr-c2): the chat is idle after our result but no final answer ever comes: ONE wake-up notice under 60 s,
    and when that is ignored too, hands-free stops with a banner (never a silent 'waiting for DSA')."""
    js = ARM + r"""
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output ONE']); }, 8000);
setTimeout(window.finish, 150000);
"""
    r = run_page(js, 160000)
    texts = [p["text"] for p in r["posted"]]
    notices = [p for p in r["posted"] if p["text"].startswith("[AIRUN NOTICE]")]
    assert len(notices) == 1, texts
    assert notices[0]["t"] - r["posted"][0]["t"] < 60000, (notices[0]["t"], r["posted"][0]["t"])
    assert r["banner"] and "never answered" in r["banner"], r["banner"]
