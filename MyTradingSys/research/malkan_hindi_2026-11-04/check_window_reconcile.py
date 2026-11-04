"""Structure check for WINDOW_RECONCILE_1104.md (card malkan-window-12-18-vs-hindi). It checks form and sources, never which window is right."""
import glob, json, pathlib, re, sys

DOC = "MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md"
IDS = ["GbXnw_tNMtw", "Wvq1TZh8aF0", "cQ-y1oULkBw", "kVIvcn7T44o", "TrZQ4Xat_sQ", "TO3pLafk7Us"]
DEVANAGARI = "[\u0900-\u097f ]+"


def problems(t, raw):
    p = []
    p += [f"video id missing: {i}" for i in IDS if i not in t]
    rows = [l for l in t.splitlines() if l.startswith("|")]
    if len(rows) < 8:
        p.append("table has fewer than 8 rows")
    for th in ("10", "12", "15", "18"):
        hit = [l for l in rows if re.search(rf"(?<![0-9.]){th}(?![0-9.])", l) and re.search("SOURCED|OURS|NOT_IN_DATA", l)]
        if not hit:
            p.append(f"no verdict row for threshold {th}")
        p += [f"threshold {th}: SOURCED row without a video id" for l in hit if "SOURCED" in l and not any(i in l for i in IDS)]
    hq = [" ".join(q.split()) for q in re.findall(DEVANAGARI, t) if len(q.split()) >= 3]
    if not hq:
        p.append("no Hindi quote in the table")
    p += [f"Hindi quote not in raw_transcripts_canonical: {q[:40]}" for q in hq if q not in raw]
    m = re.search("```json(.*?)```", t, re.S)
    try:
        j = json.loads(m.group(1))
        keys = {"min_bars", "max_bars"}
        if not (keys <= set(j) and keys <= set(j.get("reverse", {}))):
            p.append("json block needs min_bars/max_bars for regular and for reverse")
    except (AttributeError, ValueError, TypeError):
        p.append("no valid fenced json block")
    return p


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    t = pathlib.Path(DOC).read_text(encoding="utf-8")
    raw = " ".join(" ".join(pathlib.Path(f).read_text(encoding="utf-8").split()) for f in glob.glob("raw_transcripts_canonical/*_raw.txt"))
    bad = problems(t, raw)
    print("\n".join(bad) or "OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
