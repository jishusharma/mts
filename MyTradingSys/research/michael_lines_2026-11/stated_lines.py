"""Extract the trend lines Michael states in the timed yt_feed transcripts (card tl-michael-lines-detect-alert, step 1).

Descriptive only: a stated line = a "trend line" / "trendline" phrase in a caption line that carries a [hh:mm:ss] stamp.
Text without a stamp is rejected (no timestamp, no row). Asset and kind are read from the words around the phrase
(OURS heuristic: nearest earlier asset word in the 200 words before, else the video title; kind words in 8 before / 15 after). The chart frame
is not in the repo, so where a line only exists in the picture the row says NOT_IN_DATA, never a guess.

Usage: python stated_lines.py <transcripts_dir> > STATED_LINES.md
"""
import re
import sys
from pathlib import Path

TS = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\s?(.*)$")
PHRASE = re.compile(r"trend[\s-]*lines?\b", re.I)
ASSETS = (("bitcoin", "BTC"), ("btc", "BTC"), ("ethereum", "ETH"), ("nasdaq", "NASDAQ"), ("oil", "OIL"), ("gold", "GOLD"),
          ("s&p", "SPX"), ("dollar", "DXY"), ("silver", "SILVER"), ("barrel", "OIL"))
KINDS = (("retest", "retest"), ("test its", "retest"), ("break", "break"), ("resistance", "resistance"), ("support", "support"))


def parse(path):
    """(video_id, title, published, [(ts, text)]) from one timed transcript. Only stamped caption lines are kept."""
    vid = title = pub = ""
    caps = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.startswith("# Video ID:"):
            vid = ln.split(":", 1)[1].strip()
        elif ln.startswith("# Title:"):
            title = ln.split(":", 1)[1].strip()
        elif ln.startswith("# Published:"):
            pub = ln.split(":", 1)[1].strip()
        else:
            m = TS.match(ln)
            if m:
                caps.append((m.group(1), m.group(2)))
    return vid or Path(path).stem.replace("_timed", ""), title, pub, caps


def _words(caps):
    return [(ts, w) for ts, text in caps for w in text.split()]


def extract(path):
    """One row per phrase hit: video, ts (stamp of the caption line holding 'trend'), quote, asset, kind, title, published."""
    vid, title, pub, caps = parse(path)
    words = _words(caps)
    flat = " ".join(w for _, w in words)
    starts, pos = [], 0
    for _, w in words:
        starts.append(pos)
        pos += len(w) + 1
    rows = []
    for m in PHRASE.finditer(flat):
        i = max(k for k, s in enumerate(starts) if s <= m.start())
        before = " ".join(w for _, w in words[max(0, i - 200):i]).lower()
        near = " ".join(w for _, w in words[max(0, i - 8):i + 15]).lower()
        asset = "NOT_IN_DATA"
        best = -1
        for key, name in ASSETS:
            at = before.rfind(key)
            if at > best:
                best, asset = at, name
        if asset == "NOT_IN_DATA":
            low = title.lower()
            asset = next((name for key, name in ASSETS if key in low), "NOT_IN_DATA")
        kind = next((k for key, k in KINDS if key in near), "mention")
        quote = " ".join(w for _, w in words[max(0, i - 6):i + 12])
        rows.append({"video": vid, "ts": words[i][0], "quote": quote, "asset": asset, "kind": kind, "title": title, "published": pub})
    return rows


def extract_dir(folder):
    out = []
    for p in sorted(Path(folder).glob("*_timed.txt")):
        out.extend(extract(p))
    return out


def to_markdown(rows):
    head = "| video | ts | asset | kind | quote | published |\n|---|---|---|---|---|---|\n"
    return head + "".join(f"| {r['video']} | {r['ts']} | {r['asset']} | {r['kind']} | {r['quote']} | {r['published']} |\n" for r in rows)


if __name__ == "__main__":
    sys.stdout.write(to_markdown(extract_dir(sys.argv[1])))
