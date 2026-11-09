"""LEVEL TOUCH and SESSION BRIEF for the live alert loop (card level-touch-alerts-session-brief-1109, operator 2026-11-09).

11-08 21:55Z BTC spot wicked to 73,510 through the 73.5k/73.3k analyst buy zone; nothing told the operator. Now the live loop
tells him:
  LEVEL TOUCH   once per level per UTC day when a perp 1m wick comes within TOUCH_TOL (0.05 %, scripts/dev/analyst_levels.py, one
                constant) of an open analyst level, prior-day high/low, prior-day VAH/VAL or the week open.
  SESSION BRIEF at 07:00Z (Europe) and 13:30Z (US open), once per UTC day each: price vs the nearest 2 zones above and below
                (zones within ZONE_MERGE of each other are one), levels touched since the last brief, the next event, the day's
                playbook scenario ids.
Both go to the alert log (alerts/level_touch.jsonl) and to the Live Aid toast feed (one row per toast, toasts.jsonl; toast.js
shows the newest). State file: a restart never re-fires a touch or a brief. Fail closed: a fetch or level error writes ONE
degraded line (until the next good poll) and fires nothing. Alerts only: no order, no size, no gate, no new scheduler.
OURS: ZONE_MERGE, BRIEF_WINDOW_MIN, FRESH_BARS, the slot times (operator: 07:00Z and 13:30Z).
"""
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl

SYMBOL = "BTCUSDT"
TOUCH_TOL = 0.0005   # mirrors scripts/dev/analyst_levels.TOUCH_TOL (a test pins them equal)
ZONE_MERGE = 0.001   # levels within 0.1 % of each other are one zone in the brief
BRIEF_SLOTS = {"EU": (7, 0), "US": (13, 30)}   # UTC hour, minute
BRIEF_WINDOW_MIN = 60   # a brief is sent only within an hour of its slot: a late restart never sends a stale one
FRESH_BARS = 15         # first run (no state): look back this many 1m bars, never older backlog
KEEP_DAYS = 3
TOAST_KEEP = 10
LOG_NAME = "level_touch.jsonl"
UTC = timezone.utc


def empty_state():
    return {"fired": {}, "last_bar_t": None, "since_brief": [], "brief_done": [], "degraded": False}


def load_state(path):
    try:
        st = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        return {**empty_state(), **st}
    except (OSError, ValueError):
        return empty_state()


def save_state(st, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(st, sort_keys=True, indent=1), encoding="utf-8", newline="\n")


def _utc(ms):
    return datetime.fromtimestamp(ms / 1000, UTC)


def _stamp(ms):
    return _utc(ms).strftime("%Y-%m-%dT%H:%MZ")


def _touched(level, lo, hi, tol=TOUCH_TOL):
    return lo <= level * (1 + tol) and hi >= level * (1 - tol)


def touch_events(levels, bars, state, now_ms):
    """(alerts, new_state). bars: closed 1m dicts t/h/l. Pure apart from the state it returns."""
    st = {**empty_state(), **state}
    st["fired"] = dict(st["fired"])
    st["since_brief"] = list(st["since_brief"])
    last = st["last_bar_t"]
    out = []
    for b in sorted(bars, key=lambda x: x["t"]):
        if b["t"] <= last if last is not None else b["t"] < now_ms - FRESH_BARS * 60_000:
            continue
        day = _utc(b["t"]).strftime("%Y-%m-%d")
        for lv in levels:
            fk = f'{day}|{lv["key"]}'
            if fk in st["fired"] or not _touched(lv["level"], b["l"], b["h"]):
                continue
            price = b["l"] if abs(b["l"] - lv["level"]) <= abs(b["h"] - lv["level"]) else b["h"]
            side = lv.get("side") or ("support test" if price == b["l"] else "resistance test")
            text = (f'LEVEL TOUCH {SYMBOL} {lv["level"]:,.0f} ({lv["who"]}, {side}) wick {price:,.0f} {_stamp(b["t"])}')
            st["fired"][fk] = b["t"]
            st["since_brief"].append(dict(level=lv["level"], who=lv["who"], price=price, utc=_stamp(b["t"])))
            out.append({"layer": "level_touch", "sub": "touch", "tf": "1m", "event": "LEVEL TOUCH", "symbol": SYMBOL,
                        "level": lv["level"], "who": lv["who"], "side": side, "kind": lv.get("kind", ""), "price": price,
                        "t_close": b["t"], "utc": _stamp(b["t"]), "text": text})
    if bars:
        st["last_bar_t"] = max(b["t"] for b in bars) if last is None else max(last, max(b["t"] for b in bars))
    cut = _utc(now_ms).strftime("%Y-%m-%d")
    keep = {_utc(now_ms - d * 86_400_000).strftime("%Y-%m-%d") for d in range(KEEP_DAYS)} | {cut}
    st["fired"] = {k: v for k, v in st["fired"].items() if k.split("|", 1)[0] in keep}
    st["brief_done"] = [k for k in st["brief_done"] if k.split("|", 1)[0] in keep]
    return out, st


