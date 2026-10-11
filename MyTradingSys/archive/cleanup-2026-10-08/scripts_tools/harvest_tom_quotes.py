import sys, os, re, json
sys.dont_write_bytecode = True
from pathlib import Path

R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
CDIR = R / "MyTradingSys" / "mts" / "conditions"
OUT = R / "Dumps" / "tom_harvest.json"

results = []
files = sorted(CDIR.glob("*.md"))
for f in files:
    lines = f.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^>\s*[\'"](.*)$', line)
        if not m:
            i += 1
            continue
        quote_lines = [m.group(1)]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if not nxt.startswith(">"):
                break
            if re.search(r'\*\*Source GPS', nxt):
                break
            if nxt.strip() == ">":
                i += 1
                break
            quote_lines.append(nxt.lstrip(">").strip())
            i += 1
        gps = None
        j = i
        while j < min(i + 3, len(lines)):
            gm = re.search(r'Source GPS:\**\s*([A-Za-z0-9_\-]{11})\s*\|\s*\[([A-Z]+)\]', lines[j])
            if gm:
                gps = (gm.group(1), gm.group(2))
                break
            j += 1
        quote_text = " ".join(p.strip() for p in quote_lines)
        quote_text = re.split(r'\*\*Source GPS', quote_text)[0]
        quote_text = quote_text.rstrip('"\'' ).rstrip().strip()
        if not quote_text:
            i += 1
            continue
        results.append({
            "file": f.name,
            "line": i,
            "quote": quote_text,
            "video": gps[0] if gps else None,
            "position": gps[1] if gps else None,
        })
        i += 1

seen = {}
unique = []
for r in results:
    if not r["video"]:
        continue
    key = (r["video"], r["position"], r["quote"])
    if key in seen:
        continue
    seen[key] = True
    unique.append(r)

OUT.write_text(json.dumps({
    "total_citations": len(results),
    "unique_citations": len(unique),
    "quotes": unique,
}, indent=2), encoding="utf-8")

print(f"total citations: {len(results)}")
print(f"unique: {len(unique)}")
print(f"with video: {sum(1 for r in unique if r['video'])}")
from collections import Counter
print("per-file:", dict(Counter(r['file'] for r in results)))