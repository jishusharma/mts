"""
Live validation of Malkan RSI divergence signals (operator decision 2026-10-28: replaces G3 blind marking).

When a layer fires a live signal, MTS sends the operator the signal with a chart of the drawn flags. The operator confirms
or corrects ONCE per unique signal category; later look-alikes inherit "matches validated case #n"; anything that differs,
is new, or was corrected goes to a DOUBTS list. Nothing here ever writes a verdict on its own: a verdict is the operator's
text, verbatim, recorded by record_verdict / correct / correct_case.

Category key: (type regular|hidden, side bull|bear, timeframe, symbol). Malkan codes (div_flags_chart.CODE): R-BULL / R-BEAR
= regular, PRD / NRD = Malkan reverse ("hidden") divergence with the RSI 60/40 trend condition. KROWN generic hidden flags
(K-HBULL / K-HBEAR) are not Malkan: always a doubt.
Look-alike ("same flag geometry rule"): same category AND the signal itself satisfies the Malkan rule of its code with the
params in params/malkan_divergence_default.json (regular: bars 3-10 SOURCED, price and RSI move in opposite directions by
more than min_rsi_diff 0 SOURCED; PRD/NRD: bars 5-14 OURS/UNVERIFIED, RSI >= 60 / <= 40 at both points SOURCED).
Statuses from match(): "matches validated case #n" (anchor case confirmed), "PENDING case #n" (anchor case not yet
validated, no verdict), "DOUBT" (appended to doubts).

Store: one JSON file, rewritten atomically after every change; a file that does not parse raises StoreError (fail
closed: never start empty and re-ask or re-verdict). Default location MyTradingSys/runtime/live_validation/ is gitignored
(operator verdicts are runtime data; the repo is public).
Hook: on_signal(signal, store) -> match, chart with the drawn flags, message to the operator. A chart or send failure
keeps the message in the store's outbox for retry_outbox(); no verdict is written either way. The hook is a separate
module: the live runner is not changed here (live tree changes only by manual deploy).
Not trade logic: no order, no balance, no position is read or written.

CLI: python -m MyTradingSys.backtest.layers.rsi.live_validation seed|list|verdict|correct|correct-case|retry [--store P]
"""
import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PARAMS_PATH = Path(__file__).resolve().parent / "params" / "malkan_divergence_default.json"
RUNTIME_DIR = REPO / "MyTradingSys" / "runtime" / "live_validation"
DEFAULT_STORE = RUNTIME_DIR / "store.json"
DEFAULT_CHART_DIR = RUNTIME_DIR / "charts"
DEFAULT_MESSAGE_DIR = RUNTIME_DIR / "messages"
SEED_CSV = REPO / "MyTradingSys" / "research" / "malkan_div_flags_2026-10-28" / "BTCUSDT_divergences.csv"

MALKAN = {"R-BULL": ("regular", "bull"), "R-BEAR": ("regular", "bear"),
          "PRD": ("hidden", "bull"), "NRD": ("hidden", "bear")}
EVENT_CODE = {"rsi_div_bull": "R-BULL", "rsi_div_bear": "R-BEAR", "bullish": "R-BULL", "bearish": "R-BEAR",
              "prd": "PRD", "nrd": "NRD", "hidden_bullish": "K-HBULL", "hidden_bearish": "K-HBEAR"}
TYPES = ("regular", "hidden")
SIDES = ("bull", "bear")
SEED_TFS = ("1d", "1w")


class StoreError(Exception):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _params():
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def category_of(signal):
    """(type, side, tf, symbol) for a Malkan code, else None."""
    ts = MALKAN.get(signal.get("code"))
    if ts is None:
        return None
    return (ts[0], ts[1], str(signal.get("tf")), str(signal.get("symbol")))


