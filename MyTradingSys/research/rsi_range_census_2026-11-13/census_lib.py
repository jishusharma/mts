"""Pure helpers for the RSI range census: percentiles, bands, episodes, bucket lookup."""
import numpy as np

PCTS = [0.1, 0.5, 1, 2.5, 5, 10, 25, 50, 75, 90, 95, 97.5, 99, 99.5, 99.9]


def percentiles(values, pcts=PCTS):
    """Linear-interpolated percentiles of the finite values (numpy default method)."""
    a = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=float)
    return {p: float(np.percentile(a, p)) for p in pcts}


def band(x, p1, p5):
    """Operator words: below the 1st pct = rarely hit; 1st-5th = sometimes hit; else common."""
    if x < p1:
        return "rarely hit"
    if x <= p5:
        return "sometimes hit"
    return "common"


def episode_starts(vals, thr, include_equal=False):
    """Indices where a run of consecutive bars below thr (<= if include_equal) begins.
    None/NaN bars end a run."""
    starts = []
    inrun = False
    for i, v in enumerate(vals):
        ok = v is not None and np.isfinite(v) and (v <= thr if include_equal else v < thr)
        if ok and not inrun:
            starts.append(i)
        inrun = ok
    return starts


def bucket_of(x, edges):
    """edges ascending e.g. [25,30,...]; returns index 0..len(edges); x<edges[0] -> 0."""
    return int(np.searchsorted(np.asarray(edges), x, side="right"))
