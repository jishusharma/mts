"""Anonymous metadata-only fetch for the video priority method (no cookies, no captions, no downloads).

Usage (repo root):
    python MyTradingSys/research/video_priority_2026-10-15/fetch_meta.py playlists   # channel playlists -> data/playlists.json
    python MyTradingSys/research/video_priority_2026-10-15/fetch_meta.py detail ID [ID ...]  # full metadata -> data/detail/<id>.json
Rate: one request per 5 s at most; on HTTP 429 wait 60 s and retry once per id, then record the failure.
"""
import json
import sys
import time
from pathlib import Path

import yt_dlp

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CHANNEL = "https://www.youtube.com/channel/UCKxWWqBQZYKTA01GkyQdMHA"
GAP = 5.0
KEEP = ("id", "title", "description", "duration", "upload_date", "view_count", "like_count", "chapters",
        "channel", "uploader", "tags", "categories", "language", "availability", "live_status", "playlist_count")


def ydl(flat):
    return yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True,
                             "extract_flat": "in_playlist" if flat else False, "ignoreerrors": False})


def playlists():
    DATA.mkdir(exist_ok=True)
    out = {}
    with ydl(True) as y:
        top = y.extract_info(CHANNEL + "/playlists", download=False)
        pls = [(e["id"], e.get("title")) for e in top["entries"] if e.get("id")]
        print(len(pls), "playlists")
        for pid, title in pls:
            time.sleep(GAP)
            try:
                info = y.extract_info("https://www.youtube.com/playlist?list=" + pid, download=False)
                out[pid] = {"title": title, "ids": [e["id"] for e in info["entries"] if e and e.get("id")]}
                print(pid, title, len(out[pid]["ids"]))
            except Exception as e:  # noqa: BLE001
                out[pid] = {"title": title, "ids": [], "error": str(e)[:200]}
                print("ERR", pid, str(e)[:120])
    (DATA / "playlists.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


def detail(ids):
    d = DATA / "detail"
    d.mkdir(parents=True, exist_ok=True)
    with ydl(False) as y:
        for vid in ids:
            dest = d / (vid + ".json")
            if dest.exists():
                continue
            for attempt in (1, 2):
                time.sleep(GAP)
                try:
                    info = y.extract_info("https://www.youtube.com/watch?v=" + vid, download=False, process=False)
                    rec = {k: info.get(k) for k in KEEP}
                    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
                    print("ok", vid, rec.get("upload_date"), rec.get("view_count"))
                    break
                except Exception as e:  # noqa: BLE001
                    msg = str(e)
                    print("ERR", vid, attempt, msg[:140])
                    if attempt == 1 and "429" in msg:
                        time.sleep(60)
                        continue
                    (d / (vid + ".err")).write_text(msg[:500], encoding="utf-8", newline="\n")
                    break


if __name__ == "__main__":
    if sys.argv[1] == "playlists":
        playlists()
    else:
        detail(sys.argv[2:])
