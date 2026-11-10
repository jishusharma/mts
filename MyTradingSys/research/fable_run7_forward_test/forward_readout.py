"""Forward readout: closed-trades log -> one markdown table per forward slot (E+/E- rule + Krown FAIL-A/B/C).

Input (read-only): trade_ledger.jsonl rows written by MyTradingSys/execution/trade_ledger.py (one per closed
auto-trade). Fields used: source, account, plan_id, entry.ts (UTC day = cluster), net_pnl_usd (fee-net USD),
and the risk in USD, first found of: risk_usd | stop with entry.price and entry.amount
(|price - stop| / price x amount) | net_r. Rows with "unresolved" or no R are counted, never scored.

Slots (source prefix; Krown also needs account krown_s8, else the fill is CONTAMINATED and excluded):
  krown_s8            layer:krown:s8_break:4h        testnet   FAIL-A/B/C apply (FORWARD_PREREG s3)
  malkan_level_short  layer:rsi:malkan_level_short   paper     E+/E- only
  t06_rsi_ma          layer:rsi:rsi_ma_cross         paper     E+/E- only
The E+/E- math is sim_sequential.py's (eh-f1-testnet-design), loaded not copied. One observation per UTC-day
cluster (mean R of that day's trades); n in the table counts trades, n_obs counts clusters.

Run: python MyTradingSys/research/fable_run7_forward_test/forward_readout.py --ledger <trade_ledger.jsonl> [--paper [SLOT=]<journal.jsonl> ...] [--asof YYYY-MM-DD] [--out file.md]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SIM_PATH = ROOT / "MyTradingSys/research/edge_hunt_2026-11-09/results/eh-f1-testnet-design/sim_sequential.py"

# (slot key, source prefix, required account or None, Krown rules, label)
SLOTS = [
    ("krown_s8", "layer:krown:s8_break:4h", "krown_s8", True, "Krown S8 4h (testnet)"),
    ("malkan_level_short", "layer:rsi:malkan_level_short", None, False, "Malkan level short 4h (paper)"),
    ("t06_rsi_ma", "layer:rsi:rsi_ma_cross", None, False, "T06 RSI-MA 4h (paper)"),
]
FAIL_DD_R, FAIL_STREAK, FAIL_C_N, FAIL_C_Z = 12.0, 12, 30, 1.28
RETIRE_DAYS = 365


def load_sim():
    spec = importlib.util.spec_from_file_location("sim_sequential", SIM_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sim_sequential"] = mod
    spec.loader.exec_module(mod)
    return mod


def _ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def row_r(row):
    """Fee-net R of a ledger row, or None when it cannot be scored."""
    if row.get("unresolved") or row.get("net_pnl_usd") is None:
        return None
    risk = row.get("risk_usd")
    e = row.get("entry") or {}
    if risk is None and row.get("stop") and e.get("price") and e.get("amount"):
        risk = abs(e["price"] - row["stop"]) / e["price"] * e["amount"]
    if risk:
        return row["net_pnl_usd"] / risk
    if row.get("net_r") is not None:
        return float(row["net_r"])
    return None


def read_jsonl(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def drawdown_and_streak(xs):
    cum = peak = dd = 0.0
    run = longest = 0
    for x in xs:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
        run = run + 1 if x < 0 else 0
        longest = max(longest, run)
    return dd, longest


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n < 2:
        return m, float("nan")
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def krown_fail(xs):
    """First applicable of FAIL-A/B/C over the whole history, or None (FORWARD_PREREG s3)."""
    cum = peak = 0.0
    run = 0
    for i, x in enumerate(xs, 1):
        cum += x
        peak = max(peak, cum)
        run = run + 1 if x < 0 else 0
        if peak - cum >= FAIL_DD_R - 1e-9:
            return "FAIL-A"
        if run >= FAIL_STREAK:
            return "FAIL-B"
        if i >= FAIL_C_N:
            m, se = mean_se(xs[:i])
            if m + FAIL_C_Z * se < 0:
                return "FAIL-C"
    return None


def slot_stats(key, rs, days, krown, asof, sim):
    import numpy as np
    n = len(rs)
    dd, streak = drawdown_and_streak(rs)
    m, se = mean_se(rs)
    # one observation per UTC-day cluster, in time order
    clusters = {}
    for r, d in zip(rs, days):
        clusters.setdefault(d, []).append(r)
    obs = [sum(v) / len(v) for _, v in sorted(clusters.items())]
    res = {"slot": key, "n": n, "n_obs": len(obs), "mean_r": m, "se": se, "dd_r": dd, "streak": streak,
           "e_plus": 1.0, "e_minus": 1.0, "state": "RUNNING"}
    if not obs:
        return res
    cfg = sim.RuleCfg()
    try:
        x = np.array(obs, dtype=float)
        res["e_plus"] = float(sim.e_promote(x, cfg.mu0, cfg.a)[0, -1])
        res["e_minus"] = float(sim.e_kill(x, cfg.delta, cfg.b)[0, -1])
        code, _ = sim.decide(x, cfg)
    except ValueError:
        res["state"] = "REVIEW"       # an R outside [a, b]: execution failure, a human reads it
        return res
    fail = krown_fail(rs) if krown else None
    if fail:
        res["state"] = fail
    elif code[0] == -1:
        res["state"] = "KILL"
    elif code[0] == 1:
        res["state"] = "PROMOTE"
    elif len(obs) >= cfg.n_max or (asof - min(days)).days >= RETIRE_DAYS:
        res["state"] = "RETIRE"
    return res


def _paper_ts(row):
    """UTC datetime of a paper-journal row: t_fill / t_trigger (open ms) or a ts string; None if absent."""
    for k in ("t_fill", "t_trigger"):
        v = row.get(k)
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v / 1000.0, tz=timezone.utc)
    ts = row.get("ts")
    return _ts(ts) if isinstance(ts, str) else None


def _paper_slot(row, default_slot):
    src = row.get("source") or ""
    return next((s[0] for s in SLOTS if src.startswith(s[1])), default_slot)


def readout(ledger_path=None, asof=None, paper=()):
    """paper: iterable of (path, default_slot_key). Journal rows (malkan_level_short_live.py): kind outcome with
    status closed and net_r is scored; signal / no_fill / unresolved / open outcomes are counted, never scored;
    kill rows are listed. DECISION (OURS): a row without a source goes to the file's default slot."""
    sim = load_sim()
    asof_d = datetime.strptime(asof, "%Y-%m-%d").date() if asof else datetime.now(timezone.utc).date()
    buckets = {k: [] for k, *_ in SLOTS}
    contaminated = unresolved = unscored = other = 0
    pcount = {"signal": 0, "no_fill": 0, "unresolved": 0, "open": 0, "scored": 0}
    kills = []
    for path, dslot in paper:
        for row in read_jsonl(path):
            kind, key = row.get("kind"), _paper_slot(row, dslot)
            if kind == "kill":
                kills.append({"slot": key, **{k: v for k, v in row.items() if k != "kind"}})
            elif kind in ("signal", "no_fill", "unresolved"):
                pcount[kind] += 1
            elif kind == "outcome":
                t = _paper_ts(row)
                if row.get("status") != "closed":
                    pcount["open"] += 1
                elif row.get("net_r") is None or t is None:
                    unscored += 1
                else:
                    pcount["scored"] += 1
                    buckets[key].append((t, float(row["net_r"])))
    for row in (read_jsonl(ledger_path) if ledger_path else []):
        src = row.get("source") or ""
        slot = next((s for s in SLOTS if src.startswith(s[1])), None)
        if slot is None:
            other += 1
            continue
        key, _, acct, _, _ = slot
        if acct and row.get("account") != acct:
            contaminated += 1
            continue
        if row.get("unresolved"):
            unresolved += 1
            continue
        r = row_r(row)
        if r is None:
            unscored += 1
            continue
        ts = (row.get("entry") or {}).get("ts") or row.get("ts")
        buckets[key].append((_ts(ts), r))
    slots = []
    for key, _, _, krown, label in SLOTS:
        items = sorted(buckets[key])
        slots.append({**slot_stats(key, [r for _, r in items], [t.date() for t, _ in items], krown, asof_d, sim),
                      "label": label})
    return {"slots": slots, "contaminated": contaminated, "unresolved": unresolved, "unscored": unscored,
            "other_sources": other, "asof": str(asof_d),
            "paper": pcount if paper else None, "kills": kills}


