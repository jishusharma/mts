"""Verify that every quote in an extraction file appears verbatim in its transcript.

An extract block looks like:
    > "<verbatim quote>"
    **Source GPS: <VIDEO_ID> | <BEGIN|MIDDLE|END>**
The quote must occur in raw_transcripts_canonical/<VIDEO_ID>_raw.txt after
normalising case, whitespace and punctuation (auto-captions carry no reliable
punctuation). The position tag must match where the quote sits (thirds).

Usage (repo root):
    python scripts/dev/verify_extract_quotes.py extracts/processed/malkan/extract_X.md[.new] [...]
Exit code 1 if any quote is missing or mis-positioned. Prints one line per quote.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUOTE = re.compile(r'^>\s*"(.+)"\s*$')
TIMESTAMP = re.compile(r"\[\d+:\d{2}(?::\d{2})?\]")
CBP_EVIDENCE = re.compile(r'^(?:-\s*)?evidence:\s*"(.+)"\s*$')
CBP_HEAD = re.compile(r"^###\s*[^|]*\|[^|]*\|\s*([A-Za-z0-9_-]{11})\s*\|")
GPS = re.compile(r"Source GPS:\s*([A-Za-z0-9_-]{11})\s*\|\s*(BEGIN|MIDDLE|END)")


FILLERS = {"uh", "um", "uhm", "er", "erm"}


def norm(s: str) -> str:
    """Lowercase alphanumerics; auto-captions keep spoken fillers (uh, um) and stutters ("is is"),
    which a clean quote drops, so both sides lose fillers and immediate word repeats."""
    out = []
    for w in re.sub(r"[^a-z0-9%]+", " ", s.lower()).split():
        if w in FILLERS or (out and out[-1] == w):
            continue
        out.append(w)
    return " ".join(out)


def transcript_body(vid: str) -> str:
    p = ROOT / "raw_transcripts_canonical" / f"{vid}_raw.txt"
    text = p.read_text(encoding="utf-8", errors="replace")
    body = text.split("# ---", 1)[1] if "# ---" in text else text
    return TIMESTAMP.sub(" ", body)  # [m:ss] caption markers split verbatim quotes


def cbp_transcript_body(vid: str, folder: Path) -> str:
    """CBP keeps transcripts as <folder>/inbox/<Analyst>_<id>.txt next to extractions.md."""
    hits = sorted((folder / "inbox").glob(f"*_{vid}.txt"))
    if not hits:
        raise OSError(vid)
    return TIMESTAMP.sub(" ", hits[0].read_text(encoding="utf-8", errors="replace"))


def first_missing(quote: str, body_norm: str):
    """None when `quote` occurs in the normalised transcript `body_norm`, else the first fragment that does not.
    "..." / ellipsis joins fragments that must each occur, in order. The one matcher (CBP run, extract files)."""
    at = 0
    for frag in re.split(r"\.{3}|…", quote):
        q = norm(frag)
        if not q:
            continue
        at = body_norm.find(q, at)
        if at < 0:
            return frag
        at += len(q)
    return None


def check_cbp_evidence(path: Path, lines, i, m, cache) -> int:
    """CBP block: `### <Short> | <date> | <video_id> | <title>` then ONE `evidence: "<quote>"`.
    "..." / ellipsis inside the quote joins fragments that must each occur, in order. No position tag."""
    nearest = next((l for l in reversed(lines[:i]) if l.startswith("#")), "")
    head = CBP_HEAD.match(nearest)
    if not head:
        print(f"NO-HEADER {path.name}:{i + 1}")
        return 1
    vid = head.group(1)
    if vid not in cache:
        try:
            cache[vid] = norm(transcript_body(vid))
        except OSError:
            try:
                cache[vid] = norm(cbp_transcript_body(vid, path.parent))
            except OSError:
                cache[vid] = None
    body = cache[vid]
    if body is None:
        print(f"NO-TRANSCRIPT {path.name}:{i + 1} {vid}")
        return 1
    bad = first_missing(m.group(1), body)
    if bad is not None:
        print(f"MISSING  {path.name}:{i + 1} {bad.strip()[:60]!r}")
        return 1
    print(f"OK       {path.name}:{i + 1}")
    return 0


def check(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    bad = 0
    cache = {}
    for i, line in enumerate(lines):
        ev = CBP_EVIDENCE.match(line.strip())
        if ev:
            bad += check_cbp_evidence(path, lines, i, ev, cache)
            continue
        m = QUOTE.match(line.strip())
        if not m:
            continue
        gps = next((GPS.search(l) for l in lines[i + 1:i + 3] if GPS.search(l)), None)
        if not gps:
            print(f"NO-GPS   {path.name}:{i + 1}")
            bad += 1
            continue
        vid, pos = gps.groups()
        if vid not in cache:
            try:
                cache[vid] = norm(transcript_body(vid))
            except OSError:
                cache[vid] = None
        body = cache[vid]
        if body is None:
            print(f"NO-TRANSCRIPT {path.name}:{i + 1} {vid}")
            bad += 1
            continue
        q = norm(m.group(1))
        at = body.find(q)
        if not q or at < 0:
            print(f"MISSING  {path.name}:{i + 1} {m.group(1)[:60]!r}")
            bad += 1
            continue
        third = ("BEGIN", "MIDDLE", "END")[min(2, 3 * at // max(1, len(body)))]
        if third != pos:
            print(f"POSITION {path.name}:{i + 1} tagged {pos}, found {third}")
            bad += 1
        else:
            print(f"OK       {path.name}:{i + 1}")
    return bad


def main(argv) -> int:
    if not argv:
        print(__doc__)
        return 2
    bad = sum(check(Path(a)) for a in argv)
    print(f"{'FAIL' if bad else 'PASS'}: {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
