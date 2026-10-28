"""Video priority scoring (method in METHOD.md). Every weight below is OURS (judgement, not the trader's).

Usage (repo root):
    python MyTradingSys/research/video_priority_2026-10-15/score.py prelim   # flat-listing score -> data/candidates.txt
    python MyTradingSys/research/video_priority_2026-10-15/score.py final    # full score from data/detail/*.json -> RANKED_MALKAN.csv
Inputs: data/malkan_flat.jsonl (title, views, duration), data/playlists.json, data/detail/<id>.json (description, date, chapters).
"""
import csv
import json
import math
import re
import statistics
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ROOT = HERE.parents[2]
TODAY = date(2026, 10, 15)

# ---- OURS weights -------------------------------------------------------------------------------------------
W_NAMED, W_CORE, CAP_CORE = 5.0, 3.0, 8.0            # W_NAMED: setups the operator named (5-star, 7-star, RSI 40/60); W_CORE: method families (GFS, divergence/PRD/NRD, range shift, 3X3)
W_GEN, CAP_GEN = 1.0, 3.0              # generic rule words in the title (setup, strategy, rules, entry, stop, target, exit)
W_RSI = 1.0                            # the title says RSI
DESC_FACTOR = 0.5                      # description and chapter text count half
W_HINDI = 1.0                          # Hindi / Hinglish tie-break: Hindi is thin in the corpus (operator asked for it)
W_SERIES_NUM = 3.0                     # title starts with "N." inside the 3X3 Swing Trading series
W_PLAYLIST = {"RSI Mastery Series": 3.0, "Downtrend Trading Secrets": 1.5, "Find The Bottom": 1.5,
              "Tuesday Technical Talk": 1.0, "Binge Series - Top Down Approach": 1.0, "Golden Ratio Trader": 0.5}
P_NONTEACH_PL = -3.0                   # member of a testimonial / mindset / interview playlist
W_XREF, CAP_XREF = 1.0, 2.0            # other pool videos' descriptions/titles point to this id
W_VIEWS, CAP_VIEWS = 1.5, 3.0          # per decade of age-adjusted views over the channel median, capped
AGE_EXP = 0.5                          # views are divided by age^0.5 (partial age adjustment)
W_LEN_TEACH, W_LEN_LONG = 1.0, 0.5     # 7-60 min teaching length; 60+ min long form
W_CHAPTERS = 0.5                       # >= 3 chapters
P_MARKET_UPDATE = -4.0                 # weekly market update / market view
P_STOCKTIP = -3.0                      # stocks-to-watch / index target / sector call
P_OPTIONS = -2.0                       # options-only content (out of scope for the BTC layer)
P_SHORT_FLOOR = 240                    # below this many seconds: hard exclude (short)
# --------------------------------------------------------------------------------------------------------------

NAMED = [
    r"\b[57][ -]?(star|स्टार)(\b|-)|\bfive star\b|\bseven star\b|पांच स्टार|सात स्टार",
    r"\b40\W{0,3}60\b|\bsixty\b",
]
CORE = [
    r"grandfather|father[- ]?son|\bgfs\b|ग्रैंडफादर",
    r"diverg|\bprd\b|\bnrd\b|डायवर्ज|डाइवर्ज",
    r"range shift|loud move|monster move|\b3x3\b|3 ?x ?3",
]
GENERIC = [
    r"set ?-?up|सेटअप|सेट अप",
    r"strateg|रणनीति|स्ट्रेटेजी|स्ट्रैटेजी|स्ट्रेटजी|स्ट्रैटजी",
    r"\brules?\b|नियम|niyam",
    r"\bentry|\bentries|एंट्री|\bentr(y|ies)\b|kaise (pakde|kare)",
    r"stop[- ]?loss|\bstop\b|स्टॉप",
    r"\btargets?\b|टार्गेट|टारगेट",
    r"\bexit|एग्जिट",
]
RSI_RX = re.compile(r"\brsi\b|आरएसआई", re.I)
HINDI_RX = re.compile(r"[ऀ-ॿ]|\b(ka|ki|ke|kaise|kya|karo|karein|nahi|koi|mein|se|ye|sabse|jabardast|zabardast|sikhe|seekhe|samjhe|pakde|batayega)\b", re.I)
HARD_EXCLUDE = re.compile(r"\blive\b|livestream|live stream|q ?& ?a\b|q&a|ask me|testimonial|journey|success stor|motivation|mindset|"
                          r"life.?s downturn|money habits|teenager|tribute|\bjumpstart\b|how i (made|lost)|from .{0,30} to .{0,30}(trader|mindset)|"
                          r"experience|तैयार|daily (market )?update|aaj ka|today.s market|market today|intraday (live|call)", re.I)
