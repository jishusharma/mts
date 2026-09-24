# SESSION STATE SCHEMA
# Version 1.0.0 | 2026-09-13
# Purpose: AI-authored session context SSOT. Two files, two writers.

## session_state.json — AI writes, overwrite on decision
{
  "version": "1.0.0",
  "updated_utc": ISO8601,
  "session_start_utc": ISO8601,
  "asset": "BTCUSDT",
  "mode": "prep|armed|live",
  "thesis": {
    "direction": "short|long|neutral",
    "confidence": "high|medium|low",
    "text": "one paragraph"
  },
  "watch_levels": [
    { "price": float, "name": str,
      "role": "short_entry|long_entry|target|invalidation|context",
      "trigger": str, "status": "pending|fired|passed" }
  ],
  "next_trigger": { "condition": str, "expected_setup": str, "action_plan": str },
  "invalidates": { "condition": str },
  "notes": str
}

## session_log.json — apparatus appends, never overwrite
{
  "version": "1.0.0",
  "events": [
    { "ts": ISO8601, "type": "alert|decision|note|trade",
      "alert_id": int?, "verdict": str?, "setup": str?,
      "action": "passed|acted|monitored|n/a", "reason": str }
  ]
}

## Protocols
1. Missing file = fresh session. No abort.
2. Corrupt JSON = treat as empty, log warning, continue.
3. Version mismatch = log warning, best-effort read.
4. Atomic write: tmp + os.replace. No partial reads.
5. session_state.json overwritten on every AI decision.
6. session_log.json appended only. Never truncated.

# END
