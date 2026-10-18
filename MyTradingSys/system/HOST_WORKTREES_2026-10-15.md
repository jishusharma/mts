# JIS-NB worktrees on 2026-10-15: `sync.py tidy --all` dry run, tree by tree

Decision: q-host-worktree-tidy (OPERATOR_DECISIONS.md). Nothing was removed. Columns: tree, branch, real idle
(newest of branch tip, index, HEAD and the last reflog ENTRY; tidy reads the logs/HEAD file time instead), size, why.
Source: `sync.py tidy --all` (dry run, keep lines uncapped) at 2026-10-15 08:2x IST, plus `sync.py where --all`.

## A. tidy --all removes today: 2 tree(s), 25 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| amazing-blackburn-4905a8 | claude/amazing-blackburn-4905a8 | 91 | 13 | clean, on origin, idle |
| nifty-chatelet-4dac42 | claude/nifty-chatelet-4dac42 | 91 | 13 | clean, on origin, idle |

## B. would go too, but tidy reads them as 'active 5.3 h' (gc rewrote logs/HEAD at 03:07 IST): 32 tree(s), 661 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| brave-noether-416473 | claude/interesting-varahamihira-a7cb19 | 91 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| busy-jang-bbb51c | claude/beautiful-davinci-34cc59 | 92 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| confident-ramanujan-0e0dbf | claude/jolly-wilbur-c3dd17 | 93 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| confident-rhodes-4d0039 | claude/quizzical-cori-f63042 | 93 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| great-khayyam-1d90a2 | claude/dreamy-cray-1f2e0e | 93 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| infallible-jemison-d1bd4b | claude/kind-vaughan-0920bb | 92 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| keen-varahamihira-e1b189 | claude/inspiring-germain-27b6f5 | 92 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| kind-chatelet-e0a5ff | claude/fervent-hermann-e8f50e | 90 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-1011154728 | jisnb/relay-1011154728 | 83 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-10120535 | jisnb/relay-10120535 | 46 | 30 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-1013-0500 | jisnb/relay-1013-0500 | 46 | 33 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010-2050 | jisnb/relay-20261010-2050 | 102 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610100922 | jisnb/relay-202610100922 | 114 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610101311 | jisnb/relay-202610101311 | 110 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010135432 | jisnb/relay-20261010135432 | 109 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610101610 | jisnb/relay-202610101610 | 46 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010164039 | jisnb/relay-20261010164039 | 106 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010T0027 | jisnb/relay-20261010T0027 | 122 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010T0627Z | jisnb/relay-20261010T0627Z | 116 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261010T121854Z | jisnb/relay-20261010T121854Z | 46 | 23 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610110012 | jisnb/relay-202610110012 | 99 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610110910 | jisnb/relay-202610110910 | 89 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-202610111655 | jisnb/relay-202610111655 | 82 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261011T1008 | jisnb/relay-20261011T1008 | 88 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261013T182058Z | jisnb/relay-20261013T182058Z | 32 | 34 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-relay-20261013T190157Z | jisnb/relay-20261013T190157Z | 32 | 34 | clean, on origin, idle; hidden by the 03:07 gc reset |
| mts-sup | jisnb/stage1-2026-10-09 | 140 | 22 | clean, on origin, idle; hidden by the 03:07 gc reset |
| optimistic-tesla-8de153 | claude/kind-albattani-036410 | 90 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| priceless-elbakyan-ad8ac7 | claude/desk-live-guard | 103 | 24 | clean, on origin, idle; hidden by the 03:07 gc reset |
| quirky-elbakyan-3f7368 | claude/trusting-mcclintock-6ddca5 | 91 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| serene-jemison-dfd8ca | claude/dazzling-wu-ef602c | 106 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |
| wizardly-volhard-a12bd9 | claude/laughing-chandrasekhar-88e536 | 90 | 13 | clean, on origin, idle; hidden by the 03:07 gc reset |

## B!. same as B, but in use by a routine: keep: 1 tree(s), 31 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| mts-control-room | jisnb/control-room | 59 | 31 | working folder of the mts-control-room routine; never remove |

## D. detached App trees (tidy keeps detached by rule): 5 tree(s), 64 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| clever-faraday-adb017 | (detached) | 104 | 13 | detached HEAD, clean, nothing unshipped |
| cranky-taussig-fd6d83 | (detached) | 91 | 13 | detached HEAD, clean, nothing unshipped |
| distracted-margulis-40e455 | (detached) | 104 | 13 | detached HEAD, clean, nothing unshipped |
| gallant-wing-3a075d | (detached) | 90 | 13 | detached HEAD, clean, nothing unshipped |
| practical-kapitsa-119490 | (detached) | 104 | 13 | detached HEAD, clean, nothing unshipped |

