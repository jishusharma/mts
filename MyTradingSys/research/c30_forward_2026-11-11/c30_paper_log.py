"""C30 H2 paper forward logger (card c30-forward-logger). Paper only: NO order, NO account, NO scheduler, NO loop.

Frozen rule: research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md section 1, H2 (15m WaveTrend buy dot wt1 <= -53 + bullish RSI
divergence, only when the last CLOSED 2h bar structure is up; entry open of bar i+1; exit X1 = first wt1 > 0 filled at the next open,
cap 60 bars, also exit when the 2h trend turns down). All rule code is the study code, loaded by path (wt_rsi_div, wavetrend_dots,
wt_context, wt_lower_tf), not copied. Fee = wavetrend_dots.FEE = BINANCE_TAKER x 2 from MyTradingSys/backtest/fees.py.
R of a paper trade = net return / risk, risk = (entry - low of the divergence second pivot) / entry (OURS; the frozen rule has no stop).
Journal rows (jsonl, append-only, runtime_data/ is git-ignored): kind = signal | outcome | no_fill | unresolved | kill. See RULE.md.
Usage: python c30_paper_log.py --once [--journal PATH] [--history-warmup N]
"""
import argparse
import importlib.util
import json
import math
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / "MyTradingSys/research/eagle_eyes_picture_2026-10-28"

SOURCE = "layer:wt:c30_h2_long"
PARAMS_ID = "c30_h2_long_15m_2026-11-11"
STEP = 900000
MIN_BARS = 2000          # OURS: 250 closed 2h bars for the swing structure + EMA warm-up; fail closed below this
FETCH_BARS = 3000        # OURS: 3 klines pages of 1000
KILL_TRADES = 30
JOURNAL_DEFAULT = str(ROOT / "runtime_data/c30_h2_forward.jsonl")
URL = "https://data-api.binance.vision/api/v3/klines"
FIRST_I = 100            # study: signals only from bar index 100


def _err(msg):
    print(json.dumps({"key": "c30_paper_log", "error": msg}), file=sys.stderr, flush=True)


def _load_study():
    """Load the study modules by path. They read DEV caches / argv at import: point them at stubs, then restore."""
    old_argv, old_tmp, old_path = sys.argv, tempfile.tempdir, list(sys.path)
    td = tempfile.mkdtemp()
    try:
        for n in ("btc15m_bbdiv.json", "btc5m_2022_2024h1.json"):
            Path(td, n).write_text(json.dumps([[0, 1.0, 1.0, 1.0, 1.0]]))
        tempfile.tempdir = td
        sys.argv = [sys.argv[0], str(ROOT)]
        sys.path.insert(0, str(STUDY))
        mods = {}
        for name in ("wavetrend_dots", "wt_context", "wt_lower_tf", "wt_rsi_div"):
            if name in sys.modules:
                mods[name] = sys.modules[name]
                continue
            spec = importlib.util.spec_from_file_location(name, STUDY / (name + ".py"))
            m = importlib.util.module_from_spec(spec)
            sys.modules[name] = m
            spec.loader.exec_module(m)
            mods[name] = m
        return mods
    finally:
        sys.argv, tempfile.tempdir = old_argv, old_tmp
        sys.path[:] = old_path


_M = _load_study()
WD, WC, LT, V = _M["wavetrend_dots"], _M["wt_context"], _M["wt_lower_tf"], _M["wt_rsi_div"]


def clean(bars):
    """True only for strictly consecutive finite positive 15m bars (dicts t,o,h,l,c)."""
    last = None
    for b in bars:
        for k in ("o", "h", "l", "c"):
            v = b.get(k)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
                return False
        t = b.get("t")
        if isinstance(t, bool) or not isinstance(t, int) or (last is not None and t - last != STEP):
            return False
        if b["h"] < max(b["o"], b["c"]) or b["l"] > min(b["o"], b["c"]):
            return False
        last = t
    return True


def _series(bars):
    """Study arrays for the bars (all causal)."""
    b = [(x["t"], x["o"], x["h"], x["l"], x["c"]) for x in bars]
    WD.R15 = [list(x) for x in b]            # LT.htf_trend aggregates the 2h bars from this
    w1, w2 = WD.wavetrend(b)
    R = V.rsi([x[4] for x in b])
    tr = LT.htf_trend(b, 15)
    return b, w1, w2, R, tr


def fires(b, w1, w2, R, tr, i):
    """H2 signal on closed bar i (study conditions, bars <= i only)."""
    if i < FIRST_I or w1[i] is None or w2[i] is None or w2[i - 1] is None:
        return False
    return bool(w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -53 and tr[i] == 1
                and V.divergence([x[2] for x in b], [x[3] for x in b], R, i, 1))


def pivot_low(b, i):
    """Low of the divergence second pivot q = lowest low of bars i-7..i."""
    return min(b[m][3] for m in range(i - 7, i + 1))


def settle(b, w1, w2, tr, i):
    """Paper trade of the signal at bar i on the bars known now. None while open/pending, else a dict.
    Uses wt_rsi_div.forward_trade (study); final = exit condition hit at k, or the 60-bar cap reached."""
    n = len(b)
    if i + 1 >= n:
        return None
    O, T = [x[1] for x in b], [x[0] for x in b]
    r = V.forward_trade(O, w1, w2, tr, i, 1, 0, True, T)
    if r is None:
        return None
    k = i + r["bars"]
    x1 = w1[k] > 0
    hit = x1 or tr[k] == -1
    if not hit and i + V.CAP > n - 2:
        return None
    entry = O[i + 1]
    risk = (entry - pivot_low(b, i)) / entry
    out = {"t_exit_bar": T[k], "t_fill": T[i + 1], "entry": entry, "exit": O[k + 1], "bars": r["bars"], "net_pct": r["net"],
           "why": "X1" if x1 else ("trend flip" if hit else "cap"), "risk_frac": risk}
    if not (risk > 0 and math.isfinite(risk)):
        out["status"] = "bad_risk"
        return out
    out["status"] = "closed"
    out["net_r"] = r["net"] / 100.0 / risk
    return out


