# Two workers built live-aid-news-panel

1. Session built it: e74038d3d (2026-10-30 13:51 IST), card closed state=done: 2db125d50 (14:31). Both on branch claude/live-aid-design-c4174e, not on trunk yet.
2. Planner commit b595a620a (gemini-queue, 15:31) rewrote the card on trunk as state=ready (2db125d50 is not its ancestor), so trunk still said ready.
3. gemini_queue.run_job (f8c5e4895, 15:43) fetched, checked open claims only (the session never claimed), never read card state or tag, and built it again.
4. Session merge 3a6db9ee0 (15:46) put state=done on trunk, 3 min after the second build.
5. Fix: run_job now calls card_gate (state ready on origin/fast-track and no SHIPPED/STALE tag, unreadable = skip). Limit: it cannot see a close that is still on an unmerged session branch (step 1-2 window); only claims or merging the close earlier covers that.