MARKET_UPDATE = re.compile(r"market update|market view|weekly market|market outlook|trading plan for|nifty (view|outlook)|market trend", re.I)
STOCKTIP = re.compile(r"\bscan(ner|s)?\b|screener|स्कैनर|stocks? to watch|\bbanknifty target|nifty target|target nifty|breakout stocks|ये सारे stocks|top stocks|"
                      r"sector (rotation|breakout|selection)|new sector|auto sector|banking sector|in nifty|nifty &|एनएसई", re.I)
OPTIONS = re.compile(r"options? (simplified|strateg|binge)|option trading|expiry|ऑप्शन|options\b", re.I)
ID_RX = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})")

# Translations of Devanagari / Hinglish titles in the ranked set (machine-made by me; original kept in the CSV beside it).
TRANSLATE = {
    "RSI का सबसे Powerful Strategy": "RSI's most powerful strategy",
    "Swing Trading की सबसे जबरदस्त Strategy": "Swing trading's most tremendous strategy",
    "RSI + इंट्राडे ट्रेडिंग": "RSI + intraday trading",
    "RSI + Bollinger Bands ज़बरदस्त Strategy": "RSI + Bollinger Bands tremendous strategy",
    "RSI का संपूर्ण ज्ञान": "Complete knowledge of RSI",
    "GFS का Free Scanner": "GFS free scanner",
    "RSI-पहला 5 स्टार-ट्रेड": "RSI - the first 5-star trade",
    "RSI का Magic": "RSI's magic",
    "RSI Divergence Trade करना सीखे": "Learn to trade RSI divergence",
    "(7 STAR) PERFECT REVERSAL पैटर्न": "(7 STAR) perfect reversal pattern",
    "RSI का कमाल": "RSI's wonder (GFS special)",
    "RSI Divergence करें के प्रकार": "Types of RSI divergence (Class A/B/C)",
    "Swing Trading की जबरदस्त Strategy": "Swing trading's tremendous strategy",
    "Equinox Effect + GFS का जादू": "Equinox effect + GFS magic",
    "Market Structure कैसे Analyse करें?": "How to analyse market structure? (RSI, volume, sector comparison)",
    "इतनी Simple Strategy जो कोई भी कर सकता है": "A strategy so simple anyone can do it",
    "Nifty & Banknifty में GFS का कमाल": "GFS's wonder in Nifty and Banknifty",
    "क्या GFS BankNifty को ऊपर ले जाएगा ?": "Will GFS take BankNifty up?",
    "System Trading बंद करो": "Stop system trading",
    "Volatility Divergence क्या है": "What is volatility divergence",
    "ये सारे Stocks मैं Breakout है": "All these stocks are in breakout",
    "5. RSI Ki Ye Strategy Koi Nahi Batayega": "5. Nobody will tell you this RSI strategy",
    "11. Bollinger Bands Ka Father-Son Strategy": "11. Bollinger Bands' Father-Son strategy",
    "RSI Se Trend Kaise Samjhe?": "How to read the trend with RSI?",
    "RSI Se Entry Kaise Pakde?": "How to catch entries with RSI?",
    "Simple RSI Se Option Trading": "Option trading with simple RSI",
    "Bollinger Bands Ka Complete Trading Guide": "Bollinger Bands complete trading guide",
}


def pl_map():
    p = DATA / "playlists.json"
    m = {}
    if p.exists():
        for pid, rec in json.loads(p.read_text(encoding="utf-8")).items():
            for i in rec["ids"]:
                m.setdefault(i, []).append(rec["title"])
    return m


def nrx(rx, text):
    return sum(1 for r in rx if re.search(r, text, re.I))


def text_signal(text, factor=1.0):
    core = min(CAP_CORE, W_NAMED * nrx(NAMED, text) + W_CORE * nrx(CORE, text))
    gen = min(CAP_GEN, W_GEN * nrx(GENERIC, text))
    rsi = W_RSI if RSI_RX.search(text) else 0.0
    return factor * (core + gen + rsi), core > 0


def translate(title):
    base = re.split(r"\s*[|I]\s+(?=[A-Z])|\s+\|\s+", title)[0].strip()
    for k, v in TRANSLATE.items():
        if title.startswith(k) or base.startswith(k):
            return v
    return ""


