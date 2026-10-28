# Session registry

History only: no new files (the commit trailer and Result line are the record, SURFACE_POLICY.md section 4). Never delete a record.
Find the predecessor: newest file whose name contains the same `-<SURF>-<ROLE>`, e.g.
`ls MyTradingSys/system/sessions | grep -- '-CLI-SUP' | sort | tail -1`.

## Template
```
# <session ID>
surface: APP | CLI | CLD | DSA | COD
host: JIS-NB | JIS-NUC | DESKTOP-F7IU69N | cloud
account: A | B | free-pool | none
model: <model as reported by the surface>
role: SUP | BLD | ANA | EXT | MON | COO | WRK
branch: <branch commits go to, or none>
branch_alias: <harness-assigned name, or none>
predecessor: <session ID or none>
lanes: <qwen-nuc, dsaweb-nb, ask-nb, subagents used, or none>
started: <YYYY-MM-DD HH:MMZ>
ended: <YYYY-MM-DD HH:MMZ or open>
status: open | closed | handed-off
commits: <short hashes>
handoff: <receiver inbox + one line, or none>
```
