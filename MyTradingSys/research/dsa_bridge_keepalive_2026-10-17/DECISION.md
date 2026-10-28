# DSA bridge keep-alive: decision (2026-10-17)

## Finding (code read, scripts/aibridge/extension)
v0.7.0 had NO audio emitter in the repo or in F:\AIBridge\extension (identical to the repo apart from the token). The
background-tab defence was: service-worker port tick every 500 ms (background.js), a Web Lock (content.js), plain timers.
Holes: (1) the port is re-opened by a page `setTimeout`, which a hidden tab throttles to 1/s then 1/min, so a
worker restart left the page deaf for up to a minute; (2) nothing detects or shows that ticks stopped (idle was silent);
(3) a discarded tab (Memory Saver) loses the content script, and nothing opted the tab out; (4) every tick source went
through the worker, so one failure killed all pacing.

## Chosen (least hacky, all inside the existing extension)
1. Second heartbeat from a dedicated Worker (blob) inside the page: worker timers are not subject to the main thread's
   background / intensive timer throttling [1][2]. Independent of the service worker.
2. Reconnect the SW port at once on disconnect (connect() wakes the worker [3]), exponential backoff 1..15 s, plus a
   stale-link check driven by either tick source (L.linkState / reconnectDelay in loop.js, unit-tested).
3. `chrome.tabs.update(tabId, {autoDiscardable:false})` from the worker on port connect: the documented opt-out from
   automatic discarding / Memory Saver [4]. Kept: Web Lock (holding one exempts a page from freezing [2]).
4. Visible status: a dot in the panel (filled = ok, half = only worker ticks, hollow = stale) with ages in the tooltip.

## Rejected
- Silent-audio emitter / audible tab: exempts the tab from throttling and freezing but is a hack (autoplay policy,
  speaker icon, battery, breaks when the output device changes, no signal when it fails). Not added; none was in the repo.
- Offscreen document as keep-alive: allowed only for the declared reasons (AUDIO_PLAYBACK, WORKERS ...); Chrome
  states it must not be used to hold the worker alive, and it cannot host the chat page anyway [5].
- chrome.alarms: min period 30 s; wakes the worker but cannot reach a frozen page [6]. Not needed as the page pulls.
- Native messaging host: robust but a new install, manifest registration, permission; the agent is already a loopback
  HTTP server, the problem is the page side, not transport [7].
- Moving the bridge out of the tab (CDP / Playwright / headless Chrome): the chat page is the thing that must run;
  a driven browser needs its own login to DeepSeek and automation-detection risk. Reconsider only if the above fails.
- chrome://discards: manual per-tab toggle; autoDiscardable:false does the same programmatically.

## Sources
[1] https://developer.chrome.com/blog/timer-throttling-in-chrome-88   [2] https://developer.chrome.com/docs/web-platform/page-lifecycle-api
[3] https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle
[4] https://developer.chrome.com/docs/extensions/reference/api/tabs#property-update-updateProperties (autoDiscardable)
[5] https://developer.chrome.com/docs/extensions/reference/api/offscreen   [6] https://developer.chrome.com/docs/extensions/reference/api/alarms
[7] https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging
(Recalled from the docs, not re-fetched this session: budget cap. Verify the quoted behaviour on the operator's Chrome.)

## Operator confirmation (needs real Chrome; cannot be simulated here)
1. Copy scripts\aibridge\extension\* over F:\AIBridge\extension\ (keep background.js TOKEN line), chrome://extensions -> Reload AIBridge, F5 the DSA chat tab.
2. The panel shows a dot after "Hands-free": filled = ok. Hover for ages.
3. Switch to another window for 10 min with a run pending: dot stays filled/half, blocks keep running; on return the status line shows no "stale".
4. chrome://discards: the DSA tab's "Auto Discardable" column should read No.
Tests: `node scripts/aibridge/tests/loop.test.js` (14 pass; the 5 new link tests throw TypeError on the old loop.js).
