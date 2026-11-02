import sys; sys.dont_write_bytecode = True
"""AIBridge 0.7.12 permission narrowing, evidence = audit 2026-10-30..11-01: 'git branch -d' (safe, git refuses unmerged) was refused
because the confirm regex was case-insensitive and meant -D; 'git checkout --' in DSA's own mts-dsa-<chat> worktree is DSA's scratch.
Still a click: -D, checkout -- elsewhere or after a cd out, deletes, reset, clean."""
import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
pytestmark = pytest.mark.skipif(not shutil.which("powershell.exe"), reason="needs Windows PowerShell")


@pytest.fixture(scope="module")
def sb():
    from aibridge_scratch import Scratch
    s = Scratch()
    s.own = os.path.join(s.work, "IdeaProjects", "mts-dsa-t1")
    os.makedirs(s.own)
    yield s
    s.close()


def verdict(sb, cmd, cwd=None):
    st, b = sb.run(cmd, cwd=cwd or sb.work)
    return b.get("reason", "") if st != 200 else "ran"


def test_safe_branch_delete_is_not_a_click(sb):
    assert "manual_click_required" not in verdict(sb, "git branch -d no-such-branch")


def test_forced_branch_delete_still_a_click(sb):
    assert verdict(sb, "git branch -D no-such-branch").startswith("manual_click_required")


def test_checkout_dashdash_in_own_worktree_runs(sb):
    assert "manual_click_required" not in verdict(sb, "git checkout -- a.txt", cwd=sb.own)


def test_checkout_dashdash_elsewhere_still_a_click(sb):
    assert verdict(sb, "git checkout -- a.txt").startswith("manual_click_required")


def test_checkout_dashdash_after_cd_out_still_a_click(sb):
    cmd = "Set-Location '%s'\ngit checkout -- a.txt" % sb.work
    assert verdict(sb, cmd, cwd=sb.own).startswith("manual_click_required")


def test_recursive_delete_in_own_worktree_still_a_click(sb):
    assert verdict(sb, "Remove-Item -LiteralPath x -Recurse -Force", cwd=sb.own).startswith("manual_click_required")
