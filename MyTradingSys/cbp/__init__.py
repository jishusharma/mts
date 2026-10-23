"""CBP analyst-bias store: the one read path for layers.

    import cbp
    rows = cbp.query(analyst="Krown", symbol="BTC", since_days=5)

One JSON file (schema.json is owned by MTS, rows carry the fields listed in ROW_FIELDS), no queue, no acks.
Written only by scripts/dev/cbp_run.py. Data lives outside the public repo (CBP_STORE, default
F:/CryptoScrapper/cbp_store/rows.json); transcripts and runtime data never enter this repo.
Rows are analyst claims, not signals: anything that trades still passes the backtest gate (B139).
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_STORE = Path("F:/CryptoScrapper/cbp_store/rows.json")
WINDOW_DAYS = 5
ROW_FIELDS = ("analyst", "video_id", "published", "bias", "quotes", "trades", "pointers",
              "symbols", "quote_verified", "expires_at")
BIASES = ("BULLISH", "BEARISH", "NEUTRAL", "NO_VIEW")
TRADE_FIELDS = ("asset", "direction", "entry", "target", "invalidation", "quote")


def store_path(path=None):
    return Path(path or os.environ.get("CBP_STORE") or DEFAULT_STORE)


def load(path=None):
    """The whole store: {"schema": 1, "rows": [...], "rejected": [...]}. Missing file = empty store."""
    p = store_path(path)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    return {"schema": 1, "rows": d.get("rows", []), "rejected": d.get("rejected", [])}


def save(data, path=None):
    p = store_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, p)


def validate_row(r):
    """Contract violations of one row (empty list = valid)."""
    if not isinstance(r, dict):
        return ["row is not an object"]
    errs = ["missing " + k for k in ROW_FIELDS if k not in r]
    if r.get("bias") not in BIASES:
        errs.append("bias must be one of %s" % (BIASES,))
    for k in ("quotes", "trades", "pointers", "symbols"):
        if k in r and not isinstance(r[k], list):
            errs.append(k + " must be a list")
    for t in r.get("trades") or []:
        if not isinstance(t, dict) or any(k not in t for k in TRADE_FIELDS):
            errs.append("trade needs %s" % (TRADE_FIELDS,))
    return errs


def is_tradable(r):
    """A trade with entry, target and invalidation all stated (the analyst's words, nothing filled in)."""
    return any(all(str(t.get(k) or "").strip() not in ("", "—") for k in ("entry", "target", "invalidation"))
               for t in r.get("trades") or [])


def query(analyst=None, symbol=None, since_days=WINDOW_DAYS, now=None, store=None):
    """Rows published within the last since_days, newest first; optional analyst / symbol filter."""
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=since_days)).date().isoformat()
    sym = symbol.upper() if symbol else None
    out = []
    for r in load(store)["rows"]:
        if (r.get("published") or "") < cutoff:
            continue
        if analyst and r.get("analyst", "").lower() != analyst.lower():
            continue
        if sym and sym not in [s.upper() for s in r.get("symbols") or []]:
            continue
        out.append(r)
    return sorted(out, key=lambda r: r["published"], reverse=True)
