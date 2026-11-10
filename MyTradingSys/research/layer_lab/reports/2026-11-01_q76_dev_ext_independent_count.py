import csv, json, sys
import numpy as np
from pathlib import Path
EXT = Path("F:/MTS/data/dev_ext_2019_2021/klines")
W = 10.0; CUT = 1640995200000; D0 = 1577836800000; MIN = 60000
ND = 731; N = ND * 1440
def load():
    A = {k: np.full(N, np.nan) for k in "OHLCV"}; files = sorted(EXT.glob("BTCUSDT-1m-*.csv")); n = 0
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit(): continue
                t = int(float(r[0]))
                if t >= CUT: raise SystemExit("CUTOFF VIOLATION %s %d" % (f.name, t))
                i = (t - D0) // MIN
                if 0 <= i < N:
                    A["O"][i] = float(r[1]); A["H"][i] = float(r[2])
                    A["L"][i] = float(r[3]); A["C"][i] = float(r[4])
                    A["V"][i] = float(r[5]); n += 1
    return A, files, n
def profile(l, h, v):
    ok = (~np.isnan(l)) & (~np.isnan(h)) & (~np.isnan(v)) & (v > 0)
    l, h, v = l[ok], h[ok], v[ok]
    if len(l) == 0: return None
    kl = np.floor(l / W).astype(np.int64); kh = np.floor(h / W).astype(np.int64)
    k0 = int(kl.min()); k1 = int(kh.max()); vol = np.zeros(k1 - k0 + 1)
    for li, hi, vi, a, b in zip(l.tolist(), h.tolist(), v.tolist(), (kl - k0).tolist(), (kh - k0).tolist()):
        if hi > li:
            for k in range(a, b + 1):
                ov = min(hi, (k + k0 + 1) * W) - max(li, (k + k0) * W)
                if ov > 0: vol[k] += vi * ov / (hi - li)
        else: vol[a] += vi
    tot = vol.sum()
    if tot <= 0: return None
    ip = int(np.argmax(vol)); lo = ip; hi_ = ip; acc = vol[ip]
    while acc < 0.70 * tot and (lo > 0 or hi_ < len(vol) - 1):
        vl = vol[lo - 1] if lo > 0 else -1.0; vh = vol[hi_ + 1] if hi_ < len(vol) - 1 else -1.0
        if vl >= vh and lo > 0: lo -= 1; acc += vol[lo]
        elif hi_ < len(vol) - 1: hi_ += 1; acc += vol[hi_]
        else: lo -= 1; acc += vol[lo]
    return (hi_ + 1 + k0) * W, (lo + k0) * W
def five(A, d):
    s = slice(d * 1440, (d + 1) * 1440)
    O = A["O"][s].reshape(288, 5); H = A["H"][s].reshape(288, 5)
    L = A["L"][s].reshape(288, 5); C = A["C"][s].reshape(288, 5)
    ok = ~(np.isnan(O).any(1) | np.isnan(H).any(1) | np.isnan(L).any(1) | np.isnan(C).any(1))
    hh = np.nanmax(np.where(np.isnan(H), -np.inf, H), 1)
    ll = np.nanmin(np.where(np.isnan(L), np.inf, L), 1)
    return O[:, 0], np.where(ok, hh, np.nan), np.where(ok, ll, np.nan), C[:, -1], ok
def prep(A):
    lev = {}; miss = {}
    for d in range(ND):
        s = slice(d * 1440, (d + 1) * 1440)
        miss[d] = int(np.isnan(A["C"][s]).sum())
        lev[d] = profile(A["L"][s], A["H"][s], A["V"][s])
    return lev, miss
def run(A, lev, miss, rule, floor):
    ev = 0; days = set(); scanned = 0
    for d in range(1, ND):
        p = lev[d - 1]
        if p is None: continue
        if rule == "skip5" and miss[d - 1] > 5: continue
        o, h, l, c, ok = five(A, d)
        got = scan(o, h, l, c, ok, p[0], p[1], floor)
        scanned += 1
        if got: ev += got; days.add(d)
    return dict(rule=rule, floor=floor, days_scanned=scanned, feasible_events=ev, feasible_days=len(days))
def scan(o, h, l, c, ok, vah, val, floor):
    got = 0
    for side in (-1, 1):
        edge = vah if side == -1 else val
        es = edge if side == -1 else -edge
        outside = False; ext = None
        for k in range(288):
            if not ok[k]: continue
            if side == -1: beyond = h[k]; cs = c[k]
            else: beyond = -l[k]; cs = -c[k]
            if cs > es:
                outside = True; ext = beyond if ext is None else max(ext, beyond)
            elif outside and cs < es:
                entry = c[k]; stop = ext if side == -1 else -ext
                sp = abs(stop - entry) / entry * 100.0
                outside = False; ext = None
                if sp >= floor: got += 1
    return got
def main():
    A, files, n = load()
    print(json.dumps(dict(files=len(files), first=files[0].name, last=files[-1].name,
        rows=n, bars=int((~np.isnan(A["C"])).sum()), expected=N)))
    lev, miss = prep(A)
    floors = [float(x) for x in sys.argv[1:]] or [0.40]
    out = []
    for fl in floors:
        for rule in ("all", "skip5"): out.append(run(A, lev, miss, rule, fl))
    print(json.dumps(out))
if __name__ == "__main__":
    main()

