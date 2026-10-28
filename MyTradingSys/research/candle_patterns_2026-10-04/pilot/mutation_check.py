import shutil, subprocess, sys, tempfile, os
SRC = "MyTradingSys/research/candle_patterns_2026-10-04/pilot"
MUTS = [
 ("op_rule.py", 'e_px, t_e = L, b["t"] + day_ms // 2', 'e_px, t_e = b["o"], b["t"] + day_ms // 2', "stop-buy filled at open instead of L"),
 ("op_rule.py", "return bars[j][\"c\"] < bars[j - 1][\"c\"] if side > 0", "return bars[j][\"c\"] <= bars[j - 1][\"c\"] if side > 0", "exit on equal close"),
 ("op_rule.py", "net = gross - 2 * (fee + slip) - side * fund", "net = gross - 2 * (fee + slip) - fund", "short funding sign ignored"),
 ("op_rule.py", "cost = (fee + slip if d == e else 0.0) + (fee + slip if d == x else 0.0)", "cost = (fee + slip if d == e else 0.0)", "exit cost dropped from daily series"),
 ("candles.py", "and all(f[j][\"c\"] <= ins[\"h\"] for j in range(m + 3, i))", "and True", "hikkake first-occurrence dropped"),
 ("candles.py", "if x[\"body\"] <= 0.1 * x[\"rng\"]:", "if x[\"body\"] <= 0.5 * x[\"rng\"]:", "doji threshold changed"),
 ("candles.py", "p[\"red\"] and x[\"green\"] and x[\"o\"] > p[\"c\"] and x[\"c\"] < p[\"o\"]", "p[\"red\"] and x[\"green\"] and x[\"o\"] > p[\"c\"]", "harami body containment dropped"),
 ("stats_lite.py", "cen = [(x - mb) / sds[k] for x in boot[k]]", "cen = [x / sds[k] for x in boot[k]]", "bootstrap not centred"),
 ("cdata.py", "if end_ms is None or end_ms > DEV_END_MS:", "if False:", "dev-only guard removed"),
 ("cdata.py", "i, j = bisect.bisect_right(self.times, t0), bisect.bisect_right(self.times, t1)", "i, j = bisect.bisect_left(self.times, t0), bisect.bisect_right(self.times, t1)", "funding window includes t0"),
]
caught = 0
for fn, a, b, label in MUTS:
    d = tempfile.mkdtemp()
    dst = os.path.join(d, "pilot")
    shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns("__pycache__"))
    # cdata resolves ROOT from its own path; keep repo-relative loaders working by pointing it at the real tree
    p = os.path.join(dst, fn)
    s = open(p, encoding="utf-8").read()
    if a not in s:
        print("NOT-APPLIED", label); continue
    open(p, "w", encoding="utf-8", newline="\n").write(s.replace(a, b, 1))
    cd = os.path.join(dst, "cdata.py")
    t = open(cd, encoding="utf-8").read().replace("Path(__file__).resolve().parents[4]", "Path(r'%s')" % os.getcwd())
    open(cd, "w", encoding="utf-8", newline="\n").write(t)
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", dst, "-p", "test_*.py"], capture_output=True, text=True)
    ok = r.returncode != 0
    caught += ok
    print("CAUGHT " if ok else "MISSED ", label)
    shutil.rmtree(d, ignore_errors=True)
print(caught, "of", len(MUTS))
