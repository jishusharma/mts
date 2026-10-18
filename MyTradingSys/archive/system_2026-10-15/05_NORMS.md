# FILE: 05_NORMS.md
# READ ORDER: 8 of 8
# PURPOSE: Folder conventions, naming rules, archival rules
# LAST UPDATED: 2026-09-09
# SIZE: ~3KB
# NEXT FILE: (none — end of system/ chain)
# PREVIOUS FILE: 04_PER_JSON_GUIDE.md
# ---

# NORMS — File & Folder Conventions
# Scope: All files in C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\

---

## 1. FOLDER STRUCTURE

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| system/ | AI session orchestration (handoff, prompt, state, map, quickref) | sys_AI only |
| methodology/ | Research protocols, domain theory, reflection logs | sys_AI only |
| mts/conditions/ | Tom trading rules (state, zones, setups, proof, risk) | sys_AI only |
| mts/cards/ | Trading card specs, samples, templates | sys_AI only |
| mts/visual/ | Visual validation checklists | sys_AI only |
| mts/tests/ | Engine validation test suites and test run results | sys_AI only |
| mts/archive/ | Superseded or historical files | sys_AI only |
| mts/integration/ | DEPRECATED — integration files corrupted, content merged into 01_AI_BEHAVIOR.md Section 14 | sys_AI only |
| mts/research/ | Research findings, validation reports, cross-session artifacts | sys_AI only |
| mts/runtime/ | Canonical decision engine and optimization specs | sys_AI only |
| runtime_data/ | JSON schemas, DSA tasks, screener samples | sys_AI only |
| extracts/fresh/ | FRESH transcript extractions (50 videos) | sys_AI only |
| mts/extracts/ | Cross-trader extract files | sys_AI only |
| _scratch/ | Session checkpoints, transient artifacts | sys_AI only |

## 2. FILE NAMING

- Use snake_case: `market_state_rules.md`, not `MarketStateRules.md`
- Use descriptive names: `risk_protocol.md`, not `file5.md`
- No spaces in filenames. Hyphens OK for compound descriptors.
- Versioning: Append `_vN.N` before `.md` for staged versions (e.g., `sys_ai_prompt_v2.1.md`)

## 3. HEADER FORMAT

Every .md file MUST start with:

```
# TITLE — Context
# Date: YYYY-MM-DD
# Purpose: One-line description
# Status: FRESH / COMPLETE / ARCHIVED / DEPRECATED
# Canonical path: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\<folder>/
```

## 4. EDITING RULES

- Edit files directly in C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\. Use local Windows paths.
- NEVER use /mnt/agents/temp/ for project files. Temp is for session uploads ONLY.
- Use PowerShell for file ops. Use Python or bash.
- Check CRLF before edit_file. Use sed/Python if \r\n detected.
- NEVER use emoji. ASCII markers only: [OK] [WARN] [BLOCKED] [COMPLETE].
- After multi-line write_file, ALWAYS verify line count (wc -l). If 0 or 1, newlines were stripped — use shell heredoc instead.
- Every session that modifies files MUST update 03_FILE_INDEX.md and 02a_CURRENT_STATUS.md.

## 5. ARCHIVAL

- Move superseded files to mts/archive/ or _scratch/
- Do not delete. Preserve history.
- Update 03_FILE_INDEX.md when moving.
- Log move in 02b_DECISIONS_LOG.md.

# END