def score_one(r, pls, detail=None, xref=0, age_ref=None, med_views=8800):
    t = r["title"]
    sig, parts = 0.0, []
    s, has_core = text_signal(t)
    sig += s
    if s:
        parts.append(f"title{s:+.1f}")
    if HINDI_RX.search(t):
        sig += W_HINDI
        parts.append(f"hindi{W_HINDI:+.1f}")
    if re.match(r"\s*\d{1,2}\.\s", t) and re.search(r"3 ?x ?3", t, re.I):
        sig += W_SERIES_NUM
        parts.append(f"series{W_SERIES_NUM:+.1f}")
    for p in pls:
        w = max([v for k, v in W_PLAYLIST.items() if p.startswith(k)] or [0])
        if w:
            sig += w
            parts.append(f"pl:{p[:12]}{w:+.1f}")
    nonteach = [p for p in pls if p in NONTEACH]
    if nonteach and not has_core:
        sig += P_NONTEACH_PL
        parts.append(f"nonteachpl{P_NONTEACH_PL:+.1f}")
    dur = r.get("duration") or 0
    if 420 <= dur <= 3600:
        sig += W_LEN_TEACH
        parts.append(f"len{W_LEN_TEACH:+.1f}")
    elif dur > 3600:
        sig += W_LEN_LONG
        parts.append(f"long{W_LEN_LONG:+.1f}")
    views = r.get("view_count") or 0
    if detail and detail.get("upload_date"):
        ud = datetime.strptime(detail["upload_date"], "%Y%m%d").date()
        age = max(0.5, (TODAY - ud).days / 365.25)
        ratio = (views / med_views) / ((age / age_ref) ** AGE_EXP)
    else:
        ratio = views / med_views
    v = max(0.0, min(CAP_VIEWS, W_VIEWS * math.log10(max(ratio, 1e-9)))) if ratio > 1 else 0.0
    sig += v
    parts.append(f"views{v:+.1f}")
    if detail:
        dtext = (detail.get("description") or "") + " " + " ".join(c.get("title", "") for c in (detail.get("chapters") or []))
        ds, _ = text_signal(dtext, DESC_FACTOR)
        if ds:
            sig += ds
            parts.append(f"desc{ds:+.1f}")
        if len(detail.get("chapters") or []) >= 3:
            sig += W_CHAPTERS
            parts.append(f"chap{W_CHAPTERS:+.1f}")
    if xref:
        x = min(CAP_XREF, W_XREF * xref)
        sig += x
        parts.append(f"xref{x:+.1f}")
    dtxt = t + " " + ((detail or {}).get("description") or "")[:600]
    flags = []
    if MARKET_UPDATE.search(t):
        sig += P_MARKET_UPDATE
        parts.append(f"mktupd{P_MARKET_UPDATE:+.1f}")
    if STOCKTIP.search(t):
        sig += P_STOCKTIP
        parts.append(f"stocktip{P_STOCKTIP:+.1f}")
    if OPTIONS.search(t) and not re.search(r"rsi", t, re.I):
        sig += P_OPTIONS
        parts.append(f"options{P_OPTIONS:+.1f}")
    hard = None
    if dur and dur < P_SHORT_FLOOR:
        hard = "short"
    elif HARD_EXCLUDE.search(t) or (detail and (detail.get("live_status") in ("was_live", "is_live"))):
        hard = "nonteaching/live"
    return sig, parts, hard


NONTEACH = {"Level Up To Win", "LevelUp to Win Series", "Pro Trader Talks | Season 3", "PRO Trader Talks | SEASON 2", "PRO Trader Talks",
            "Yuva Gurukool", "Wealth & Beyond Show", "Trading Inner Circle", "Build Your Brand", "High Performance", "TraderinMe",
            "Anybody Can Trade", "Upgrade Challenge", "2021 Finish Your Year Strong",
            "Identity Transformation Stories", "Mindset & Manifestation Experiences", "From Trading Losses to a More Disciplined Approach",
            "First Profitable Month or Quarter Stories", "RSI Strategy Learning Experiences", "Women Trader Success Stories",
            "Tier-2/Tier-3 Cities Success Stories", "50+ Success Stories", "Student & Under-25 Success Stories",
            "Professional & Salaried Success Stories", "Homemaker Success Stories"}


def load_flat():
    return {d["id"]: d for d in (json.loads(l) for l in open(DATA / "malkan_flat.jsonl", encoding="utf-8"))}


def captioned():
    canon = ROOT / "raw_transcripts_canonical"
    return {m.group(1) for f in canon.glob("*_raw.txt") if (m := re.match(r"(.{11})_(?:hi_)?raw\.txt$", f.name))}


def prelim():
    flat, pls = load_flat(), pl_map()
    scored = []
    for i, r in flat.items():
        s, parts, hard = score_one(r, pls.get(i, []))
        if not hard:
            scored.append((s, i))
    scored.sort(reverse=True)
    ids = [i for _, i in scored[:60]]
    for must in ("A-CQiV_UFB4", "W1HrDl70Lhk", "Wvq1TZh8aF0", "fgN6QBFY3Ss", "kVIvcn7T44o", "FHEoMmD6xKM", "TYB7GJODt-k", "WBByyLBp8-c"):
        if must not in ids:
            ids.append(must)
    (DATA / "candidates.txt").write_text("\n".join(ids) + "\n", encoding="utf-8", newline="\n")
    print(len(ids), "candidates; prelim cut score", scored[59][0] if len(scored) > 59 else None)


