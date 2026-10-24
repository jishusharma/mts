# NUC harvest: bring overnight burn outputs onto trunk

Why: codex/agy runners on the NUC commit only to NUC-local branches (`gpt-q/<name>`, `gemini-q/<name>`); nothing pushes them. `git push` on the NUC hangs on a credential prompt, so never push there. Read and copy out only.

## Where
- Repo `F:\MTS\mts-codex-lab`; one worktree per job `F:\MTS\gq\<name>\`; log `F:\MTS\gq\<name>.log` (last line `EXIT 0 after Ns` = finished OK; `START` only = still running; `EXIT 3` = failed).
- Outputs: `MyTradingSys/research/gemini_burn_<date>/`, `MyTradingSys/research/gpt_burn_<date>/<name>/`, Gemini YouTube notes `extracts/gemini_out/<channel>/`.

## Steps (from your own worktree, `sync.py start nuc-harvest`)
1. Write a `.ps1` (an inline command is refused; NUC has PowerShell 5, no `-AsUTC`) and pipe it:
   `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps < script.ps1 2>/dev/null | grep -v '^\*\*'`
2. List: for each log tail check EXIT 0; `git -C <wt> diff-tree --no-commit-id --name-only -r HEAD` lists exactly what the runner committed. The research files can sit in an earlier commit than HEAD (a "cards: mark done" commit follows): use `git -C <wt> log --oneline -4` and `show --stat`.
3. Pack only those paths: `tar -cf F:\MTS\gq\harvest_pack.tar -C <wt> <file> ...` (only `MyTradingSys/research/*` and `extracts/gemini_out/*`; never the card json, caches, data, the worktree).
4. Pull: `scp` fails (the remote shell prints output). Use `[Convert]::ToBase64String([IO.File]::ReadAllBytes("F:\MTS\gq\harvest_pack.tar"))` in a .ps1, strip `\r\n`, decode in Python, `tarfile` extract with `python -I` (GNU tar reads `C:` as a host). Assert every member starts with an allowed prefix and has no `..`.
5. Gate before commit: `python scripts/dev/verify_extract_quotes.py <each extract.md>` exit 0 (if not, do not commit it and say why); grep for key/secret/password; no raw price files.
6. Commit, `sync.py ship --release <slug>`.

## Check before trusting
- Gemini notes: quotes only count if they pass `verify_extract_quotes.py`; "UNVERIFIED" notes (no captions) carry no quote marks. Gemini research reports cite sources it may have invented: spot-check one citation per file.
- GPT outputs are proposals: `fix.patch` / `patch.diff` / `.java` copies live under `research/gpt_burn_<date>/<name>/` and are never applied from here. A fix goes through a normal card with its own fail-first test.
- Renamed on harvest: a `test_*.py` under research/ is picked up by step 3xt (run_extra_tests.py) and a proposed test that fails on unpatched code breaks the ship gate; rename it `proposed_test_*.py`.
- A job whose NUC worktree shows uncommitted source changes (e.g. `gx4-statecode-races`) is harvested from the committed copies only.
- Numbers in reports are the runner's claim: re-run the stated command or recompute from FORMULAS.md before using them.
- Still running = log has only START; harvest it next time, do not copy partial output.
