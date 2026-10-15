"""Apply RANKED_MALKAN.csv to the caption card and the transcript inventory (run once after score.py final)."""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score as S

ROOT = HERE.parents[2]
rows = list(csv.DictReader(open(HERE / "RANKED_MALKAN.csv", encoding="utf-8")))
by = {r["id"]: r for r in rows}
sel = [r for r in rows if r["include"] == "Y"]
sel_ids = [r["id"] for r in sel]
flat, pls = S.load_flat(), S.pl_map()
cl = (ROOT / "MyTradingSys/research/malkan_extract_2026-10-15/CHANNEL_LIST.md").read_text(encoding="utf-8")
listed = []
for i in re.findall(r"`?([A-Za-z0-9_-]{11})`?", cl):
    if i in flat and i not in listed:
        listed.append(i)
have = S.captioned()
dropped = []
for i in listed:
    if i in sel_ids or i in have:
        continue
    if i in by:
        sc, rk = by[i]["score"], f"rank {by[i]['rank']} of {len(rows)}"
    else:
        sc, rk = f"{S.score_one(flat[i], pls.get(i, []))[0]:.2f}", "flat score only, below the detail cut"
    dropped.append((i, sc, rk, flat[i]["title"]))

sel_txt = ", ".join(f"{r['id']} (rank {r['rank']}, {r['score']})" for r in sel)
card_p = ROOT / "MyTradingSys/system/tasks/malkan-captions-fetch-noauth.json"
raw = card_p.read_bytes()
card = json.loads(raw.decode("utf-8"))
card["title"] = (f"Malkan: fetch captions for the {len(sel)} ranked-top videos only (video_priority_2026-10-15), no cookies, spaced retries; "
                 "DONE when each is in raw_transcripts_canonical or has a NOT AVAILABLE line")
card["goal"] = (f"Get the Malkan captions that matter, anonymously, with spaced retries: only the {len(sel)} ids ranked include=Y in "
                "MyTradingSys/research/video_priority_2026-10-15/RANKED_MALKAN.csv (method: METHOD.md). The other shortlisted ids are NOT SELECTED "
                "(score in transcript_inventory_2026-10-09.md); do not fetch them.")
card["done_when"] = (f"each of the {len(sel)} selected ids ({', '.join(sel_ids)}) is in raw_transcripts_canonical/ or has a NOT AVAILABLE line with reason "
                     "in transcript_inventory_2026-10-09.md, on origin/fast-track")
card["steps"] = [
    "try ONE id first, highest rank first: python scripts/dev/fetch_captions_timed.py --analyst Malkan --out raw_transcripts_canonical <id> (also try the JIS-NB host if the NUC is rate-limited); Hindi videos --langs hi,en",
    "on success fetch the next selected id (RANKED_MALKAN.csv order), at least 60 s apart; on 429 STOP for today and record the attempt in the card note (retry once a day, 3 days max, then NOT AVAILABLE)",
    "fetch ONLY include=Y ids; never the NOT SELECTED ones, even if a fetch is working (re-rank with video_priority_2026-10-15/score.py first if a new video appears)",
    "update the Malkan selected-ids row in MyTradingSys/research/transcript_inventory_2026-10-09.md for each id (fetched / NOT AVAILABLE + reason)",
]
card["note"] = (card["note"] + " 2026-10-15 (video-priority session): the card is restricted to the ranked top. Selected (include=Y): " + sel_txt +
                f". Method and validation: research/video_priority_2026-10-15/METHOD.md. {len(dropped)} shortlisted ids are NOT SELECTED (inventory). "
                "Still no cookies, tokens or third-party caption sites; retry once a day for 3 days, one request at a time, 60 s apart.")
card["refs"] = sorted(set(card["refs"] + ["MyTradingSys/research/video_priority_2026-10-15/METHOD.md",
                                          "MyTradingSys/research/video_priority_2026-10-15/RANKED_MALKAN.csv"]))
card["scope_in"] = sorted(set(card["scope_in"] + ["MyTradingSys/research/video_priority_2026-10-15/"]))
out = json.dumps(card, indent=2, sort_keys=True, ensure_ascii=False) + ("\n" if raw.endswith(b"\n") else "")
card_p.write_bytes(out.encode("utf-8").replace(b"\r\n", b"\n"))

inv_p = ROOT / "MyTradingSys/research/transcript_inventory_2026-10-09.md"
inv = inv_p.read_text(encoding="utf-8")
new_rows = [
    "| Malkan | " + ", ".join(sel_ids) + f" | - | PENDING_CAPTIONS | SELECTED by video_priority_2026-10-15 (ranked top {len(sel)}; HTTP 429 still the blocker, anonymous, no cookies); retry once a day, 3 days max, then NOT AVAILABLE; order = RANKED_MALKAN.csv |",
    "| Malkan | other shortlisted ids (below) and the rest of the channel | - | NOT SELECTED | not in the ranked top; score and rank in the rows below; full pool scores in video_priority_2026-10-15/RANKED_MALKAN.csv; the other ~815 channel videos scored below the detail cut (flat score < 4.7) |",
]
for i, sc, rk, t in dropped:
    t = t.encode("ascii", "replace").decode().replace("|", "/")
    new_rows.append(f"| Malkan | {i} | - | NOT SELECTED | score {sc} ({rk}); {t[:70]} |")
lines = inv.split("\n")
keep = [l for l in lines if not (l.startswith("| Malkan | fgN6QBFY3Ss") or l.startswith("| Malkan | Hindi RSI/divergence picks"))]
idx = max(k for k, l in enumerate(keep) if l.startswith("| Malkan | dXxQOnK2jhQ"))
keep[idx + 1:idx + 1] = new_rows
inv_p.write_bytes("\n".join(keep).encode("utf-8").replace(b"\r\n", b"\n"))
print(len(sel), "selected;", len(dropped), "NOT SELECTED rows")