def due_brief(now_ms, state):
    """"EU" / "US" when a brief slot started within BRIEF_WINDOW_MIN and is not done today, else None."""
    now = _utc(now_ms)
    day = now.strftime("%Y-%m-%d")
    for name, (h, m) in BRIEF_SLOTS.items():
        mins = (now.hour * 60 + now.minute) - (h * 60 + m)
        if 0 <= mins < BRIEF_WINDOW_MIN and f"{day}|{name}" not in state.get("brief_done", []):
            return name
    return None


def _zones(levels):
    zs = []
    for lv in sorted(levels, key=lambda x: x["level"]):
        if zs and lv["level"] <= zs[-1]["level"] * (1 + ZONE_MERGE):
            if lv["who"] not in zs[-1]["who"]:
                zs[-1]["who"].append(lv["who"])
            continue
        zs.append({"level": lv["level"], "who": [lv["who"]]})
    return zs


def _fmt_zone(z):
    return f'{z["level"]:,.0f} {"+".join(z["who"])}'


def brief_text(slot, price, levels, since, next_event, scenario_ids, now_ms, sister=None):
    zs = _zones(levels)
    above = [z for z in zs if z["level"] > price][:2]
    below = [z for z in reversed([z for z in zs if z["level"] <= price])][:2]
    touched = "; ".join(f'{x["level"]:,.0f} {x["who"]} (wick {x["price"]:,.0f} {x["utc"]})' for x in since) or "none"
    return (f'SESSION BRIEF {slot} {_stamp(now_ms)} {SYMBOL} {price:,.0f} | above: {", ".join(map(_fmt_zone, above)) or "none"}'
            f' | below: {", ".join(map(_fmt_zone, below)) or "none"} | touched since last brief: {touched}'
            f' | next: {next_event or "n/a"} | playbook: {", ".join(scenario_ids) if scenario_ids else "n/a"}'
            + (f" | {sister}" if sister else ""))   # sister-signals-wired-1109: Monday EU brief only


def _write(alerts, alerts_dir, toast_path):
    append_alerts_jsonl(alerts, pathlib.Path(alerts_dir) / LOG_NAME)
    if alerts and toast_path:
        pathlib.Path(toast_path).parent.mkdir(parents=True, exist_ok=True)
        with open(toast_path, "a", encoding="utf-8", newline="\n") as f:
            for a in alerts:
                f.write(json.dumps({"t": a["t_close"], "event": a["event"], "text": a["text"]}, sort_keys=True) + "\n")
        rows = [json.loads(x) for x in pathlib.Path(toast_path).read_text(encoding="utf-8").splitlines()[-TOAST_KEEP:] if x.strip()]
        # the Live Aid page is a static file: it reads the newest toasts from this script tag (toast.js), no fetch
        pathlib.Path(toast_path).with_suffix(".js").write_text("window.LIVE_TOASTS = " + json.dumps(rows) + ";\n", encoding="utf-8", newline="\n")


def poll(fetch, levels, state_path, alerts_dir, toast_path, now_ms, brief_ctx=None):
    """One loop pass. fetch() -> closed 1m bars; levels(now_ms) -> level dicts; brief_ctx(now_ms) -> dict(price, next_event,
    scenario_ids) (best effort). Returns the alerts emitted. Never raises."""
    st = load_state(state_path)
    try:
        bars = fetch()
        lv = levels(now_ms)
    except Exception as exc:  # noqa: BLE001 - fail closed: nothing fires, ONE degraded line until the next good poll
        if not st["degraded"]:
            st["degraded"] = True
            row = {"layer": "level_touch", "sub": "touch", "tf": "1m", "event": "LEVEL TOUCH DEGRADED", "t_close": now_ms,
                   "text": f"LEVEL TOUCH DEGRADED: {type(exc).__name__}: {exc}"}
            _write([row], alerts_dir, None)  # log only: a degraded feed is not toast material
            save_state(st, state_path)
        return []
    st["degraded"] = False
    alerts, st = touch_events(lv, bars, st, now_ms)
    slot = due_brief(now_ms, st)
    if slot:
        try:
            ctx = (brief_ctx(now_ms) if brief_ctx else {}) or {}
        except Exception as exc:  # noqa: BLE001 - the brief still goes out with what it has
            print(f"[level_touch] brief context: {exc}", file=sys.stderr)
            ctx = {}
        price = ctx.get("price") or (bars[-1]["c"] if bars else None)
        if price:
            text = brief_text(slot, price, lv, st["since_brief"], ctx.get("next_event"), ctx.get("scenario_ids"), now_ms,
                              sister=ctx.get("sister"))
            alerts.append({"layer": "level_touch", "sub": "brief", "tf": "1m", "event": "SESSION BRIEF", "symbol": SYMBOL,
                           "slot": slot, "t_close": now_ms, "text": text})
            st["brief_done"].append(f'{_utc(now_ms).strftime("%Y-%m-%d")}|{slot}')
            st["since_brief"] = []
    _write(alerts, alerts_dir, toast_path)
    save_state(st, state_path)
    return alerts


