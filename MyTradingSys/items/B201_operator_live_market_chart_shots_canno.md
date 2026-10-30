# B201 - Operator live-market chart shots cannot be closed cheaply: `shot.py done` refuses a chart until `shot.py read 

Filed: 2026-10-26
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B201 | 2026-10-26 | OPEN | HIGH | Operator live-market chart shots cannot be closed cheaply: `shot.py done` refuses a chart until `shot.py read --extract` has run, and `read` wants a TEMPLATE.md file (Prior line, claim rows MATCH/MISMATCH/NOT_IN_DATA with a data-check file). In live mode the operator posts a chart every few minutes and wants a bias read, not 15 claim tables, so 15 classified shots sat unclosed for hours and the intake notice kept firing. Candidate fix: a `read --live` form (one line per shot: class + bias + ladder ref, no claim rows) or let `done --outcome note:` close a chart that is already logged in a live_reads READ.md. | shot.py done REFUSED twice on 10-26 (outcome prefix, then 'chart that has not been read'); shot ids 43cec1ee0a19 c1ddfcef535f d31c5690e8c0 43fc5ddec27b 7a8737e4c81b df6257dd397a 8dc124f61332 1f3d02f3e0aa e74b902ed53e 34bad00c5501 4056ec02fa78 c9ba9cd2ca1a a3330d10c427 dbbaf63b656e 13c9d9d2cd6e | |
