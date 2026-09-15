# CODEBASE DUMP SCRIPT SPEC
# Date: 2026-08-08
# Purpose: Define what the PowerShell dump script should produce.
#   → Jishu runs this before each DSA session to generate the codebase dump.
#   → DSA reads the dump, not the live filesystem.
#
# GOAL: One markdown file with all source code, ready for DSA consumption.

---

## OUTPUT FILE

**Name:** `binance_code_dump.md`
**Location:** `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\`
**Format:** Markdown

---

## INCLUDE PATTERN

```powershell
# Include these:
- pom.xml
- src/main/java/datafeed/*.java
- prompts/*.md
- scripts/*.ps1

# Exclude these:
- data/                    # Generated JSON snapshots
- target/                  # Maven build artifacts
- .idea/                   # IDE config
- *.class                  # Compiled bytecode
- *.jar                    # Packaged artifacts
```

---

## FILE FORMAT

Each included file becomes a markdown code block with a header:

```markdown
// ============================================
// FILE: src/main/java/datafeed/Main.java
// SIZE: 2.0 KB
// ============================================

```java
[full file content here]
```
```

---

## USAGE FLOW

```
Jishu opens PowerShell
→ Runs: .\scripts\Dump_BinanceDataFeed.ps1
→ Output: binance_code_dump.md
→ Jishu copies content
→ Pastes into DSA chat at session start
→ DSA auto-audits against prompt principles
```

---

# END OF DUMP SPEC
