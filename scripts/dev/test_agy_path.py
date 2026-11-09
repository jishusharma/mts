import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agy_path import find_agy  # noqa: E402


def _mk(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'')
    return p


def test_laptop_path_found(tmp_path):
    want = _mk(tmp_path / 'AppData' / 'Local' / 'agy' / 'bin' / 'agy.exe')
    assert find_agy(tmp_path) == want


def test_nuc_path_preferred(tmp_path):
    nuc = _mk(tmp_path / '.gemini' / 'bin' / 'agy.exe')
    _mk(tmp_path / 'AppData' / 'Local' / 'agy' / 'bin' / 'agy.exe')
    assert find_agy(tmp_path) == nuc


def test_none_falls_back_to_nuc_default(tmp_path):
    assert find_agy(tmp_path) == tmp_path / '.gemini' / 'bin' / 'agy.exe'


def test_scripts_use_finder():
    here = Path(__file__).resolve().parent
    for name in ('gemini_queue.py', 'ask_model.py', 'argon_blind_read.py'):
        src = (here / name).read_text(encoding='utf-8')
        assert 'find_agy' in src, name
