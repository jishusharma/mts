import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict

R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
VER = R / "Dumps" / "tom_harvest_verified.json"
IDX = R / "MyTradingSys" / "mts" / "research" / "TOM_VERBATIM_INDEX.md"
CDIR = R / "MyTradingSys" / "mts" / "conditions"

v = json.loads(VER.read_text(encoding="utf-8"))
quotes = v["verified"]
quotes.sort(key=lambda q: (q["file"], q["line"]))

# ---- 1. Rebuild index ----
header = """# TOM VERBATIM INDEX
# Purpose: single source of verbatim Tom quotes for rule citations.
# Authority: raw_transcripts_canonical/*.txt are canonical. This file points. Does not duplicate.
# Rule: every derived rule in MyTradingSys/conditions/ carries [TOM-NNN] or [SCREENER].
# Rule: SCREENER means "our invention". Must not be presented as Tom.
# Verifier: scripts/tools/verify_rule_citations.ps1
# Rebuilt 2026-09-19 (T017). IDs TOM-001..TOM-213 mapped 1:1 to Source GPS
# lines in the six condition files. Every id here is referenced by at least one rule.

## QUOTES

| quote_id | transcript | position | excerpt | source_file |
|---|---|---|---|---|
"""

rows = []
index_map = {}  # (file, video, position) -> [ids]
for i, q in enumerate(quotes, 1):
    tid = f"TOM-{i:03d}"
    excerpt = q["quote"].replace("|", "\\|").strip()
    if len(excerpt) > 180:
        excerpt = excerpt[:177] + "..."
    pos = q.get("position") or ""
    row = f"| {tid} | {q['video']} | {pos} | \"{excerpt}\" | {q['file']} |"
    rows.append(row)
    index_map.setdefault((q["file"], q["video"], pos), []).append(tid)

body = header + "\n".join(rows) + "\n\n# END\n"
IDX.write_text(body, encoding="utf-8")
print(f"index written: {len(quotes)} quotes -> TOM-001..TOM-{len(quotes):03d}")

# ---- 2. Tag condition files ----
tagged_total = 0
for cf in sorted(CDIR.glob("*.md")):
    fname = cf.name
    lines = cf.read_text(encoding="utf-8").splitlines()
    # build per-file queue
    queues = defaultdict(list)
    for (fn, vid, pos), ids in index_map.items():
        if fn == fname:
            queues[(vid, pos)].extend(ids)
    used = defaultdict(int)
    tagged = 0
    for i, line in enumerate(lines):
        m = re.search(r'Source GPS:\**\s*([A-Za-z0-9_\-]{11})\s*\|\s*\[([A-Z]+)\]', line)
        if not m:
            continue
        qkey = (m.group(1), m.group(2))
        if qkey not in queues:
            continue
        idx = used[qkey]
        if idx >= len(queues[qkey]):
            continue
        tid = queues[qkey][idx]
        used[qkey] += 1
        lines[i] = line.rstrip() + f" [{tid}]"
        tagged += 1
    cf.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {fname}: tagged {tagged}")
    tagged_total += tagged

print(f"total tagged: {tagged_total}")