def compute():
    flat, pls = load_flat(), pl_map()
    details = {}
    for f in (DATA / "detail").glob("*.json"):
        details[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    ext = {"W1HrDl70Lhk"}  # not on the Malkansview channel (Trader Insights); metadata from its detail file
    rows = {}
    for i, d in details.items():
        base = flat.get(i) or {"id": i, "title": d["title"], "view_count": d.get("view_count"), "duration": d.get("duration")}
        if i in ext:
            base = {"id": i, "title": d["title"], "view_count": d.get("view_count"), "duration": d.get("duration")}
        rows[i] = base
    ages = [(TODAY - datetime.strptime(d["upload_date"], "%Y%m%d").date()).days / 365.25 for d in details.values() if d.get("upload_date")]
    age_ref = statistics.median(ages)
    med_views = statistics.median([r.get("view_count") or 0 for r in flat.values()])
    # cross references: ids mentioned in other pool videos' descriptions
    xref = {i: 0 for i in rows}
    for i, d in details.items():
        for m in set(ID_RX.findall(d.get("description") or "")):
            if m in xref and m != i:
                xref[m] += 1
    have = captioned()
    out = []
    for i, r in rows.items():
        s, parts, hard = score_one(r, pls.get(i, []), details.get(i), xref[i], age_ref, med_views)
        out.append({"id": i, "title": r["title"], "english_title": translate(r["title"]) or (r["title"] if not HINDI_RX.search(r["title"]) else ""),
                    "score": round(s, 2), "signals": " ".join(parts) + (f" HARD:{hard}" if hard else ""),
                    "hard": hard, "views": r.get("view_count"), "dur_min": round((r.get("duration") or 0) / 60),
                    "upload": details[i].get("upload_date") or "", "lang_guess": "hi" if HINDI_RX.search(r["title"]) else "en",
                    "have_captions": "Y" if i in have else "N", "playlists": ";".join(pls.get(i, []))})
    out.sort(key=lambda x: (x["hard"] is not None, -x["score"]))
    for rank, o in enumerate(out, 1):
        o["rank"] = rank
    return out, flat, age_ref, med_views


FAMILIES = {  # coverage guarantee: the best uncaptioned video of each operator-named rule family is always selected
    "5-star": r"\b5[ -]?(star|स्टार)|five star",
    "7-star": r"\b7[ -]?(star|स्टार)|seven star",
    "40/60+GFS": r"\b40\W{0,3}60\b|grandfather|father[- ]?son|\bgfs\b",
    "divergence": r"diverg|\bprd\b|\bnrd\b|डायवर्ज|डाइवर्ज",
    "range-shift": r"range shift",
}


def final():
    out, flat, age_ref, med_views = compute()
    BLOCKED = {"fgN6QBFY3Ss", "kVIvcn7T44o", "FHEoMmD6xKM", "TYB7GJODt-k", "WBByyLBp8-c"}
    todo = [o for o in out if not o["hard"] and o["have_captions"] == "N" and o["id"] in flat]
    chosen, fam_pick = [], {}
    for fam, rx in FAMILIES.items():
        for o in todo:
            if re.search(rx, o["title"], re.I) and o["id"] not in chosen:
                chosen.append(o["id"])
                fam_pick[o["id"]] = fam
                break
    for o in todo:
        if len(chosen) >= 10:
            break
        if o["id"] not in chosen:
            chosen.append(o["id"])
    cut = min(o["score"] for o in todo if o["id"] in chosen)
    chosen = set(chosen)
    for o in todo[10:]:
        if o["id"] in BLOCKED and o["score"] >= cut:
            chosen.add(o["id"])
    for o in out:
        o["include"] = "Y" if o["id"] in chosen else "N"
        if o["id"] in fam_pick:
            o["signals"] += " COVERAGE:" + fam_pick[o["id"]]
    cols = ["rank", "id", "title", "english_title", "score", "signals", "include", "have_captions", "lang_guess", "views", "dur_min", "upload", "playlists"]
    with open(HERE / "RANKED_MALKAN.csv", "w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print("age_ref", round(age_ref, 2), "median views", med_views, "pool", len(out), "selected", sorted(chosen))
    for o in out[:25]:
        print(o["rank"], o["id"], o["score"], o["include"], o["have_captions"], o["title"][:60])
    for k in ("A-CQiV_UFB4", "W1HrDl70Lhk", "Wvq1TZh8aF0"):
        print("KNOWN", k, [o["rank"] for o in out if o["id"] == k], "of", len(out))


if __name__ == "__main__":
    {"prelim": prelim, "final": final}[sys.argv[1]]()