def geometry_ok(signal, params=None):
    """The signal satisfies the Malkan rule of its own code (module docstring). Missing or non-numeric fields -> False."""
    p = params or _params()
    code = signal.get("code")
    try:
        bars = int(signal["bars"])
        pa, pb = float(signal["price_a"]), float(signal["price_b"])
        ra, rb = float(signal["rsi_a"]), float(signal["rsi_b"])
    except (KeyError, TypeError, ValueError):
        return False
    d = float(p.get("min_rsi_diff", 0.0))
    if code in ("R-BULL", "R-BEAR"):
        if not p["min_bars"] <= bars <= p["max_bars"]:
            return False
        return (pb < pa and rb - ra > d) if code == "R-BULL" else (pb > pa and ra - rb > d)
    if code in ("PRD", "NRD"):
        rv = p["reverse"]
        if not rv["min_bars"] <= bars <= rv["max_bars"]:
            return False
        if code == "PRD":
            return pb > pa and ra - rb > d and ra >= rv["prd_min_rsi"] and rb >= rv["prd_min_rsi"]
        return pb < pa and rb - ra > d and ra <= rv["nrd_max_rsi"] and rb <= rv["nrd_max_rsi"]
    return False


def signal_from_event(ev, tf, symbol):
    """A live layer event (live_rsi_divergence: event rsi_div_bull/bear) or a div_flags_chart event (kind) -> signal."""
    code = EVENT_CODE.get(ev.get("event")) or EVENT_CODE.get(ev.get("kind")) or ev.get("code")
    t = ev.get("t", ev.get("t_close"))
    return {"id": "%s-%s-%s-%s" % (symbol, tf, t, code), "symbol": symbol, "tf": tf, "code": code, "t": t,
            "bars": ev.get("bars"), "price_a": ev.get("close_a"), "price_b": ev.get("close_b"),
            "rsi_a": ev.get("rsi_a"), "rsi_b": ev.get("rsi_b")}


class Store:
    def __init__(self, path=DEFAULT_STORE):
        self.path = Path(path)
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
                for k in ("cases", "doubts", "outbox", "next_case"):
                    self.data[k]
            except (ValueError, KeyError, TypeError) as e:
                raise StoreError("live validation store %s is unreadable (%s); refusing to start empty" % (self.path, e))
        else:
            self.data = {"version": 1, "cases": [], "doubts": [], "outbox": [], "next_case": 1}

    # ---------- persistence ----------
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".store-", dir=str(self.path.parent))
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(self.data, fh, indent=1, sort_keys=True)
        os.replace(tmp, self.path)

    # ---------- reads ----------
    def cases(self):
        return list(self.data["cases"])

    def doubts(self):
        return list(self.data["doubts"])

    def outbox(self):
        return list(self.data["outbox"])

    def case_for(self, category):
        """The anchor case of a category: its lowest case number."""
        cat = list(category)
        hits = [c for c in self.data["cases"] if c["category"] == cat]
        return min(hits, key=lambda c: c["case"]) if hits else None

    def _case(self, n):
        for c in self.data["cases"]:
            if c["case"] == n:
                return c
        raise KeyError("no case #%s" % n)

    # ---------- writes ----------
    def add_case(self, category, example, source, verdict=None, from_signal=None, chart=None):
        n = self.data["next_case"]
        self.data["next_case"] = n + 1
        case = {"case": n, "category": list(category), "example": example, "source": source, "verdict": verdict,
                "from_signal": from_signal, "chart": chart, "added": _now()}
        self.data["cases"].append(case)
        self.save()
        return case

    def record_verdict(self, case_no, text, by):
        """The operator's verbatim confirmation of a case (once per category)."""
        self._case(case_no)["verdict"] = {"status": "confirmed", "text": text, "by": by, "utc": _now()}
        self.save()

    def correct_case(self, case_no, text, by):
        """The operator says a validated case is wrong: later look-alikes become doubts, not inherited verdicts."""
        self._case(case_no)["verdict"] = {"status": "corrected", "text": text, "by": by, "utc": _now()}
        self.save()

    def add_doubt(self, signal, reason):
        if not any(d["signal"].get("id") == signal.get("id") for d in self.data["doubts"]):
            self.data["doubts"].append({"signal": signal, "reason": reason, "utc": _now(), "verdict": None})
            self.save()

    def correct(self, signal_id, text, by):
        """The operator's verdict on a doubt: the doubt leaves the list and becomes a case with that verdict."""
        for i, d in enumerate(self.data["doubts"]):
            if d["signal"].get("id") == signal_id:
                break
        else:
            raise KeyError("no doubt for signal %s" % signal_id)
        d = self.data["doubts"].pop(i)
        s = d["signal"]
        cat = category_of(s) or ("non-malkan", str(s.get("code")), str(s.get("tf")), str(s.get("symbol")))
        return self.add_case(cat, s, "doubt:" + d["reason"], from_signal=signal_id,
                             verdict={"status": "confirmed", "text": text, "by": by, "utc": _now()})

    def queue(self, msg):
        if not any(m["signal"].get("id") == msg["signal"].get("id") for m in self.data["outbox"]):
            self.data["outbox"].append(msg)
            self.save()

    def unqueue(self, signal_id):
        self.data["outbox"] = [m for m in self.data["outbox"] if m["signal"].get("id") != signal_id]
        self.save()

    # ---------- the rule ----------
    def match(self, signal):
        cat = category_of(signal)
        if cat is None:
            self.add_doubt(signal, "not a Malkan code")
            return "DOUBT"
        if not geometry_ok(signal):
            self.add_doubt(signal, "geometry differs from the Malkan rule")
            return "DOUBT"
        case = self.case_for(cat)
        if case is None:
            self.add_doubt(signal, "new category, no validated case")
            return "DOUBT"
        v = case["verdict"]
        if v is None:
            return "PENDING case #%d" % case["case"]
        if v.get("status") != "confirmed":
            self.add_doubt(signal, "category case #%d was corrected by the operator" % case["case"])
            return "DOUBT"
        return "matches validated case #%d" % case["case"]


