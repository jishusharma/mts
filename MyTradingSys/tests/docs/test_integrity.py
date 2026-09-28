# test_integrity.py - 5 doc/project integrity checks
# Run: python -m pytest MyTradingSys/tests/docs -v
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MTS = REPO / "MyTradingSys"


def _live_files(extensions):
    for p in MTS.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensions:
            continue
        rel = str(p.relative_to(MTS))
        if "archive" in rel or "monitor_" in rel or "__pycache__" in rel or ".pytest_cache" in rel:
            continue
        if p.name.endswith((".old", ".new", ".bak")):
            continue
        yield p


def test_1_no_old_files_outside_archive():
    offenders = []
    for p in MTS.rglob("*.old"):
        rel = str(p.relative_to(MTS))
        if not rel.startswith("archive"):
            offenders.append(rel)
    assert not offenders, f".old files outside archive: {offenders}"


def test_2_no_forbidden_refs():
    patterns = [
        r"\bgit init\b",
        r"\bgit status\b",
        r"\bgit add\b",
        r"\bgit commit\b",
        r"\bgit diff\b",
        r"\bgit log\b",
        r"\bgit checkout\b",
        r"\bversion control\b",
    ]
    regexes = [re.compile(p) for p in patterns]
    hits = []
    for p in _live_files({".md", ".py", ".ps1", ".java", ".txt"}):
        # research/ holds runbooks and session receipts whose deploy steps ARE git
        # commands (FT-1/FT-2 promotion is git-based since 2026-09-27); the rule
        # still applies to the live doc set (system/, items/, runtime/, ...).
        if p.relative_to(MTS).parts[0] == "research":
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for r in regexes:
                if r.search(line):
                    hits.append(f"{p.relative_to(MTS)}:{i}: {line.strip()[:80]}")
                    break
    assert not hits, "Forbidden refs found:\n" + "\n".join(hits)


def test_3_version_consistency():
    version_re = re.compile(r"v4\.\d+\.\d+(?:-p\d+)?")
    files = [
        MTS / "system" / "00_START_HERE.md",
        MTS / "system" / "02a_CURRENT_STATUS.md",
        MTS / "system" / "03_FILE_INDEX.md",
        MTS / "runtime" / "compiled_engine.md",
        MTS / "system" / "COMPILED_DECISIONS.md",
    ]
    versions = {}
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = version_re.search(text)
        if m:
            versions[f.name] = m.group(0)
    unique = set(versions.values())
    assert len(unique) <= 1, f"Version drift: {versions}"


def test_4_file_index_size_claim():
    idx = MTS / "system" / "03_FILE_INDEX.md"
    assert idx.exists()
    text = idx.read_text(encoding="utf-8")
    m = re.search(r"# SIZE:\s*~?([\d.]+)KB", text)
    assert m, "SIZE header not found"
    claimed = float(m.group(1))
    actual = idx.stat().st_size / 1024.0
    diff = abs(claimed - actual)
    assert diff <= 1.0, f"SIZE claim {claimed}KB vs actual {actual:.1f}KB (diff {diff:.1f})"


def test_5_no_stray_cleanup_candidates():
    """Fail only on .old/.bak outside archive and stray '=' file.
    .new files are in-flight work by parallel sessions - reported, not failed."""
    bad = []
    for p in MTS.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(MTS))
        if "archive" in rel:
            continue
        if p.suffix in (".old", ".bak"):
            bad.append(f"stray {p.suffix}: {rel}")
    weird = REPO / "="
    if weird.exists():
        bad.append("stray '=' file at project root")
    assert not bad, f"Stray cleanup candidates: {bad}"
