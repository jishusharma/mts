# B177 - operator: Control Room 'Layer Board' tab - per active layer: dev/test activity, combined indicators, step count, actionables only

Source: Control Room inbox 0c3c2rw1dc5hz27ph4ro (verbatim in MyTradingSys/system/OPERATOR_INBOX.md), picked up 2026-10-11 by the unstick session: the cloud poller had marked these in_progress/needs_local but nothing was recorded, filed or carded.

## Plan
Build the tab from the registry + layer config (make_control_room.py, control_room.tpl.html, control_room.json) with a test; one row per active layer. Operator approves layout after the first publish.

## 2026-10-12 built (JIS-NUC relay)
Layer Board section shipped: `layers` list in control_room.json (each entry carries `src`), `layer_board()` in make_control_room.py resolves open-row count and worst severity from BUGS.md, parked layers are not shown. Test `test_layer_board_one_row_per_active_layer` failed on the old code (KeyError 'layers'), green now. NUC-account page republished (v5), Inbox item 0c3c2rw1dc5hz27ph4ro replied. Row stays OPEN until the operator approves the layout.