def kill_status(rows):
    nets = [r["net_r"] for r in rows if r.get("kind") == "outcome" and r.get("status") == "closed"]
    n, total = len(nets), sum(nets)
    return {"verdict": "RUNNING" if n < KILL_TRADES else ("KILL" if total <= 0 else "PAST_30"), "closed": n,
            "net_r_sum": total, "net_r_mean": (total / n) if n else None}


def _read(path):
    rows, p = [], Path(path)
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _append(path, rows):
    if not rows:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def step(bars, journal_path=JOURNAL_DEFAULT, min_bars=MIN_BARS):
    """One poll: `bars` = closed 15m history (dicts t,o,h,l,c), newest last. Settles open paper trades, evaluates ONLY the newest
    bar, appends rows. Returns the rows appended. Fails closed (returns [], writes nothing) on bad/short data. Never raises."""
    try:
        if not bars or len(bars) < min_bars or not clean(bars):
            _err("bad or short history: no evaluation")
            return []
        b, w1, w2, R, tr = _series(bars)
        i = len(b) - 1
        rows = _read(journal_path)
        base = {"params_id": PARAMS_ID, "source": SOURCE, "side": "long"}
        sig = {r["t_trigger"] for r in rows if r.get("kind") == "signal"}
        done = {r["t_trigger"] for r in rows if r.get("kind") in ("outcome", "no_fill", "unresolved")}
        outs = {r["t_trigger"]: r for r in rows if r.get("kind") == "outcome"}
        idx = {x[0]: k for k, x in enumerate(b)}
        new, busy_until = [], None

        def busy(t):
            nonlocal busy_until
            busy_until = t if busy_until is None or t > busy_until else busy_until

        for t in sorted(sig):
            if t in done:
                if t in outs:
                    busy(outs[t]["t_exit_bar"])
                continue
            if t not in idx:
                new.append({"kind": "unresolved", "t": t, "t_trigger": t, **base, "why": "trigger bar left the history window"})
                continue
            res = settle(b, w1, w2, tr, idx[t])
            if res is None:
                busy(b[-1][0] + STEP * V.CAP)     # still open or pending
            elif res["status"] == "bad_risk":
                new.append({"kind": "unresolved", "t": t, "t_trigger": t, **base, "why": "entry not above divergence pivot low"})
            else:
                new.append({"kind": "outcome", "t": res["t_fill"], "t_trigger": t, **base, **res})
                busy(res["t_exit_bar"])
        allrows = rows + new
        k = kill_status(allrows)
        if k["verdict"] == "KILL":
            if not any(r.get("kind") == "kill" for r in allrows):
                new.append({"kind": "kill", "t": b[i][0], "params_id": PARAMS_ID, "source": SOURCE, **k})
            _append(journal_path, new)
            return new
        if b[i][0] not in sig and fires(b, w1, w2, R, tr, i) and (busy_until is None or b[i][0] > busy_until):
            new.append({"kind": "signal", "t": b[i][0], "t_trigger": b[i][0], **base, "entry_ref": b[i][4],
                        "pivot_low": pivot_low(b, i), "wt1": w1[i], "flag": "BELOW-SIZE-RULE"})
        _append(journal_path, new)
        return new
    except Exception as exc:  # noqa: BLE001 - fail closed
        _err(f"step: {exc!r}"[:200])
        return []


def fetch_closed(n=FETCH_BARS, now_ms=None, timeout=20):
    """Closed 15m BTCUSDT klines, oldest first, from the public endpoint. Raises on any problem (caller fails closed)."""
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    out, end = [], now_ms
    while len(out) < n:
        with urllib.request.urlopen(f"{URL}?symbol=BTCUSDT&interval=15m&limit=1000&endTime={end}", timeout=timeout) as r:
            page = json.loads(r.read())
        if not isinstance(page, list) or not page:
            raise ValueError("empty or bad klines page")
        out = [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]), "ct": int(x[6])}
               for x in page] + out
        end = page[0][0] - 1
    seen, uniq = set(), []
    for x in out:
        if x["ct"] < now_ms and x["t"] not in seen:
            seen.add(x["t"])
            uniq.append({k: x[k] for k in ("t", "o", "h", "l", "c")})
    return sorted(uniq, key=lambda x: x["t"])[-n:]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", required=True)
    ap.add_argument("--journal", default=JOURNAL_DEFAULT)
    ap.add_argument("--history-warmup", type=int, default=FETCH_BARS, help="bars to fetch; must be >= %d" % MIN_BARS)
    a = ap.parse_args(argv)
    if a.history_warmup < MIN_BARS:
        _err("history-warmup below minimum %d" % MIN_BARS)
        return 2
    try:
        bars = fetch_closed(a.history_warmup)
    except Exception as exc:  # noqa: BLE001
        _err(f"fetch: {exc!r}"[:200])
        return 2
    if len(bars) < MIN_BARS or not clean(bars):
        _err("fetched history failed the checks")
        return 2
    new = step(bars, a.journal)
    print(json.dumps({"key": "c30_paper_log", "bar": bars[-1]["t"], "appended": [r["kind"] for r in new]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