## E1. BROKEN HEAD, clean + shipped once repaired: 17 tree(s), 576 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| mts-aibridge-fix | jis-nb/aibridge-fluent | 11 | 39 | broken HEAD (case); after repair clean + shipped |
| mts-bld | jis-nb/bld-lock-fix | 83 | 24 | broken HEAD (case); after repair clean + shipped |
| mts-cicd | jis-nb/cicd-deploy | 124 | 24 | broken HEAD (case); after repair clean + shipped |
| mts-codexbridge | jis-nb/codex-bridge | 80 | 24 | broken HEAD (case); after repair clean + shipped |
| mts-fix-docs-cards | jis-nb/fix-docs-cards | 14 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-fix-exec-reject-diag | jis-nb/fix-exec-reject-diag | 15 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-fix-live-edits | jis-nb/fix-live-edits | 14 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-fix-mirror-root | jis-nb/fix-mirror-root | 14 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-fix-relay-claims | jis-nb/fix-relay-claims | 15 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-fix-sched-catchup | jis-nb/fix-sched-catchup | 15 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-labfix | jis-nb/lab-unstick | 8 | 42 | broken HEAD (case); after repair clean + shipped |
| mts-liveedits | jis-nb/live-edits-1014 | 10 | 43 | broken HEAD (case); after repair clean + shipped |
| mts-nb-0 | jis-nb/loop-fix-1013 | 46 | 33 | broken HEAD (case); after repair clean + shipped |
| mts-ops1014 | jis-nb/ops-1014 | 14 | 38 | broken HEAD (case); after repair clean + shipped |
| mts-refine | jis-nb/task-refinement | 46 | 24 | broken HEAD (case); after repair clean + shipped |
| mts-task | jis-nb/task-2026-10-10 | 123 | 23 | broken HEAD (case); after repair clean + shipped |
| mts-tombtc | jis-nb/tombtc-1013 | 21 | 35 | broken HEAD (case); after repair clean + shipped |

## C. really active (< 24 h): keep: 14 tree(s), 504 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| cool-golick-9a29ee | claude/stale-pointers-1015 | 0 | 37 | really active |
| eloquent-lederberg-84d46c | claude/pinned-chats-consolidation-5abc14 | 9 | 13 | really active |
| focused-swanson-833614 | claude/focused-swanson-833614 | 0 | 42 | really active |
| mts-relay-1014-1340 | jisnb/relay-1014-1340 | 13 | 40 | really active |
| mts-relay-1014-1441 | jisnb/relay-1014-1441 | 12 | 38 | really active |
| mts-relay-1014-1541 | jisnb/relay-1014-1541 | 10 | 41 | really active |
| mts-relay-1014-1641 | jisnb/relay-1014-1641 | 10 | 41 | really active |
| mts-relay-1014-1909 | jisnb/relay-1014-1909 | 8 | 42 | really active |
| mts-relay-20261014T0517 | jisnb/relay-20261014T0517 | 22 | 35 | really active |
| mts-relay-20261014T1959 | jisnb/relay-20261014T1959 | 7 | 42 | really active |
| mts-relay-20261015T1212 | jisnb/relay-20261015T1212 | 7 | 42 | really active |
| reverent-wing-466364 | claude/reverent-wing-466364 | 0 | 42 | really active |
| session-token-optimization-125f4a | claude/token-opt-1015 | 5 | 37 | really active |
| silly-bohr-f01129 | claude/yellow-banner-session-switch-efb21f | 9 | 13 | really active |

## E2. BROKEN HEAD, holds files once repaired: keep: 6 tree(s), 216 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| mts-eset | jis-nb/auto-deploy-lock | 46 | 24 | broken HEAD (case); after repair holds 0 changed / 33 untracked file(s) |
| mts-eurlow | jis-nb/eur-low-sweep | 10 | 41 | broken HEAD (case); after repair holds 99 changed / 0 untracked file(s) |
| mts-krown-layer | jis-nb/krown-layer | 9 | 42 | broken HEAD (case); after repair holds 101 changed / 2 untracked file(s) |
| mts-pastehdr | jis-nb/pastehdr | 9 | 42 | broken HEAD (case); after repair holds 1 changed / 2 untracked file(s) |
| mts-relay-queue | jis-nb/relay-queue-lanes | 8 | 42 | broken HEAD (case); after repair holds 99 changed / 0 untracked file(s) |
| mts-unstick | jis-nb/unstick | 82 | 24 | broken HEAD (case); after repair holds 0 changed / 8 untracked file(s) |

