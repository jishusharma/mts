"""Classify the channel video list (raw/videos.txt, raw/streams.txt, raw/pl/*.txt) -> VIDEO_LIST.csv + counts. Titles only; no content read."""
import csv, re, glob, collections, os
rd = lambda p: open(p, "rb").read().decode("utf8", "replace").splitlines()
pls = {}
names = dict(l.split("|", 1) for l in rd("raw/playlists.txt"))
for f in glob.glob("raw/pl/*.txt"):
    pid = os.path.basename(f)[:-4]
    for l in rd(f):
        i = l.split("|", 1)[0]; pls.setdefault(i, []).append(names.get(pid, pid))
vids = {}
for src in ("videos", "streams"):
    for l in rd(f"raw/{src}.txt"):
        p = l.split("|")
        if len(p) < 4: continue
        vids.setdefault(p[0], dict(id=p[0], dur=p[2], title="|".join(p[3:]), src=set()))["src"].add(src)
TEACH = re.compile(r"TA 101|Start HERE|Technical Analysis Trading Strateg|Psychology|Inside the Machine|Options 101", re.I)
def cls(v):
    t, pl = v["title"], pls.get(v["id"], [])
    if t in ("NA", "[Private video]", "[Deleted video]"): return "HIDDEN"
    if "TA 101 - Everything You Need To Know" in pl: return "TEACH_TA101"
    if any(TEACH.search(x) for x in pl): return "TEACH_OTHER"
    if re.search(r"Within \d+ (Days|Weeks)|of \d+ Times|Only Done|Signal|Setup|Target|Landing Zone|Held|Fired", t): return "CALL_EVENT_STUDY" if "streams" not in v["src"] or "videos" in v["src"] else "CALL_LIVE"
    if re.search(r"\bLive\b|LIVE", t) or "streams" in v["src"] and "videos" not in v["src"]: return "LIVE_STREAM"
    if "Weekly Q&A" in pl or "Q&A" in t: return "QA"
    if any("Alt" in x or "Simps" in x for x in pl): return "ALTS"
    if any("SPX" in x for x in pl): return "SPX_NDX"
    if re.search(r"lifetime|sale|course|Bible|Indicators", t, re.I): return "SALES"
    return "COMMENTARY_OTHER"
rows = []
for v in vids.values():
    rows.append([v["id"], v["dur"], "+".join(sorted(v["src"])), cls(v), ";".join(sorted(pls.get(v["id"], []))), v["title"]])
with open("VIDEO_LIST.csv", "w", encoding="utf8", newline="") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["video_id", "duration_s", "tab", "class", "playlists", "title"]); w.writerows(rows)
c = collections.Counter(r[3] for r in rows); print(len(rows), dict(c))
tot = collections.Counter(); 
for r in rows:
    try: tot[r[3]] += int(r[1])
    except: pass
print({k: round(v/3600) for k, v in tot.items()}, "hours")
