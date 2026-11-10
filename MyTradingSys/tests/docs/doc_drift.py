"""report_only: a doc-wording or doc-format test that prints what drifted and passes (ARCH_REVIEW_2026-11-10 row 1).

Wording and format checks never caught a code defect but blocked ships (2 of 3 reds on 2026-11-10). They still run and
print one `DOC-DRIFT <test>: <what>` line per drift; the gate no longer fails on them. Keep a plain assert for path-exists
checks, live-path rule checks and the CLAUDE.md size cap.
"""
import functools
import sys
import warnings


def report(name, what):
    line = "DOC-DRIFT %s: %s" % (name, what)
    print(line, file=sys.stderr)
    warnings.warn(line)


def report_only(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as e:   # AssertionError, a missing doc, a regex that no longer matches: all are drift here
            line = "DOC-DRIFT %s: %s: %s" % (fn.__name__, type(e).__name__, str(e).replace("\n", " | ")[:400])
            print(line, file=sys.stderr)
            warnings.warn(line)
    return wrapper
