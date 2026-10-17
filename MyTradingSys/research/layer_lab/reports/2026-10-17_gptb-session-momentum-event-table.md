# gptb-session-momentum-event-table

- DEV 5m run: `python MyTradingSys/research/layer_lab/session_momentum_event_table/event_table.py --output <csv>` -> rows=912 ok=911 not_in_data=1 long=458 short=453 mean_MFE_R=2.6997 mean_MAE_R=2.8101 (gross, forward to 24:00 UTC, R = ATR14 of closed 1h bars).
- NOT_IN_DATA: 2022-01-01 only (no prior 1h bars inside DEV).
- Tests: `python -m pytest MyTradingSys/research/layer_lab/session_momentum_event_table/test_event_table.py -q -p no:cacheprovider` -> 10 passed (red first: event_table.py missing).
- Details: `MyTradingSys/research/layer_lab/session_momentum_event_table/REPORT.md`.