# ---------- production providers (network; injected in tests) ----------

def _klines(interval, limit):
    from MyTradingSys.runtime.binance_doh import urlopen
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={SYMBOL}&interval={interval}&limit={limit}"
    with urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def default_fetch():
    """Closed perp 1m bars (the open one is dropped)."""
    now = int(time.time() * 1000)
    return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
            for k in _klines("1m", 20) if int(k[0]) + 60_000 <= now]


_cache = {"t": 0, "levels": []}
LEVELS_TTL_S = 600


def _load_script(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _root():
    return next(q for q in pathlib.Path(__file__).resolve().parents if (q / "MyTradingSys").is_dir())


def default_levels(now_ms):
    """Open unexpired analyst levels + PDH/PDL/VAH/VAL/WEEK_OPEN. Cached 10 min. Raises when the analyst ladder cannot be priced
    (fail closed). System levels are best effort: missing ones are simply not watched."""
    if time.time() - _cache["t"] < LEVELS_TTL_S and _cache["levels"]:
        return _cache["levels"]
    root = _root()
    al = _load_script("analyst_levels", root / "scripts" / "dev" / "analyst_levels.py")
    now = _utc(now_ms)
    out = []
    lad = [x for x in al.ladder(al.recent_rows(10, now)) if not x["expires_at"] or al.cbp.parse_expiry(x["expires_at"]) > now]
    if lad:
        since = min(datetime.fromisoformat(x["published"]) for x in lad).replace(tzinfo=UTC)
        bars, _src = al.bars_with_source(since)
        al.mark(lad, bars, now)
        for x in lad:
            if not x["hit"]:
                out.append(dict(key=f'an:{x["analyst"]}:{x["level"]:.0f}', level=x["level"], who=x["analyst"],
                                side=(x.get("bias") or "").lower(), kind="analyst"))
    try:
        dp = _load_script("daily_playbook", root / "MyTradingSys" / "tools" / "live_aid" / "daily_playbook.py")
        hb = [(int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])) for k in _klines("1h", 400)]
        kl = dp.key_levels([b for b in hb if b[0] + 3_600_000 <= now_ms], now.date(), now)
        for k in ("PDH", "PDL", "VAH", "VAL", "WEEK_OPEN"):
            if kl.get(k):
                out.append(dict(key=k, level=float(kl[k]), who=k, side="", kind="system"))
    except Exception as exc:  # noqa: BLE001
        print(f"[level_touch] system levels skipped: {exc}", file=sys.stderr)
    _cache.update(t=time.time(), levels=out)
    return out


def default_brief_ctx(now_ms):
    root = _root()
    ctx = {}
    try:
        txt = (root / "MyTradingSys" / "tools" / "live_aid" / "events_strip_data.js").read_text(encoding="utf-8")
        sched = json.loads(txt.split("= ", 1)[1].rstrip().rstrip(";")).get("schedule", [])
        nxt = next((e for e in sorted(sched, key=lambda e: e["t0"]) if e["t0"] >= now_ms and not e.get("stale")), None)
        if nxt:
            ctx["next_event"] = f'{nxt["cls"]} {_stamp(nxt["t0"])}'
    except Exception:  # noqa: BLE001
        pass
    try:
        txt = (root / "MyTradingSys" / "tools" / "live_aid" / "playbook_data.js").read_text(encoding="utf-8")
        data = json.loads(txt.split("= ", 1)[1].rstrip().rstrip(";"))
        ctx["scenario_ids"] = [s["id"] for c in data.get("sessions", []) for s in c.get("scenarios", [])]
    except Exception:  # noqa: BLE001
        pass
    return ctx