def _f(x, nd=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def to_markdown(res):
    lines = [f"# Forward readout (as of {res['asof']})", "",
             "| slot | n | mean R | SE | DD R | streak | E+ | E- | state |", "|---|---|---|---|---|---|---|---|---|"]
    for s in res["slots"]:
        lines.append(f"| {s['slot']} | {s['n']} | {_f(s['mean_r'], 3)} | {_f(s['se'], 3)} | {_f(s['dd_r'])} | "
                     f"{s['streak']} | {_f(s['e_plus'])} | {_f(s['e_minus'])} | {s['state']} |")
    lines += ["", "Rule: PROMOTE E+ >= 80 after n_obs >= 30; KILL E- >= 10 after n_obs >= 10; RETIRE at 150 obs or "
              "12 months; Krown only: FAIL-A 12 R drawdown, FAIL-B 12 straight losers, FAIL-C n >= 30 and "
              "mean + 1.28 SE < 0. Fee-net R, one observation per UTC-day cluster (n counts trades).",
              f"Excluded: contaminated (Krown source, other account) {res['contaminated']}, unresolved "
              f"{res['unresolved']}, no risk/R {res['unscored']}, other sources {res['other_sources']}."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger")
    ap.add_argument("--paper", action="append", default=[],
                    help="paper journal jsonl, repeatable; optional SLOT=path (default slot malkan_level_short)")
    ap.add_argument("--asof")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    paper = []
    for spec in a.paper:
        slot, _, path = spec.partition("=")
        paper.append((path, slot) if path and slot in {x[0] for x in SLOTS} else (spec, "malkan_level_short"))
    if not a.ledger and not paper:
        ap.error("need --ledger and/or --paper")
    md = to_markdown(readout(a.ledger, a.asof, paper))
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8", newline="\n")
    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
