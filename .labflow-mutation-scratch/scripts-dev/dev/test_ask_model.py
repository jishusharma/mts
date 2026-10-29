"""ask_model: read-only, scratch-only, no permission skipping (python scripts/dev/test_ask_model.py)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ask_model as am  # noqa: E402


def test_gemini_model_mapping():
    assert am.gemini_model('flash', 'low') == 'gemini-3.8-flash-low'
    assert am.gemini_model('argon', 'high') == 'gemini-4-argon-high'
    assert am.gemini_model('claude-opus-5-5-medium', 'low') == 'claude-opus-5-5-medium'


def test_gemini_cmd_never_skips_permissions():
    cmd = am.gemini_cmd('hi', 'flash', 'low', exe='agy.exe')
    assert cmd[:2] == ['agy.exe', '--print'] and '--dangerously-skip-permissions' not in cmd and '--mode' not in cmd


def test_gpt_cmd_is_read_only_and_non_git():
    cmd = am.gpt_cmd(None, 'low', Path('x'), 'codex')
    assert cmd[cmd.index('-s') + 1] == 'read-only' and '--skip-git-repo-check' in cmd and cmd[-1] == '-'


def test_stage_files_refuses_secret_paths_and_copies_others():
    d = Path(tempfile.mkdtemp())
    (d / 'a.txt').write_text('x')
    out = Path(tempfile.mkdtemp())
    assert am.stage_files([d / 'a.txt'], out) == ['a.txt'] and (out / 'a.txt').exists()
    try:
        am.stage_files([d / '.env'], out)
    except SystemExit as e:
        assert 'secret' in str(e)
    else:
        raise AssertionError('secret path accepted')


if __name__ == '__main__':
    for n, f in sorted(globals().items()):
        if n.startswith('test_'):
            f()
    print('ok')
