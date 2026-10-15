"""Order the pending Krown caption ids (the operator chose them, so nothing is cut; this only sets the fetch order). Weights are OURS."""
import csv
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score as S

HERE = Path(__file__).resolve().parent
TA101 = {"hNfjyrJEytI", "fMRvOt26xcA", "LB3DRYxnA0A", "_JoJbu_Ug-A"}  # MANIFEST.csv PENDING_CAPTIONS rows of the operator's TA 101 playlist
QUEUE_PRIO = {"UHY740h3e-Y": 2.0, "SOaAP9vBgM4": 1.0}  # options/research/KROWN_FREE_VS_PAID.md s6 transcript queue (priority 1, 2)
W_PLAYLIST_KROWN, W_STEP, CAP_STEP, W_LEN, W_VIEWS_K, VIEWS_BASE = 2.0, 1.0, 2.0, 1.0, 1.5, 5000
P_INTERVIEW, P_OPTIONS_K, W_CH = -3.0, -1.0, 0.5
STEP_RX = r"step|sequence|checklist|engine|essentials?|exact|fix|rules?|order"
rows = []
for f in sorted((HERE / "data" / "detail_krown").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    i, t, desc, dur = d["id"], d["title"], d.get("description") or "", d.get("duration") or 0
    sig, parts = 0.0, []
    s, _ = S.text_signal(t)
    ds, _ = S.text_signal(desc[:1500], S.DESC_FACTOR)
    st = min(CAP_STEP, W_STEP * len(re.findall(STEP_RX, t + " " + desc[:600], re.I)))
    for name, v in (("title", s), ("desc", ds), ("steps", st)):
        if v:
            sig += v
            parts.append(f"{name}{v:+.1f}")
    if i in TA101:
        sig += W_PLAYLIST_KROWN
        parts.append(f"ta101{W_PLAYLIST_KROWN:+.1f}")
    if i in QUEUE_PRIO:
        sig += QUEUE_PRIO[i]
        parts.append(f"queue{QUEUE_PRIO[i]:+.1f}")
    if 420 <= dur <= 3600:
        sig += W_LEN
        parts.append(f"len{W_LEN:+.1f}")
    age = max(0.5, (date(2026, 10, 15) - datetime.strptime(d["upload_date"], "%Y%m%d").date()).days / 365.25)
    ratio = (d["view_count"] / VIEWS_BASE) / (age / 2.9) ** S.AGE_EXP
    v = max(0.0, min(S.CAP_VIEWS, W_VIEWS_K * math.log10(ratio))) if ratio > 1 else 0.0
    sig += v
    parts.append(f"views{v:+.1f}")
    if len(d.get("chapters") or []) >= 3:
        sig += W_CH
        parts.append(f"chap{W_CH:+.1f}")
    note = ""
    if re.search(r"interview|krown.s crypto cave|and charlie", t + desc[:200], re.I):
        sig += P_INTERVIEW
        parts.append(f"interview{P_INTERVIEW:+.1f}")
    if re.search(r"option", t, re.I):
        sig += P_OPTIONS_K
        parts.append(f"options{P_OPTIONS_K:+.1f}")
    if dur < S.P_SHORT_FLOOR:
        note = f"SHORT ({dur}s): cheap to fetch, little rule content; last"
        sig -= 100  # sorts below every teaching-length video, regardless of its other signals
    elif dur < 420:
        note = f"short teaching clip ({dur}s)"
    rows.append({"id": i, "title": t, "english_title": t, "score": round(sig, 2), "signals": " ".join(parts), "include": "Y", "duration_s": dur,
                 "upload": d["upload_date"], "views": d["view_count"], "channel": d["channel"], "note": note})
rows.sort(key=lambda r: -r["score"])
for n, r in enumerate(rows, 1):
    r["order"] = n
    if r["score"] < -50:
        r["score"] = round(r["score"] + 100, 2)
        r["signals"] += " SHORT-LAST"
cols = ["order", "id", "title", "english_title", "score", "signals", "include", "duration_s", "upload", "views", "channel", "note"]
with open(HERE / "RANKED_KROWN.csv", "w", encoding="utf-8", newline="\n") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["order"], r["id"], r["score"], r["duration_s"], r["title"][:55], "|", r["signals"])
