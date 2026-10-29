# MTS Alert Dock: redesign spec for the alert popup (2026-10-28, Opus review)

Replaces: one `scripts/core/show-alert.ps1` window per alert, spawned by `start-trading-day.ps1`, `scripts/live/tape-watch.ps1` and `scripts/sched/check_live_health.py`. Why it fails today: `PICTURE_AND_PLAN.md` s.3.2.
Live path is single-owner: this file is a spec with its acceptance tests. Builders write code and tests in a worktree; only the live owner (DESKTOP-F7IU69N) deploys in a restart window (DEPLOY_RUNBOOK.md). Labels: SOURCED (web, read 2026-10-28) / OURS.

## 1. What modern alert UIs do (research)

| Practice | Source |
|---|---|
| Summarise repeated events into one message ("uploaded 12 files"); never several toasts for one cause | SOURCED [Canva toasts](https://www.canva.dev/docs/apps/design-guidelines/toasts/), [techinterview toast system](https://www.techinterview.org/post/3233475200/build-notification-toast-system/) |
| Cap the visible stack: Canva shows one at a time (new replaces old); Maersk allows up to 3; Singapore GDS stacks only similar toasts; unbounded growth is the classic bug | SOURCED [Maersk](https://designsystem.maersk.com/components/toast/), [Singapore GDS](https://designsystem.tech.gov.sg/components/toast) |
| Duration per severity; start the timer when visible; pause on hover; always show a close control when shown > 10 s; respect reduced motion | SOURCED same pages |
| Status semantics, not interruptive: focus does not move into the toast | SOURCED [Red Hat alert accessibility](https://ux.redhat.com/patterns/alert/accessibility/) |
| Replace or remove by key: Windows toasts carry Tag + Group; a new toast with the same Tag/Group replaces the old; RemoveGroup clears a group; SuppressPopup sends straight to the history (Action Center) | SOURCED [Microsoft toast collections](https://learn.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/toast-collections), [RemoveGroup](https://learn.microsoft.com/en-us/uwp/api/windows.ui.notifications.toastnotificationhistory.removegroup?view=winrt-22621) |
| Dedup key: an event whose key matches an open incident is appended to it, not a new incident; group similar alerts; pause flappy alerts; suppress non-actionable ones; time-limited silences | SOURCED [PagerDuty event management](https://support.pagerduty.com/docs/event-management), [PagerDuty reduce noise](https://www.pagerduty.com/ops-guides/ops-practices/reduce-noise/), [Rootly dedup](https://rootly.com/alert-management/alert-deduplication-and-correlation.md) |
| Windows no-focus window: WS_EX_NOACTIVATE (+ WS_EX_TOPMOST so it does not drop behind); handle WM_MOUSEACTIVATE -> MA_NOACTIVATE so clicks do not activate; reports that TopMost can still take focus, so test on the target Windows; NOACTIVATE removes the taskbar button unless WS_EX_APPWINDOW | SOURCED [StackOverflow 7750517](https://kaweah.freedombox.rocks/kiwix/content/stackoverflow.com_en_all_2023-11/questions/7750517/notification-window-preventing-the-window-from-ever-getting-focus), [AutoIt 154953](https://autoitscript.com/forum/topic/154953-can-you-make-a-gui-always-on-top-but-not-focusable-toast-like) |

## 2. Design (OURS)

### 2.1 Architecture
- **Producers never open windows.** Every producer appends one JSON line to `runtime_data/alert_inbox.jsonl` (append-only, `newline='\n'`, UTF-8) through one helper `scripts/core/alert_inbox.py post ...` (PowerShell callers run it the same way they now run `session_state.py`).
- **One consumer: the Dock.** A single-instance process (named mutex `Global\MTS_ALERT_DOCK`; a second start exits 0). It tails the inbox, keeps its own state in `runtime_data/alert_dock_state.json` (offset read, pins, snoozes, position). If the Dock is not running, producers lose nothing: lines wait in the inbox.
- **Layer alerts reach the Dock** by a small reader that follows `MyTradingSys/runtime/alerts/<tf>.jsonl` (read-only) and posts summaries to the inbox. The auto-trader stays the only consumer that trades.
- **Fallback**: if the Dock has not written its heartbeat for 120 s, `check_live_health.py` reports it RED in its own row; never respawn per alert.
- Tech (OURS): WinForms via `Add-Type` C# in one PowerShell host, as today (no new runtime dependency on the laptop); custom-painted cards. Native Windows toasts (Tag/Group) were considered: simpler, but the operator wants pin, snooze and a history list in one place and toasts give no control over size and stacking. Optional later: a Windows toast for ACTION only, with Tag = dedupe key, so a phone-style banner appears even when the Dock is behind a full-screen app.

### 2.2 Inbox record
```json
{"ts":"2026-10-28T17:40:00Z","source":"tom|layer|tape|health|dock","kind":"verdict_change","severity":"ACTION|WATCH|INFO|HEALTH","key":"tom:SETUP_FORMING:short:zone_82400","title":"SETUP FORMING short @ 82,400","summary":"one line, <= 90 chars","card_text":"full card, optional","tf":"15m","expires_s":900}
```
- `key` = dedupe/group key. Rules: tom = `tom:<verdict>:<direction>:<zone>`; layer = `layer:<layer>:<event>:<tf>`; tape = `tape:<divergence>`; health = `health:<failing set hash>`.
- No prices of positions, balances, order ids or account labels in the record (public repo; the inbox file itself lives in `runtime_data/`, which is gitignored).

### 2.3 Behaviour
| Rule | Spec |
|---|---|
| Grouping | same `key` within its `expires_s` -> update the existing card: count badge "x4", newest time, newest summary; no new card |
| Severity | ACTION (amber, stays until closed, one short sound), WATCH (blue, 60 s), INFO (grey, 8 s, silent; layer alerts default here), HEALTH (red, stays, sound once per new failing set) |
| Stack | at most 3 cards visible, newest on top, ACTION/HEALTH before WATCH/INFO; the rest go into the history drawer ("+12 more") |
| Timer | starts when the card is visible; pauses on hover; pinned cards never expire |
| Actions per card | Close (x), Pin, Snooze key 15 min / 1 h, Copy card, Open log; Close all; Snooze all INFO for 1 h |
| Focus | never activates: `Show()` (not `ShowDialog()`), `ShowWithoutActivation`, WS_EX_NOACTIVATE + WS_EX_TOPMOST, WM_MOUSEACTIVATE -> MA_NOACTIVATE; the keyboard stays in the IDE |
| Position | docked to a corner of a chosen monitor (default bottom-right, primary); drag snaps to the nearest corner; position stored per monitor id; off-screen after a monitor change -> reset to default; per-monitor DPI aware |
| Size | card 360 x 88 px collapsed (title, one-line summary, time, count, severity bar); click expands to the full card text in place; no 600 x 680 window |
| History drawer | last 200 records, newest first, filter by severity and source, search box; opens in the Dock, not a new window |
| Quiet mode | a header toggle: only ACTION and HEALTH show; INFO counted silently |
| Taskbar | one taskbar/tray entry for the Dock (WS_EX_APPWINDOW or a tray icon with unread count) so it can always be found |
| Look | dark theme matching today's colours (bg 20,22,28; amber 255,190,0), Segoe UI 10/9, rounded 8 px cards, 150 ms slide/fade, none when reduced motion is on |

### 2.4 Migration (the owner runs it, in this order)
1. Ship `alert_inbox.py` + Dock + tests (worktree, CI green).
2. Producers post to the inbox AND keep their old popup behind a flag `MTS_ALERT_UI=legacy|dock` (default `legacy`), so the deploy changes nothing until the owner flips it.
3. Owner restart window: start the Dock, set `dock`, watch one US session; rollback = set `legacy`.
4. After 3 clean sessions: remove the legacy spawn paths and the title-regex kill loop.

## 3. Acceptance tests (must fail on today's code at least once, per CLAUDE.md Gates)

| id | Test | Fails today because |
|---|---|---|
| AD1 | 10 posts with the same key within expires_s -> 1 card, count 10 | today: 10 windows |
| AD2 | 3 producers post (tom, tape, health) -> no new process is spawned; 3 records in the inbox | today: 3 processes |
| AD3 | 8 different keys -> 3 visible, 5 in history, ordering ACTION > HEALTH > WATCH > INFO then newest | no stack today |
| AD4 | snooze key K for 15 min (injected clock) -> posts with K counted but not shown; shown again after 15 min | no snooze today |
| AD5 | second Dock start -> exits 0, first keeps running | no single instance today |
| AD6 | Dock state file missing or corrupt -> starts with defaults, reads inbox from the end, no crash (restart/reset state, CLAUDE.md live-path rule) | n/a today: add as regression |
| AD7 | inbox line not JSON or missing key -> skipped, counted in a `bad_lines` counter, Dock keeps running (fail closed for that line only) | n/a: regression |
| AD8 | record carrying a field named like balance, order_id, account or position size -> rejected by `alert_inbox.py post` | no guard today |
| AD9 | window style check: the created Dock window has WS_EX_NOACTIVATE and WS_EX_TOPMOST; opened with Show | today: no NOACTIVATE, not topmost, ShowDialog |
| AD10 | `MTS_ALERT_UI=legacy` -> producers behave as today (popup spawned) and also post; `dock` -> no popup spawned | flag absent today |
| AD11 | layer reader: 300 rsi cross lines on 5m in one hour -> INFO cards grouped to one per (layer, event, tf) | layer alerts not shown today |

Pure logic (grouping, ordering, snooze, inbox parse, field guard) goes in a Python module with unit tests so CI on Ubuntu runs it; window-style tests (AD9) run on Windows CI only.
