"""Live validation (replaces G3 blind marking): per-category verdict store, doubts list, signal-to-chart hook.

A live Malkan RSI-divergence signal is sent to the operator with a chart. The operator confirms or corrects ONCE per
unique category (symbol, tf, type regular|hidden, side bull|bear). A look-alike (same category + same flag geometry)
inherits the verdict ('matches validated case #n'). Anything else is a DOUBT: appended to the doubts list, NEVER an
auto-verdict. Seed cases carry verdict None (unreviewed) and therefore never match.

No order path, no balance, no network: sending and charting are injected callables. Fail closed: a malformed signal, a
corrupt store file, a chart or send error all end as DOUBT / PENDING, never as a verdict.
"""
import json
import os

# code -> (type, side). PRD/NRD = price HL + RSI LL (hidden bull) / price LH + RSI HH (hidden bear); K-* = generic hidden.
CODE_MAP = {"R-BULL": ("regular", "bull"), "R-BEAR": ("regular", "bear"),
            "PRD": ("hidden", "bull"), "K-HBULL": ("hidden", "bull"),
            "NRD": ("hidden", "bear"), "K-HBEAR": ("hidden", "bear")}
TFS = ("1d", "1w")
WINDOW = (3, 10)   # bars A..B, OURS (Malkan window, see malkan_div_flags_2026-10-28 md)


class StoreError(Exception):
    pass


def _num(x):
    v = float(x)
    if v != v:
        raise ValueError("nan")
    return v


def validate(sig):
    """Return a normalised signal or raise ValueError (non-signal events, e.g. balance moves, are rejected)."""
    if not isinstance(sig, dict):
        raise ValueError("not a dict")
    code = sig.get("code")
    if code not in CODE_MAP or sig.get("tf") not in TFS or not sig.get("symbol"):
        raise ValueError("not a divergence signal")
    out = {"symbol": str(sig["symbol"]), "tf": sig["tf"], "code": code,
           "date_A": str(sig["date_A"]), "date_B": str(sig["date_B"])}
    for k in ("price_A", "price_B", "rsi_A", "rsi_B", "bars_A_to_B"):
        out[k] = _num(sig[k])
    return out


def category_key(sig):
    s = validate(sig)
    typ, side = CODE_MAP[s["code"]]
    return "%s|%s|%s|%s" % (s["symbol"], s["tf"], typ, side)


def signal_id(sig):
    s = validate(sig)
    return "%s|%s|%s|%s|%s" % (s["symbol"], s["tf"], s["code"], s["date_A"], s["date_B"])


def geometry(sig):
    """Flag geometry rule: price direction A->B, RSI direction A->B, RSI zone at both points, bars inside the window."""
    s = validate(sig)
    pd = 1 if s["price_B"] > s["price_A"] else -1 if s["price_B"] < s["price_A"] else 0
    rd = 1 if s["rsi_B"] > s["rsi_A"] else -1 if s["rsi_B"] < s["rsi_A"] else 0
    lo, hi = min(s["rsi_A"], s["rsi_B"]), max(s["rsi_A"], s["rsi_B"])
    zone = "hi" if lo >= 60 else "lo" if hi <= 40 else "mid"
    return {"price_dir": pd, "rsi_dir": rd, "rsi_zone": zone,
            "in_window": WINDOW[0] <= s["bars_A_to_B"] <= WINDOW[1]}


