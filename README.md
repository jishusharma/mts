# BinanceDataFeed

**Running MTS by hand: start with [MTS_USER_GUIDE.md](MTS_USER_GUIDE.md).**
One command (`mts`) and three Desktop shortcuts cover the whole day.

Real-time Bitcoin trading system. Watches BTCUSDT, applies a fixed
rule set, and alerts when a setup candidate is close to its entry.

## How a session starts

In PowerShell, at the project root:

    cd scripts
    .\start-session.ps1

That loads the shortcuts and writes Dumps\SESSION_PASTE.txt.
Copy that file into a fresh chat to bring the AI up to speed.

## Shortcuts

    quick     deltas    trend
    snapshot  overview  health  alerts

## Folders

    MyTradingSys/     the decision system
      runtime/          live state and Python math layer
      conditions/       rule files
      research/         written findings
      tests/            test suite
      system/           reference docs
      methodology/      research gate

    scripts/          PowerShell helpers
      core/             start and stop the runtime loop
      live/             the seven shortcuts
      monitor/          station reads

    src/              Java source (screener, state machine)

    runtime_data/             snapshots and runtime logs
    Dumps/            boot paste and one-time dumps
    extracts/         cleaned transcript work
    raw_transcripts_canonical/   source transcripts

    backup_session/   one backup per session

## Files at root

    DSA_SESSION_PROMPT.md   behavior rules for the AI
    USER.md                 user preferences
    COMMANDS.md             operator commands
    VERSION                 project and engine versions

## Authority order

When rules conflict:

1. compiled_engine.md wins.
2. Condition files under MyTradingSys/conditions/.
3. Tom transcripts, the only source for rules and levels.
4. DSA_SESSION_PROMPT.md, for behavior.

## Rule of thumb

The tree is the map: git ls-files, MyTradingSys/system/LAYERS.md (layers) and PROJECT_MAP.md (groups).

# END