# Qriptal call scoring: resolution rules

All numbers OURS, fixed 2026-10-14 before any scoring (lab run 2026-10-14 BLOCKED for lack of them).

- eligible call = BTC, forward-looking, entry + stop + at least one target stated
- call time = video publish time (raw file name/metadata), else the call is NO_TIME and not scored
- limit entry not filled within 24 h = NOT_FILLED (counted, not scored)
- stop and target inside the same 1m candle = stop
- several targets: primary score exits all at T1, second column exits at the last target
- open after 7 days = closed at market.
