COUNTS: MATCH=5 DIFF=2 NOT_IN_DATA=1

# Audit Report: `scripts/dev/aibridge_install.py` Docstring Clauses vs Implementation Code

- **Card**: `gemini-blind-read-aibridge-install-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-12
- **Scope In**:
  - `scripts/dev/aibridge_install.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-aibridge-install-docstring-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read; read only, never run it.

---

## 1. Summary of Scan

Eight specific clauses from the header docstring of `scripts/dev/aibridge_install.py` (lines 1–7) were evaluated against the implementation in `scripts/dev/aibridge_install.py`:
- `--dry` flag behavior
- `--restart-agent` flag behavior
- `.pre_v07` backup mechanism
- What files it copies and what it prints / never prints
- Default root target and `--fresh` flag semantics
- Preservation of token, `AGENT_CWD`, and `config.json`
- Policy merging semantics (`policy.json` merged, not replaced)
- Host targeting scope (JIS-NB, JIS-NUC)

Summary counts:
- **MATCH (5)**: Clauses 1, 2, 3, 5, 6
- **DIFF (2)**: Clauses 4, 7
- **NOT_IN_DATA (1)**: Clause 8

---

## 2. Clause Verification Table

| # | Topic | Docstring Clause Quote & Line | Implementation Citation & Evidence | Status | Audit Findings & Verification |
|---|---|---|---|---|---|
| 1 | `--dry` flag | SOURCED (`scripts/dev/aibridge_install.py:2`): `"[--dry]"` and line 22: `"--dry', action='store_true', help='print what would be written'"` | SOURCED (`scripts/dev/aibridge_install.py:28`): `dry = '--dry' in sys.argv`; `scripts/dev/aibridge_install.py:47-49`: `if dry: print('  would write', p); return`; `scripts/dev/aibridge_install.py:57`: `if os.path.exists(p) and not os.path.exists(b) and not dry: shutil.copy2(p, b)`; `scripts/dev/aibridge_install.py:156`: `if not dry:` | MATCH | `--dry` bypasses writing files, bypasses `.pre_v07` backups, skips restarting agent, and prints `would write <p>`. Exact match between docstring and code. |
| 2 | `--restart-agent` flag | SOURCED (`scripts/dev/aibridge_install.py:2`): `"[--restart-agent]"` and lines 6-7: `"restart the agent (--restart-agent does it, or: powershell -File <root>\scripts\start-agent.ps1 after stopping the old one)."` | SOURCED (`scripts/dev/aibridge_install.py:23,29,158-164`): `_ap.add_argument('--restart-agent', ...); restart = '--restart-agent' in sys.argv; if not dry: if restart: ps = os.path.join(root, 'scripts', 'start-agent.ps1'); cfg = json.loads(read(os.path.join(root, 'src/config.json'))...); stop = ("$c = Get-NetTCPConnection -LocalPort %d -State Listen ... Stop-Process -Id $c.OwningProcess -Force..."); subprocess.call(['powershell.exe', '-NoProfile', '-Command', stop]); subprocess.call(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps])` | MATCH | Implements stopping the existing listening port process and launching `scripts\start-agent.ps1` via PowerShell when `--restart-agent` is passed and `--dry` is not set. |
| 3 | `.pre_v07` backup mechanism | SOURCED (`scripts/dev/aibridge_install.py:5`): `"Every overwritten file is first copied to <name>.pre_v07 (once)."` | SOURCED (`scripts/dev/aibridge_install.py:55-59`): `def backup(p): b = p + '.pre_v07'; if os.path.exists(p) and not os.path.exists(b) and not dry: shutil.copy2(p, b)`; called at `scripts/dev/aibridge_install.py:132,139,153` before writing payload files, task files, and `policy.json`. | MATCH | Only copies if target `p` exists and backup `b` does not exist (`not os.path.exists(b)`), fulfilling the "once" constraint and appending `.pre_v07`. |
| 4 | Copied files and console output ("never prints") | SOURCED (`scripts/dev/aibridge_install.py:1`): `"Install / update AIBridge to the payload in scripts/aibridge"` | SOURCED (`scripts/dev/aibridge_install.py:110-142,154-155`): Copies files in list `files` (`src/agent.ps1`, `src/checks.ps1`, `src/concurrency.ps1`, `src/lease.ps1`, `src/audit.ps1`, `extension/panel.css`, `extension/content.js`, `extension/loop.js`, `extension/manifest.json`, `extension/background.js`, `scripts/start-agent.ps1`, `scripts/run-task.ps1`, `docs/V07_CONTRACT.md`, `policy_patch.json`, `RELEASES.json`, tests) plus `tasks/*`. Line 134: `print('  ' + rel)`; line 141: `print('  tasks/' + tf)`; line 155: `print('  src/policy.json (merged)')`. However, it NEVER prints `src/config.json` contents or token values (lines 78-80 write token silently; line 97-100 only prints `token taken from src/config.json...` without showing token string). | DIFF | Discrepancy/Nuance: The docstring does not explicitly state what is copied vs not printed, but code explicitly prints every copied relative path (`  <rel>`) while strictly never printing sensitive token contents or config body, and never copies `src/config.json` during update (only created fresh). |
| 5 | Token, `AGENT_CWD`, and `config.json` preservation | SOURCED (`scripts/dev/aibridge_install.py:4-5`): `"Token-free: the machine's own TOKEN, AGENT_CWD and config.json are kept."` | SOURCED (`scripts/dev/aibridge_install.py:93-109`): `bg_old = read(os.path.join(root, 'extension/background.js'))`; extracts `tm = re.search(r"const TOKEN = '([0-9a-f]{16,})';", bg_old)`; falls back to `src/config.json` token if missing; extracts `cm = re.search(r"const AGENT_CWD = ('(?:[^'\\]|\\.)*');", bg_old)`; replaces `'__TOKEN__'` and `AGENT_CWD` in payload's `background.js` before writing. `files` list on line 110-124 does NOT contain `src/config.json`, keeping existing `src/config.json` untouched on updates. | MATCH | Existing token, `AGENT_CWD`, and `config.json` are retained and substituted back into the updated `extension/background.js`. |
| 6 | `policy.json` merged, not replaced | SOURCED (`scripts/dev/aibridge_install.py:5`): `"policy.json is MERGED, not replaced."` | SOURCED (`scripts/dev/aibridge_install.py:143-155`): `pol = json.loads(read(pp)...) if os.path.exists(pp) else {}`; `pol.update(POLICY_PATCH)`; adds `EXTRA_ROOTS` to `roots` array if not already present; writes merged dictionary back to `pp`. | MATCH | Existing policy entries are preserved while `POLICY_PATCH` keys and `EXTRA_ROOTS` are merged in, rather than replacing the file wholesale. |
| 7 | Default root and CLI arguments | SOURCED (`scripts/dev/aibridge_install.py:2`): `"Usage: python scripts/dev/aibridge_install.py [F:/AIBridge] [--dry] [--restart-agent] [--fresh [--origin=chrome-extension://<id>]]"` | SOURCED (`scripts/dev/aibridge_install.py:20-31`): `_ap.add_argument('root', nargs='?', default='F:/AIBridge')`; line 27: `args = [_ns.root] if _ns.root != 'F:/AIBridge' else []`; line 31: `root = (args[0] if args else 'F:/AIBridge').rstrip('/\\')`. | DIFF | Docstring lists `[F:/AIBridge]` as the positional example, but code accepts any path string as `root` (positional optional argument defaulting to `'F:/AIBridge'`). Furthermore, argument parsing mixes `argparse` namespace (`_ns.root`) with manual `sys.argv` inspection (`'--dry' in sys.argv`, `'--restart-agent' in sys.argv`, `'--fresh' in sys.argv`). |
| 8 | Host execution scope | SOURCED (`scripts/dev/aibridge_install.py:4`): `"Run on each host that has an AIBridge (JIS-NB, JIS-NUC)."` | SOURCED (`scripts/dev/aibridge_install.py:1-167`): No hostname or machine check exists anywhere in `scripts/dev/aibridge_install.py`. Host list `(JIS-NB, JIS-NUC)` is purely operational guidance in the docstring. | NOT_IN_DATA | The code contains no hostname validation or host restriction enforcing `(JIS-NB, JIS-NUC)`; it executes on whichever host invokes the script. |

