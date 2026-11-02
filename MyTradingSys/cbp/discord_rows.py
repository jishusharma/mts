"""Discord posts -> CBP rows (claims, not signals). No network, no token, no login: pure parsing.

Inputs (all read from local files, never fetched here):
  * hand-read rows  : research/qriptal_2026-10-10/discord_rows.json  (posted_local = IST)
  * message JSON    : [{"id","timestamp"(ISO with UTC offset),"author":{"name"},"content"}]
  * saved page HTML : Discord DOM of a read-only browser session
                      (li#chat-messages-<chan>-<id>, <time datetime>, #message-content-<id>)
Rows go beside cbp_store via cbp.save, deduped on video_id. Real channel content never enters the public repo:
the store lives under CBP_HOME (outside the repo); tests use hand-made fixtures only.

Live read (operator machine, later step; dry run unless --ingest):
  python MyTradingSys/cbp/discord_rows.py --html <saved_page.html> --channel habib-trading-thoughts --analyst Habib --ingest
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cbp  # noqa: E402

IST = timedelta(hours=5, minutes=30)
DIR_MAP = {"long": ("LONG", "BULLISH"), "short": ("SHORT", "BEARISH")}
NONE = chr(0x2014)  # em dash = not stated (cbp.is_tradable treats it as missing)


def ist_to_utc(s):
    """'YYYY-MM-DD HH:MM' in IST -> aware UTC datetime."""
    return (datetime.strptime(s.strip(), "%Y-%m-%d %H:%M") - IST).replace(tzinfo=timezone.utc)


def _vid(*parts):
    return "d" + hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]  # 11 chars


def _clean(v):
    v = str(v or "").strip()
    return NONE if v.lower().startswith("not stated") or v == "" else v


def _build(analyst, channel, utc, text, direction, entry, target, stop, symbols, uid):
    d, bias = DIR_MAP.get(str(direction or "").lower(), (None, "NO_VIEW"))
    trades = []
    if d:
        trades.append({"asset": (symbols or ["BTC"])[0], "direction": d, "entry": _clean(entry),
                       "target": _clean(target), "invalidation": _clean(stop), "quote": text})
    return {"analyst": analyst, "channel": channel, "video_id": _vid(channel, uid, utc.isoformat()),
            "published": utc.date().isoformat(), "published_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bias": bias, "quotes": [text], "trades": trades, "pointers": [], "symbols": list(symbols or ["BTC"]),
            "quote_verified": False,
            "expires_at": (utc + timedelta(days=cbp.WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")}


def row_from_hand(post, channel, analyst, symbols=("BTC",)):
    """One hand-read post (posted_local IST, kind, dir, q, entry/targets) -> CBP row. Raises ValueError if bad."""
    if not post.get("q") or not post.get("posted_local"):
        raise ValueError("post needs q and posted_local")
    utc = ist_to_utc(post["posted_local"])
    return _build(analyst, channel, utc, post["q"], post.get("dir"), post.get("entry"), post.get("targets"),
                  post.get("stop"), list(symbols), str(post.get("src", "")) + "|" + post["q"])


def row_from_message(msg, channel, analyst=None, symbols=("BTC",)):
    """One chat message (ISO timestamp with UTC offset) -> text-only claim row (NO_VIEW)."""
    text = (msg.get("content") or "").strip()
    ts = str(msg.get("timestamp") or "")
    if not text or not ts:
        raise ValueError("message needs content and timestamp")
    if not ts.endswith("Z") and "+" not in ts[10:] and "-" not in ts[10:]:
        raise ValueError("timestamp must carry a UTC offset")
    utc = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    who = analyst or (msg.get("author") or {}).get("name") or "unknown"
    return _build(who, channel, utc, text, None, None, None, None, list(symbols), str(msg.get("id", "")))


def _collect(items, fn):
    rows, rejected = [], []
    for it in items:
        try:
            r = fn(it)
            errs = cbp.validate_row(r)
            if errs:
                rejected.append({"post": it, "errors": errs})
            else:
                rows.append(r)
        except (ValueError, TypeError, AttributeError) as e:
            rejected.append({"post": it, "errors": [str(e)]})
    return rows, rejected


def load_rows(json_path, channel, analyst, symbols=("BTC",)):
    """Hand-read JSON list -> (valid rows, rejected)."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("expected a JSON list")
    return _collect(data, lambda p: row_from_hand(p, channel, analyst, symbols))


