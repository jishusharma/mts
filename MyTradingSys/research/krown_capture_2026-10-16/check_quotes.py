"""Verify every '> "quote"' + 'Source: <id> @hh:mm:ss' pair in a markdown file against transcripts/<id>_timed.txt.
Normalised match (lowercase, punctuation stripped, whitespace joined). Reports the real timestamp; --fix rewrites @ts.
Usage: python -I check_quotes.py RULES_DRAFT.md [--fix]"""
import re, sys
from pathlib import Path
here = Path(__file__).resolve().parent
norm = lambda s: " ".join(re.sub(r"[^a-z0-9%]+", " ", s.lower()).split())
cache = {}
def load(vid):
    if vid not in cache:
        words, ts = [], []
        for l in (here/"transcripts"/f"{vid}_timed.txt").read_text(encoding="utf8").splitlines():
            m = re.match(r"\[(\d+):(\d+):(\d+)\] (.*)", l)
            if not m: continue
            t = "%02d:%02d:%02d" % tuple(map(int, m.groups()[:3]))
            for w in norm(m[4]).split(): words.append(w); ts.append(t)
        cache[vid] = (words, ts)
    return cache[vid]
f = Path(sys.argv[1]); fix = "--fix" in sys.argv
lines = f.read_text(encoding="utf8").splitlines()
bad = 0; n = 0
for i, l in enumerate(lines):
    m = re.match(r'^>\s*"(.+)"\s*$', l)
    if not m: continue
    s = re.match(r"^Source:\s*([A-Za-z0-9_-]{11}) @(\d\d:\d\d:\d\d)", lines[i+1])
    n += 1
    if not s: print("NO SOURCE LINE", i+1); bad += 1; continue
    words, ts = load(s[1]); q = norm(m[1]).split(); k = len(q)
    pos = next((j for j in range(len(words)-k+1) if words[j:j+k] == q), None)
    if pos is None: print("MISSING", i+1, s[1], m[1][:70]); bad += 1; continue
    real = ts[pos]
    if real != s[2]:
        print("TS", i+1, s[2], "->", real)
        if fix: lines[i+1] = lines[i+1].replace("@"+s[2], "@"+real, 1)
if fix: f.write_text("\n".join(lines)+"\n", encoding="utf8", newline="\n")
print(f"{n} quotes, {bad} problems")
sys.exit(1 if bad else 0)
