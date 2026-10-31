# KROWN_APP_PROBE: APP BLOCKED

Probe time: 2026-10-30T21:45Z (clock of the probing machine). Target: https://app.krowntrading.net/desk/cryptos/dashboard. Public only, no login, no account, no payment.

## Result: APP BLOCKED (nothing loaded)

| Test | Outcome (SOURCED, seen 2026-10-30T21:45Z) |
|---|---|
| Claude in Chrome, new MCP tab, navigate to the dashboard URL | Tab URL set, title stayed the bare URL; get_page_text and screenshot error: "Frame with ID 0 is showing error page" |
| First navigate attempt | Tab fell back to chrome://newtab; tools said "page navigated to a different domain" (security check), then retry gave the error page above |
| Console messages | none captured |
| DNS (nslookup) | app.krowntrading.net resolves to 198.54.117.242 |
| curl to https://app.krowntrading.net/ | "Failed to connect to app.krowntrading.net port 443 after 4013 ms: Could not connect to server" |

The browser and the script fetch fail the same way: the host resolves but port 443 does not accept connections from this machine/network. Cause is unknown (network block, site down, or geo/ISP filter); not inferred.

## Not recorded (page never loaded)
- Page text of visible panels: none
- Login wall: not reached
- Free signals (name, fields, symbols, timeframes): 0 seen
- Rule or setup definitions: none seen

## Tabs
User had no tabs open (only the empty MCP tab group). The tab used was closed after the probe.

## DECISION (OURS)
Record APP BLOCKED, do not use computer-use clicking on the browser, do not try proxies or other networks. Retry from another machine/network (e.g. NUC or phone data) as a separate card if the app still matters.
