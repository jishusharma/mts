import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path

R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
HARV = R / "Dumps" / "tom_harvest.json"
CORP = R / "raw_transcripts_canonical"
OUT = R / "Dumps" / "tom_harvest_verified.json"

def norm(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

corpus_files = {}
for f in CORP.glob("*_raw.txt"):
    vid = f.name.replace("_raw.txt", "")
    corpus_files[vid] = norm(f.read_text(encoding="utf-8"))

h = json.loads(HARV.read_text(encoding="utf-8"))
verified = []
unverified = []

for q in h["quotes"]:
    vid = q["video"]
    qt = norm(q["quote"])
    if not qt or len(qt) < 20:
        unverified.append({**q, "reason": "quote too short"})
        continue
    if vid not in corpus_files:
        unverified.append({**q, "reason": f"corpus file for {vid} missing"})
        continue
    body = corpus_files[vid]
    # try full quote substring first
    if qt in body:
        verified.append({**q, "match": "full"})
        continue
    # try 40-char anchor from middle
    mid = len(qt) // 2
    anchor = qt[max(0, mid - 40): mid + 40].strip()
    if len(anchor) >= 20 and anchor in body:
        verified.append({**q, "match": "anchor"})
        continue
    # try first 40 chars
    head = qt[:40]
    if len(head) >= 20 and head in body:
        verified.append({**q, "match": "head"})
        continue
    unverified.append({**q, "reason": "no match in corpus"})

OUT.write_text(json.dumps({
    "verified_count": len(verified),
    "unverified_count": len(unverified),
    "verified": verified,
    "unverified": unverified,
}, indent=2), encoding="utf-8")

print(f"verified:   {len(verified)}")
print(f"unverified: {len(unverified)}")
print(f"written: {OUT}")

print()
print("Sample unverified (first 8):")
for u in unverified[:8]:
    qq = u["quote"][:90] if u["quote"] else ""
    print(f"  {u['video']} [{u['position']}] {u['reason']}: {qq}")