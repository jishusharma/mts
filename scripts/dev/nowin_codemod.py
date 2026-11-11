"""One-shot codemod (kept for re-runs): add creationflags to subprocess calls that capture output. See test_nowin_calls.py."""
import ast, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import nowin_scan  # noqa: E402

FLAG = 'creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)'


def patch(path):
    src = Path(path).read_bytes().decode("utf-8")
    lines = src.split("\n")
    blines = [l.encode("utf-8") for l in lines]
    hits = [c for c in nowin_scan.offending_calls(src) if c["captured"]]
    for c in sorted(hits, key=lambda c: (c["end_lineno"], c["end_col"]), reverse=True):
        i, col = c["end_lineno"] - 1, c["end_col"] - 1   # position of the closing paren
        b = blines[i]
        assert b[col:col + 1] == b")", (path, c)
        before = b[:col].rstrip()
        if not before:   # the paren is alone on its line: flag goes on its own line above it
            ind = blines[i - 1][:len(blines[i - 1]) - len(blines[i - 1].lstrip())]
            blines[i:i + 1] = [ind + FLAG.encode() + b",", b[:col] + b[col:]]
            continue
        sep = b"" if before.endswith(b"(") else (b" " if before.endswith(b",") else b", ")
        blines[i] = before + sep + FLAG.encode() + b[col:]
    out = b"\n".join(blines).decode("utf-8")
    if out != src:
        Path(path).write_bytes(out.encode("utf-8"))
    return len(hits)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(patch(p), p)
