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
GPS = re.compile(r"Source GPS:\s*([A-Za-z0-9_-]{11})\s*\|\s*(BEGIN|MIDDLE|END)")


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", s.lower()).split())


def transcript_body(vid: str) -> str:
    p = ROOT / "raw_transcripts_canonical" / f"{vid}_raw.txt"
    text = p.read_text(encoding="utf-8", errors="replace")
    body = text.split("# ---", 1)[1] if "# ---" in text else text
    return TIMESTAMP.sub(" ", body)  # [m:ss] caption markers split verbatim quotes


def check(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    bad = 0
    cache = {}
    for i, line in enumerate(lines):
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
