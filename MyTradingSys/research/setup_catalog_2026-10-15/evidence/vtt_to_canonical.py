"""P2 (Fable catalogue audit 2026-10-16): caption files on F: -> raw_transcripts_canonical/<id>_raw.txt.

Usage (repo root):
    python MyTradingSys/research/setup_catalog_2026-10-15/evidence/vtt_to_canonical.py convert
    python MyTradingSys/research/setup_catalog_2026-10-15/evidence/vtt_to_canonical.py check

convert: 9IliXww64uM.en.vtt and DyS79Eb92Ug.txt (both under F:/MTS/data/fabio_videos/) -> canonical transcript with the
header block the quote gate expects (`# Video ID`, `# Source`, ..., `# ---`), then one caption cue per line as
`[m:ss] text` (`[h:mm:ss]` from one hour) so a quote can be cited as file:line and as a time. Rolling-caption duplicates
are dropped, HTML entities decoded, [music]/[applause]/[laughter] tags removed (as in the Tom canonical files).
DyS79Eb92Ug is converted from its .en.vtt (the flattened DyS79Eb92Ug.txt the audit read omits ~260 words, and its
second stamps differ from the cue starts by a few seconds); the .txt is cross-checked against the vtt text.
check: compares the other four Fabio vtt files with their canonical copies, prints the word-level agreement.
"""
import difflib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CANON = ROOT / "raw_transcripts_canonical"
SRC = Path("F:/MTS/data/fabio_videos")
TS_RE = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)\s+-->")
TAGS = re.compile(r"\[(?:music|applause|laughter)\]", re.I)
STAMP = re.compile(r"\[\d+:\d{2}(?::\d{2})?\]")
SCRIPT = "MyTradingSys/research/setup_catalog_2026-10-15/evidence/vtt_to_canonical.py"


def clean(t):
    t = html.unescape(t)
    t = TAGS.sub(" ", t)
    return " ".join(t.split())


def parse_vtt(vtt):
    cues, start, last = [], None, None
    for line in vtt.splitlines():
        line = line.strip()
        m = TS_RE.match(line)
        if m:
            start = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            continue
        if (not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")) or line.isdigit()
                or start is None):
            continue
        t = clean(re.sub(r"<[^>]+>", "", line))
        if t and t != last:
            cues.append((start, t))
            last = t
    return cues


def parse_txt(txt):
    cues = []
    for line in txt.splitlines():
        head, _, rest = line.partition(" ")
        if head.isdigit():
            t = clean(rest)
            if t:
                cues.append((int(head), t))
    return cues


def stamp(s):
    return f"[{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}]" if s >= 3600 else f"[{s // 60}:{s % 60:02d}]"


def words(text):
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", text.lower()).split()).split()


def write_canonical(vid, cues, source):
    n = sum(len(t.split()) for _, t in cues)
    head = (f"# Video ID: {vid}\n# Source: {source}\n# Analyst: Fabio Valentini (trader-interview/live-session caption file)\n"
            f"# Word count: {n}\n# ---\n")
    body = "\n".join(f"{stamp(s)} {t}" for s, t in cues)
    dest = CANON / f"{vid}_raw.txt"
    dest.write_text(head + body + "\n", encoding="utf-8", newline="\n")
    return dest, n


def agree(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    same = sum(blk.size for blk in sm.get_matching_blocks())
    return same, sm


def convert():
    vtt = parse_vtt((SRC / "9IliXww64uM.en.vtt").read_text(encoding="utf-8", errors="replace"))
    d, n = write_canonical("9IliXww64uM", vtt, "F:/MTS/data/fabio_videos/9IliXww64uM.en.vtt (yt-dlp auto captions, en), "
                           f"converted 2026-10-16 by {SCRIPT}; rolling duplicates dropped, entities decoded, [music] tags removed")
    print(f"wrote {d.name}: {n} words, {len(vtt)} cues")
    vv = parse_vtt((SRC / "DyS79Eb92Ug.en.vtt").read_text(encoding="utf-8", errors="replace"))
    d, n = write_canonical("DyS79Eb92Ug", vv, "F:/MTS/data/fabio_videos/DyS79Eb92Ug.en.vtt (yt-dlp auto captions, en), "
                           f"converted 2026-10-16 by {SCRIPT}; rolling duplicates dropped, entities decoded, [music] tags removed. "
                           "Built from the .en.vtt, not from DyS79Eb92Ug.txt: the flattened .txt omits about 260 words "
                           "(see vtt_to_canonical_output.txt)")
    print(f"wrote {d.name}: {n} words, {len(vv)} cues")
    txt = parse_txt((SRC / "DyS79Eb92Ug.txt").read_text(encoding="utf-8", errors="replace"))
    a, b = words(" ".join(t for _, t in txt)), words(" ".join(t for _, t in vv))
    same, sm = agree(a, b)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    print(f"DyS79Eb92Ug .txt vs .en.vtt: txt {len(a)} words, vtt {len(b)} words, common {same} "
          f"({100 * same / max(len(a), len(b)):.2f} % of the longer)")
    print(f"   {sum(1 for o in ops if o[0] == 'insert')} spans only in the vtt ({sum(o[4] - o[3] for o in ops if o[0] == 'insert')} words, "
          f"back-channel fillers 'mhm'/'yeah' and a few short clauses), {sum(1 for o in ops if o[0] == 'delete')} stray tokens only in the .txt")


def check():
    for vid in ("0jM5Y31YJak", "8CWKfoSJu3c", "fZlNGWvd2Ko", "jasv3L-d8ZE"):
        vv = parse_vtt((SRC / f"{vid}.en.vtt").read_text(encoding="utf-8", errors="replace"))
        canon = (CANON / f"{vid}_raw.txt").read_text(encoding="utf-8", errors="replace")
        body = canon.split("# ---", 1)[1] if "# ---" in canon else canon
        a, b = words(STAMP.sub(" ", TAGS.sub(" ", body))), words(" ".join(t for _, t in vv))
        same, sm = agree(a, b)
        print(f"{vid}: canonical {len(a)} words, vtt {len(b)} words, common {same} "
              f"({100 * same / max(len(a), len(b)):.2f} % of the longer)")
        shown = 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal" and shown < 6:
                shown += 1
                print(f"   {tag}: canonical[{i1}:{i2}]={' '.join(a[i1:i2])[:70]!r} | vtt[{j1}:{j2}]={' '.join(b[j1:j2])[:70]!r}")
        print(f"   {sum(1 for o in sm.get_opcodes() if o[0] != 'equal')} differing spans")


if __name__ == "__main__":
    {"convert": convert, "check": check}[sys.argv[1]]()