## F. uncommitted work: keep: 12 tree(s), 388 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| goofy-brattain-9fbecd | claude/goofy-brattain-9fbecd | 8 | 42 | 1 uncommitted file(s), e.g. MyTradingSys/system/LAYERS.md |
| mts-daxbt | jisnb/daxbt | 102 | 28 | 44 uncommitted file(s), e.g. MyTradingSys/backtest/bigtrade/__init__.py |
| mts-extract | jisnb/extract-2026-10-09 | 138 | 22 | 3 uncommitted file(s), e.g. extracts/v2/tom/ShYS_pD5cxQ_v2.md |
| mts-livemkt | jisnb/livemkt-20261012 | 46 | 31 | 1 uncommitted file(s), e.g. MyTradingSys/research/STATUS.md |
| mts-relay-1014-1849 | jisnb/relay-1014-1849 | 7 | 42 | 1 uncommitted file(s), e.g. raw_transcripts_canonical/hNfjyrJEytI_raw.txt |
| mts-relay-20261011-0112 | jisnb/relay-20261011-0112 | 98 | 24 | 1 uncommitted file(s), e.g. MyTradingSys/research/STATUS.md |
| mts-relay-20261011-1830 | jisnb/relay-20261011-1830 | 80 | 24 | 2 uncommitted file(s), e.g. scripts/sched/relay_prompts/INSTALL.md |
| mts-relay-202610110310 | jisnb/relay-202610110310 | 96 | 24 | 1 uncommitted file(s), e.g. MyTradingSys/research/STATUS.md |
| mts-relay-202610141855 | jisnb/relay-202610141855 | 8 | 42 | 1 uncommitted file(s), e.g. MyTradingSys/system/relay_runs.jsonl |
| mts-relay-20261014T1939 | jisnb/relay-20261014T1939 | 7 | 42 | 2 uncommitted file(s), e.g. MyTradingSys/backtest/fetch_binance_archive.py |
| mts-research | research/agenda-2026-10-06 | 182 | 27 | 7 uncommitted file(s), e.g. MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md |
| wf_91275c63-c80-5 | tokopt-git | 7 | 42 | 1 uncommitted file(s), e.g. .pt_rv/ |

## G. commits not on origin/fast-track: keep: 8 tree(s), 297 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| BinanceDataFeed.registry | fast-track-work | 133 | 20 | 1 commit(s) not on origin/fast-track |
| mts-relay-20261011T122539 | jisnb/relay-20261011T122539 | 86 | 24 | 3 commit(s) not on origin/fast-track |
| mts-relay-20261014T174914Z | jisnb/relay-20261014T174914Z | 9 | 42 | 1 commit(s) not on origin/fast-track |
| wf_91275c63-c80-1 | tokopt-relay | 7 | 42 | 4 commit(s) not on origin/fast-track |
| wf_91275c63-c80-2 | tokopt-hooks | 7 | 42 | 1 commit(s) not on origin/fast-track |
| wf_91275c63-c80-3 | tokopt-claudemd-surfaces | 7 | 42 | 2 commit(s) not on origin/fast-track |
| wf_91275c63-c80-4 | tokopt-records | 7 | 42 | 2 commit(s) not on origin/fast-track |
| wf_91275c63-c80-6 | tokopt-tools | 7 | 42 | 4 commit(s) not on origin/fast-track |

## H. named lanes: keep: 4 tree(s), 135 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| mts-dsa | jisnb/dsa | 63 | 32 | named lane |
| mts-push | nb/tzdata-ci | 46 | 24 | named lane |
| mts-refiner | jisnb/refiner | 2 | 37 | named lane |
| mts-relay | jisnb/relay | 6 | 42 | named lane |

## S. skipped: 2 tree(s), 5677 MB

| tree | branch | idle h | MB | why |
|---|---|---|---|---|
| BinanceDataFeed | fast-track | 2 | 5635 | live tree or this session's tree (tidy never looks at them) |
| vigorous-moser-b72ecf | claude/vigorous-moser-b72ecf | 0 | 42 | live tree or this session's tree (tidy never looks at them) |