def seed_from_csv(store, csv_path=SEED_CSV):
    """One example per Malkan category from the history flags table (first row of each); no verdict. Idempotent."""
    csv_path = Path(csv_path)
    symbol = csv_path.name.split("_")[0]
    added = 0
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            s = {"id": "history-%s-%s-%s" % (symbol, r["tf"], r["n"]), "symbol": symbol, "tf": r["tf"],
                 "code": r["code"], "bars": int(r["bars_A_to_B"]), "price_a": float(r["price_A"]),
                 "price_b": float(r["price_B"]), "rsi_a": float(r["rsi_A"]), "rsi_b": float(r["rsi_B"]),
                 "date_a": r["date_A"], "date_b": r["date_B"], "known_on": r["event_known_on"]}
            cat = category_of(s)
            if cat is None or store.case_for(cat) is not None:
                continue
            try:
                rel = csv_path.resolve().relative_to(REPO).as_posix()
            except ValueError:
                rel = csv_path.name
            store.add_case(cat, s, "history:%s#%s-%s" % (rel, r["tf"], r["n"]),
                           chart="%s/charts/%s_%s.png" % (Path(rel).parent.as_posix(), symbol, r["tf"]))
            added += 1
    want = [[t, sd, tf, symbol] for t in TYPES for sd in SIDES for tf in SEED_TFS]
    have = [c["category"] for c in store.cases()]
    return {"added": added, "missing": sorted(c for c in want if c not in have), "present": sorted(have)}


def default_chart(signal, out_png):
    """Candles + RSI with the Malkan flags drawn (div_flags_chart.render) for the signal's symbol and timeframe."""
    from MyTradingSys.backtest.layers.rsi import div_flags_chart as dfc
    days = dfc.load_daily(dfc.find_data_root(signal["symbol"]), signal["symbol"])
    bars = dfc.weekly_from_daily(days) if signal["tf"] == "1w" else days
    evs, rsi = dfc.detect_all(bars)
    dfc.render(bars, evs, rsi, signal["tf"], signal["symbol"], 250, out_png)
    return str(out_png)