def _read(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise StoreError("unreadable %s: %s" % (path, e))


def _write(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


class Store:
    """Files in `root`: validation_store.json {cases:[...]}, doubts.json {doubts:[...]}, hook_state.json."""

    def __init__(self, root):
        self.root = str(root)
        self.p_store = os.path.join(self.root, "validation_store.json")
        self.p_doubts = os.path.join(self.root, "doubts.json")
        self.p_state = os.path.join(self.root, "hook_state.json")

    # ---- reads (raise StoreError on a corrupt file: callers fail closed)
    def cases(self):
        return _read(self.p_store, {"cases": []})["cases"]

    def doubts(self):
        return _read(self.p_doubts, {"doubts": []})["doubts"]

    def state(self):
        return _read(self.p_state, {"pending": {}, "sent": []})

    # ---- writes
    def add_case(self, sig, verdict, verbatim, date, chart_path, source):
        """New case; verdict None = unreviewed seed. Case numbers are never reused."""
        cases = self.cases()
        n = max([c["case"] for c in cases] + [0]) + 1
        cases.append({"case": n, "category": category_key(sig), "signal": validate(sig),
                      "geometry": geometry(sig), "verdict": verdict, "operator_verbatim": verbatim,
                      "date": date, "chart_path": chart_path, "source": source})
        _write(self.p_store, {"cases": cases})
        return n

    def add_doubt(self, sig, reason):
        sid = signal_id(sig)
        d = self.doubts()
        if not any(x["id"] == sid for x in d):   # idempotent: a restart or replay never duplicates
            d.append({"id": sid, "category": category_key(sig), "signal": validate(sig),
                      "geometry": geometry(sig), "reason": reason, "status": "open"})
            _write(self.p_doubts, {"doubts": d})

    def correct(self, sig, verdict, verbatim, date, chart_path=None):
        """Operator confirm/correct: writes the verdict as a new case and moves the doubt (status closed)."""
        n = self.add_case(sig, verdict, verbatim, date, chart_path, "operator")
        sid = signal_id(sig)
        d = self.doubts()
        for x in d:
            if x["id"] == sid:
                x["status"] = "closed"
                x["resolved_by_case"] = n
        _write(self.p_doubts, {"doubts": d})
        return n


def match(store, sig):
    """-> 'matches validated case #n' or 'DOUBT' (doubt appended). Never an auto-verdict; fails closed."""
    try:
        key, geo = category_key(sig), geometry(sig)
        for c in store.cases():
            if c["category"] == key and c["verdict"] is not None and c["geometry"] == geo and geo["in_window"]:
                return "matches validated case #%d" % c["case"]
        store.add_doubt(sig, "no validated look-alike in %s" % key)
    except (ValueError, KeyError, TypeError, StoreError):
        return "DOUBT"
    return "DOUBT"


def process_signal(store, sig, render_chart, send):
    """Hook called by the signal path. Returns 'SENT', 'DUPLICATE', 'PENDING' or 'REJECTED'.

    render_chart(sig) -> chart path; send(text, chart_path) -> None (raises on API error). Any error leaves the signal
    in hook_state pending (retry_pending resends); nothing is marked sent unless send returned."""
    try:
        sid = signal_id(sig)
        st = store.state()
    except (ValueError, KeyError, TypeError):
        return "REJECTED"
    except StoreError:
        return "PENDING"
    if sid in st["sent"]:
        return "DUPLICATE"
    s = validate(sig)
    verdict = match(store, s)
    text = "%s %s %s %s..%s: %s" % (s["symbol"], s["tf"], s["code"], s["date_A"], s["date_B"], verdict)
    if verdict == "DOUBT":
        text += " -- confirm or correct once for category %s" % category_key(s)
    try:
        chart = render_chart(s)
        send(text, chart)
    except Exception:
        st["pending"][sid] = s
        try:
            _write(store.p_state, st)
        except OSError:
            pass
        return "PENDING"
    st["pending"].pop(sid, None)
    st["sent"].append(sid)
    _write(store.p_state, st)
    return "SENT"


def retry_pending(store, render_chart, send):
    out = {}
    for sid, s in list(store.state()["pending"].items()):
        out[sid] = process_signal(store, s, render_chart, send)
    return out


def seed_from_history(store, csv_path, chart_dir, date):
    """One example per type (symbol/tf/regular|hidden/bull|bear) present in the history flags; verdict None."""
    import csv
    seen = {c["category"] for c in store.cases()}
    made = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sig = dict(row, symbol=os.path.basename(csv_path).split("_")[0])
            try:
                key = category_key(sig)
            except ValueError:
                continue
            if key in seen:
                continue
            seen.add(key)
            chart = "%s/charts/%s_%s.png" % (chart_dir, sig["symbol"], sig["tf"])
            made.append(store.add_case(sig, None, None, date, chart, "history_flags n=%s" % row.get("n")))
    return made
