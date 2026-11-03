import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TSV = "scripts/dev/extra_tests.tsv"
NL = chr(10)


def _git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True)


def test_gitattributes_sets_union_merge_for_tsv():
    with open(os.path.join(ROOT, ".gitattributes"), encoding="utf-8") as f:
        lines = [ln.split() for ln in f.read().split(NL) if ln.strip() and not ln.startswith("#")]
    assert any(p[0] == TSV and "merge=union" in p[1:] for p in lines), lines


def test_two_parallel_appended_rows_merge_clean_with_repo_attributes():
    d = tempfile.mkdtemp()
    try:
        _git(d, "init", "-q")   # no `init -b`: needs git 2.28, JIS-NUC runs 2.24
        _git(d, "symbolic-ref", "HEAD", "refs/heads/base")
        os.makedirs(os.path.join(d, "scripts", "dev"))
        shutil.copy(os.path.join(ROOT, ".gitattributes"), os.path.join(d, ".gitattributes"))
        p = os.path.join(d, TSV)
        with open(p, "w", newline=NL) as f:
            f.write("# header" + NL + "scripts/dev/test_a.py" + NL)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")
        for br, row in (("one", "scripts/dev/test_one.py"), ("two", "scripts/dev/test_two.py")):
            _git(d, "checkout", "-q", "-b", br, "base")
            with open(p, "a", newline=NL) as f:
                f.write(row + NL)
            _git(d, "commit", "-qam", br)
        _git(d, "checkout", "-q", "one")
        r = _git(d, "merge", "--no-edit", "two")
        assert r.returncode == 0, r.stdout + r.stderr
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        assert "test_one.py" in txt and "test_two.py" in txt
    finally:
        shutil.rmtree(d, ignore_errors=True)
