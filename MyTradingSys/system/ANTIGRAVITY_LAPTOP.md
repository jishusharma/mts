# ANTIGRAVITY ON THE LENOVO LAPTOP (DESKTOP-F7IU69N), written 2026-10-25 by the Doctor on JIS-NB

Goal: use the laptop Antigravity Gemini quota (about 32% of the week left, resets in about 6 h) before the reset, on read-only research and review work, without touching the live loop this laptop runs.
Setup facts and rules: `GEMINI_START.md` ("Laptop" section) and `GEMINI.md`. The Claude session on this laptop runs `LENOVO_NEXT_SESSION.md` separately. The two never share a card: the claim is the lock.

## Before the first prompt (operator, once)
- Check the account: the Antigravity profile icon must show the Google AI Pro login recorded for this laptop in `GEMINI_START.md`. If it shows another account, sign out and in again first.
- File > Open Folder: `C:\Users\e-ngineers\IdeaProjects\mts-gemini` only.
- Model: Gemini 3.8 Flash for cards A and B. Gemini 4 Argon for card C, when its weekly pool shows more than 25% (`View Usage` in the model menu).
- Approval: leave terminal commands on ask-first, or allow them with a deny list: `taskkill`, `Stop-Process`, `mts_run.py`, `git reset`, `git rebase`, `git stash`, `git push --force`, `Remove-Item -Recurse`, `rm -rf`.

## Hard limits (this laptop runs the testnet live loop)
- Never stop, start or restart any process. Never touch `.mts_live`, HALT files, `mts_run.py` or `C:\MTS\mts-lenovo`. Never deploy.
- Never read `.secrets/`, `.env` or keys. Testnet only. The repo is PUBLIC: no account, order or runtime data in any file.
- Never rebase, reset, force-push or stash. Never self-stamp ACCEPT (GEMINI_START rule 8).
- Removing, demoting or parking a layer is out of scope (operator NO, 2026-10-25). Collect facts only.

## Loop (repeat until the Gemini weekly pool is under 3% or it resets)
0. `python scripts/dev/sync.py start gemini-agy-1025`, then `python scripts/dev/sync.py where`.
1. Between cards: `python scripts/dev/mts_signal.py read --hours 1`. A note from `jis-nb` (the desktop guide) outranks this list.
2. Take the next item below that nobody has claimed: `python scripts/dev/sync.py claim "<item>"`.
3. Write the result, commit with a `Result:` line, `python scripts/dev/sync.py ship --release <slug>`, then `python scripts/dev/mts_signal.py send "agy: <item> shipped <sha>" --to jis-nb`.

## Items, in order
A. Ready `[GEMINI]` cards: `python scripts/dev/tasks.py list --lane CODEX --state ready`. Today: `gemini-ccu-dxntdn3jfTg-check`, then `yt-gem-fabio-fetch-2`. YouTube rule: fetch the real captions first. Every quote must pass `python scripts/dev/verify_extract_quotes.py <extract.md>` with exit 0 before it ships. Never "watch the video" and write quotes from memory.
B. Cross-vendor review of today's Claude ships: `f581b9d20`, `8971d69e6`, `c540fc3d8`, `242fbf7a1`, `7d01c1d85`, and every `lenovo: <card> shipped <sha>` the Claude session reports. For each sha: does the diff do what its `Result:` line says? Cite `file:line`. Mark each finding OK, FIX or UNVERIFIED. Write to `MyTradingSys/research/gemini_burn_2026-10-25/claude_ships_review.md`.
C. Layer fact sheets for the coming layer review (card `layer-review-after-simulator`). One file per layer family in `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/<family>.md`. Start from `python scripts/dev/lab_query.py layers` and `LAYERS.md`. For each layer, from repo files only, each fact with `file:line`:
   - origin: which analyst or indicator, with a quoted source;
   - its parameters, each labelled SOURCED or OURS;
   - every backtest run on it: report path, fee-net or not, in-sample or out-of-sample, n trades;
   - known bugs, fabrications or assumptions in those runs (`lab_query.py rulings <family>`);
   - which other layers it was meant to confirm, or be confirmed by (confluence).
   Write NOT_IN_DATA where the repo has no answer. Give no verdict on keeping or dropping a layer.

## End
Ship, run `sync.py where` (it must show clean), then send one line: `python scripts/dev/mts_signal.py send "agy: done, items <list>, Gemini week <pct>%" --to jis-nb`.
