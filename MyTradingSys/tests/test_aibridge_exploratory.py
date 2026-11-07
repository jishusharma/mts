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


def test_find_browser_skips_empty_dump(tmp_path):
    import aibridge_dom
    empty = tmp_path / 'empty.cmd'
    good = tmp_path / 'good.cmd'
    if os.name == 'nt':
        empty.write_text('@echo off' + chr(13) + chr(10) + 'exit /b 0' + chr(13) + chr(10), newline='')
        good.write_text('@echo off' + chr(13) + chr(10) + 'echo aib-probe-ok' + chr(13) + chr(10), newline='')
    else:
        empty.write_text('#!/bin/sh' + chr(10) + 'exit 0' + chr(10)); good.write_text('#!/bin/sh' + chr(10) + 'echo aib-probe-ok' + chr(10))
        empty.chmod(0o755); good.chmod(0o755)
    assert aibridge_dom.find_browser([str(empty), str(good)]) == str(good)
    assert aibridge_dom.find_browser([str(empty)]) is None


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
def test_E3_mts_ship_runs_sync_ship_with_release_and_never_the_gate(tmp_path):
    """mts-ship = status, ship --release <slug>, where: sync.py ship runs its own smoke gate, so the playbook never runs run_all_tests."""
    log = tmp_path / "calls.txt"
    files = {"repo/scripts/dev/run_all_tests.py": "open(r'%s.gate', 'w').write('gate ran')\n" % log,
             "repo/scripts/dev/sync.py": "import sys\nopen(r'%s', 'a').write(' '.join(sys.argv[1:]) + chr(10))\n" % log}
    subprocess.run(["git", "init", "-q", str(tmp_path / "repo")], check=False)
    _run_task(tmp_path, "mts-ship", params={"repo": str(tmp_path / "repo"), "release": "my-slug"}, files=files)
    assert log.read_text().splitlines() == ["ship --release my-slug", "where"]
    assert not (tmp_path / "calls.txt.gate").exists(), "mts-ship ran the gate"


# ---------------------------------------------------------------- extension side (real content.js in headless Edge)

# an airun without cmd is an audit event (content.js auditEvent, 0.7.18; 0.7.27 adds the "no reply-finished marker" line on a page without .ds-message)
# a "dry" airun is the button-label preflight (content.js ~l.311), sent whenever a block is first scanned - under CPU load it lands after
# the batch and is not a run; only non-dry calls count as executions.
def _ps_blocks(n):
    return [("# AIRUN cwd=C:\\x\nWrite-Output b%d" % i) for i in range(1, n + 1)]


@needs_browser
def test_guard_six_blocks_run_once_each_seventh_not_run():
    js = ARM + "setTimeout(function(){ window.dsaReply('go', %s); }, 8000); setTimeout(window.finish, 60000);" % json.dumps(_ps_blocks(7))
    r = run_page(js, 70000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and "cmd" in c and not c.get("dry")]
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
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and "cmd" in c and not c.get("dry")]
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
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and "cmd" in c and not c.get("dry")]
    assert runs == [], runs


@needs_browser
def test_E5_failed_read_kind_command_stops_the_dependent_block():
    """exit=128 on a kind=read command (git fetch) must stop the batch like any other failure; today block 2 still runs."""
    js = ARM + r"""
window.agent = function(msg){ if (String(msg.cmd).indexOf('FAILME')>=0) return {body:{exit:128, kind:'read', out:'fatal: unable to access'}}; return {body:{out:'ok'}}; };
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\ngit fetch FAILME', '# AIRUN cwd=C:\\x\nWrite-Output DEPENDENT']); }, 8000);
setTimeout(window.finish, 40000);
"""
    r = run_page(js, 50000)
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and "cmd" in c and not c.get("dry")]
    assert runs == ["git fetch FAILME"], runs


@needs_browser
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
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and "cmd" in c and not c.get("dry")]
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


# ---- 0.7.7 source guards for the content.js fixes (the page-level behaviour is covered by the browser tests above) ----
def _src(rel):
    from pathlib import Path
    return (Path(__file__).resolve().parents[2] / rel).read_text(encoding="utf-8")


def test_077_stop_resets_the_reply_watch_and_draft_counts_as_busy():
    c = _src("scripts/aibridge/extension/content.js")
    stop = c[c.index("function stopAuto"):]
    stop = stop[:stop.index("}")]
    assert "watch = null" in stop, "a stale watch survives an operator untick (c2)"
    assert "busy: inRun || !!inputText(findInput()" in c, "a draft being typed must hold the notice (c2)"
    assert "L.blockFailed(resp)" in c, "E5: exit rule lives in loop.js"
    assert "L.expireMs(it.opts.timeout_s, !!it.opts.task)" in c, "E6: task default"


def test_077_agent_task_default_follows_the_playbook_budget():
    a = _src("scripts/aibridge/src/agent.ps1")
    assert "$sumS + 60" in a and "[Math]::Min($hardS, [Math]::Max(600, $sumS + 60))" in a


# ---------------------------------------------------------------- 0.7.11 idle signal (operator screenshot 2026-11-02, JIS-NUC)

@needs_browser
def test_idle_signal_survives_a_live_timer_in_a_hidden_tab():
    """A chat that shows a live timer ('Thought for N s', length wobbles 0-3 chars every 700 ms) must still count as idle.
    Before 0.7.11 the page-text quiet clock reset on every wobble: the block never ran / the result was never posted and
    hands-free switched itself OFF ('the chat never became idle'). The tab is simulated hidden (visibilityState=hidden)."""
    js = ARM + r"""
Object.defineProperty(document, 'hidden', {get: function(){ return true; }});
Object.defineProperty(document, 'visibilityState', {get: function(){ return 'hidden'; }});
var tk = document.createElement('div'); tk.id = 'timer'; document.body.appendChild(tk);
var k = 0; setInterval(function(){ k++; tk.textContent = 'Thought for ' + '1234567890'.slice(0, 1 + (k % 4)) + ' s'; }, 700);
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output idle1']); }, 8000);
setTimeout(window.finish, 45000);
"""
    r = run_page(js, 60000)
    assert any("ran:" in p["text"] or "idle1" in p["text"] for p in r["posted"]), (r["posted"], r["status"], r["banner"])
    assert not r["banner"], r["banner"]


@needs_browser
def test_V1_stale_extension_reloads_itself_when_idle():
    """0.7.13: manifest.json on disk is newer than the loaded extension: with nothing running the page asks the worker to reload it."""
    js = "window.diskVersion='9.9.9';\nsetTimeout(window.finish, 75000);\n"
    r = run_page(js, 80000)
    assert any(c["type"] == "reload" for c in r["calls"]), [c["type"] for c in r["calls"]]
    assert r["dbg"] is not None


@needs_browser
def test_V2_agent_version_mismatch_is_put_in_the_receipt():
    """0.7.13: an agent on another version than the extension adds an [AIRUN WARNING] line to the posted receipt (DSA and the operator see it)."""
    js = ARM + r"""
window.agentVersion='0.0.1';
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output ONE']); }, 8000);
setTimeout(window.finish, 60000);
"""
    r = run_page(js, 70000)
    assert any("[AIRUN WARNING] VERSION MISMATCH: extension" in p["text"] and "but the agent runs 0.0.1" in p["text"] for p in r["posted"]), r["posted"]
