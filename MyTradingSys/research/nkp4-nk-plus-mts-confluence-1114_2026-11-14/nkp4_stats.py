"""Day-cluster statistics (numpy only). Fixed seeds."""
import numpy as np

B = 2000


def day_sums(day, x):
    ud, inv = np.unique(day, return_inverse=True)
    return ud, np.bincount(inv, weights=x), np.bincount(inv).astype(float)


def boot_means(sums, cnts, rng, b=B):
    nd = len(sums)
    idx = rng.integers(0, nd, (b, nd))
    return sums[idx].sum(1) / cnts[idx].sum(1)


def cluster(day, x, rng, b=B):
    """mean, n, days, lo90 (5th pct), lo95 (2.5th), hi95, one-sided p (mean<=0)."""
    ud, s, c = day_sums(day, x)
    bm = np.sort(boot_means(s, c, rng, b))
    return dict(n=int(len(x)), days=int(len(ud)), mean=float(x.mean()), lo90=float(bm[int(0.05 * b)]),
                lo95=float(bm[int(0.025 * b)]), hi95=float(bm[int(0.975 * b)]),
                p=float((np.sum(bm <= 0) + 1) / (b + 1)))


def ex_best(day, x, k=5):
    ud, s, c = day_sums(day, x)
    keep = np.argsort(-s)[k:]
    return float(s[keep].sum() / c[keep].sum()) if len(keep) and c[keep].sum() > 0 else float("nan")


def diff_cluster(day_a, xa, day_b, xb, rng, b=B):
    """Day-clustered difference mean(a)-mean(b) with se (joint resampling of days)."""
    ud = np.union1d(day_a, day_b)
    ia = np.searchsorted(ud, day_a); ib = np.searchsorted(ud, day_b)
    sa = np.bincount(ia, weights=xa, minlength=len(ud)); ca = np.bincount(ia, minlength=len(ud)).astype(float)
    sb = np.bincount(ib, weights=xb, minlength=len(ud)); cb = np.bincount(ib, minlength=len(ud)).astype(float)
    idx = rng.integers(0, len(ud), (b, len(ud)))
    with np.errstate(invalid="ignore", divide="ignore"):
        d = sa[idx].sum(1) / ca[idx].sum(1) - sb[idx].sum(1) / cb[idx].sum(1)
    return float(xa.mean() - xb.mean()), float(np.nanstd(d))


def bh(pvals, q=0.10):
    """Benjamini-Hochberg adjusted q-values."""
    p = np.asarray(pvals, float); m = len(p)
    if m == 0:
        return np.array([])
    o = np.argsort(p); adj = p[o] * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(adj, 1.0)
    return out
