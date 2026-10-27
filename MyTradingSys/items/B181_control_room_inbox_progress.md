# B181 - operator: Control Room Inbox shows no progress per item; an item without a registry ref shows nothing

Source: Control Room inbox wlfq6r3l1by15luk1rhc (verbatim in MyTradingSys/system/OPERATOR_INBOX.md), picked up 2026-10-11 by the unstick session: the cloud poller had marked these in_progress/needs_local but nothing was recorded, filed or carded.

## Plan
Page must show status + reply + ref for EVERY inbox item, including items with no ref (these were the stuck ones). Change control_room.tpl.html/make_control_room.py with a test; add a changelog line.
