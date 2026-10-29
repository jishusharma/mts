# PF_ARM_TRACE: can a PF-* candidate arm or send an order on testnet?

**VERDICT: NO. A PF-* candidate cannot send an order today (auto_trader rejects it at the side parse), and the state machine never sees it. It can reach the Tom card, the popup and the dashboards when it is the only candidate. Static read of origin/fast-track at 6d4a9f6b1; nothing was run.**

## Path trace

| # | Consumer (file:line) | Can PF-* arm / send an order? | Why |
|---|---|---|---|
| 1 | Flag read `PitchforkSignalLayer.java:29-30` (`Boolean.getBoolean("mts.pitchfork")`, FLAG at :27) | n/a | Default false; set true by `start-trading-day.ps1:113`, `:445`, `:475` |
| 2 | Producer `SetupCandidatesBuilder.java:271-277` | Emits | PF candidates are appended AFTER the sort at `:200`, so rank is always last; `setup_type` PF-REV-L/S, PF-HAG-L/S (`PitchforkSignalLayer.java:491,504`); no `"arm"` field (the fade candidates set it, `:264`) |
| 3 | State machine JVM `start-trading-day.ps1:445` (`-Dmts.pitchfork=true ... statemachine`) -> `Main.java:28-38` -> `StateCodeEmitter` | NO | `StateCodeEmitter.java` has no reference to `SetupCandidatesBuilder`, `setup_candidates` or `setup_type` (grep, 0 hits); it emits state codes from ticks. The flag at `:445` is inert for that JVM |
| 4 | Snapshot JVM `start-trading-day.ps1:113`, `:475` -> `MarketDataSnapshot.java:457,1310` -> `root.set("setup_candidates")` `:469,:1322` | Writes to snapshot JSON | Flag is live here only |
| 5 | `Compute-Verdict` `start-trading-day.ps1:202-219` | CONDITIONAL (only if PF is `cands[0]`) | Reads only `$cands[0]`; PF is `cands[0]` only when no Tom/ExtraSetup candidate exists. Its `math.tier` (`PitchforkSignalLayer.java` `trigger_ready`/`conditional`/`ignore`) and `proof_count` then pick WAIT_*/WATCH/SETUP_FORMING. PF sets `score.proof_count` (`PitchforkSignalLayer.java:594`), so the verdict can reach WATCH/SETUP_FORMING (`:260-263`) and is displayed; this alone sends nothing |
| 6 | `Build-Card` `start-trading-day.ps1:318-352`, `SETUP:` line `:329`, ENTRY/STOP/TARGET `:350-353` | Card text only | Writes `SETUP:   PF-REV-L` etc. into `last_alert.json` |
| 7 | `math_object_builder.py:410-441` (`setup_candidates[0]` -> `setup_candidate`, hard stop net_rr) and `build_mo_cli.py` via `start-trading-day.ps1:~523` | NO | Advisory / proof-direction check only; no order call |
| 8 | **`auto_trader.py:182`** `side = "long" if setup.endswith("_long") else "short" if setup.endswith("_short") else None`, then `tom_signal` `:279-280` `elif p["side"] is None: reject = "unknown setup side"` | **NO (decisive gate)** | `PF-REV-L`, `PF-HAG-S` etc. end in `-L`/`-S`, not `_long`/`_short`, so side is None and the signal carries `reject`; `cycle` `:879` then logs `signal_rejected` (`:892`) and never reaches `place()` |
| 9 | Layer-alert path `auto_trader.py:882` (`read_new_layer_alerts`, dir `:51`) | NO | Nothing writes a pitchfork alert into `MyTradingSys/runtime/alerts` (grep of `*.py/*.java/*.ps1`: no pitchfork producer; the only hits are `layer_map.json:677` metadata and the Java layer); `layer_signal` would also reject unmapped events (`:517`) |
| 10 | Dashboards `scripts/live/live.ps1:51`, `mts-dashboard.ps1:67,110`, `mts-watch.ps1:76,121`, `snapshot.ps1:15`, `tape-watch.ps1:40`; `HistoricalScreening.java:28` | NO | Display / screening only |

## Caveats (what would change the verdict)

| Risk | Detail |
|---|---|
| Rename | If anyone renames PF setup types to end `_long`/`_short`, gate 8 opens; all other Tom gates (verdict list `auto_trader_config.json:27-31`, net_rr floor, TIME age, fee-to-stop, `promotion_reject("tom")` `:302`) would then be the only guards. `promotion_reject("tom")` keys on the source "tom", not the setup, so it does NOT separate PF from Tom setups. |
| Display | PF can show as the top card/popup (`Build-Card`), so an operator may read a PF zone as a Tom setup though no order follows. |
| Not verified | Runtime behaviour on the live tree (not touched); whether `promoted_setups.json` currently lists "tom" as trade. Static trace only. |

## Consequence

The live Java card for PF is NOT urgent on order-safety grounds: PF cannot trade on testnet via this chain. Gate 8 is an accident of naming, not a designed block; a test pinning it (PF setup type -> `tom_signal` reject) is cheap and would turn it into a guard.
