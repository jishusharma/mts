"""check_spec_quotes.py: every quoted Tom line in a spec must be verbatim in the transcript lines it cites.

A citation is a double-quoted string followed, before the next quote, by `(<video id>:<a>-<b>)` (or a single line `:<a>`,
or two ranges `:<a>-<b>, <c>-<d>` when two quotes share one citation). Transcripts are `<dir>/<video id>.txt`, one caption
per line as `mm:ss text`. Comparison ignores case, the timestamps and whitespace.

Usage: python scripts/dev/check_spec_quotes.py <spec.md> [--dir F:/MTS/data/tom_videos]
Exit 0 = every quote found (or the transcript folder is not on this machine: said in one line), 1 = a quote is not verbatim.
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_DIR = "F:/MTS/data/tom_videos"
CITE = re.compile(r"\(([A-Za-z0-9_-]{11}):(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)(?:,\s*paraphrase)?\)")
QUOTE = re.compile(r'"([^"\n]{12,})"')
STAMP = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?\s+")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("&gt;", ">").replace("&amp;", "&")).strip().lower()


def span_text(lines, spec):
    """Text of the cited line ranges (1-based, inclusive), timestamps removed."""
    out = []
    for part in re.split(r",\s*", spec):
        a, _, b = part.partition("-")
        a = int(a)
        b = int(b) if b else a
        out.extend(STAMP.sub("", ln) for ln in lines[a - 1:b])
    return norm(" ".join(out))


def pairs(text):
    """(quote, video id, line spec) for each quote that has a citation before the next quote on its line."""
    found = []
    for raw in text.splitlines():
        quotes = list(QUOTE.finditer(raw))
        cites = list(CITE.finditer(raw))
        for i, q in enumerate(quotes):
            for c in cites:
                if c.start() < q.end():
                    continue
                between = [x for x in quotes[i + 1:] if x.end() <= c.start()]
                # quotes chained by "and" share the citation that follows the last of them
                if all(raw[x.start() - 6:x.start()].strip().endswith(("and", ";")) for x in between):
                    found.append((q.group(1), c.group(1), c.group(2)))
                break
    return found


def check(text, tdir):
    """List of (quote, id, lines, reason) for every quote that is not verbatim in its cited lines."""
    bad, cache = [], {}
    for quote, vid, spec in pairs(text):
        if vid not in cache:
            p = Path(tdir) / f"{vid}.txt"
            cache[vid] = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else None
        if cache[vid] is None:
            bad.append((quote, vid, spec, "transcript missing"))
        elif norm(quote) not in span_text(cache[vid], spec):
            bad.append((quote, vid, spec, "not verbatim in cited lines"))
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    a = ap.parse_args(argv)
    text = Path(a.spec).read_text(encoding="utf-8")
    if not Path(a.dir).is_dir():
        print(f"check_spec_quotes: transcript folder {a.dir} is not on this machine; nothing checked")
        return 0
    n = len(pairs(text))
    bad = check(text, a.dir)
    for quote, vid, spec, why in bad:
        print(f"MISMATCH {vid}:{spec} {why}: \"{quote[:70]}\"")
    print(f"check_spec_quotes: {n - len(bad)}/{n} cited quotes verbatim")
    return 1 if bad or n == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
