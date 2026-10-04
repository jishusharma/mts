# B129 - test_b074_rule_order.py harness fragility

Status: CLOSED
Opened: 2026-10-04
Test authored: MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper
Verified: MTS-2026-10-04-0916Z-DSA-COO

## Defect

MyTradingSys/tests/test_b074_rule_order.py extracts a function block from
scripts/core/start-trading-day.ps1 and runs it under pwsh. The extraction
depends on line layout. On the pre-change file (commit 8604bc0), the joined
function text parses badly and pwsh returns ParserError on $rc. Both tests
fail, but they fail at parse time, not at the assertion.

## Why this matters

The fail-before proof asks: does this test fail on old code and pass on new
code? Yes, it does. The stronger question: does the test fail because the old
code produces the wrong result? Today it fails because the extraction
assembles invalid PowerShell. A future whitespace edit to start-trading-day.ps1,
or a rename inside the extracted region, can re-break the extraction and mask
a real regression.

## Evidence

- Fail-before run 2026-10-04 against 8604bc0: 2 failed, both ParserError.
- Pass-after run 2026-10-04 against d9b295f: 2 passed.

## Fix shape (undecided)

- Anchor the extraction on a named function boundary instead of raw text.
- Or parse the function once, hold the AST, invoke the AST.
- Or move the wrapper logic into a sourceable module and dot-source it.

Whichever path, the test must fail on old code by assertion, not parser error.

Receipt 2026-10-04: AST extraction (Parser.ParseFile, FunctionDefinitionAst by name; wrapper = statements from $umsCmd to $s) + B074_PS1 path override; current file 2 passed, 8604bc0 2 failed by assertion (WAIT_PROOF vs WAIT_RR; 'exit=0' missing), no ParserError.
