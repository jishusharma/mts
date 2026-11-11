"""T02 follow-up: truncation + NaN-poison test for study detectors, one study per run.

Usage: python t02_study_trunc.py <study> [--cuts N] [--seed S]

For each seeded cut index k on the shared DEV tape: T = bar[k].t; tail bars k+1.. are NaN-poisoned; the study
build runs on the truncated tape; events are keyed by their own stamp t.
  late    = in full (t <= T) not in trunc  (confirmation lag, expected; not a fail)
  repaint = in trunc (t <= T) not in full  (a later bar changes a past event: LOOK-AHEAD, FAIL)

Mirrors scripts/T02/t02_truncation.py (live layers) for the 3b study detectors that load F:/MTS/data.
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = HERE.parents[4]
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

STUDIES = {} ; STUDIES = {
    "preopen": dict(dir="opr_preopen_tops_2026-10-16", build="build", key="t"),
}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_tape():
    sys.path.insert(0, str(R / "MyTradingSys" / "research" / "chart_read_g5_2026-10-16"))
    import common as K
    return K.load(), K


def events(mod, cfg, A):
    res = getattr(mod, cfg["build"])(A)
    ev = res[0] if isinstance(res, tuple) else res
    return np.asarray(ev[cfg["key"]], dtype=np.int64)


def run(name, n_cuts, seed):
    cfg = STUDIES[name]
    A, K = load_tape()
    mod = load_module(R / "MyTradingSys" / "research" / cfg["dir"] / "study.py", "t02_" + name)
    n = len(A["O"])
    t_all = events(mod, cfg, A)
    rng = np.random.default_rng(seed)
    cuts = sorted(set(int(x) for x in rng.integers(2000, n - 1, size=n_cuts)))
    rows = []
    t0 = time.time()
    for k in cuts:
        T = K.TS0 + k * K.MS
        A2 = {k2: v.copy() for k2, v in A.items()}
        for k2 in A2:
            A2[k2][k + 1:] = np.nan
        try:
            t_tr = events(mod, cfg, A2)
        except Exception as e:
            rows.append(dict(k=k, err=type(e).__name__ + ": " + str(e)[:100]))
            continue
        ft = set(int(x) for x in t_all[t_all <= T])
        at = set(int(x) for x in t_tr[t_tr <= T])
        rows.append(dict(k=k, full=len(ft), trunc=len(at), late=len(ft - at), repaint=len(at - ft)))
    n_bad = sum(1 for r in rows if r.get("repaint", 0) > 0)
    n_err = sum(1 for r in rows if "err" in r)
    if n_err == len(rows):
        verdict = "HARNESS_ERR"
    elif n_bad:
        verdict = "FAIL (repaint)"
    else:
        verdict = "PASS"
    out = dict(study=name, n=n, cuts=len(cuts), secs=round(time.time() - t0, 1),
               n_full=int(len(t_all)), verdict=verdict, errs=n_err,
               max_late=max((r.get("late", 0) for r in rows), default=0),
               first=rows[:3], last=rows[-3:])
    (OUT / ("study_trunc_" + name + ".json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("study", choices=sorted(STUDIES))
    ap.add_argument("--cuts", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261016)
    a = ap.parse_args()
    return run(a.study, a.cuts, a.seed)


if __name__ == "__main__":
    sys.exit(main())
