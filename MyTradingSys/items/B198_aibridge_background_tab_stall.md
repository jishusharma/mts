# B198 - AIBridge hands-free stalls when tab is backgrounded

Status: OPEN. Opened 2026-10-22.
Owner: [FIXER: Claude] [LOGGER: DSA]
Source: Operator observation, DSA chat MTS-2026-10-22-0601Z (JIS-NB)

## What happened

Operator returned to the DeepSeek chat to find the AIBridge hands-free widget active ("27/50", "running #43"), but the latest # AIRUN block was sitting unrun. The "Run (auto)" button had not been clicked. The operator reports it "was perhaps clicked when I returned to this tab".

The block then ran, but not cleanly: previous replies showed blocks_seen=8 for 6 sent, cwd dropping to F:\AIBridge, and result outputs for commands never sent. This points to a stale, throttled message queue waking up on tab focus and executing in the wrong order/context.

## Why it breaks the contract

DSA_SESSION_PROMPT.md section 0.1: "# AIRUN blocks ... run by themselves and the result comes back". Hands-free is supposed to be independent of operator focus. If Chrome background throttling pauses the extension's timer/observer, autonomous execution stops and the batch logic breaks.

## Proposed fix

Extension must run its polling loop in a context that is not throttled by tab visibility (e.g., chrome.alarms, a service worker, or an offscreen document). If that is not possible, it must detect the background state and explicitly pause the queue with a clear UI warning, rather than letting it stall and later misfire.

## Evidence

- Screenshot 2026-10-22 14:26 local (08:56 UTC): Hands-free widget active, block unrun.
