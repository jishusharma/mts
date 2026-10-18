"""Qriptal call ledger (card qriptal-call-ledger, B162 step 1).

Reviewed rows live in ledger_rows.json (one per statement that could be a call, written by a person reading the
transcript). This module does not decide what he meant; it only
  * proves every quote is verbatim in the staged raw transcript and finds its file:line,
  * attaches the video publish time (PUBLISH_TIMES.tsv) as the call time (RULES.md),
  * applies the RULES.md eligibility test mechanically (BTC, forward-looking, entry + stop + at least one target),
  * writes CALL_LEDGER.csv.

Usage (repo root):
    python MyTradingSys/research/qriptal_2026-10-10/ledger.py build   # rewrite CALL_LEDGER.csv, print counts
    python MyTradingSys/research/qriptal_2026-10-10/ledger.py check   # exit 1 if the CSV differs from a rebuild
"""
import csv
import io
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # qriptal_2026-10-10 -> research -> MyTradingSys -> repo root
RAW_REL = "extracts/_staged_2026-09-27/raw"
RAW_DIR = ROOT / RAW_REL
ROWS_JSON = HERE / "ledger_rows.json"
TIMES_TSV = HERE / "PUBLISH_TIMES.tsv"
CSV_PATH = HERE / "CALL_LEDGER.csv"

NOT_STATED = "NOT STATED"
KINDS = ("PLAN", "RECAP", "HYPO", "VIEW")
MAX_QUOTE_WORDS = 25
# BACKTEST_PROTOCOL s2: DEV ends 2026-06-25, HOLDOUT starts 2026-06-26. RULES.md: a limit entry may wait 24 h and the
# trade may stay open 7 days, so the longest a call can touch the candles is 8 days from the video time.
HOLDOUT_START = datetime(2026, 6, 26, tzinfo=timezone.utc)
MAX_WINDOW = timedelta(days=8)

COLUMNS = ("call_id", "video_id", "published_utc", "time_source", "file_line", "video_ts", "quote", "asset", "direction",
           "entry", "stop", "targets", "aux_refs", "kind", "eligible", "reason", "window_split", "note")

_STAMP = re.compile(r"^\[(\d+:\d{2}(?::\d{2})?)\]\s?(.*)$")


class QuoteError(ValueError):
    pass


def norm(s):
    """Case, punctuation and whitespace are ignored (auto captions carry no reliable punctuation)."""
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", s.lower()).split())


def parse_transcript(text):
    """-> [(line_number, 'm:ss', text)] for every caption line; line numbers are the physical file lines."""
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        m = _STAMP.match(line.rstrip("\r"))
        if m:
            out.append((i, m.group(1), m.group(2)))
    return out


def load_transcript(vid, raw_dir=None):
    p = (raw_dir or RAW_DIR) / f"qriptal_{vid}_raw.txt"
    return parse_transcript(p.read_text(encoding="utf-8", errors="replace"))


def check_quote_length(quote):
    n = len(quote.split())
    if n > MAX_QUOTE_WORDS:
        raise QuoteError(f"quote has {n} words, limit {MAX_QUOTE_WORDS}: {quote[:60]}")


def locate(lines, quote):
    """-> (first_line, last_line, 'm:ss' of first line). The quote must occur exactly once."""
    toks = []  # (token, index into lines)
    for idx, (_, _, text) in enumerate(lines):
        for t in norm(text).split():
            toks.append((t, idx))
    q = norm(quote).split()
    if not q:
        raise QuoteError("empty quote")
    words = [t for t, _ in toks]
    hits = [i for i in range(len(words) - len(q) + 1) if words[i:i + len(q)] == q]
    if not hits:
        raise QuoteError(f"quote not found in transcript: {quote[:70]}")
    if len(hits) > 1:
        raise QuoteError(f"quote occurs {len(hits)} times, lengthen it: {quote[:70]}")
    a, b = lines[toks[hits[0]][1]], lines[toks[hits[0] + len(q) - 1][1]]
    return a[0], b[0], a[1]


def stated(value):
    v = (value or "").strip()
    return bool(v) and not v.upper().startswith(NOT_STATED)


def classify(row):
    """RULES.md eligibility. -> (eligible, reason). First failing rule wins."""
    kind = row.get("kind")
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}")
    if row.get("asset", "BTC") != "BTC":
        return False, "not BTC"
    if kind == "RECAP":
        return False, "retrospective"
    if kind == "HYPO":
        return False, "hypothetical"
    if kind == "VIEW":
        return False, "view only, no trade offered"
    if not (row.get("published_utc") or "").strip():
        return False, "NO_TIME"
    missing = [n for n, f in (("entry", "entry"), ("stop", "stop"), ("target", "targets")) if not stated(row.get(f))]
    if missing:
        return False, ", ".join(f"no {m}" for m in missing)
    return True, "entry+stop+target stated, forward-looking, BTC, publish time known"


def parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def window_split(published_utc):
    """DEV when the whole fill+open window ends before the holdout starts, else HOLDOUT."""
    if not (published_utc or "").strip():
        return "NO_TIME"
    return "DEV" if parse_utc(published_utc) + MAX_WINDOW <= HOLDOUT_START else "HOLDOUT"


def load_times(path=None):
    out = {}
    for r in csv.DictReader(io.StringIO((path or TIMES_TSV).read_text(encoding="utf-8")), delimiter="\t"):
        out[r["video_id"]] = r
    return out


def _span(l1, l2):
    return f"{l1}" if l1 == l2 else f"{l1}-{l2}"


def build_rows(rows_json=None, times=None, raw_dir=None):
    entries = json.loads((rows_json or ROWS_JSON).read_text(encoding="utf-8"))
    times = times if times is not None else load_times()
    cache, seq, out = {}, {}, []
    for e in entries:
        vid = e["v"]
        if vid not in cache:
            cache[vid] = load_transcript(vid, raw_dir)
        lines = cache[vid]
        check_quote_length(e["q"])
        l1, l2, ts = locate(lines, e["q"])
        aux = []
        for field, q in e.get("aux", []):
            check_quote_length(q)
            a1, a2, ats = locate(lines, q)
            aux.append(f"{field}: L{_span(a1, a2)} [{ats}] \"{q}\"")
        t = times.get(vid, {})
        row = {
            "video_id": vid,
            "published_utc": t.get("published_utc", ""),
            "time_source": t.get("source", "") if t.get("published_utc") else "",
            "file_line": f"{RAW_REL}/qriptal_{vid}_raw.txt:{_span(l1, l2)}",
            "video_ts": ts,
            "quote": e["q"],
            "asset": e.get("asset", "BTC"),
            "direction": e.get("dir", NOT_STATED),
            "entry": e.get("entry", NOT_STATED),
            "stop": e.get("stop", NOT_STATED),
            "targets": e.get("targets", NOT_STATED),
            "aux_refs": " | ".join(aux),
            "kind": e["kind"],
            "note": e.get("note", ""),
        }
        ok, reason = classify(row)
        row["eligible"] = "Y" if ok else "N"
        row["reason"] = reason
        row["window_split"] = window_split(row["published_utc"])
        out.append(row)
    out.sort(key=lambda r: (r["published_utc"], r["video_id"], int(r["file_line"].rsplit(":", 1)[1].split("-")[0])))
    seq = {}
    for r in out:
        seq[r["video_id"]] = seq.get(r["video_id"], 0) + 1
        r["call_id"] = f"QRP-{r['video_id']}-{seq[r['video_id']]:02d}"
    return out


def render_csv(rows):
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for r in rows:
        w.writerow([r[c] for c in COLUMNS])
    return buf.getvalue()


def read_csv_text():
    """The committed CSV as UTF-8 text with LF line ends. render_csv() always writes LF, but a Windows checkout with
    core.autocrlf=true (the Git for Windows default, so the windows-latest CI runner) stores the same file with CRLF.
    Only the line-end convention of the checkout is normalised; every other byte is still compared."""
    return CSV_PATH.read_bytes().decode("utf-8").replace("\r\n", "\n")


def summary(rows):
    def count(key):
        d = {}
        for r in rows:
            d[r[key]] = d.get(r[key], 0) + 1
        return d
    elig = [r for r in rows if r["eligible"] == "Y"]
    return {"rows": len(rows), "eligible": len(elig), "by_kind": count("kind"), "by_reason": count("reason"),
            "eligible_by_split": {s: sum(1 for r in elig if r["window_split"] == s) for s in ("DEV", "HOLDOUT", "NO_TIME")},
            "videos": len({r["video_id"] for r in rows})}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    rows = build_rows()
    text = render_csv(rows)
    if cmd == "build":
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"wrote {CSV_PATH.relative_to(ROOT)}")
        print(json.dumps(summary(rows), indent=1))
        return 0
    if cmd == "check":
        same = CSV_PATH.exists() and read_csv_text() == text
        print("CALL_LEDGER.csv matches a rebuild" if same else "CALL_LEDGER.csv DIFFERS from a rebuild: run `build`")
        return 0 if same else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