---

## 3. Detailed File Copy and Print Analysis

In `scripts/dev/aibridge_install.py`:
1. **Copied/Written Files**:
   - `src/agent.ps1`
   - `src/checks.ps1`
   - `src/concurrency.ps1`
   - `src/lease.ps1`
   - `src/audit.ps1`
   - `extension/panel.css`
   - `extension/content.js`
   - `extension/loop.js`
   - `extension/manifest.json`
   - `extension/background.js` (with token/cwd patched)
   - `scripts/start-agent.ps1`
   - `scripts/run-task.ps1`
   - `docs/V07_CONTRACT.md`
   - `policy_patch.json`
   - `RELEASES.json`
   - `tests/loop.test.js`
   - `tests/handsfree.test.js`
   - `tests/start_trigger.test.js`
   - `tests/agent_live_selftest.py`
   - Every file under `scripts/aibridge/tasks/*`
   - `src/policy.json` (merged)
   - `src/config.json` (ONLY when `--fresh` is passed and `config.json` does not exist)
2. **Printed vs Never Printed**:
   - Printed: Each written file path is printed to stdout as `  <rel>`, `  tasks/<tf>`, or `  src/policy.json (merged)`. If `--dry` is passed, `  would write <p>` is printed.
   - Never Printed: Secret tokens (`token = secrets.token_hex(16)` or `tm.group(1)`), full configuration JSON, and internal script contents are never printed to stdout.
