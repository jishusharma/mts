"""Tests for rulebook_check.py (fail-first: a new layer folder with no INDEX row must fail)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rulebook_check as rc  # noqa: E402


def _mk(root, folders, index_text):
    for f in folders:
        d = root / rc.LAYERS / f
        d.mkdir(parents=True)
        (d / "x.py").write_text("pass\n")
    idx = root / rc.INDEX
    idx.parent.mkdir(parents=True)
    idx.write_text(index_text, encoding="utf-8")


def test_new_layer_without_row_fails(tmp_path):
    _mk(tmp_path, ["rsi", "newlayer"], "| RSI | x | `layer:rsi` |\n")
    assert rc.missing(tmp_path) == ["newlayer"]
    assert rc.main(["--root", str(tmp_path)]) == 1


def test_all_covered_passes(tmp_path):
    _mk(tmp_path, ["rsi", "adx"], "| a | `layer:rsi` |\n| b | `layer:adx`, `layer:rsi` |\n")
    assert rc.missing(tmp_path) == []
    assert rc.main(["--root", str(tmp_path)]) == 0


def test_ignores_empty_and_hidden_dirs(tmp_path):
    _mk(tmp_path, ["rsi"], "`layer:rsi`\n")
    (tmp_path / rc.LAYERS / "__pycache__").mkdir()
    (tmp_path / rc.LAYERS / "emptydir").mkdir()
    (tmp_path / rc.LAYERS / "fixtures").mkdir()
    ((tmp_path / rc.LAYERS / "fixtures") / "a.csv").write_text("1")
    assert rc.missing(tmp_path) == []


def test_real_repo_index_covers_every_layer():
    root = Path(__file__).resolve().parents[2]
    assert rc.missing(root) == []
