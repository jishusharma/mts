# NUC handoff (from JIS-NB, 2026-10-11): Codex bridge + standby dispatcher

Paste into a JIS-NUC session (Sonnet, one task). Budget: this account has ~26% weekly left until Fri 2026-10-16: spend on steps 1-2 only.
1. `python scripts/dev/sync.py start`; read `MyTradingSys/system/CODEX_START.md`.
2. Codex: work tree `F:\MTS\mts-codex` (branch nuc/codex-first) exists. `git -C F:\MTS\mts-codex merge origin/fast-track`. In the Codex app: Add project = that folder, "Ask for approval", paste the block in CODEX_START.md.
   Per card: `python scripts/dev/codex_pack.py <card-id>` (CODEX_HOME=F:\codex_home set; pack lands in F:\codex_home\packs\). Pass the pack path to Codex.
   Take SONNET cards: `tasks.py next --lane SONNET`; Codex skips OPUS. Never add the live tree as a Codex project.
3. Dispatcher on NUC: do NOT enable a second primary. Follow `scripts/sched/relay_prompts/INSTALL.md`; create `mts-dispatcher-standby` only after card `relay-two-host-standby` ships `--standby-hours`. Until then no NUC scheduled tasks.
4. `sync.py ship`, `sync.py where` clean, stop.
Open for operator: share Control Room (EoHi2q...) with jishu.awgp@gmail.com (edit) so NUC can pin it.
