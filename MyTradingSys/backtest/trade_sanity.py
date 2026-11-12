import sys
sys.dont_write_bytecode = True
"""Log sanity and per-year / long-short lines for backtest RESULTs (card backtest-log-sanity-and-year-lines-1112).

Source: research/backtest_howto_K31xH_1112/GAP_TABLE.md S5 (long/short split), S6 (log sanity), S8 (per-year row).
Descriptive only: nothing here chooses a parameter or changes a result.

Trade dict: side (+1 long / -1 short), entry_ms / exit_ms (open time of the fill bar, UTC ms), entry_px / exit_px,
ret (return-like, any one unit). A fill is "at the open" (default) or "at the close" of its 1m bar (DECISION OURS:
exact match within tol_pct, because every study here fills on a bar open; a shifted fill lands on a neighbouring bar
whose open differs).
"""
import csv
import datetime as dt
from collections import defaultdict

MS = 60_000


class LogSanityError(Exception):
    """A logged fill does not match the 1m kline it claims."""


def load_klines(paths):
    """{open_ms: (open, high, low, close)} from Binance 1m csv files (ms or us timestamps, header skipped)."""
    k = {}
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                k[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]))
    return k


def _utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def _leg(kl, ms, px, leg, tol_pct):
    """(bar open, bar close, ok) for one fill."""
    bar = kl.get(int(ms))
    if bar is None:
        return None, None, False
    ref = bar[0] if leg == "open" else bar[3]
    return bar[0], bar[3], abs(px - ref) <= abs(ref) * tol_pct / 100.0


def check_trades(trades, klines, n=5, entry_leg="open", exit_leg="open", tol_pct=1e-6):
    """Rows for the last n trades (by entry_ms); each row says whether both fills match their 1m bar."""
    if entry_leg not in ("open", "close") or exit_leg not in ("open", "close"):
        raise ValueError("leg must be 'open' or 'close'")
    rows = []
    for t in sorted(trades, key=lambda x: x["entry_ms"])[-n:]:
        eo, ec, eok = _leg(klines, t["entry_ms"], t["entry_px"], entry_leg, tol_pct)
        xo, xc, xok = _leg(klines, t["exit_ms"], t["exit_px"], exit_leg, tol_pct)
        rows.append(dict(side=t["side"], entry_ms=t["entry_ms"], exit_ms=t["exit_ms"], entry_px=t["entry_px"],
                         exit_px=t["exit_px"], k_entry_open=eo, k_entry_close=ec, k_exit_open=xo, k_exit_close=xc,
                         entry_ok=eok, exit_ok=xok))
    return rows


def sanity_lines(rows):
    out = ["Log sanity (last %d trades vs 1m klines; entry/exit px vs bar open/close):" % len(rows)]

    def f(v):
        return "n/a" if v is None else "%.2f" % v

    for r in rows:
        out.append("  %s %-5s entry %s px %.2f | kline o %s c %s | %s   exit %s px %.2f | kline o %s c %s | %s" % (
            "OK  " if r["entry_ok"] and r["exit_ok"] else "FAIL", "long" if r["side"] > 0 else "short",
            _utc(r["entry_ms"]), r["entry_px"], f(r["k_entry_open"]), f(r["k_entry_close"]),
            "ok" if r["entry_ok"] else "MISMATCH", _utc(r["exit_ms"]), r["exit_px"], f(r["k_exit_open"]),
            f(r["k_exit_close"]), "ok" if r["exit_ok"] else "MISMATCH"))
    return out


def log_sanity(trades, klines, n=5, **kw):
    """Print the sanity block; raise LogSanityError (after printing) if any fill mismatches. Call BEFORE any metric."""
    rows = check_trades(trades, klines, n, **kw)
    text = "\n".join(sanity_lines(rows))
    print(text)
    bad = [r for r in rows if not (r["entry_ok"] and r["exit_ok"])]
    if bad:
        raise LogSanityError("%d of %d logged trades do not match the 1m klines\n%s" % (len(bad), len(rows), text))
    return rows


def _stat(items):
    r = [x["ret"] for x in items]
    return len(r), (sum(r) / len(r) if r else float("nan")), sum(r)


def year_side_lines(trades):
    """RESULT rows: per calendar year (entry year, UTC) and long vs short; n, mean, sum, so one bad year cannot hide."""
    out = ["| cut | n | mean | sum |", "|---|---|---|---|"]
    by = defaultdict(list)
    for t in trades:
        by[dt.datetime.fromtimestamp(t["entry_ms"] / 1000, dt.timezone.utc).year].append(t)
    for y in sorted(by):
        n, m, s = _stat(by[y])
        out.append("| year %d | %d | %.4f | %.4f |" % (y, n, m, s))
    for name, sd in (("long", 1), ("short", -1)):
        n, m, s = _stat([t for t in trades if t["side"] == sd])
        out.append("| %s | %d | %.4f | %.4f |" % (name, n, m, s))
    return out
