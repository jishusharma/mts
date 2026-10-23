# B180 - operator: DSA picks its tasks by default from the machine it runs on, and something assigns DSA tasks on a schedule (cost)

Source: Control Room inbox u0tq16gl6lcu4hw8jtgn (verbatim in MyTradingSys/system/OPERATOR_INBOX.md), picked up 2026-10-11 by the unstick session: the cloud poller had marked these in_progress/needs_local but nothing was recorded, filed or carded.

## Plan
Extend desk.py/DSA_DELEGATION.md routing (1m-kline->NB, 1h/1d+inventories->NUC): `desk.py next --host` returns the first pending row for this host or for target DSA, plus a scheduled assigner that posts cards whose lane is DSA/DSA-NB/DSA-NUC (tasks.py lanes). Test with fixture rows.
