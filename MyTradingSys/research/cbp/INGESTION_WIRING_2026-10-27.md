# CBP ingestion audit and repair

Operator request: supply MTS (called MJS in the request) twice daily from analyst YouTube videos.

## Findings
- `cbp_run.py --due` was a callable command with no recurring caller. The old CBP routine was retired;
  the October 23 design depended on a coordinator wake. Integration alone did not schedule ingestion.
- Runner read `F:/CryptoScrapper/transcripts`; the migrated canonical store is
  `F:/CryptoScrapper/raw_transcripts_canonical`. It also ignored raw-only files.
- Fetch subprocess failures were ignored; extractor outages could mark the time window complete.
  Mixed cached-success/rate-limit fetches incorrectly returned success, while no recent uploads returned failure.
- The former queue/acks/consumer was deliberately removed. The supported MTS read interface is `cbp.query()`.
  Search found no production layer calling it yet. Supplying research inputs does not activate a trading strategy.

## Shipped repair
- Canonical timed/raw inputs, one extraction per analyst/video, shared raw output directory.
- Nonzero fetch/extraction results fail the run; unavailable or malformed extraction is retried, never
  permanently rejected. Verified partial rows survive extraction failures; the completion stamp does not advance.
- `cbp_schedule.py` supplies install/check/run/status/remove for the single CBP-only Windows task.
  Two starts at 09:00 and 13:00 UTC (14:30/18:30 IST, OURS): Europe underway and before US cash open.
  UTC times are fixed across DST; windows remain open until the next slot/midnight to permit retry.
  Days include weekends. Three 15-minute failure retries, wake/catch-up and scheduled overlap suppression.
- Stable paths: CBP_HOME/cbp_store/{rows.json,stamp.json,ingestion.log}; transcripts in
  CBP_HOME/raw_transcripts_canonical. Existing MTS query default remains F:/CryptoScrapper/cbp_store/rows.json.
  For a different home, consumers must set CBP_STORE to that same rows.json.

## Verification and activation
20 focused tests pass, including fetch -> extraction -> quote validation -> store -> MTS query;
six new regression cases failed on the original code before repair. External YouTube and LLM calls
are mocked in these tests. No fresh live-video ingestion has been demonstrated by this session.

NUC preflight fails: F:/CryptoScrapper/cbp_v2/analysts.json does not exist. No task was registered
against this missing location. Claude path confirmation is pending (operator: "ask claude").
The legacy C:/Users/E-ngineers/IdeaProjects/CryptoScrapper checkout exists, but has no cbp_store/rows.json
and still uses the old analyst configuration (no actionable profile); its preflight also refuses.
From a durable work checkout on the confirmed data host, the activation commands are:

```
python scripts/dev/cbp_schedule.py check --home F:/CryptoScrapper
python scripts/dev/cbp_schedule.py run --home F:/CryptoScrapper
python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper
python scripts/dev/cbp_schedule.py status
```

Record LastTaskResult=0, a fresh stamp and rows queryable from the MTS consumer host before calling
the twice-daily feed operational. YouTube 429 and Claude login/model availability are external dependencies.
