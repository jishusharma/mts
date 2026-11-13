# Indicator rule book: template (operator order 2026-11-13, OPERATOR_DECISIONS.md)

One file per indicator, named `<NAME>.md`, in this folder, one row in `INDEX.md`. Model: `research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md`.
Header line: `Sources:` keys used. Then one bold result line: what the indicator is good for and what OUR data says. No section may be dropped: write "none found" or "UNTESTED".

Labels. SOURCED = a quote or number from a source you opened and read (URL or file:line). OURS = our reading or our measurement. UNVERIFIED = a web claim you did not open and read, or a fetch summary you could not check. Never invent a quote. Every number carries a file pointer.

## 1. What it measures
Plain words, 2-3 lines. Formula pointer: `backtest/layers/FORMULAS.md` section N, and `VERIFIED-TV <date>` or `NOT VERIFIED-TV`. Code module.

## 2. Developer's own rules (SOURCED)
Who wrote it, year, original source link (book, article, TradingView script page). Their stated use: levels, signals, timeframe, warnings. If the page states no rule, say "the page states no rule".

## 3. What the internet and crypto traders say
Table: claim | source URL | evidence grade. Grades: `measured` (data, period, fees, sample stated), `anecdote` (screenshot, one trade, opinion), `none`. A vendor claim without a costed sample is `anecdote`.

## 4. What our analysts say (extracts)
Table: analyst (Krown, Tom, Fabio, Malkan, NK, CCU, Habib/CBP, CryptoCred, others) | their rule in plain words | file pointer (extract id + timestamp). "No extract mentions it" is a valid row.

## 5. OUR measurements
Table: study folder | what was tested | n | fee-net result | verdict. One verdict per timeframe: USE AS FILTER / CONTEXT ONLY / DO NOT USE / UNTESTED / UNDERPOWERED. Add `Regime mix:` and the DEV / VALIDATION / RECENT split when the study has it. Copy numbers from the study's RESULT or REPORT file, never from memory or from another summary.

## 6. How to read it now on Live Aid
Which panel shows it (name as in `tools/live_aid/live_aid.html`, e.g. Momentum, Moving averages, Timeframe strip), what the cell means, or "not shown".

## 7. Confluence role
Exactly one of: TREND GATE / EXHAUSTION / FLOW / LEVEL / TIMING. Then: what it may add confidence to (a setup, a position size step, a veto), and the rule in one line. It is never an entry by itself unless a fee-net out-of-sample pass exists in section 5. Say which it is today (usually: context only).

## 8. Open tests
List of the next studies, one line each: card id or "not filed", what is tested, the rule fixed before the run.

Quality check before you finish: every section present; every number has a pointer; every web claim has a URL and a SOURCED/UNVERIFIED mark; the verdict words are from the list above; section 7 names one role.
