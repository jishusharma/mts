"""Family plan triggers (sister + aunt) in the live alert loop (card sister-signals-wired-1109, operator 2026-11-09).

The sister plan's triggers (SISTER_NOTE_2026-11-07/09) as code the live loop runs, so a trigger flip reaches the operator the
same hour instead of waiting for his prompt. States, from BTC daily and weekly closes (perp first via binance_doh, spot
fallback), thresholds in sister_signals.json (OURS):
  STOP       weekly close < 60,000 or a daily low < 57,800        (checked first: the plan's "we were wrong" rule)
  CONFIRMED  weekly close > 80,500
  TOP_UP     daily close < 72,000, or price 65,000-67,000
  PHASE2_ON  the last 2 daily closes inside 72,000-75,000
  WAIT       none of these
A flip raises one SISTER toast + alert log line (state file: a restart never re-fires; a fetch error writes ONE degraded line
and fires nothing). On each flip and every Monday 07:00Z it writes two DRAFT WhatsApp notes (sister ladder; aunt in English and
Hindi) to notes_dir, outside the repo; the operator reads and sends them himself. No holdings, no amounts, no orders.
"""
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl

CONFIG_PATH = pathlib.Path(__file__).with_name("sister_signals.json")
LOG_NAME = "sister_signals.jsonl"
UTC = timezone.utc
DAY_MS = 86_400_000
WEEK_MS = 7 * DAY_MS
STATES = ("STOP", "CONFIRMED", "TOP_UP", "PHASE2_ON", "WAIT")
TOAST_KEEP = 10


def load_config(path=CONFIG_PATH):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def compute_state(daily, weekly, price, cfg):
    """daily / weekly: CLOSED bars (dicts t, c, l), oldest first. price: the latest trade price."""
    d = sorted(daily, key=lambda b: b["t"])
    w = sorted(weekly, key=lambda b: b["t"])
    if (w and w[-1]["c"] < cfg["stop_weekly"]) or any(b["l"] < cfg["stop_low"] for b in d):
        return "STOP"
    if w and w[-1]["c"] > cfg["confirm_weekly"]:
        return "CONFIRMED"
    if (d and d[-1]["c"] < cfg["topup_close_below"]) or (cfg["topup_lo"] <= price <= cfg["topup_hi"]):
        return "TOP_UP"
    n = int(cfg["phase2_days"])
    if len(d) >= n and all(cfg["phase2_lo"] <= b["c"] <= cfg["phase2_hi"] for b in d[-n:]):
        return "PHASE2_ON"
    return "WAIT"


# ---------- state ----------

def _empty():
    return {"state": None, "since": None, "last_fetch": 0, "degraded": False, "notes_done": []}