def parse_messages_json(text, channel, analyst=None, symbols=("BTC",)):
    data = json.loads(text)
    if isinstance(data, dict):
        data = data.get("messages", [])
    return _collect(data, lambda m: row_from_message(m, channel, analyst, symbols))


class _DomParser(HTMLParser):
    """Collects {id, timestamp, author, content} from Discord-style li#chat-messages-* items."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.msgs, self.cur, self.field, self.depth = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        i = a.get("id", "") or ""
        cls = a.get("class", "") or ""
        if tag == "li" and i.startswith("chat-messages-"):
            self.cur = {"id": i.rsplit("-", 1)[-1], "timestamp": "", "author": {"name": ""}, "content": ""}
            self.msgs.append(self.cur)
            return
        if self.cur is None:
            return
        if self.field:
            if tag not in ("br", "img"):
                self.depth += 1
            return
        if tag == "time" and a.get("datetime") and not self.cur["timestamp"]:
            self.cur["timestamp"] = a["datetime"]
        elif i.startswith("message-content-"):
            self.field, self.depth = "content", 1
        elif "username" in cls.split():
            self.field, self.depth = "name", 1

    def handle_endtag(self, tag):
        if self.field and tag not in ("br", "img"):
            self.depth -= 1
            if self.depth <= 0:
                self.field = None

    def handle_data(self, data):
        if self.cur is None:
            return
        if self.field == "content":
            self.cur["content"] += data
        elif self.field == "name" and not self.cur["author"]["name"]:
            self.cur["author"]["name"] = data.strip()


def parse_html(html, channel, analyst=None, symbols=("BTC",)):
    p = _DomParser()
    p.feed(html)
    for m in p.msgs:
        m["content"] = " ".join(m["content"].split())
    return _collect(p.msgs, lambda m: row_from_message(m, channel, analyst, symbols))


def ingest(rows, store=None):
    """Merge rows into the CBP store, deduped on video_id (newer wins). Returns count added."""
    data = cbp.load(store)
    have = {r.get("video_id"): i for i, r in enumerate(data["rows"]) if isinstance(r, dict)}
    added = 0
    for r in rows:
        if r["video_id"] in have:
            data["rows"][have[r["video_id"]]] = r
        else:
            data["rows"].append(r)
            have[r["video_id"]] = len(data["rows"]) - 1
            added += 1
    cbp.save(data, store)
    return added


def main(argv=None):
    ap = argparse.ArgumentParser(description="Discord posts -> CBP rows (no network, no token)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--html")
    g.add_argument("--messages-json")
    g.add_argument("--hand-json")
    ap.add_argument("--channel", required=True)
    ap.add_argument("--analyst", default=None)
    ap.add_argument("--store", default=None)
    ap.add_argument("--ingest", action="store_true", help="write to the CBP store (default: dry run)")
    a = ap.parse_args(argv)
    if a.hand_json:
        if not a.analyst:
            ap.error("--hand-json needs --analyst")
        rows, rej = load_rows(a.hand_json, a.channel, a.analyst)
    elif a.html:
        rows, rej = parse_html(Path(a.html).read_text(encoding="utf-8"), a.channel, a.analyst)
    else:
        rows, rej = parse_messages_json(Path(a.messages_json).read_text(encoding="utf-8"), a.channel, a.analyst)
    n = ingest(rows, a.store) if a.ingest else 0
    print("rows=%d rejected=%d added=%d%s" % (len(rows), len(rej), n, "" if a.ingest else " (dry run)"))
    return 0 if rows or not rej else 1


if __name__ == "__main__":
    sys.exit(main())
