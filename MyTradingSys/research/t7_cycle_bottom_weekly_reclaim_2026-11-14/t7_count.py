"""T7 counting step: signal and unit counts only. NO return, trade outcome or price change is computed here (risk % is
a price-structure quantity of the stop, not an outcome). Output printed and written to counts.json."""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t7_core as core  # noqa: E402


def main():
    print(core.set_below_normal())
    lk = core.acquire_slot("t7_count")
    try:
        here = pathlib.Path(__file__).resolve().parent
        uni = core.universe()
        segs = []
        for coin, sp, fp in uni:
            segs.extend(core.load_segments(sp, coin))
        alive = core.alive_counts(segs)
        thin = {ms for ms, c in alive.items() if c < core.MIN_ALIVE_COINS}
        rows, risks = [], []
        skipped_incomplete = 0
        for s in segs:
            for ev in core.events(s):
                d0 = ev["d0"]
                complete = (d0 + core.HOLD_DAYS - 1 < s.n) or s.ended
                if not complete:
                    skipped_incomplete += 1
                    continue
                r = core.stop_risk(s, d0, float(s.o[d0]))
                if r != r:
                    continue
                risks.append(r)
                rows.append((s.name, int(s.ms[ev["s"]]), int(s.ms[d0]), core.split_of(int(s.ms[ev["s"]])), r,
                             int(s.ms[ev["s"]]) in thin))
        out = dict(coins=len(uni), segments=len(segs), signals_total=len(rows) + skipped_incomplete,
                   skipped_incomplete_window=skipped_incomplete, thin_dates=len(thin))
        for sp in ("DEV", "VAL"):
            use = [r for r in rows if r[3] == sp and not r[5]]
            wk = sorted({core.week_index(r[2]) for r in use})
            out[sp] = dict(trades=len(use), thin_excluded=sum(1 for r in rows if r[3] == sp and r[5]),
                           entry_weeks=len(wk), coins=len({r[0] for r in use}))
            if sp == "VAL":
                lo = core.week_index(int(__import__("datetime").datetime(2024, 1, 1,
                                        tzinfo=__import__("datetime").timezone.utc).timestamp() * 1000))
                blocks = {(w - lo) // 4 for w in wk}
                out[sp]["blocks4"] = len(blocks)
                out[sp]["n_gate"] = min(37, len(blocks))
                eps = []
                last = None
                for r in sorted(use, key=lambda r: r[2]):
                    if last is not None and r[2] - last < 28 * core.DAY:
                        eps[-1] += 1
                    else:
                        eps.append(1)
                    last = r[2]
                out[sp]["episodes"] = len(eps)
        out["risk_median"] = float(np.median(risks))
        out["risk_p10_p90"] = [float(np.percentile(risks, 10)), float(np.percentile(risks, 90))]
        out["fee_R_median"] = core.FEE_RT / out["risk_median"]
        out["fee_rt"] = core.FEE_RT
        (here / "counts.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(json.dumps(out, indent=1))
    finally:
        core.release_slot(lk)


if __name__ == "__main__":
    main()
