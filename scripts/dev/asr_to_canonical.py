"""Turn an asr_transcribe.py JSONL into a canonical transcript (raw_transcripts_canonical/<id>_raw.txt).

Output format = the timestamped canonical files (FawPrRUGNpk_raw.txt): `[m:ss] text` per line ([h:mm:ss] from one
hour on), a `# ---` header block above the body, machine-transcription marking in the header.
Lines are cut from the word timestamps: at a sentence end once the line is >= 4 s, always at 10 s, and after
any pause of 1.5 s or more. Loops (the same line 4+ times in a row) and credit-line hallucinations ("Subs by www...") are dropped and counted.

Usage (any python, stdlib only):
    python scripts/dev/asr_to_canonical.py --jsonl F:/MTS/data/fabio_videos/asr/<id>.jsonl --id <id> \
        --title "<title>" --published YYYY-MM-DD --uploader "<channel>" --model medium.en \
        --analyst Fabio --out raw_transcripts_canonical/<id>_raw.txt [--note "<extra header line>"]
"""
import argparse
import json
import re
import sys
from pathlib import Path

SENT_END = re.compile(r"[.?!]$")
# Whisper's known credit-line hallucinations on silence/music at slice or file ends.
HALLUCINATION = re.compile(r"^(subs by |subtitles? by |transcribed by |amara\.org|thanks? for watching|www\.\S+)", re.I)


def stamp(t):
    t = int(t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return "[%d:%02d:%02d]" % (h, m, s) if h else "[%d:%02d]" % (m, s)


def load_words(jsonl):
    words, flagged = [], 0
    for line in Path(jsonl).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("compression_ratio", 0) > 2.4 or r.get("avg_logprob", 0) < -1.0:
            flagged += 1
        for w, s, e, p in r["words"]:
            words.append((w, s, e))
    words.sort(key=lambda x: x[1])
    return words, flagged


def build_lines(words):
    lines, cur, t0, prev_end = [], [], None, None
    for w, s, e in words:
        if cur:
            dur = prev_end - t0
            gap = s - prev_end
            if gap >= 1.5 or dur >= 10 or (dur >= 4 and SENT_END.search(cur[-1].strip())):
                lines.append((t0, "".join(cur).strip()))
                cur, t0 = [], None
        if not cur:
            t0 = s
        cur.append(w)
        prev_end = e
    if cur:
        lines.append((t0, "".join(cur).strip()))
    return [(t, x) for t, x in lines if x]


def collapse_loops(lines):
    out, run, dropped = [], 0, 0
    for t, x in lines:
        if HALLUCINATION.match(x.strip()):
            dropped += 1
            continue
        if out and x.lower() == out[-1][1].lower():
            run += 1
            if run >= 3:
                dropped += 1
                continue
        else:
            run = 0
        out.append((t, x))
    return out, dropped


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--published", default="")
    ap.add_argument("--uploader", default="")
    ap.add_argument("--analyst", default="")
    ap.add_argument("--model", required=True)
    ap.add_argument("--date", default="2026-10-16")
    ap.add_argument("--note", default="", help="extra header line, e.g. speaker warning")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    words, flagged = load_words(a.jsonl)
    lines, dropped = collapse_loops(build_lines(words))
    body = "\n".join("%s %s" % (stamp(t), x) for t, x in lines)
    n_words = len(body.split()) - len(lines)  # minus the stamps
    head = [
        "# Video ID: %s" % a.id,
        "# Title: %s" % a.title,
        "# Published: %s" % a.published,
        "# Source: MACHINE TRANSCRIPTION (ASR), NOT CAPTIONS; audio = YouTube format 251; uploader: %s" % a.uploader,
        "# Method: ASR faster-whisper %s, local, %s" % (a.model, a.date),
        "# Quote rule: anything quoted from this file is an ASR quote and must be labelled ASR; misheard words and "
        "numbers are possible, check against the frames",
        "# Analyst: %s" % a.analyst,
        "# Word count: %d" % n_words,
        "# ASR QA: %d low-confidence segment(s) (compression_ratio > 2.4 or avg_logprob < -1.0), %d looped or "
        "hallucinated-credit line(s) dropped" % (flagged, dropped),
    ]
    if a.note:
        head.append("# Note: %s" % a.note)
    head.append("# ---")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(head) + "\n" + body + "\n")
    print("wrote %s: %d lines, %d words, %d flagged segments, %d looped lines dropped" % (
        a.out, len(lines), n_words, flagged, dropped))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
