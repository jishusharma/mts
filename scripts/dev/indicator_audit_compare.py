"""Compare reviewer answers with our engine's indicator values, in code (card indicator-values-multi-model-audit).

  python scripts/dev/indicator_audit_compare.py --packets <dir> --replies <replies.json> [--reviewer Haiku]

replies.json = {packet_id: {answer_key: number}}. Engine values are computed here from the packet's closes by the
functions every layer reads: rsi_core (RSI), chart_verify.bollinger / stochrsi, live_bb_top_reversal.bollinger.
A model is never shown our value. Exit code 1 when any value is a mismatch.

Tolerance (OURS, fixed before any reply): RSI and StochRSI K, D absolute 0.01 points; Bollinger mid/upper/lower
relative 1e-6 (population sd, FORMULAS.md s22).
"""
import argparse
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

TOL_ABS = {"RSI": 0.01, "StochRSI_K": 0.01, "StochRSI_D": 0.01}
TOL_REL = {"BB_mid": 1e-6, "BB_up": 1e-6, "BB_low": 1e-6}


def engine_values(indicator, closes):
    import chart_verify as cv
    out = {}
    if indicator == "RSI":
        out["RSI"] = cv.rsi(closes)[-1]
    elif indicator == "BB":
        up, mid, lo = cv.bollinger(closes)
        out.update(BB_mid=mid[-1], BB_up=up[-1], BB_low=lo[-1])
    elif indicator == "STOCHRSI":
        k, d = cv.stochrsi(closes)
        out.update(StochRSI_K=k[-1], StochRSI_D=d[-1])
    else:
        raise ValueError(indicator)
    return out


def engine_bb_live(closes):
    """Second engine route for Bollinger: the live alert layer's own copy (upper, lower)."""
    from MyTradingSys.backtest.layers.alerts.live_bb_top_reversal import bollinger
    up, lo = bollinger(closes)
    return {"BB_up": up[-1], "BB_low": lo[-1]}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def compare_value(indicator, engine, reply):
    """-> one row per expected key: {key, engine, reviewer, diff, tol, ok}. Missing / non-finite reply = not ok."""
    rows = []
    for key, eng in engine.items():
        rev = reply.get(key) if isinstance(reply, dict) else None
        if not _num(rev) or not _num(eng):
            rows.append({"key": key, "engine": eng, "reviewer": rev, "diff": None, "tol": None, "ok": False})
            continue
        diff = rev - eng
        if key in TOL_ABS:
            tol, ok = TOL_ABS[key], abs(diff) <= TOL_ABS[key]
        else:
            tol, ok = TOL_REL[key], (abs(diff) <= TOL_REL[key] * abs(eng) if eng != 0 else diff == 0)
        rows.append({"key": key, "engine": eng, "reviewer": rev, "diff": diff, "tol": tol, "ok": ok})
    return rows


def run(packets, replies):
    """-> {n_values, n_mismatch, rows, mismatches}. A packet with no reply counts all its values as mismatches."""
    rows, bad = [], []
    for p in packets:
        eng = engine_values(p["indicator"], p["closes"])
        for r in compare_value(p["indicator"], eng, replies.get(p["id"], {})):
            r = dict(r, packet=p["id"], indicator=p["indicator"])
            rows.append(r)
            if not r["ok"]:
                bad.append(r)
    return {"n_values": len(rows), "n_mismatch": len(bad), "rows": rows, "mismatches": bad}


def live_route_check(packets):
    """Engine self-consistency: the live alert layer's Bollinger must equal chart_verify's. -> list of disagreements."""
    out = []
    for p in packets:
        if p["indicator"] != "BB":
            continue
        a, b = engine_values("BB", p["closes"]), engine_bb_live(p["closes"])
        for key in ("BB_up", "BB_low"):
            if abs(a[key] - b[key]) > 1e-9 * abs(a[key]):
                out.append({"packet": p["id"], "key": key, "chart_verify": a[key], "live_bb": b[key]})
    return out


def other_routes(packets):
    """Other copies of the same maths that layers read: krown_core.rsi and wlow_bounce.detector.bollinger_upper.
    -> list of disagreements with the main engine route (RSI abs 0.01, BB relative 1e-6, same tolerance as the audit)."""
    from MyTradingSys.backtest.layers.krown.krown_core import rsi as krown_rsi
    from MyTradingSys.backtest.layers.wlow_bounce.detector import bollinger_upper
    out = []
    for p in packets:
        if p["indicator"] == "RSI":
            a, b = engine_values("RSI", p["closes"])["RSI"], krown_rsi(p["closes"], 14)[-1]
            if abs(a - b) > TOL_ABS["RSI"]:
                out.append({"packet": p["id"], "key": "RSI", "main": a, "krown_core": b})
        elif p["indicator"] == "BB":
            a, b = engine_values("BB", p["closes"])["BB_up"], bollinger_upper(p["closes"])[-1]
            if abs(a - b) > TOL_REL["BB_up"] * abs(a):
                out.append({"packet": p["id"], "key": "BB_up", "main": a, "wlow_bounce": b})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--packets", required=True)
    ap.add_argument("--replies", required=True)
    ap.add_argument("--reviewer", default="reviewer")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    pk = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(pathlib.Path(a.packets).glob("*.json"))
          if f.name != "manifest.json"]
    replies = json.loads(pathlib.Path(a.replies).read_text(encoding="utf-8"))
    res = run(pk, replies)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"{a.reviewer}: values={res['n_values']} mismatches={res['n_mismatch']}")
        for r in res["mismatches"]:
            print(f"  MISMATCH {r['packet']} {r['key']} engine={r['engine']} reviewer={r['reviewer']} diff={r['diff']}")
    return 1 if res["n_mismatch"] else 0


if __name__ == "__main__":
    sys.exit(main())
