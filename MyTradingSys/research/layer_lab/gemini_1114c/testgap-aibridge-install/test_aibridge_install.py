import sys; sys.dont_write_bytecode = True
"""Unit tests for scripts/dev/aibridge_install.py.

Existing coverage noted via git grep:
- MyTradingSys/tests/test_aibridge_install_fresh.py (--fresh CLI + aibridge_verify.py)
- MyTradingSys/tests/test_aibridge_probe_noise.py (--help --dry CLI)
- MyTradingSys/tests/test_aibridge_version_bump.py (version fingerprint guard)
None is named test_aibridge_install.py or directly unit-tests ext_id_for_path / backup / fail.

Mutation test record (Step 4):
Mutated copy created in a temporary scratch dir by removing `and not os.path.exists(b)`:
  File: scripts/dev/aibridge_install.py:57
  Original:
    if os.path.exists(p) and not os.path.exists(b) and not dry:
  Mutated:
    if os.path.exists(p) and not dry:
Resulting failure when pointed at the mutated scratch copy:
  test_write_read_and_backup_preserves_first_snapshot FAILED with:
    AssertionError: assert 'v2\n' == 'v1\n'
  (1 failed, 4 passed in 1.37s)
"""
import tempfile
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[5]
DEV = REPO / "scripts" / "dev"
if str(DEV) not in sys.path:
    sys.path.insert(0, str(DEV))

_saved_argv = sys.argv[:]
try:
    _dry_root = Path(tempfile.gettempdir()) / "aibridge_install_import_dry_nonexistent"
    sys.argv = ["aibridge_install.py", str(_dry_root), "--fresh", "--dry"]
    import aibridge_install
finally:
    sys.argv = _saved_argv


def test_ext_id_for_path_normal():
    # SOURCED: h = hashlib.sha256(os.path.normpath(path).replace('/', BS).encode('utf-16-le')).hexdigest()[:32] (scripts/dev/aibridge_install.py:67)
    # SOURCED: return ''.join(chr(ord('a') + int(c, 16)) for c in h) (scripts/dev/aibridge_install.py:68)
    # OURS: "F:/AIBridge/extension" normalizes to "F:\\AIBridge\\extension"; UTF-16LE SHA-256[:32] is
    #       "a68678b6a36a36746f819192832c49a6", mapping 0-f -> a-p yields "kgighilgkdgkdghegpibjbjcidcmejkg".
    expected = "kgighilgkdgkdghegpibjbjcidcmejkg"
    assert aibridge_install.ext_id_for_path("F:/AIBridge/extension") == expected
    assert aibridge_install.ext_id_for_path(r"F:\AIBridge\extension") == expected


def test_ext_id_for_path_empty():
    # SOURCED: os.path.normpath(path).replace('/', BS).encode('utf-16-le') (scripts/dev/aibridge_install.py:67)
    # OURS: os.path.normpath("") returns "."; UTF-16LE SHA-256[:32] of "." is
    #       "075d3ddf5a3a826e13a92288e853bc4b", mapping 0-f -> a-p yields "ahfndnnpfkdkicgobdkjcciioifdlmel".
    assert aibridge_install.ext_id_for_path("") == "ahfndnnpfkdkicgobdkjcciioifdlmel"


def test_ext_id_for_path_malformed_none_raises():
    # SOURCED: os.path.normpath(path) (scripts/dev/aibridge_install.py:67)
    # OURS: passing None (non-path-like) to os.path.normpath raises TypeError.
    with pytest.raises(TypeError):
        aibridge_install.ext_id_for_path(None)


def test_fail_formats_prefix_and_exits():
    # SOURCED: sys.exit('aibridge_install: ' + msg) (scripts/dev/aibridge_install.py:38)
    # OURS: fail("bad root") raises SystemExit with code "aibridge_install: bad root".
    with pytest.raises(SystemExit) as exc_info:
        aibridge_install.fail("bad root")
    assert exc_info.value.code == "aibridge_install: bad root"


def test_write_read_and_backup_preserves_first_snapshot(tmp_path, monkeypatch):
    # SOURCED: b = p + '.pre_v07'; if os.path.exists(p) and not os.path.exists(b) and not dry: shutil.copy2(p, b) (scripts/dev/aibridge_install.py:56-58)
    # OURS: first backup() creates .pre_v07 with "v1\n"; after overwriting target with "v2\n", second backup() keeps "v1\n".
    monkeypatch.setattr(aibridge_install, "dry", False)
    target = str(tmp_path / "sub" / "sample.txt")
    aibridge_install.write(target, "v1\n")
    assert aibridge_install.read(target) == "v1\n"
    aibridge_install.backup(target)
    assert aibridge_install.read(target + ".pre_v07") == "v1\n"
    aibridge_install.write(target, "v2\n")
    aibridge_install.backup(target)
    assert aibridge_install.read(target + ".pre_v07") == "v1\n"
