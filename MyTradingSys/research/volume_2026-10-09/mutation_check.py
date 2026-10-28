"""Fail-before proof: each mutation of the study code must make test_volume.py fail (LESSONS_LEARNED 2026-10-08: no git stash;
mutants live in a scratch copy). Run: python mutation_check.py"""
import sys
sys.dont_write_bytecode = True
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MUTS = [
    ("vfeat.py", '(rv >= 2) & up_bar, (rv >= 2) & dn_bar', '(rv >= 3) & up_bar, (rv >= 2) & dn_bar'),
    ("vfeat.py", '(clv <= 1 / 3)', '(clv <= 1 / 2)'),
    ("vfeat.py", 'ag, al = gain[:period].mean(), loss[:period].mean()', 'ag, al = gain[:period].sum() / max(1, (gain[:period] > 0).sum()), loss[:period].sum() / max(1, (loss[:period] > 0).sum())'),
    ("vfeat.py", 'out[w:] = fn(swv(x, w)[:-1], axis=1)', 'out[w:] = fn(swv(x, w)[1:], axis=1)'),
    ("vfeat.py", 'f["dp"] = (2 * tbv - v) / v', 'f["dp"] = (tbv - v) / v'),
    ("vfeat.py", 'bup, bdn = c > f["up_prev"], c < f["lo_prev"]', 'bup, bdn = c > f["bb_up"], c < f["bb_lo"]'),
    ("vfeat.py", 'weekday = ((day + 3) % 7).astype(int)', 'weekday = ((day + 4) % 7).astype(int)'),
    ("vfeat.py", 'sg = np.where(slot <= 1, 0, np.where(slot <= 3, 1, 2))', 'sg = np.where(slot <= 2, 0, np.where(slot <= 3, 1, 2))'),
    ("vfeat.py", 'out[s * k:] = v[s * k:] / np.median(stack, axis=0)', 'out[s * k:] = v[s * k:] / np.mean(stack, axis=0)'),
    ("vdata.py", 'i = bisect.bisect_right(self.times, t0)', 'i = bisect.bisect_left(self.times, t0)'),
    ("vdata.py", 'if end_ms > VALID_END_MS and not unseal:', 'if end_ms > VALID_END_MS + 10 ** 12 and not unseal:'),
    ("vstats.py", 'stat = sum_ev_val / n[:, None] - sum_all / m', 'stat = sum_ev_val / n[:, None]'),
    ("vstate.py", 'e[k + "_HI"] = (pr >= 2 / 3) & valid', 'e[k + "_HI"] = (pr >= 1 / 2) & valid'),
    ("vstate.py", 'out[win:] = (prev <= x[win:, None]).mean(axis=1)', 'out[win:] = (prev < x[win:, None]).mean(axis=1)'),
    ("vstate.py", 'if hr >= 16:', 'if hr >= 15:'),
    ("vstate.py", 'bull, bear = rsi >= 60, rsi <= 40', 'bull, bear = rsi > 60, rsi < 40'),
    ("vstate.py", 's["VT"] = np.log(m20 / m100)', 's["VT"] = np.log(m20 / roll_sum(v, 50) * 50)'),
    ("vstate.py", 's["D20"] = roll_sum(dv, 20) / roll_sum(v, 20)', 's["D20"] = roll_sum(dv, 20) / roll_sum(v, 21)'),
    ("vstats.py", '"p_one": float((np.sum(cen >= diff) + 1.0) / (len(d) + 1))}', '"p_one": float((np.sum(cen <= diff) + 1.0) / (len(d) + 1))}'),
    ("vstats.py", 'diff = float(sumA.sum() / nA - sumB.sum() / nB)', 'diff = float(sumB.sum() / nB - sumA.sum() / nA)'),
    ("vstats.py", 'return (z_alpha + z_power) * sd / np.sqrt(max(n, 1))', 'return (z_alpha + z_power) * sd / max(n, 1)'),
]
bad = 0
for fname, old, new in MUTS:
    tmp = Path(tempfile.mkdtemp(prefix="vmut_"))
    try:
        shutil.copytree(HERE, tmp / "volume_2026-10-09", ignore=shutil.ignore_patterns("__pycache__", "*.md", "*.csv"))
        shutil.copytree(HERE.parent / "candle_patterns_2026-10-04" / "pilot", tmp / "candle_patterns_2026-10-04" / "pilot",
                        ignore=shutil.ignore_patterns("__pycache__"))
        p = tmp / "volume_2026-10-09" / fname
        s = p.read_text(encoding="utf-8")
        if old not in s:
            print("MUTATION TEXT NOT FOUND", fname, old[:50]); bad += 1; continue
        p.write_text(s.replace(old, new, 1), encoding="utf-8", newline="\n")
        # vdata.ROOT is parents[3]: keep the data root reachable by running from the scratch copy with ROOT patched
        killed = False
        for tf_ in ("test_volume.py", "test_state.py"):
            r = subprocess.run([sys.executable, str(tmp / "volume_2026-10-09" / tf_)], capture_output=True, text=True, timeout=600)
            killed = killed or r.returncode != 0
        print(("KILLED  " if killed else "SURVIVED"), fname, "|", old[:55].replace("\n", " "))
        if not killed:
            bad += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print("survivors:", bad)
sys.exit(1 if bad else 0)
