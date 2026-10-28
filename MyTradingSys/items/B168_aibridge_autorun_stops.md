# B168 - AI Bridge auto-run stops between turns and is slow

Status: IN-FIX (filed 2026-10-10). Severity MED.
Source: BUGS.md row B168; Control Room inbox 5ejhc3ak0x4u11jxvg3s, ldkziormfnb5jzgtosjy, i258bxlg4o668ipiy40c.

## Verbatim ask

Auto-run must keep running between turns and must not be slow; the second bridge (NUC) is undocumented.

## State

2026-10-10: content.js stays armed after a block-less answer (runs reset, writes still behind their checkbox), quiet 4000->2000 ms, poll 700->250 ms, post-answer wait 1500->600 ms; backup content.js.pre_stayarmed; node --check ok. DSA_DELEGATION.md section Two DSA bridges: routing by data location (DSA-NB for 1m klines, DSA-NUC for 1h/1d + inventories), cheapest-first tiers. NOT done: reload the extension on both machines (operator), and the NB-vs-NUC interference is not reproduced (needs the NUC audit.jsonl).

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN/IN-FIX row has a matching items/ file. State copied from the BUGS.md row.
