# test_integrity.py - doc/project integrity checks (test_6: no bannered docs in system/; test_7: size caps)
# Run: python -m pytest MyTradingSys/tests/docs -v
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
MTS = REPO / "MyTradingSys"
INDEX_CEILING_KB = 100
# Bytes. Files read at every session boot or on every pickup: a cap stops them growing back (token cost per session).
SIZE_CAPS = {
    "CLAUDE.md": 6144,
    "MyTradingSys/system/SURFACE_POLICY.md": 4096,
    "MyTradingSys/system/OPERATOR_INBOX.md": 30720,
    "MyTradingSys/system/RELAY.md": 6656,
}
BANNER_RE = re.compile(r"\b(SUPERSEDED|HISTORICAL|STALE)\b")


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
        # OPERATOR_INBOX.md is the operator's words verbatim (CONTROL_ROOM.md step 3): pasted logs may name git commands.
        if p.name == "OPERATOR_INBOX.md":
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
    """The SIZE header is not a hand-kept number (B087b): a claim edited to fit a check inverts the check.
    The header must say it is computed (no NNKB figure), and the measured size must stay under the read-budget ceiling."""
    idx = MTS / "system" / "03_FILE_INDEX.md"
    assert idx.exists()
    text = idx.read_text(encoding="utf-8")
    m = re.search(r"^# SIZE:(.*)$", text, re.M)
    assert m, "SIZE header not found"
    assert not re.search(r"\d\s*KB", m.group(1), re.I), f"SIZE header carries a hand-kept figure: {m.group(1).strip()}"
    assert "computed" in m.group(1), "SIZE header must read 'computed'"
    actual = idx.stat().st_size / 1024.0
    assert actual <= INDEX_CEILING_KB, f"03_FILE_INDEX.md is {actual:.1f}KB, ceiling {INDEX_CEILING_KB}KB: split or archive rows"


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


def test_6_no_banner_docs_in_system():
    """A system/ doc that opens with a SUPERSEDED / HISTORICAL / STALE banner is dead weight in every glob, grep and
    accidental Read. Move it with git mv to MyTradingSys/archive/<topic>_<date>/ (archive/ is skipped by _live_files)
    instead of leaving it bannered."""
    hits = []
    for p in sorted((MTS / "system").glob("*.md")):
        head = p.read_text(encoding="utf-8", errors="ignore").splitlines()[:5]
        for i, line in enumerate(head, 1):
            if BANNER_RE.search(line):
                hits.append(f"{p.relative_to(MTS)}:{i}: {line.strip()[:80]}")
                break
    assert not hits, "Bannered docs in system/ (git mv them to MyTradingSys/archive/<topic>_<date>/):\n" + "\n".join(hits)


@pytest.mark.parametrize("rel", sorted(SIZE_CAPS))
def test_7_size_cap(rel):
    """Boot and pickup files stay small. Over the cap: trim the file (CLAUDE.md, SURFACE_POLICY.md, RELAY.md) or rotate
    it (OPERATOR_INBOX.md: CONTROL_ROOM.md step 3) instead of raising the number."""
    p = REPO / rel
    assert p.exists(), f"{rel} is missing"
    size = p.stat().st_size
    assert size <= SIZE_CAPS[rel], f"{rel} is {size} B, cap {SIZE_CAPS[rel]} B"
