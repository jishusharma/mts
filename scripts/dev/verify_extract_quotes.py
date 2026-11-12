"""Verify that every quote in an extraction file appears verbatim in its transcript.

An extract block looks like:
    > "<verbatim quote>"
    **Source GPS: <VIDEO_ID> | <BEGIN|MIDDLE|END>**
The quote must occur in raw_transcripts_canonical/<VIDEO_ID>_raw.txt after
normalising case, whitespace and punctuation (auto-captions carry no reliable
punctuation). The position tag must match where the quote sits (thirds).

Usage (repo root):
    python scripts/dev/verify_extract_quotes.py extracts/processed/malkan/extract_X.md[.new] [...]
A repo-doc sheet (layer_facts, layer reviews) is checked too: every `path:line[-line]` cite must name an
existing repo file with that line, and every "double-quoted" span on a line with cites must occur in a cited
file (normalised) within 3 lines of the cited range; "..." joins fragments as for transcripts.
Exit code 1 if any quote is missing or mis-positioned. Prints one line per quote.
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUOTE = re.compile(r'^>\s*"(.*)"\s*$')
TIMESTAMP = re.compile(r"\[\d+:\d{2}(?::\d{2})?\]")
CBP_EVIDENCE = re.compile(r'^(?:-\s*)?evidence:\s*"(.*)"\s*$')
CBP_HEAD = re.compile(r"^###\s*[^|]*\|[^|]*\|\s*([A-Za-z0-9_-]{11})\s*\|")
GPS = re.compile(r"Source GPS:\s*([A-Za-z0-9_-]{11})\s*\|\s*(BEGIN|MIDDLE|END)")


FILLERS = {"uh", "um", "uhm", "er", "erm"}


def norm(s: str) -> str:
    """Lowercase alphanumerics (Latin and Devanagari); auto-captions keep spoken fillers (uh, um) and stutters ("is is"),
    which a clean quote drops, so both sides lose fillers and immediate word repeats."""
    out = []
    s = unicodedata.normalize("NFC", s).replace("‌", "").replace("‍", "")  # joiners are not speech
    # Devanagari (U+0900-U+097F) is compared too, so pure-Hindi quotes can pass; the danda (U+0964/0965) is punctuation.
    for w in re.sub(r"[^a-z0-9%ऀ-ॣ०-ॿ]+", " ", s.lower()).split():
        if w in FILLERS or (out and out[-1] == w):
            continue
        out.append(w)
    return " ".join(out)


def transcript_body(vid: str) -> str:
    p = ROOT / "raw_transcripts_canonical" / f"{vid}_raw.txt"
    text = p.read_text(encoding="utf-8", errors="replace")
    body = text.split("# ---", 1)[1] if "# ---" in text else text
    # a nested metadata block (Video ID .. Description) after the first '# ---' is not speech: drop its '# ' run and the closing '# ---'
    lines = body.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        while i < len(lines) and lines[i].startswith("# "):
            i += 1
        if i < len(lines) and lines[i].strip() == "# ---":
            i += 1
        body = "\n".join(lines[i:])
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
    seen_any = False
    for frag in re.split(r"\.{3}|…", quote):
        q = norm(frag)
        if not q:
            continue
        seen_any = True
        p = re.compile(rf"(?:^|\s){re.escape(q)}(?:\s|$)")
        m = p.search(body_norm, at)
        if not m:
            return frag
        start = m.start() + (1 if body_norm[m.start()] == " " else 0)
        at = start + len(q)
    return None if seen_any else quote


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


DOC_CITE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|json|java|txt|csv|ya?ml|sh|ts|js)):((?:\d+(?:-\d+)?)(?:,\d+(?:-\d+)?)*)`")
DOC_QUOTE = re.compile(r'"([^"\n]{12,}?)"')
SLACK = 3
_doc_cache = {}


def _doc_lines(rel: str):
    if rel not in _doc_cache:
        p = ROOT / rel
        _doc_cache[rel] = p.read_text(encoding="utf-8", errors="replace").split("\n") if p.is_file() else None
    return _doc_cache[rel]


def check_doc_line(name: str, n: int, line: str) -> int:
    """Repo-doc cites on one line: file:line must exist; quoted spans must occur in a cited file near its lines."""
    cites = []
    for m in DOC_CITE.finditer(line):  # `file:7,75,144` or `file:3-9` -> one (file, a, b) per span
        for span in m.group(2).split(","):
            a, _, b = span.partition("-")
            cites.append((m.group(1), int(a), int(b or a)))
    if not cites:
        return 0
    bad = 0
    live = []
    for rel, a, b in cites:
        src = _doc_lines(rel)
        if src is None:
            print(f"NO-FILE  {name}:{n} {rel}")
            bad += 1
        elif a < 1 or a > len(src) or b < a:
            print(f"NO-LINE  {name}:{n} {rel}:{a}-{b} (file has {len(src)} lines)")
            bad += 1
        else:
            live.append((rel, a, b))
    if not live:
        return bad
    stripped = DOC_CITE.sub(" ", line)
    for qm in DOC_QUOTE.finditer(stripped):
        quote = qm.group(1)
        if len(norm(quote).split()) < 3:
            continue
        in_file = in_range = False
        for rel, a, b in live:
            src = _doc_lines(rel)
            if first_missing(quote, norm("\n".join(src))) is None:
                in_file = True
                if first_missing(quote, norm("\n".join(src[max(0, a - 1 - SLACK):b + SLACK]))) is None:
                    in_range = True
        if not in_file:
            print(f"NO-QUOTE {name}:{n} {quote[:60]!r} not in cited file")
            bad += 1
        elif not in_range:
            print(f"WRONG-LINE {name}:{n} {quote[:60]!r} in file but not within {SLACK} lines of the cited range")
            bad += 1
    if not bad:
        print(f"OK       {name}:{n} ({len(live)} cite(s))")
    return bad


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
            bad += check_doc_line(path.name, i + 1, line)
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
        if not q:
            print(f"MISSING  {path.name}:{i + 1} {m.group(1)[:60]!r}")
            bad += 1
            continue
        p = re.compile(rf"(?:^|\s){re.escape(q)}(?:\s|$)")
        m_word = p.search(body)
        if not m_word:
            print(f"MISSING  {path.name}:{i + 1} {m.group(1)[:60]!r}")
            bad += 1
            continue
        at = m_word.start() + (1 if body[m_word.start()] == " " else 0)
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
