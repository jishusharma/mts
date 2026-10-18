"""Tests for check_handoff.py, derived from the spec (not from the implementation)."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_handoff as ch  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture()
def repo(tmp_path):
    def g(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    g("init", "-q")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
    h = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "--short=10", "HEAD"],
                       capture_output=True, text=True, check=True).stdout.strip()
    return tmp_path, h


def doc(block_lines=None, end="End: ship via sync.py ship, sync.py where must show 0 unshipped, overwrite this file.",
        state="## State at handoff\n- Shipped: nothing.\n"):
    body = block_lines if block_lines is not None else [
        "MTS builder. Read CLAUDE.md, STATUS.md, then this file's State section.",
        "0. Start: `python scripts/dev/sync.py start`, then `sync.py where`.",
        "1. Do the thing.",
    ]
    lines = list(body) + ([end] if end else [])
    return "# NEXT SESSION PROMPT (x)\n\n```text\n" + "\n".join(lines) + "\n```\n\n" + state


def test_good_file_passes(repo):
    r, h = repo
    assert ch.check(doc(state=f"## State at handoff\n- Shipped: fix at {h}.\n"), repo=r) == []


def test_block_of_31_lines_fails(repo):
    r, _ = repo
    body = ["0. Start: sync.py start"] + [f"step {i}" for i in range(29)]  # 30 + End = 31
    fails = ch.check(doc(block_lines=body), repo=r)
    assert any(f.startswith("a:") for f in fails)


def test_block_of_30_lines_passes(repo):
    r, _ = repo
    body = ["0. Start: sync.py start"] + [f"step {i}" for i in range(28)]  # 29 + End = 30
    assert ch.check(doc(block_lines=body), repo=r) == []


def test_missing_end_line_fails(repo):
    r, _ = repo
    fails = ch.check(doc(end=None), repo=r)
    assert any(f.startswith("b:") for f in fails)


def test_end_line_without_ship_fails(repo):
    r, _ = repo
    fails = ch.check(doc(end="End: just stop."), repo=r)
    assert any(f.startswith("b:") for f in fails)


def test_missing_sync_start_fails(repo):
    r, _ = repo
    fails = ch.check(doc(block_lines=["Read CLAUDE.md.", "1. Do it."]), repo=r)
    assert any(f.startswith("b:") for f in fails)


def test_missing_state_heading_fails(repo):
    r, _ = repo
    fails = ch.check(doc(state="- Shipped: nothing.\n"), repo=r)
    assert any(f.startswith("c:") for f in fails)


def test_unknown_hash_fails(repo):
    r, _ = repo
    fails = ch.check(doc(state="## State at handoff\n- Shipped: abc1234def.\n"), repo=r)
    assert any(f.startswith("d:") and "abc1234def" in f for f in fails)


def test_hash_outside_state_section_is_ignored(repo):
    r, _ = repo
    text = doc() + "\n## Other\n- abc1234def\n"
    assert ch.check(text, repo=r) == []


@pytest.mark.parametrize("s", ["git log", "git status", "git add", "git commit", "git diff",
                               "git checkout", "git init", "version control"])
def test_forbidden_string_fails(repo, s):
    r, _ = repo
    fails = ch.check(doc(state=f"## State at handoff\n- Run {s} now.\n"), repo=r)
    assert any(f.startswith("e:") for f in fails)


def test_forbidden_list_matches_doc_test():
    src = (REPO / "MyTradingSys" / "tests" / "docs" / "test_integrity.py")
    if not src.exists():
        pytest.skip("test_integrity.py not present")
    text = src.read_text(encoding="utf-8")
    block = text.split("def test_2_no_forbidden_refs", 1)[1].split("regexes", 1)[0]
    theirs = re.findall(r'r"([^"]+)"', block)
    assert sorted(theirs) == sorted(ch.FORBIDDEN)


def test_cli_exit_codes(tmp_path):
    bad = tmp_path / "n.md"
    bad.write_text("nothing here\n", encoding="utf-8")
    p = subprocess.run([sys.executable, str(Path(ch.__file__)), str(bad)], capture_output=True, text=True)
    assert p.returncode == 1 and p.stdout.startswith("FAIL")
