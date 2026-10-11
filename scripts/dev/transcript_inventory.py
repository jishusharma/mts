"""Transcript inventory: raw transcripts vs extracts, with the quote gate run on every extract.

Usage (repo root):  python scripts/dev/transcript_inventory.py [--out research/transcript_inventory_2026-10-09.md]

T0 script. Reads raw_transcripts_canonical/*_raw.txt and every extract file under extracts/
(fresh, processed, v2, pending_raw; _staged is listed separately), runs
scripts/dev/verify_extract_quotes.py on each extract, and writes one markdown table per video id.

Definitions (see MyTradingSys/methodology/extraction.md and research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md):
  V2 re-extracted = an extract under extracts/v2/ exists AND the quote gate passes with >= 1 anchor.
  V1 only         = an older extract (extracts/fresh, extracts/processed) exists, no V2 extract.
  not yet         = no extract file at all.
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "raw_transcripts_canonical"
EXT = ROOT / "extracts"
GATE = ROOT / "scripts" / "dev" / "verify_extract_quotes.py"
ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
SCORE_RE = re.compile(r"\b(risk|stop|target|size)\b", re.I)

FABIO_IDS = set()
for p in (EXT / "processed" / "fabio_valentini").rglob("*"):
    m = re.match(r"(?:extract_)?([A-Za-z0-9_-]{11})", p.name)
    if m:
        FABIO_IDS.add(m.group(1))
for p in (EXT / "_staged_2026-09-27" / "raw").glob("fabervaale_*_raw.txt"):
    FABIO_IDS.add(p.name.split("_", 1)[1][:11])


def header(text, key):
    m = re.search(r"^# %s:\s*(.*)$" % key, text, re.M)
    return m.group(1).strip() if m else ""


def body_of(text):
    return text.split("# ---", 1)[1] if "# ---" in text else text


def classify(vid, text):
    """Return (trader, note). Tom = Tom Vorwald EN channel corpus (project convention)."""
    if header(text, "Analyst").lower() == "malkan" or "Vishal" in header(text, "Title"):
        return "Malkan", ""
    if vid in FABIO_IDS:
        return "Fabio", ""
    b = body_of(text)
    n_serge = len(re.findall(r"\bSerge\b", b))
    n_pat = len(re.findall(r"\bPatrick\b", b))
    wall = re.search(r"wall ?street|hedge|scalper", header(text, "Title"), re.I)
    if n_serge >= 3 or (n_serge >= 1 and wall):
        return "Tom channel (guest)", "guest scalper Serge Hoffmann named %dx" % n_serge
    if n_pat >= 3:
        return "Tom channel (guest)", "guest Patrick Nill named %dx" % n_pat
    return "Tom", ""


def extract_files():
    out = []
    for p in sorted(EXT.rglob("*")):
        if not p.is_file() or "_staged_2026-09-27" in p.parts:
            continue
        if "pending_raw" in p.parts or p.name == "CONSOLIDATED_RULES.md":
            continue
        if p.suffix not in (".md", ".txt"):
            continue
        m = re.search(r"(?:extract_)?([A-Za-z0-9_-]{11})(?:_|\.)", p.name)
        vid = m.group(1) if m else None
        if p.parent.name in ("recon",):
            kind = "recon"
        elif "v2" in p.parts:
            kind = "V2"
        elif "fresh" in p.parts:
            kind = "V1-fresh"
        elif "processed" in p.parts:
            kind = "V1-processed"
        else:
            kind = "other"
        out.append((vid, kind, p))
    return out


def gate(path):
    r = subprocess.run([sys.executable, str(GATE), str(path)], capture_output=True, text=True, cwd=ROOT,
                       encoding="utf-8", errors="replace")
    ok = bad = 0
    kinds = defaultdict(int)
    for line in r.stdout.splitlines():
        if line.startswith("OK "):
            ok += 1
        elif line.split(" ")[0] in ("MISSING", "POSITION", "NO-GPS", "NO-TRANSCRIPT"):
            bad += 1
            kinds[line.split(" ")[0]] += 1
    return ok, bad, r.returncode, dict(kinds)


FRAG = re.compile(r'"([^"\n]{25,})"')


def fragments(path, vid):
    """Supplementary (not the official gate): quoted fragments of >= 25 chars anywhere in the file,
    tested as normalised substrings of the raw transcript. Returns (verbatim, total)."""
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import verify_extract_quotes as g
    try:
        body = g.norm(g.transcript_body(vid))
    except OSError:
        return 0, 0
    text = path.read_text(encoding="utf-8", errors="replace")
    ok = tot = 0
    for m in FRAG.finditer(text):
        q = g.norm(m.group(1))
        if len(q.split()) < 5:
            continue
        tot += 1
        if q in body:
            ok += 1
    return ok, tot


def main():
    out_path = ROOT / "MyTradingSys" / "research" / "transcript_inventory_2026-10-09.md"
    if "--out" in sys.argv:
        out_path = ROOT / sys.argv[sys.argv.index("--out") + 1]
    raws = {}
    for p in sorted(RAW.glob("*_raw.txt")):
        vid = p.name[: -len("_raw.txt")]
        t = p.read_text(encoding="utf-8", errors="replace")
        b = body_of(t)
        words = len(b.split())
        score = len(SCORE_RE.findall(b)) * 1000.0 / max(1, words)
        trader, note = classify(vid, t)
        raws[vid] = dict(title=header(t, "Title")[:80].replace("|", "/"), trader=trader, note=note, words=words, score=score, path=p)
    exts = defaultdict(list)
    orphan = []
    for vid, kind, p in extract_files():
        res = gate(p)
        fr = fragments(p, vid) if vid in raws else (0, 0)
        rec = (kind, p.relative_to(ROOT).as_posix(), res, fr)
        if vid in raws:
            exts[vid].append(rec)
        else:
            orphan.append((vid, rec))

    def status(vid):
        recs = exts.get(vid, [])
        v2 = [r for r in recs if r[0] == "V2"]
        v1 = [r for r in recs if r[0].startswith("V1") or r[0] == "other"]
        if v2 and any(r[2][0] > 0 and r[2][1] == 0 for r in v2):
            return "V2"
        if v2:
            return "V2-gate-fail"
        if v1:
            return "V1-only"
        return "not-yet"

    def gate_str(vid):
        recs = [r for r in exts.get(vid, []) if r[0] != "recon"]
        if not recs:
            return "-"
        parts = []
        for kind, path, (ok, bad, rc, kinds), fr in recs:
            if ok + bad == 0:
                g = "no anchors"
            elif bad == 0:
                g = "PASS %d/%d" % (ok, ok + bad)
            else:
                g = "FAIL %d/%d (%s)" % (ok, ok + bad, ",".join("%s %d" % kv for kv in sorted(kinds.items())))
            if fr[1]:
                g += "; fragments %d/%d" % fr
            parts.append(g)
        return "<br>".join(parts)

    groups = defaultdict(list)
    for vid, r in raws.items():
        groups[r["trader"]].append(vid)

    L = []
    L.append("# Transcript inventory 2026-10-09")
    L.append("")
    L.append("Generated by `python scripts/dev/transcript_inventory.py` (T0). Counts are parsed from the files, not read from a truncated listing.")
    L.append("Gate = `scripts/dev/verify_extract_quotes.py` run on every extract file below (quotes verbatim + position third).")
    L.append("")
    L.append("Definitions: **V2 re-extracted** = extracts/v2/<id>_v2.md exists and the gate passes with at least 1 anchor (current method:")
    L.append("research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md + methodology/extraction.md + playbook Part J). **V1 only** = an older")
    L.append("tier/in-vivo-code extract (extracts/fresh, extracts/processed) exists. **not yet** = no extract.")
    L.append("Trader: Tom = Tom Vorwald EN channel corpus (project convention). 'Tom channel (guest)' = guest speaker named in the transcript; counted separately.")
    L.append("")
    L.append("## Totals")
    L.append("")
    L.append("| Trader | raw files | V2 re-extracted | V1 only | (of V1: gate PASS with anchors) | not yet |")
    L.append("|---|---|---|---|---|---|")
    tot = defaultdict(int)
    for tr in sorted(groups, key=lambda k: (k != "Tom", k)):
        vids = groups[tr]
        c = defaultdict(int)
        for v in vids:
            c[status(v)] += 1
        v1p = sum(1 for v in vids if status(v) == "V1-only" and any(r[2][0] > 0 and r[2][1] == 0 for r in exts[v] if r[0] != "recon"))
        L.append("| %s | %d | %d | %d | %d | %d |" % (tr, len(vids), c["V2"], c["V1-only"], v1p, c["not-yet"] + c["V2-gate-fail"]))
        tot["raw"] += len(vids)
        tot["V2"] += c["V2"]
        tot["V1"] += c["V1-only"]
        tot["not"] += c["not-yet"] + c["V2-gate-fail"]
    L.append("| **all** | %d | %d | %d |  | %d |" % (tot["raw"], tot["V2"], tot["V1"], tot["not"]))
    L.append("")
    allrecs = [r for v in exts.values() for r in v if r[0] != "recon"]
    n_ok = sum(1 for r in allrecs if r[2][0] > 0 and r[2][1] == 0)
    n_fail = sum(1 for r in allrecs if r[2][1] > 0)
    n_none = sum(1 for r in allrecs if r[2][0] + r[2][1] == 0)
    L.append("Extract files matched to a canonical raw transcript: %d (gate PASS with anchors: %d, gate FAIL: %d, no anchors in file: %d)." % (len(allrecs), n_ok, n_fail, n_none))
    L.append("")
    if orphan:
        L.append("### Extract files with no matching raw in raw_transcripts_canonical (gate cannot pass: NO-TRANSCRIPT)")
        L.append("")
        for vid, (kind, path, (ok, bad, rc, kinds), fr) in orphan:
            L.append("- %s `%s` (%s): gate ok=%d bad=%d" % (vid, path, kind, ok, bad))
        L.append("")

    L.append("## Next 10 candidates for the Tom core (never extracted, speaker = Tom)")
    L.append("")
    L.append("Rank = (count of the whole words risk, stop, target, size) per 1,000 words (same measure as EXTRACTION_ROUND2_2026-10-01.md),")
    L.append("Tom-speaker transcripts with no extract of any kind; ties broken by length. Guests and other traders are excluded (separate layers).")
    L.append("")
    L.append("| rank | video id | title | words | score/1000w |")
    L.append("|---|---|---|---|---|")
    cand = [v for v in groups.get("Tom", []) if status(v) == "not-yet"]
    cand.sort(key=lambda v: (-raws[v]["score"], -raws[v]["words"]))
    for i, v in enumerate(cand[:10], 1):
        L.append("| %d | %s | %s | %d | %.1f |" % (i, v, raws[v]["title"], raws[v]["words"], raws[v]["score"]))
    L.append("")
    L.append("Never-extracted Tom ids in total: %d. Also worth a V2 pass (V1 only, highest density):" % len(cand))
    L.append("")
    v1c = [v for v in groups.get("Tom", []) if status(v) == "V1-only"]
    v1c.sort(key=lambda v: -raws[v]["score"])
    for v in v1c[:8]:
        L.append("- %s %.1f/1000w, %d words: %s" % (v, raws[v]["score"], raws[v]["words"], raws[v]["title"]))
    L.append("")

    L.append("## Per video")
    L.append("")
    L.append("| trader | video id | raw file | extract file(s) | gate | status | title |")
    L.append("|---|---|---|---|---|---|---|")
    for tr in sorted(groups, key=lambda k: (k != "Tom", k)):
        for v in sorted(groups[tr]):
            r = raws[v]
            files = "<br>".join("%s: %s" % (k, p.split("/", 1)[1]) for k, p, _, _f in exts.get(v, []) if k != "recon") or "-"
            tr_s = r["trader"] + ((" (" + r["note"] + ")") if r["note"] else "")
            L.append("| %s | %s | raw_transcripts_canonical/%s_raw.txt | %s | %s | %s | %s |" % (
                tr_s, v, v, files, gate_str(v), status(v), r["title"]))
    L.append("")
    L.append("## Extracts that are not per-video raw matches")
    L.append("")
    L.append("- CryptoCred (5: BHwoN7VPrBE, inqHN8q57X4, XeQV2ECtZVQ, Yp0k8HD5xro, _ndAoizXy64) and Flow Horse (3: Oy2Z-FQ77NM, UcPp0gFI5M8, zMM9QgxfEFI) extracts exist under extracts/processed, but their raw transcripts are not in raw_transcripts_canonical (see the orphan list above).")
    L.append("- extracts/_staged_2026-09-27/ holds 13 Fabio and 22 Qriptal raw transcripts staged outside the canonical folder; not counted in the totals.")
    out_path.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out_path)
    print("totals:", dict(tot))


if __name__ == "__main__":
    main()
