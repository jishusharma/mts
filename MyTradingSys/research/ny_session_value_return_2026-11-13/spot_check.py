"""Independent re-computation of one prior-session value area (not via auction_context) vs study.prior_profile."""
import sys, datetime as dt, math
import numpy as np
import study
npz = sys.argv[1]
bars, sess = study.build_sessions(npz, "BTCUSDT")
t, o, h, l, c, v = bars
by = {s["date"]: (k, s) for k, s in enumerate(sess)}
d = dt.date(2024, 3, 12)
k, cur = by[d]; prev = sess[k - 1]
p = study.prior_profile(bars, prev, cur)
i0, i1 = prev["i0"], prev["i1"]
bin_ = float(c[i0:i1].mean()) * study.BIN_FRAC
vol = {}
for j in range(i0, i1):
    key = math.floor(((h[j] + l[j] + c[j]) / 3) / bin_)
    vol[key] = vol.get(key, 0) + v[j]
tot = sum(vol.values()); poc = max(vol, key=vol.get); lo = hi = poc; acc = vol[poc]
while acc < 0.7 * tot:
    up = vol.get(hi + 1, 0); dn = vol.get(lo - 1, 0)
    if up >= dn: hi += 1; acc += up
    else: lo -= 1; acc += dn
print("repo", p["val"], p["vah"], p["poc"]); print("indep", lo * bin_, (hi + 1) * bin_, poc * bin_)
