"""Synthetic quote audit; no real CBP rows, transcripts, network or store access."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("quote_verifier", ROOT / "scripts/dev/verify_extract_quotes.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="cbp-quote-audit-") as folder:
        root = Path(folder)
        (root / "raw_transcripts_canonical").mkdir()
        vid = "AAAAAAAAAAA"
        body = "[0:00] we do not recommend buying bitcoin today\n[0:01] these assets belong together\n"
        (root / "raw_transcripts_canonical" / f"{vid}_raw.txt").write_text(body, encoding="utf-8")
        v.ROOT = root
        cases = [
            ("exact_control", "we do not recommend buying bitcoin today", 0),
            ("altered_control", "we do not recommend selling bitcoin today", 1),
            ("empty_ellipsis", "...", 0),
            ("punctuation_only", "!!!", 0),
            ("partial_word", "long", 0),
            ("negation_removed_by_ellipsis", "we ... recommend buying bitcoin today", 0),
        ]
        for name, quote, expected_current in cases:
            path = root / "extract.md"
            path.write_text(f'### Fixture | 2026-01-01 | {vid} | Synthetic\nevidence: "{quote}"\n', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                bad = v.check(path)
            assert bad == expected_current, (name, bad, output.getvalue())
            results.append({"probe": name, "problems": bad, "output": output.getvalue().strip()})
        path.write_text("No evidence lines at all.\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = v.main([str(path)])
        assert exit_code == 0
        results.append({"probe": "zero_quotes", "exit_code": exit_code})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
