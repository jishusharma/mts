"""Finish a transcript copied from the YouTube transcript panel (YT_PROXY.md, "Never blocked: path order", path 3).

Usage: python scripts/dev/cache_panel_transcript.py raw_transcripts_canonical/<id>_timed.txt [...]
The _timed.txt file has the same header as fetch_captions_timed.py writes (# Video ID ... # ---) then one
`[HH:MM:SS] text` cue per line; the Source header says "browser transcript panel". This tool sets the
`# Word count:` line and writes the untimed shared-store file <id>_raw.txt next to it (git-ignored, like the
fetcher's cache), so verify_extract_quotes.py and later tools read it as a normal cached caption file.
Makes no network request.
"""
import re
import sys
from pathlib import Path

CUE = re.compile(r"^\[\d+:\d{2}:\d{2}\] (.*)$")


def finish(path):
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    sep = lines.index("# ---")
    head, body = lines[:sep], lines[sep + 1:]
    texts = []
    for ln in body:
        m = CUE.match(ln)
        if not m:
            raise SystemExit(f"{path}: not a cue line: {ln[:60]!r}")
        texts.append(m.group(1).strip())
    words = sum(len(t.split()) for t in texts)
    head = [f"# Word count: {words}" if h.startswith("# Word count:") else h for h in head]
    path.write_text("\n".join(head + ["# ---"] + body) + "\n", encoding="utf-8", newline="\n")
    raw_head = [h for h in head if not h.startswith("# Duration_s")]
    raw = path.with_name(path.name.replace("_timed.txt", "_raw.txt"))
    raw.write_text("\n".join(raw_head + ["# ---", " ".join(texts)]) + "\n", encoding="utf-8", newline="\n")
    return f"{path.name}: {len(texts)} cues, {words} words -> {raw.name}"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(finish(p))
