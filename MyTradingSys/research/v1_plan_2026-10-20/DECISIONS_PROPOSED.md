# Decisions proposed for the operator (to post on the decision page; format of OPERATOR_DECISIONS.md)

Each has a default so S0 can start with zero operator input (CLAUDE.md boot rule 4). The operator answers yes / no / change.

## q-v1-freeze
Question: Freeze new layers, vendors, pages and rule documents from now until the GO-LIVE BAR holds, and apply D1
(finish / park / close) as written?
Default: yes. Effect: S0 starts; D1 dispositions are executed by one Pipeliner pass; nothing is deleted, only closed or parked.

## q-v1-layers
Question: Slot 1 Levels Confluence, slot 2 CryptoCred 4h/1d; next in line Tom v2, then RSI deep-buy, then Kurisko. Confirm, or swap?
Default: as proposed. Effect: WIP = 2 enforced in tasks.py; other research cards parked.

## q-v1-keepers
Question: The 22 Windows scheduled tasks on JIS-NB (15 enabled). (a) unregister all; (b) keep an explicit keeper list
(MTS-Feed-Watchdog, MTS-Live-Health, MTS-OI-Recorder, MTS-Wrapper, MTS testnet canary) with an owner, unregister 17.
Default: (b). Effect: SCHEDULING_POLICY.md gets the keeper list as its one written exception; the uptime bar item (D3 M4)
is read from a heartbeat file, not from a reviver.

## q-v1-cbp-routine
Question: The cbp-daily-workflow Claude scheduled task (Haiku, 3x per day). (a) stop it; the coordinator runs the CBP
pipeline on wake; (b) keep it as the one named routine exception with an owner.
Default: (a). Effect: consistent with q-v1-keepers; CBP becomes a module dispatched by MTS (D5).

## q-v1-bar
Question: Revise GO_LIVE_BAR.md with D3: add M1-M7; rolling 30-day window with at most 1 failed uptime day instead of
"one failing day restarts the clock"; time-outs become a per-layer promotion condition; 200 trades or 60 days, with at least
30 per promoted config.
Default: yes. Effect: D2 acceptance points at the revision; S2 cards are M1-M4.

## q-v1-config-1023
Question: At the 2026-10-23 review of auto_trader_config.json, keep only sources of families in a slot or with a KEEP rule;
move FAIL families to trade_blocklist; leave the rest parked.
Default: yes. Effect: a config change signed by the operator, deployed by the runbook, not by a builder.

## q-v1-spec
Question: Sign D2 as the v1 spec (with any change written on the page)?
Default: none; this one needs the operator. Until signed, S2-S4 do not start; S0 runs.
