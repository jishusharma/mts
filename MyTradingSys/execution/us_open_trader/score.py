"""score.py - replay a plan over public 1m klines and write the scored jsonl (DESIGN section 3).

Public market data only (no keys, no account). CLI: python score.py <plan.json>
jsonl keys are a stable contract for the Live Aid learner: trade rows carry the engine trade keys plus
"type":"trade","mode":"replay","day"; the last row is "type":"summary".
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402

HOSTS = ("data-api.binance.vision", "api.binance.com")  # SOURCED (DESIGN section 3): host order
BAR_MS = 60000  # 1m klines, OURS
REPO = Path(__file__).resolve().parents[3]


def default_out_dir():
    # DESIGN header: runtime output under <repo>/runtime_data/us_open_trader/, env override US_OPEN_TRADER_DIR
    return Path(os.environ.get("US_OPEN_TRADER_DIR") or REPO / "runtime_data" / "us_open_trader")


def http_fetch(url):
    """Default fetch: GET url, parsed JSON. Public endpoints only."""
    req = urllib.request.Request(url, headers={"User-Agent": "mts-us-open-score"})
    with urllib.request.urlopen(req, timeout=20) as r:  # nosec - public klines
        return json.loads(r.read().decode())


def _symbol(plan):
    return plan["ref_feed"].rsplit("_", 1)[-1]  # "binance_spot_BTCUSDT" -> "BTCUSDT"


def parse_klines(rows):
    """Binance kline rows -> engine bars {"t","o","h","l","c"}. The one parser for score.py AND the runner (V2-4)."""
    return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
            for k in rows]


def fetch_klines(symbol, start_ms, end_ms, fetch=None):
    """Public 1m klines [start_ms, end_ms] as bars, trying HOSTS in order. RuntimeError if every host fails
    or returns nothing. Reusable by the runner (V2-4); the last bar may still be open: use closed_bars()."""
    fetch = fetch or http_fetch
    last_err = None
    for host in HOSTS:
        url = ("https://%s/api/v3/klines?symbol=%s&interval=1m&startTime=%d&endTime=%d&limit=1000"
               % (host, symbol, start_ms, end_ms))
        try:
            bars = parse_klines(fetch(url))
            if not bars:
                raise ValueError("no klines returned")
            return bars
        except Exception as e:  # try the next host
            last_err = e
    raise RuntimeError("all kline hosts failed: %r" % (last_err,))


def closed_bars(bars, now_ms):
    """Only bars whose whole minute is over at now_ms (the runner steps the engine on closed 1m klines only)."""
    return [b for b in bars if b["t"] + BAR_MS <= now_ms]


def fetch_bars(plan, fetch=None):
    """1m bars from arm through the first bar at/after flat (flat+1 bar)."""
    st = engine.new_state(plan)
    return fetch_klines(_symbol(plan), st["arm_ms"], st["flat_ms"] + BAR_MS, fetch)


def summarize(plan, trades):
    return {
        "type": "summary", "mode": "replay", "day": plan["day"], "n_trades": len(trades),
        "wins": sum(1 for t in trades if t["r_net"] > 0),
        "r_gross_sum": sum(t["r_gross"] for t in trades),
        "r_net_sum": sum(t["r_net"] for t in trades),
    }


def render_md(plan, trades, summary):
    lines = ["| id | side | kind | level | entry | exit | reason | r_gross | r_net |", "|---|---|---|---|---|---|---|---|---|"]
    for t in trades:
        lines.append("| %s | %s | %s | %s | %g | %g | %s | %.2f | %.2f |" % (
            t["order_id"], t["side"], t["kind"], t["level"], t["entry"], t["exit"], t["exit_reason"],
            t["r_gross"], t["r_net"]))
    if not trades:
        lines.append("| - | - | - | no trade | - | - | - | - | - |")
    lines.append("")
    lines.append("%s: %d trade(s), %d net win(s), r_gross %.2f, r_net %.2f (replay, public 1m klines)" % (
        plan["day"], summary["n_trades"], summary["wins"], summary["r_gross_sum"], summary["r_net_sum"]))
    return "\n".join(lines)


def score(plan_path, bars=None, out_dir=None, fetch=None):
    """Replay the plan, write <out_dir>/<day>.jsonl, print the markdown table, return a result dict."""
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    if bars is None:
        bars = fetch_bars(plan, fetch)
    res = engine.replay(plan, bars)
    trades = res["trades"]
    summary = summarize(plan, trades)
    out = Path(out_dir) if out_dir else default_out_dir()
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("%s.jsonl" % plan["day"])
    rows = [dict(t, type="trade", mode="replay", day=plan["day"]) for t in trades] + [summary]
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(render_md(plan, trades, summary))
    return {"trades": trades, "summary": summary, "path": str(path), "events": res["events"],
            "complete": res["state"]["done"]}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: score.py <plan.json>", file=sys.stderr)
        return 2
    try:
        r = score(argv[0])
    except RuntimeError as e:  # no kline host reachable: clean message, non-zero exit
        print("score failed: %s" % e, file=sys.stderr)
        return 1
    if not r["complete"]:
        print("(session not finished: flat bar not in the data yet; open position, if any, is not scored)")
    print("wrote %s" % r["path"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