def load_state(path):
    try:
        return {**_empty(), **json.loads(pathlib.Path(path).read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return _empty()


def save_state(st, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(st, sort_keys=True, indent=1), encoding="utf-8", newline="\n")


def _utc(ms):
    return datetime.fromtimestamp(ms / 1000, UTC)


def _stamp(ms):
    return _utc(ms).strftime("%Y-%m-%dT%H:%MZ")


def _in_monday_slot(now_ms, cfg):
    now = _utc(now_ms)
    h, m = cfg.get("notes_slot_utc", [7, 0])
    mins = now.hour * 60 + now.minute - (h * 60 + m)
    return now.weekday() == 0 and 0 <= mins < int(cfg.get("notes_window_min", 60))


# ---------- notes (drafts for the operator; prices filled in, no holdings or amounts) ----------

def _round_price(coin, p):
    if coin == "BTC":
        return round(p / 100) * 100
    if p >= 1000:
        return round(p / 10) * 10
    if p >= 10:
        return round(p, 1)
    if p >= 1:
        return round(p, 2)
    return round(p * 2000) / 2000          # HBAR-like: steps of 0.0005


def _fmt(coin, p):
    v = _round_price(coin, p)
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 10:
        return f"{v:.1f}" if coin != "LINK" else f"{v:.2f}"
    if v >= 1:
        return f"{v:.2f}"
    return f"{v:.4f}"


STATE_LINES = {
    "PHASE2_ON": ("🟢 PHASE 2 ON", "Bitcoin held 2 days inside our Phase 2 zone (72,000-75,000). Place half A now, half B deeper."),
    "TOP_UP": ("🟠 TOP UP", "Bitcoin closed a day under 72,000 or is at 65,000-67,000. Top up Phase 2 at these prices; no Phase 3."),
    "STOP": ("🔴 STOP", "A week closed under 60,000 or a new low under 57,800. STOP buying. Phase 3 cash stays in the bank."),
    "CONFIRMED": ("🎉 CONFIRMED", "A week closed above 80,500: bottom confirmed by our rule. The dips plan ends; slow weekly buying starts."),
    "WAIT": ("⏸ WAIT", "No trigger. Keep your open limit orders; nothing new this week."),
}
AUNT_PART = {"TOP_UP": "🟢 Part 2 now", "STOP": "🔴 Stop buying (Part 3 stays in the bank)", "CONFIRMED": "🎉 Confirmed, buy the rest slowly",
             "PHASE2_ON": "Part 1 only (this week)", "WAIT": "Part 1 only; Parts 2 and 3 wait"}
AUNT_PART_HI = {"TOP_UP": "🟢 हिस्सा 2 अभी", "STOP": "🔴 खरीदना बंद (हिस्सा 3 बैंक में रहे)", "CONFIRMED": "🎉 पक्का, बाकी धीरे-धीरे खरीदें",
                "PHASE2_ON": "सिर्फ हिस्सा 1 (इसी हफ्ते)", "WAIT": "सिर्फ हिस्सा 1; हिस्सा 2 और 3 रुकें"}
FOOTER = "_From Jishu's research setup: public prices and the analysts we follow. Not a licensed advisor. Your money, your call._"


def sister_note(state, prices, cfg, now_ms):
    head, why = STATE_LINES[state]
    rows = []
    for coin in cfg["sister_coins"]:
        if coin not in prices:
            continue
        a, b = cfg["sister_ladder_pct"]["BTC" if coin == "BTC" else "ALT"]
        p = prices[coin]
        rows.append(f"{coin:<5} {_fmt(coin, p * (1 - a / 100)):>8} {_fmt(coin, p * (1 - b / 100)):>8}")
    ladder = "\n".join([f"{'Coin':<5} {'Half A':>8} {'Half B':>8}"] + rows)
    return (f"DRAFT (state {state}, {_stamp(now_ms)}; check before sending)\n\n*Sister note: {head}*\n\n"
            f"📍 Bitcoin ${_fmt('BTC', prices['BTC'])}. {why}\n\n🛒 *Limit orders (never Market)*\n```\n{ladder}\n```\n"
            f"• Prices in $; CoinSwitch shows ₹: use the same % below today's ₹ price. Alts A = 2% below, B = 5% below; "
            f"Bitcoin A = 1%, B = 2%.\n\n{FOOTER}\n")


def aunt_note(state, prices, cfg, now_ms):
    pct = cfg["aunt_limit_pct"]
    split = cfg["aunt_split_pct"]
    lim = {c: _fmt(c, prices[c] * (1 - pct / 100)) for c in split if c in prices}
    rows_en = "\n".join(f"{c:<9} {split[c]:>3}%  limit {lim[c]}" for c in split if c in lim)
    rows_hi = "\n".join(f"{c:<9} {split[c]:>3}%  लिमिट {lim[c]}" for c in split if c in lim)
    return (f"DRAFT (state {state}, {_stamp(now_ms)}; check before sending)\n\n"
            f"*Aunty, your crypto plan · update* 🙏\n\n📲 *Now:* {AUNT_PART[state]}\n\n"
            f"🪙 *Each part:* one Limit order per coin, {pct}% below today's price:\n```\n{rows_en}\n```\n"
            f"Part 2 when Bitcoin is at 65,000-67,000 $; Part 3 near 60,000 $. If it never falls, I will tell you.\n\n{FOOTER}\n\n"
            f"## Hindi\n\n*आंटी, आपका क्रिप्टो प्लान · अपडेट* 🙏\n\n📲 *अभी:* {AUNT_PART_HI[state]}\n\n"
            f"🪙 *हर हिस्सा:* हर कॉइन का एक Limit ऑर्डर, आज की कीमत से {pct}% कम:\n```\n{rows_hi}\n```\n"
            f"हिस्सा 2 जब Bitcoin 65,000-67,000 $ पर आए; हिस्सा 3 जब 60,000 $ के पास आए।\n\n"
            f"_Jishu के रिसर्च सेटअप से। मैं लाइसेंस वाला सलाहकार नहीं हूँ। पैसा आपका, फैसला आपका।_\n")


def write_notes(state, prices, cfg, notes_dir, now_ms, why):
    """Two draft files in notes_dir. Never raises: a missing drive or a bad dir is one stderr line."""
    try:
        d = pathlib.Path(notes_dir)
        d.mkdir(parents=True, exist_ok=True)
        tag = _utc(now_ms).strftime("%Y-%m-%d_%H%M") + f"_{state}_{why}"
        (d / f"sister_{tag}.txt").write_text(sister_note(state, prices, cfg, now_ms), encoding="utf-8", newline="\n")
        (d / f"aunt_{tag}.txt").write_text(aunt_note(state, prices, cfg, now_ms), encoding="utf-8", newline="\n")
        return True
    except Exception as exc:  # noqa: BLE001 - notes are a convenience; the alert still fires
        print(f"[sister_signals] notes not written: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False


# ---------- one loop pass ----------

def _toast(alerts, toast_path):
    if not alerts or not toast_path:
        return
    p = pathlib.Path(toast_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        for a in alerts:
            f.write(json.dumps({"t": a["t_close"], "event": a["event"], "text": a["text"]}, sort_keys=True) + "\n")
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()[-TOAST_KEEP:] if x.strip()]
    p.with_suffix(".js").write_text("window.LIVE_TOASTS = " + json.dumps(rows) + ";\n", encoding="utf-8", newline="\n")


def poll(fetch, state_path, alerts_dir, toast_path, notes_dir, now_ms, cfg=None):
    """fetch() -> dict(daily, weekly, price, prices, source). Fetches at most every fetch_every_min. Returns alerts. Never raises."""
    cfg = cfg or load_config()
    st = load_state(state_path)
    if now_ms - int(st["last_fetch"] or 0) < int(cfg["fetch_every_min"]) * 60_000:
        return []
    st["last_fetch"] = now_ms
    try:
        data = fetch()
        state = compute_state(data["daily"], data["weekly"], float(data["price"]), cfg)
    except Exception as exc:  # noqa: BLE001 - fail closed: no flip, ONE degraded line until the next good fetch
        if not st["degraded"]:
            st["degraded"] = True
            append_alerts_jsonl([{"layer": "sister", "sub": "plan", "tf": "1d", "event": "SISTER DEGRADED", "t_close": now_ms,
                                  "text": f"SISTER DEGRADED: {type(exc).__name__}: {exc}"}], pathlib.Path(alerts_dir) / LOG_NAME)
        save_state(st, state_path)
        return []
    st["degraded"] = False
    prev = st["state"]
    alerts = []
    if prev is not None and state != prev:
        text = (f"SISTER {prev} -> {state} BTC {data['price']:,.0f} ({data.get('source', '?')}) {_stamp(now_ms)}: "
                f"{STATE_LINES[state][1]} Draft notes in {notes_dir}.")
        alerts.append({"layer": "sister", "sub": "plan", "tf": "1d", "event": "SISTER", "from": prev, "to": state,
                       "price": data["price"], "t_close": now_ms, "utc": _stamp(now_ms), "text": text})
        st["since"] = now_ms
        write_notes(state, data.get("prices") or {"BTC": data["price"]}, cfg, notes_dir, now_ms, "flip")
    elif prev is None:
        st["since"] = now_ms
    day = _utc(now_ms).strftime("%Y-%m-%d")
    if prev is not None and _in_monday_slot(now_ms, cfg) and day not in st["notes_done"]:
        if not alerts:   # a flip in this pass already wrote today's notes
            write_notes(state, data.get("prices") or {"BTC": data["price"]}, cfg, notes_dir, now_ms, "monday")
        st["notes_done"] = (st["notes_done"] + [day])[-8:]
    st["state"] = state
    if alerts:
        append_alerts_jsonl(alerts, pathlib.Path(alerts_dir) / LOG_NAME)
        _toast(alerts, toast_path)
    save_state(st, state_path)
    return alerts


def brief_line(state_path, now_ms, cfg=None):
    """"SISTER: <state>" for the Monday 07:00Z SESSION BRIEF, else None. Reads the state file only; never raises."""
    try:
        cfg = cfg or load_config()
        if not _in_monday_slot(now_ms, cfg):
            return None
        st = load_state(state_path)["state"]
        return f"SISTER: {st}" if st else None
    except Exception:  # noqa: BLE001
        return None


# ---------- production provider (network; injected in tests) ----------

PERP = "https://fapi.binance.com/fapi/v1"
SPOT = "https://api.binance.com/api/v3"


def _get(url):
    from MyTradingSys.runtime.binance_doh import urlopen
    with urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def _bars(base, interval, limit, now_ms, span):
    ks = _get(f"{base}/klines?symbol=BTCUSDT&interval={interval}&limit={limit}")
    closed = [{"t": int(k[0]), "c": float(k[4]), "l": float(k[3])} for k in ks if int(k[0]) + span <= now_ms]
    return closed, float(ks[-1][4])


def default_fetch(now_ms=None):
    """BTC closed 1d/1w bars + last price (perp, spot fallback) and spot-or-perp prices for the note coins."""
    now_ms = now_ms or int(time.time() * 1000)
    last_exc = None
    for name, base in (("perp", PERP), ("spot", SPOT)):
        try:
            daily, price = _bars(base, "1d", 14, now_ms, DAY_MS)
            weekly, _ = _bars(base, "1w", 6, now_ms, WEEK_MS)
            prices = {"BTC": price}
            for coin in ("ETH", "SOL", "LINK", "HBAR"):
                try:
                    tick = _get(f"{base}/ticker/price?symbol={coin}USDT")
                    prices[coin] = float(tick["price"])
                except Exception:  # noqa: BLE001 - a missing alt only drops its row from the draft
                    pass
            return {"daily": daily, "weekly": weekly, "price": price, "prices": prices, "source": name}
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    raise last_exc