def default_send(msg, out_dir=DEFAULT_MESSAGE_DIR):
    """Operator message sink: one JSON file per signal (the surface that shows the operator reads this folder)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(msg["signal"].get("id")))
    (out_dir / (name + ".json")).write_text(json.dumps(msg, indent=1, sort_keys=True), encoding="utf-8")


def _text(signal, status):
    return ("%s %s %s (bars %s, price %s -> %s, RSI %s -> %s): %s. Confirm or correct once for this category."
            % (signal.get("symbol"), signal.get("tf"), signal.get("code"), signal.get("bars"), signal.get("price_a"),
               signal.get("price_b"), signal.get("rsi_a"), signal.get("rsi_b"), status))


def on_signal(signal, store, chart_fn=default_chart, send_fn=default_send, chart_dir=DEFAULT_CHART_DIR):
    """Live signal -> match -> chart with drawn flags -> operator message. Fails closed: on any chart or send error the
    message stays in the outbox (retry_outbox) and nothing is marked sent or validated."""
    status = store.match(signal)
    msg = {"signal": signal, "status": status, "text": _text(signal, status), "chart": None, "utc": _now(),
           "error": None}
    try:
        name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(signal.get("id")))
        Path(chart_dir).mkdir(parents=True, exist_ok=True)
        msg["chart"] = str(chart_fn(signal, str(Path(chart_dir) / (name + ".png"))))
    except Exception as e:  # noqa: BLE001 - any chart failure keeps the signal pending
        msg["error"] = "chart: %s" % e
        store.queue(msg)
        return {"status": status, "sent": False, "error": msg["error"]}
    try:
        send_fn(msg)
    except Exception as e:  # noqa: BLE001 - any send failure keeps the signal pending
        msg["error"] = "send: %s" % e
        store.queue(msg)
        return {"status": status, "sent": False, "error": msg["error"]}
    return {"status": status, "sent": True, "error": None}


def retry_outbox(store, send_fn=default_send, chart_fn=None, chart_dir=DEFAULT_CHART_DIR):
    """Re-send queued messages (re-drawing a missing chart when chart_fn is given). Returns how many were sent."""
    sent = 0
    for msg in store.outbox():
        msg = dict(msg)
        if not msg.get("chart"):
            if chart_fn is None:
                continue
            try:
                name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(msg["signal"].get("id")))
                msg["chart"] = str(chart_fn(msg["signal"], str(Path(chart_dir) / (name + ".png"))))
            except Exception:  # noqa: BLE001
                continue
        msg["error"] = None
        try:
            send_fn(msg)
        except Exception:  # noqa: BLE001
            continue
        store.unqueue(msg["signal"].get("id"))
        sent += 1
    return sent


def main(argv=None):
    ap = argparse.ArgumentParser(description="Malkan live validation store")
    ap.add_argument("cmd", choices=["seed", "list", "verdict", "correct", "correct-case", "retry"])
    ap.add_argument("arg", nargs="?", help="case number (verdict, correct-case) or signal id (correct)")
    ap.add_argument("--text", help="the operator's words, verbatim")
    ap.add_argument("--by", default="operator")
    ap.add_argument("--store", default=str(DEFAULT_STORE))
    a = ap.parse_args(argv)
    st = Store(a.store)
    if a.cmd == "seed":
        print(json.dumps(seed_from_csv(st), indent=1))
    elif a.cmd == "list":
        for c in st.cases():
            v = c["verdict"]
            print("case #%d %s %s %s" % (c["case"], "/".join(c["category"]), v["status"] if v else "PENDING", c["source"]))
        for d in st.doubts():
            print("DOUBT %s %s" % (d["signal"].get("id"), d["reason"]))
        print("outbox %d" % len(st.outbox()))
    elif a.cmd in ("verdict", "correct", "correct-case"):
        if not a.arg or not a.text:
            ap.error("%s needs the case/signal and --text (the operator's words)" % a.cmd)
        if a.cmd == "verdict":
            st.record_verdict(int(a.arg), a.text, a.by)
        elif a.cmd == "correct-case":
            st.correct_case(int(a.arg), a.text, a.by)
        else:
            st.correct(a.arg, a.text, a.by)
        print("recorded")
    elif a.cmd == "retry":
        print("sent %d" % retry_outbox(st))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    sys.exit(main())
