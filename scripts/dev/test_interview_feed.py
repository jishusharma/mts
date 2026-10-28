"""interview_feed.py: front matter selection, refusals, export."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interview_feed as F

GOOD = "---\ninterview: yes\ntopic: Hooks\nlevel: beginner\ndate: 2026-10-22\n---\n# Hooks\nPlain text.\n"


def notes(tmp, **files):
    for name, text in files.items():
        (Path(tmp) / f"{name}.md").write_text(text, encoding="utf-8", newline="\n")
    return tmp


def test_only_interview_yes_notes_are_picked():
    with tempfile.TemporaryDirectory() as t:
        notes(t, good=GOOD, no=GOOD.replace("yes", "no"), nofm="# no front matter\ninterview: yes\n")
        assert [p.stem for p, _, _ in F.scan(t)] == ["good"]


def test_refusals():
    bad = {
        "winpath": "C:\\Users\\someone\\proj\\x.py",
        "slashpath": "see C:/Users/someone/file",
        "secrets": "read .secrets/keys",
        "runtime": "from runtime_data/orders.json",
        "ghp": "ghp_" + "a" * 30,
        "keyval": "api_key = abcdef1234567890",
    }
    with tempfile.TemporaryDirectory() as t:
        notes(t, **{k: GOOD + v + "\n" for k, v in bad.items()}, clean=GOOD)
        res = {p.stem: why for p, _, why in F.scan(t)}
        assert res["clean"] == []
        for k in bad:
            assert res[k], k


def test_size_cap():
    with tempfile.TemporaryDirectory() as t:
        notes(t, big=GOOD + "x" * 3000)
        assert F.scan(t, max_kb=1)[0][2] and not F.scan(t, max_kb=10)[0][2]


def test_export_copies_good_skips_refused_and_writes_index():
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as out:
        notes(t, good=GOOD, bad=GOOD + "C:\\Users\\x\\y\n")
        n = F.cmd_export(out, folder=t, out=lambda *_: None)
        names = sorted(p.name for p in Path(out).iterdir())
        assert n == 1 and names == ["INDEX.md", "good.md"]
        assert "good.md" in (Path(out) / "INDEX.md").read_text(encoding="utf-8")


def test_export_without_target_is_a_dry_run(monkeypatch):
    monkeypatch.delenv("MTS_INTERVIEW_DIR", raising=False)
    with tempfile.TemporaryDirectory() as t:
        notes(t, good=GOOD)
        lines = []
        assert F.cmd_export(None, folder=t, out=lines.append) == 0
        assert any("dry run" in l for l in lines)


def test_env_dir_is_the_default_target(monkeypatch):
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as out:
        notes(t, good=GOOD)
        monkeypatch.setenv("MTS_INTERVIEW_DIR", out)
        F.cmd_export(None, folder=t, out=lambda *_: None)
        assert (Path(out) / "good.md").exists()


def test_the_real_primer_passes_the_filter():
    rows = F.scan()
    assert rows and all(not why for _, _, why in rows), rows
