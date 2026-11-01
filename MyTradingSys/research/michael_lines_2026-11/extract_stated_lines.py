"""Extract every 'trend line' statement from timed transcripts (descriptive only; no edge claim)."""
import re
import sys
from pathlib import Path

TS = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\s*(.*)$")
LINE = re.compile(r"trend ?line", re.I)
ASSETS = ("gold", "oil", "bitcoin", "btc", "ethereum", "eth", "s&p", "nasdaq", "dollar", "silver")  # OURS keyword list
KINDS = (("break", r"break|broke"), ("retest", r"retest|test"), ("resistance", r"resist|selling|top end|lower high"),
         ("support", r"support|lows|higher low"))  # OURS keyword map


def extract_lines(lines, video, radius=6):
    parsed = [TS.match(l.strip()) for l in lines]
    out = []
    for i, m in enumerate(parsed):
        if not m or not LINE.search(m.group(2)):
            continue
        lo, hi = max(0, i - radius), min(len(lines), i + radius + 1)
        win = " ".join(p.group(2) for p in parsed[lo:hi] if p)
        low = win.lower()
        asset = next((a for a in ASSETS if re.search(r"\b" + re.escape(a), low)), "NOT_IN_DATA")
        kinds = [k for k, rx in KINDS if re.search(rx, low)] or ["unspecified"]
        out.append({"video": video, "timestamp": m.group(1), "quote": m.group(2).strip(),
                    "quote_window": " ".join(p.group(2) for p in (parsed[j] for j in (i - 1, i, i + 1) if 0 <= j < len(parsed)) if p),
                    "asset": asset, "kind": "/".join(kinds)})
    return out


def extract_file(path):
    p = Path(path)
    return extract_lines(p.read_text(encoding="utf-8").splitlines(), p.name.split("_timed")[0])


def extract_all(folder):
    rows = []
    for p in sorted(Path(folder).glob("*_timed.txt")):
        rows += extract_file(p)
    return rows


def main():
    here = Path(__file__).resolve().parent
    rows = extract_all(here.parent / "yt_feed_2026-10-31" / "transcripts_michael-pizzino-new10")
    o = ["# STATED_LINES: trend lines Michael states (2026-10-31 yt_feed, 10 transcripts)", "",
         "Asset and kind are OURS keyword guesses from a +-6 line window; the line itself is drawn on the chart frame (NOT_IN_DATA: frames not in repo).",
         "", "| video | timestamp | asset (OURS) | kind (OURS) | quote | chart geometry |", "|---|---|---|---|---|---|"]
    for r in rows:
        o.append(f"| {r['video']} | {r['timestamp']} | {r['asset']} | {r['kind']} | {r['quote'].replace('|', '/')} | NOT_IN_DATA |")
    o += ["", f"{len(rows)} statements in {len({r['video'] for r in rows})} of 10 videos."]
    (here / "STATED_LINES.md").write_text("\n".join(o) + "\n", encoding="utf-8", newline="\n")
    print(len(rows))


if __name__ == "__main__":
    sys.exit(main())
