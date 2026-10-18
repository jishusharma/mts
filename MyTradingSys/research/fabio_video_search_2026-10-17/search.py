"""Metadata-only yt-dlp search for Fabio Valentini trade-recap videos. No downloads, no captions."""
import json, subprocess, sys, csv
QUERIES = ["Fabio Valentini live trade recap", "Fabio Valentini NQ session", "Fabio Valentini order flow trade breakdown",
           "Fabio Valentini ES futures trade", "Fabio Valentini volume profile live trading", "Fabio Valentini Robbins world cup trades"]
seen = {}
for q in QUERIES:
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", f"ytsearch15:{q}"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        print("ERR", q, r.stderr[-300:]); continue
    for e in json.loads(r.stdout).get("entries", []):
        seen.setdefault(e["id"], dict(id=e["id"], title=e.get("title"), channel=e.get("channel") or e.get("uploader"), duration=e.get("duration"), query=q))
with open("MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "title", "channel", "duration", "query"], lineterminator="\n"); w.writeheader(); w.writerows(seen.values())
print(len(seen))
