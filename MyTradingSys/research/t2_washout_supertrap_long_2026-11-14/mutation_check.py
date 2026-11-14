"""Apply one deliberate bug at a time to a COPY of lib.py and confirm test_lib.py goes red. Writes mutation_check.txt."""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
MUTANTS = [
    ("non-causal VWAP (window-end VWAP)", "if c[s] > anchored_vwap(o, h, l, c, v, j, s):", "if c[s] > anchored_vwap(o, h, l, c, v, j, min(j + window, n - 1)):"),
    ("non-causal cycle lookup (next day row)", "d = int(ts_ms) // DAY_MS * DAY_MS", "d = int(ts_ms) // DAY_MS * DAY_MS + DAY_MS"),
    ("non-causal BTC 4h gate (bar containing the trap)", "latest_start = np.floor_divide(hs + HOUR_MS - H4_MS, H4_MS) * H4_MS", "latest_start = np.floor_divide(hs, H4_MS) * H4_MS"),
    ("gap fills at stop instead of open", 'return k, float(o[k]), "gap_stop"', 'return k, float(stop), "gap_stop"'),
    ("low checked after open only (stop ignored inside bar)", "if l[k] <= stop:", "if l[k] < stop - 1e9:"),
    ("fee ignores slippage", "FEE_RT_12 = 2 * (BINANCE_TAKER + SLIPPAGE_SIDE)", "FEE_RT_12 = 2 * BINANCE_TAKER"),
    ("trap strict > 50%", "return (np.asarray(h) > np.asarray(l)) & (f >= frac)", "return (np.asarray(h) > np.asarray(l)) & (f > frac)"),
    ("BB sample sd (ddof 1)", "sd[s + n - 1:e] = w.std(axis=1, ddof=0)", "sd[s + n - 1:e] = w.std(axis=1, ddof=1)"),
    ("hold 23 bars", "HOLD_BARS = 24", "HOLD_BARS = 23"),
    ("episode gap >= 72h splits", "if prev is None or sig[i] - prev > gap_ms:", "if prev is None or sig[i] - prev >= gap_ms:"),
    ("entry at signal bar open", "e = s + 1\n        free_from = s + 1", "e = s\n        free_from = s + 1"),
    ("no 1.2% floor in D", "return max(entry - trap_low, ATR_MULT * atr, D_FLOOR * entry)", "return max(entry - trap_low, ATR_MULT * atr)"),
    ("RSI seed uses first value (not SMA)", "ag = gain[:n].mean()", "ag = gain[0]"),
    ("window 13 bars", "MAX_WAIT = 12", "MAX_WAIT = 13"),
    ("drop stop-resolved trade when a later bar is missing (old rule)", "    n = len(o)\n    if e >= n or np.isnan(o[e]):\n        return None", "    n = len(o)\n    if e + hold >= n or np.isnan(o[e:e + hold + 1]).any():\n        return None\n    if e >= n or np.isnan(o[e]):\n        return None"),
    ("fee-net sign wrong", "return r, r - fee_rt * entry / D", "return r, r + fee_rt * entry / D"),
]
lines = []
base = open(os.path.join(HERE, "lib.py")).read()
for name, old, new in MUTANTS:
    assert base.count(old) == 1, name
    d = tempfile.mkdtemp()
    open(os.path.join(d, "lib.py"), "w").write(base.replace(old, new))
    shutil.copy(os.path.join(HERE, "test_lib.py"), d)
    # lib.py finds fees.py relative to its folder; point it at the real one
    s = open(os.path.join(d, "lib.py")).read().replace('_BT = os.path.abspath(os.path.join(_HERE, "..", "..", "backtest"))', '_BT = %r' % os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
    open(os.path.join(d, "lib.py"), "w").write(s)
    r = subprocess.run([sys.executable, "-m", "pytest", "test_lib.py", "-q", "-p", "no:cacheprovider", "-x"], cwd=d, capture_output=True, text=True)
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    lines.append("%-55s %s %s" % (name, "CAUGHT" if r.returncode != 0 else "SURVIVED", failed[0][:90] if failed else ""))
    shutil.rmtree(d, ignore_errors=True)
r = subprocess.run([sys.executable, "-m", "pytest", "test_lib.py", "-q", "-p", "no:cacheprovider"], cwd=HERE, capture_output=True, text=True)
lines.append("unmutated lib.py: " + r.stdout.strip().splitlines()[-1])
open(os.path.join(HERE, "mutation_check.txt"), "w").write("Each mutant = one deliberate bug in a copy of lib.py; test_lib.py must fail.\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
