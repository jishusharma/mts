import sys; sys.dont_write_bytecode = True
"""AIBridge version numbers must agree everywhere (operator 2026-11-02: extension page, chat label and the two machines showed different
numbers). One release record (scripts/aibridge/RELEASES.json) feeds manifest.json, loop.js VERSION and agent.ps1; no other file may carry
a literal version; the chat label shows the extension, page, disk and agent versions side by side and says what to do on a mismatch."""
import json
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aibridge_dom import find_browser, run_page

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
BR = ROOT / "scripts" / "aibridge"
needs_browser = pytest.mark.skipif(not find_browser(), reason="needs headless Edge/Chrome")


def _cur():
    return json.loads((BR / "RELEASES.json").read_text(encoding="utf-8"))["current"]


def test_all_version_sources_match_the_release_record():
    v = _cur()
    manifest = json.loads((BR / "extension" / "manifest.json").read_text(encoding="utf-8-sig"))["version"]
    loop = re.search(r"L\.VERSION = '([^']+)'", (BR / "extension" / "loop.js").read_text(encoding="utf-8")).group(1)
    agent = re.search(r"\$AgentVersion = '([^']+)'", (BR / "src" / "agent.ps1").read_text(encoding="utf-8")).group(1)
    assert {manifest, loop, agent, v} == {v}, {"manifest": manifest, "loop.js": loop, "agent.ps1": agent, "RELEASES": v}


def test_no_other_extension_file_hard_codes_a_version():
    for name in ("content.js", "background.js"):
        txt = (BR / "extension" / name).read_text(encoding="utf-8")
        hits = [m for m in re.findall(r"['\"]\d+\.\d+\.\d+['\"]", txt)]
        assert not hits, (name, hits)


@needs_browser
def test_label_shows_all_four_versions_and_says_what_to_do_on_a_stale_page():
    js = """
sessionStorage.setItem('aibridge_page_reload', String(Date.now()));
window.loadedVersion = '9.9.9'; window.diskVersion = '9.9.9';
setTimeout(function(){ window.extra = { label: (document.querySelector('.aibridge-ctl .aibridge-ver') || {}).textContent, info: (document.querySelector('.aibridge-ctl') || {}).dataset.ver }; window.finish(); }, 20000);
"""
    r = run_page(js, 30000)
    lab = r["extra"]["label"] or ""
    assert "extension 9.9.9" in lab and "this page " in lab and "disk 9.9.9" in lab and "agent " in lab and "MISMATCH" in lab, lab
    assert r["extra"]["info"] == "page_stale", r["extra"]


@needs_browser
def test_label_says_all_match_when_everything_agrees():
    js = """
setTimeout(function(){ window.extra = { label: (document.querySelector('.aibridge-ctl .aibridge-ver') || {}).textContent }; window.finish(); }, 20000);
"""
    r = run_page(js, 30000)
    assert "all match" in (r["extra"]["label"] or ""), r["extra"]
