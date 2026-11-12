# FETCH_LOG: guarded caption fetch, newest Tom uploads (card of-extract-fetch-1112)

| UTC | id | row | note |
|---|---|---|---|
| 2026-11-12T02:53Z | j-JVi02_C88 | BLOCKED | one request (card extract-50w-ma-j-JVi02-retry-1112) answered HTTP 429; first 429 ends the run |
| 2026-11-12T02:53Z | newest @TomVorwald (since 2026-11-04) | DEFERRED | no fetch: guard `BLOCKED until 2026-11-13T02:53:04+00:00` (lockout level 2 of 3, 6/24/72 h, OURS) |

Retry: after 2026-11-13T02:54Z, j-JVi02_C88 first (one video), then `--analyst Tom --channel @TomVorwald --since 2026-11-04 --latest 3 --scan 12 --max-videos 3`.

Gemini-lane list (no captions available yet; no ASR here): j-JVi02_C88, BB3c8visnkI, e83njGZFrPw. Queue only if still blocked or NO_CAPTIONS after the retry.

| 2026-11-12T06Z | BB3c8visnkI | BLOCKED | new WARP exit run exited 3, guard `BLOCKED until 2026-11-13T02:53:04+00:00`, no request made |
| 2026-11-12T06Z | e83njGZFrPw | BLOCKED | same run, no request made; retry after 2026-11-13T02:54Z |
