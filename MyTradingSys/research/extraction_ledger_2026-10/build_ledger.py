"""Extraction ledger: one row per (video id, extract file) for everything extracted so far, plus GAPS.md.

Usage (repo root):  python MyTradingSys/research/extraction_ledger_2026-10/build_ledger.py [--root DIR] [--out DIR]

Inputs (all read-only):
  <root>/raw_transcripts_canonical/<id>_raw.txt | _hi_raw.txt | _asr_raw.txt   -> method captions | hindi_asr | whisper
  extract files under <root>/extracts and <root>/MyTradingSys/research (.md whose name/path says extract, and which carry
    `Source GPS: <id> | ...` quotes or CBP `evidence: "..."` lines); gemini_out / gemini_burn paths are labelled gemini
  <root>/MyTradingSys/research/video_priority_2026-10-15/RANKED_*.csv        -> ids seen + channel
  <root>/MyTradingSys/backtest/layers/**  (*.json params, *.md spec/catalog)  -> used_by = layer:file mentioning the id

Quote check = scripts/dev/verify_extract_quotes.py matcher (norm + first_missing), run against the transcripts under --root.
Hindi extracts (`- Language: hi`) = the check_hindi.py rule: every `- Hindi original:` line occurs in <id>_hi_raw.txt.
Earlier inventories are linked in GAPS.md, not overwritten.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import verify_extract_quotes as vq  # noqa: E402

QUOTE = vq.QUOTE
GPS = vq.GPS
CBP_EVIDENCE = vq.CBP_EVIDENCE
CBP_HEAD = vq.CBP_HEAD
HI = re.compile(r'^- Hindi original:\s*"(.+)"\s*$')
LANG = re.compile(r"^- Language:\s*(\w+)")
ID = re.compile(r"[A-Za-z0-9_-]{11}")
SUFFIX = {"_asr_raw.txt": ("whisper", "en"), "_hi_raw.txt": ("hindi_asr", "hi"), "_raw.txt": ("captions", "en")}
COLS = ["video_id", "channel", "language", "method", "transcript_file", "extract_file", "extract_source",
        "quotes", "quotes_verified", "used_by"]
SKIP_DIRS = {".git", "node_modules", "__pycache__", "_archive"}


def following(lines, i):
    """The two text lines after quote line i (a source tag, not a price series)."""
    return lines[slice(i + 1, i + 3)]


def norm_ws(s):
    return " ".join(re.sub(r"\[[^\]]*\]", " ", s).split())


def split_name(fname):
    for suf, (method, lang) in SUFFIX.items():  # longest suffixes first (dict order)
        if fname.endswith(suf):
            return fname[: -len(suf)], method, lang
    return None


def read_transcripts(tdir):
    out = {}
    for p in sorted(tdir.glob("*_raw.txt")):
        sp = split_name(p.name)
        if not sp:
            continue
        vid, method, lang = sp
        text = p.read_text(encoding="utf-8", errors="replace")
        head = text.split("# ---", 1)[0]
        am = re.search(r"^# Analyst:\s*(.+)$", head, re.M)
        lm = re.search(r"^Language:\s*(\w+)", text, re.M)
        out[vid] = {"file": p.name, "method": method, "language": (lm.group(1) if lm else lang),
                    "channel": am.group(1).strip().split(" (")[0] if am else ""}
    return out


def body_for(tdir, vid, trans, hindi):
    if hindi:
        p = tdir / f"{vid}_hi_raw.txt"
    else:
        p = tdir / (trans[vid]["file"] if vid in trans else f"{vid}_raw.txt")
    text = p.read_text(encoding="utf-8", errors="replace")
    return text.split("# ---", 1)[1] if "# ---" in text else text


def is_extract_path(rel, text):
    low = rel.lower()
    named = "extract" in low or "/gemini_out/" in low
    if not named:
        return False
    return bool(GPS.search(text) or re.search(r'^- Hindi original:', text, re.M) or any(CBP_EVIDENCE.match(l.strip()) for l in text.splitlines()))


def find_extracts(root):
    found = []
    for top in (root / "extracts", root / "MyTradingSys" / "research"):
        if not top.exists():
            continue
        for p in sorted(top.rglob("*.md")):
            if SKIP_DIRS & set(p.relative_to(root).parts):
                continue
            rel = p.relative_to(root).as_posix()
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if is_extract_path(rel, text):
                found.append((p, rel, text))
    return found


def check_extract(root, tdir, trans, text):
    """-> {vid: [n_quotes, n_bad]} ; vid '' collects quotes with no id."""
    lines = text.splitlines()
    hindi = (next((LANG.match(l).group(1) for l in lines if LANG.match(l)), "") == "hi")
    vm = next((re.match(r"^- Video ID:\s*(\S+)", l) for l in lines if re.match(r"^- Video ID:\s*(\S+)", l)), None)
    res, cache = {}, {}

    def rec(vid, bad):
        r = res.setdefault(vid, [0, 0])
        r[0] += 1
        r[1] += bad

    def nbody(vid):
        if vid not in cache:
            try:
                cache[vid] = vq.norm(vq.TIMESTAMP.sub(" ", body_for(tdir, vid, trans, False)))
            except OSError:
                cache[vid] = None
        return cache[vid]

    hbody = {}
    for i, line in enumerate(lines):
        s = line.strip()
        ev = CBP_EVIDENCE.match(s)
        if ev:
            head = CBP_HEAD.match(next((l for l in reversed(lines[:i]) if l.startswith("#")), ""))
            vid = head.group(1) if head else ""
            b = nbody(vid) if vid else None
            rec(vid, 1 if (b is None or vq.first_missing(ev.group(1), b) is not None) else 0)
            continue
        if hindi and HI.match(s):
            vid = vm.group(1) if vm else ""
            if vid not in hbody:
                try:
                    hbody[vid] = norm_ws(body_for(tdir, vid, trans, True))
                except OSError:
                    hbody[vid] = None
            rec(vid, 1 if (hbody[vid] is None or norm_ws(HI.match(s).group(1)) not in hbody[vid]) else 0)
            continue
        m = QUOTE.match(s)
        if not m or hindi:
            continue
        gps = next((GPS.search(l) for l in following(lines, i) if GPS.search(l)), None)
        if not gps:
            rec("", 1)
            continue
        vid, pos = gps.groups()
        b = nbody(vid)
        q = vq.norm(m.group(1))
        at = b.find(q) if b is not None and q else -1
        if at < 0:
            rec(vid, 1)
        else:
            third = ("BEGIN", "MIDDLE", "END")[min(2, 3 * at // max(1, len(b)))]
            rec(vid, 0 if third == pos else 1)
    return res, hindi, (vm.group(1) if vm else "")


def ids_for_extract(rel, text, known, quote_ids, hint):
    ids = {v for v in quote_ids if v}
    ids |= {m.group(1) for m in GPS.finditer(text)}
    if hint:
        ids.add(hint)
    for kid in known:  # a known id in the file name or its folder
        if kid in rel:
            ids.add(kid)
    return ids


def load_usage(root):
    ldir = root / "MyTradingSys" / "backtest" / "layers"
    files = []
    if ldir.exists():
        for p in sorted(ldir.rglob("*")):
            if p.is_file() and p.suffix in (".json", ".md") and not SKIP_DIRS & set(p.parts):
                rel = p.relative_to(ldir)
                files.append((rel.parts[0] if len(rel.parts) > 1 else "", p.name, p.read_text(encoding="utf-8", errors="replace")))
    return files


def used_by(vid, files):
    hits = sorted({f"{layer or '*'}:{name}" for layer, name, text in files if vid in text})
    return ";".join(hits)


def priority_ids(root):
    out = {}
    d = root / "MyTradingSys" / "research" / "video_priority_2026-10-15"
    for p in sorted(d.glob("RANKED_*.csv")) if d.exists() else []:
        with p.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("id"):
                    out[r["id"]] = r.get("channel", "")
    return out


def channel_from_path(rel):
    low = rel.lower()
    for k, v in (("malkan", "Malkan"), ("fabio", "Fabio"), ("tom", "Tom"), ("krown", "Krown"), ("kurisko", "Kurisko"),
                 ("cryptocred", "CryptoCred"), ("flowhorse", "Flowhorse"), ("cbp", "CBP")):
        if k in low:
            return v
    return ""


def build(root, out):
    tdir = root / "raw_transcripts_canonical"
    trans = read_transcripts(tdir)
    prio = priority_ids(root)
    usage = load_usage(root)
    rows, gaps = [], {"no_extract": [], "bad_quotes": [], "unused": [], "one_place": [], "extract_no_id": [],
                      "prio_no_transcript": []}
    ext_ids = {}
    for p, rel, text in find_extracts(root):
        res, hindi, hint = check_extract(root, tdir, trans, text)
        ids = ids_for_extract(rel, text, trans, res.keys(), hint)
        if not ids:
            gaps["extract_no_id"].append(rel)
            continue
        src = "gemini" if ("gemini" in rel.lower()) else "claude_or_manual"
        for vid in sorted(ids):
            n, bad = res.get(vid, [0, 0])
            if "" in res and len(ids) == 1:
                n, bad = n + res[""][0], bad + res[""][1]
            status = "NA" if n == 0 else ("FAIL" if bad else "PASS")
            ext_ids.setdefault(vid, []).append((rel, src, n, status))
    all_ids = sorted(set(trans) | set(ext_ids) | set(prio))
    for vid in all_ids:
        t = trans.get(vid)
        ub = used_by(vid, usage)
        ch = (t["channel"] if t else "") or prio.get(vid, "")
        exts = ext_ids.get(vid) or [("", "", 0, "")]
        for rel, src, n, status in exts:
            if not ch and rel:
                ch = channel_from_path(rel)
            rows.append({"video_id": vid, "channel": ch, "language": t["language"] if t else "",
                         "method": t["method"] if t else "", "transcript_file": t["file"] if t else "",
                         "extract_file": rel, "extract_source": src, "quotes": n if rel else "",
                         "quotes_verified": status, "used_by": ub or "none"})
        places = sum([bool(t), vid in ext_ids, vid in prio, bool(ub)])
        if t and vid not in ext_ids:
            gaps["no_extract"].append(vid)
        if not t and vid in prio:
            gaps["prio_no_transcript"].append(vid)
        for rel, src, n, status in ext_ids.get(vid, []):
            if status in ("FAIL", "NA"):
                gaps["bad_quotes"].append(f"{vid} {status} {rel}")
        if vid in ext_ids and not ub:
            gaps["unused"].append(vid)
        if places == 1:
            gaps["one_place"].append(vid)
    rows.sort(key=lambda r: (r["video_id"], r["extract_file"]))
    out.mkdir(parents=True, exist_ok=True)
    with (out / "EXTRACTION_LEDGER.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    write_gaps(out / "GAPS.md", gaps, rows, trans)
    return rows, gaps


def write_gaps(path, g, rows, trans):
    L = ["# Extraction gaps (generated by build_ledger.py; do not hand-edit)", "",
         f"Ledger rows: {len(rows)}; transcripts: {len(trans)}. Counts:", "",
         "| Gap | Count |", "|---|---|",
         f"| transcript but no extract | {len(g['no_extract'])} |",
         f"| extract with FAIL or NA quotes | {len(g['bad_quotes'])} |",
         f"| extracted but used by no layer | {len(g['unused'])} |",
         f"| id seen in only one place | {len(g['one_place'])} |",
         f"| priority-list id with no transcript | {len(g['prio_no_transcript'])} |",
         f"| extract file with no resolvable id | {len(g['extract_no_id'])} |", "",
         "Method notes: used_by is a text match of the id in layers params json and layer md files, so none means no",
         "layer file names the id (an extract may still feed a layer by rule text, not id). NA = extract file has no",
         "checkable quote for that id. Earlier inventories (linked, not replaced): "
         "MyTradingSys/research/transcript_inventory_2026-10-09/RESULT.md.", ""]
    names = [("no_extract", "Transcript but no extract"), ("bad_quotes", "Extract with FAIL / NA quotes"),
             ("unused", "Extracted, used by no layer"), ("one_place", "Id seen in only one place"),
             ("prio_no_transcript", "Priority id with no transcript"), ("extract_no_id", "Extract with no id")]
    for k, title in names:
        L += [f"## {title} ({len(g[k])})", ""] + [f"- {x}" for x in g[k]] + [""]
    path.write_text("\n".join(L), encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--out", default=str(HERE.parent))
    a = ap.parse_args(argv)
    rows, gaps = build(Path(a.root), Path(a.out))
    print(f"rows={len(rows)} " + " ".join(f"{k}={len(v)}" for k, v in gaps.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
