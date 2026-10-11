"""Fill position tags and pos% in a V2 extract so the writer never guesses them.

Usage (repo root):  python scripts/dev/extract_fix_gps.py extracts/v2/tom/<id>_v2.md [...]

1. Every anchor `> "<quote>"` followed by `**Source GPS: <ID> | <anything>**` gets the real BEGIN/MIDDLE/END
   (same normalisation and third-split as verify_extract_quotes.py). A quote that is not verbatim is reported and left alone.
2. Every token `{{pos:<few words>}}` is replaced by the integer pos% (0-100) of those words in the transcript of the
   video id found in the file's header line `video_id: <id>`. Not found = reported, token left.
3. Every token `{{loc:<few words>}}` becomes `[T/<id>:<file line>@<char offset>]` (same tag form as EXTRACTION_ROUND2).
Then run verify_extract_quotes.py (the real gate).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_extract_quotes as g  # noqa: E402

QUOTE = g.QUOTE
GPS = re.compile(r"(\*\*Source GPS:\s*)([A-Za-z0-9_-]{11})(\s*\|\s*)([A-Za-z?]+)(\*\*)")
POS = re.compile(r"\{\{pos:([^}]+)\}\}")
LOC = re.compile(r"\{\{loc:([^}]+)\}\}")
TOK = re.compile(r"[a-z0-9%]+")


def locate(vid, words):
    """Return 'T/<vid>:<file line>@<char offset in that line>' of the first token of `words`, or None."""
    full = (g.ROOT / "raw_transcripts_canonical" / ("%s_raw.txt" % vid)).read_text(encoding="utf-8", errors="replace")
    cut = full.index("# ---") + len("# ---") if "# ---" in full else 0
    low = full.lower()
    toks = [(m.group(0), m.start()) for m in TOK.finditer(low, cut)]
    want = TOK.findall(words.lower())
    names = [t for t, _ in toks]
    for i in range(len(names) - len(want) + 1):
        if names[i:i + len(want)] == want:
            start = toks[i][1]
            line_no = full.count(chr(10), 0, start) + 1
            line_start = full.rfind(chr(10), 0, start) + 1
            return "T/%s:%d@%d" % (vid, line_no, start - line_start)
    return None


def main(argv):
    bad = 0
    for a in argv:
        path = Path(a)
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        m = re.search(r"video_id:\s*([A-Za-z0-9_-]{11})", text)
        vid_header = m.group(1) if m else None
        cache = {}

        def body(v):
            if v not in cache:
                cache[v] = g.norm(g.transcript_body(v))
            return cache[v]

        for i, line in enumerate(lines):
            q = QUOTE.match(line.strip())
            if q:
                for j in (i + 1, i + 2):
                    if j < len(lines) and GPS.search(lines[j]):
                        gm = GPS.search(lines[j])
                        b = body(gm.group(2))
                        at = b.find(g.norm(q.group(1)))
                        if at < 0:
                            print("NOT-VERBATIM %s:%d %r" % (path.name, i + 1, q.group(1)[:70]))
                            bad += 1
                        else:
                            third = ("BEGIN", "MIDDLE", "END")[min(2, 3 * at // max(1, len(b)))]
                            lines[j] = GPS.sub(lambda mm: mm.group(1) + mm.group(2) + mm.group(3) + third + mm.group(5), lines[j], 1)
                        break
            if LOC.search(line) and vid_header:
                def repl(mm):
                    r = locate(vid_header, mm.group(1))
                    if r is None:
                        print("LOC-NOT-FOUND %s:%d %r" % (path.name, i + 1, mm.group(1)[:60]))
                        return mm.group(0)
                    return "[" + r + "]"
                lines[i] = LOC.sub(repl, lines[i])
                line = lines[i]
            if POS.search(line) and vid_header:
                def rep(mm):
                    global_bad = 0
                    b = body(vid_header)
                    at = b.find(g.norm(mm.group(1)))
                    if at < 0:
                        print("POS-NOT-FOUND %s:%d %r" % (path.name, i + 1, mm.group(1)[:60]))
                        return mm.group(0)
                    return str(100 * at // len(b))
                lines[i] = POS.sub(rep, line)
        path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        # fragment audit: every double-quoted fragment of >= 4 words must be verbatim in the transcript
        if vid_header:
            b = body(vid_header)
            tot = miss = 0
            for i, line in enumerate(lines):
                for fm in re.finditer(r'"([^"]+)"', line):
                    frag = g.norm(fm.group(1))
                    if len(frag.split()) < 4:
                        continue
                    tot += 1
                    if frag not in b:
                        miss += 1
                        print("FRAG-NOT-VERBATIM %s:%d %r" % (path.name, i + 1, fm.group(1)[:80]))
            print("%s: quoted fragments verbatim %d/%d" % (path.name, tot - miss, tot))
    print("done" if not bad else "%d anchor(s) not verbatim" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
