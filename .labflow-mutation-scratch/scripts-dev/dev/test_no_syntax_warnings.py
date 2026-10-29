"""Every scripts/dev/test_*.py must compile without SyntaxWarning (invalid escapes)."""
import pathlib
import warnings

import pytest

DEV = pathlib.Path(__file__).resolve().parent
FILES = sorted(DEV.glob("test_*.py"))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_compiles_without_syntax_warning(path):
    src = path.read_text(encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        compile(src, str(path), "exec")
