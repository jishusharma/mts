"""
Mutation check for bigmoves.py / capture.py: every mutant below is a deliberately broken implementation (one source edit). The test files
test_bigmoves.py and test_capture.py must FAIL on each of them and PASS on the unmodified code. A mutant that survives means a missing test.

Run from the repo root:  python -B MyTradingSys/backtest/bigtrade/mutation_check_bigmoves_capture.py
Exit code 0 only if the baseline passes and every mutant is killed. Nothing on disk is modified (mutants are exec'd in memory).
"""
import importlib
import io
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PKG = "MyTradingSys.backtest.bigtrade."
ALL = ("bigmoves", "capture", "test_bigmoves", "test_capture")

# (name, module, old text, new text)
MUTANTS = [
    ("atr uses the NEXT bar (lookahead)", "bigmoves",
     "a = (a * (period - 1) + trl[i]) / period", "a = (a * (period - 1) + trl[min(i + 1, n - 1)]) / period"),
    ("zigzag: equal high moves the pivot to the later bar", "bigmoves", "if h_l[i] > ext:", "if h_l[i] >= ext:"),
    ("zigzag: a bar may confirm its own reversal", "bigmoves",
     "            if h_l[i] > ext:\n                e, ext = i, h_l[i]\n            elif l_l[i] <= ext - r * a_l[e]:\n",
     "            if h_l[i] > ext and not (l_l[i] <= ext - r * a_l[e]):\n                e, ext = i, h_l[i]\n            elif l_l[i] <= ext - r * a_l[e]:\n"),
    ("zigzag: reversal of exactly r x ATR does not count", "bigmoves", "elif l_l[i] <= ext - r * a_l[e]:", "elif l_l[i] < ext - r * a_l[e]:"),
    ("labels: tie on the max picks the LAST bar", "bigmoves",
     "ih = hh.argmax(axis=1)  # first bar that makes the max high", "ih = hh.shape[1] - 1 - hh[:, ::-1].argmax(axis=1)"),
    ("labels: MAE taken over the whole window, not before the MFE", "bigmoves",
     "mae_l = entry - np.minimum.accumulate(ll, axis=1)[rows, ih]", "mae_l = entry - ll.min(axis=1)"),
    ("legs: flag ignores whether the leg exists in that r", "bigmoves",
     "flags = {(r, k): (in_r[r] & (size >= k)).astype(np.uint8) for r in r_list for k in k_list}",
     "flags = {(r, k): (size >= k).astype(np.uint8) for r in r_list for k in k_list}"),
    ("legs: leg times use bar OPEN instead of close", "bigmoves", '"t_start": b["t_close"][i0] if m', '"t_start": b["t_open"][i0] if m'),
    ("capture: EARLY upper edge exclusive", "capture", "c_e = np.searchsorted(fire_t, ts + d * EARLY_FRAC, side=\"right\")",
     "c_e = np.searchsorted(fire_t, ts + d * EARLY_FRAC, side=\"left\")"),
    ("capture: a fire exactly at the leg end is lost", "capture", "c_l = np.searchsorted(fire_t, te, side=\"right\")",
     "c_l = np.searchsorted(fire_t, te, side=\"left\")"),
    ("capture: side of the fire ignored", "capture", 'm = (legs["flags"][(r, k)] == 1) & (legs["side"] == side_sign)',
     'm = (legs["flags"][(r, k)] == 1)'),
    ("capture: fee_dominated uses >= 1", "capture", "dom[i] = fee_r[i] > 1.0", "dom[i] = fee_r[i] >= 1.0"),
    ("capture: round-trip fee counted as one side", "capture", "RT_FEE = 2 * _fees.DERIBIT_TAKER", "RT_FEE = _fees.DERIBIT_TAKER"),
    ("capture: fire time mapped FORWARD to the next bar", "capture", "j = np.searchsorted(t_close, t, side=\"right\") - 1",
     "j = np.searchsorted(t_close, t, side=\"left\")"),
    ("capture: base rate over all bars, not the fire span", "capture",
     "bm_mask = (t_close >= span_ms[0]) & (t_close <= span_ms[1]) & np.isfinite(mfe)", "bm_mask = np.isfinite(mfe)"),
    ("capture: duplicate fires on one bar counted twice", "capture", "j_sel = np.unique(j_all[sel])", "j_sel = np.sort(j_all[sel])"),
    ("capture: fee-dominated set never emitted", "capture", "if dom.any():", "if False:"),
]


def _forget(pkg):
    """Drop our modules from sys.modules AND from the package attributes (a stale attribute would win over a fresh import)."""
    for n in ALL:
        sys.modules.pop(PKG + n, None)
        if hasattr(pkg, n):
            delattr(pkg, n)


def run_suite(sources):
    pkg = importlib.import_module(PKG[:-1])
    _forget(pkg)
    try:
        for n, text in sources.items():
            mod = types.ModuleType(PKG + n)
            mod.__file__ = str(HERE / (n + ".py"))
            mod.__package__ = PKG[:-1]
            sys.modules[PKG + n] = mod
            setattr(pkg, n, mod)
            exec(compile(text, mod.__file__, "exec"), mod.__dict__)
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        for tn in ("test_bigmoves", "test_capture"):
            suite.addTests(loader.loadTestsFromModule(importlib.import_module(PKG + tn)))
        return unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    finally:
        _forget(pkg)


def main():
    src = {n: (HERE / (n + ".py")).read_text(encoding="utf-8") for n in ("bigmoves", "capture")}
    base = run_suite({})
    print("baseline (unmodified code): %d run, %d failed, %d errors" % (base.testsRun, len(base.failures), len(base.errors)))
    survived = 0
    for name, mod, old, new in MUTANTS:
        assert src[mod].count(old) == 1, "mutation anchor not unique/found: " + name
        res = run_suite({mod: src[mod].replace(old, new)})
        bad = res.failures + res.errors
        first = bad[0][0].id().split(".")[-2] + "." + bad[0][0].id().split(".")[-1] if bad else "-"
        print("%-62s %-8s killed=%-5s failing tests=%-2d first=%s" % (name, mod, bool(bad), len(bad), first))
        survived += 0 if bad else 1
    print("mutants: %d, survived: %d" % (len(MUTANTS), survived))
    return 0 if (base.wasSuccessful() and survived == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
