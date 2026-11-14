# Test Gap: `scripts/dev/aibridge_verify.py` (`testgap-aibridge-verify-gemini3-1114`)

## 1. Existing Coverage Search
Command: `git grep -l aibridge_verify -- scripts MyTradingSys`
- No test file named for `aibridge_verify` (e.g. `test_aibridge_verify.py`) existed.
- Indirect/integration references in tests:
  - `MyTradingSys/tests/test_aibridge_install_fresh.py:33`: `v = _run(DEV / "aibridge_verify.py", dst, "--json", "--no-roundtrip")` (SOURCED)
  - `MyTradingSys/tests/test_aibridge_install_fresh.py:49`: `v = _run(DEV / "aibridge_verify.py", dst, "--json", "--no-roundtrip")` (SOURCED)
  - `scripts/aibridge/tests/e2e_bridge.py:168`: `res = aibridge_verify.check(str(installed_root))` (SOURCED)
  - `scripts/dev/test_nowin_calls.py:21`: lists `"aibridge_verify.py": 1` as a fingerprinted bridge file (SOURCED)

## 2. Pure Functions & Hand-Computed Cases (`scripts/dev/aibridge_verify.py`)
- `lf(b)` (`scripts/dev/aibridge_verify.py:42-43`): `return b.replace(b'\r\n', b'\n')` (SOURCED)
  - Normal: `b"a\r\nb\r\nc"` -> `b"a\nb\nc"` (OURS)
  - Empty: `b""` -> `b""` (OURS)
  - Lone CR/LF: `b"a\nb\rc"` -> `b"a\nb\rc"` (OURS)
- `mask_bg(b)` (`scripts/dev/aibridge_verify.py:62-67`): masks `TOKEN`, `AGENT_CWD`, `AGENT_URL` with `'X'` after `b.decode('utf-8', 'replace')` (SOURCED)
  - Normal: masks all 3 constants to `'X'` (OURS)
  - Empty: `b""` -> `b""` (OURS)
  - Malformed UTF-8 + unterminated quote: `\xff\xfe` -> `\xef\xbf\xbd\xef\xbf\xbd`, terminated `TOKEN` masked, unterminated `TOKEN` preserved (OURS)
- `ext_id_for_path(path)` (`scripts/dev/aibridge_verify.py:70-72`): `hashlib.sha256(os.path.normpath(path).replace('/', BS).encode('utf-16-le')).hexdigest()[:32]` mapped `0..f` -> `a..p` (SOURCED)
  - Normal: `"F:/AIBridge/extension"` and `"F:\\AIBridge\\extension\\"` -> `"kgighilgkdgkdghegpibjbjcidcmejkg"` (OURS)
  - Empty: `""` -> `"ahfndnnpfkdkicgobdkjcciioifdlmel"` (OURS)
- `check(root, roundtrip=True)` (`scripts/dev/aibridge_verify.py:82-96`):
  - Empty directory: returns 1 row `check="installed"`, `status="FAIL"` without network calls (OURS)
  - Malformed `src/config.json` (`"{not json"` with required stub files present): raises `json.JSONDecodeError` (OURS)

## 3. Verification
- Test file: `MyTradingSys/research/layer_lab/gemini_1114c/testgap-aibridge-verify/test_aibridge_verify.py`
- Passing run: `python -m pytest -v MyTradingSys/research/layer_lab/gemini_1114c/testgap-aibridge-verify/test_aibridge_verify.py` -> `5 passed in 0.26s` (OURS)
- Broken scratch copy mutation: replaced `return b.replace(b'\r\n', b'\n')` with `return b` in `lf(b)`; rerun failed `test_lf_normal_empty_and_lone_cr` (`1 failed, 4 passed in 0.44s`) with `AssertionError: assert b'a\r\nb\r\nc' == b'a\nb\nc'` (OURS)
