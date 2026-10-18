# OPERATOR INBOX - verbatim record of what the operator sent through the Control Room Inbox

Procedure: MyTradingSys/system/CONTROL_ROOM.md (step 3). One entry per item, oldest first, text exactly as sent.
Older entries: MyTradingSys/archive/operator_inbox/ (rotation rule: CONTROL_ROOM.md step 3; cap 30 KB, test_integrity test_7).

## 3nk95q0pnm8hwyf26yvm | 2026-10-11T09:41:56Z | requirement
```
We need all deployments and script running times to be optimized -  make it faster end to end to optimize CI/CD
```
## cx26ff1q1gy35ed4lxxl | 2026-10-11T12:27:16Z | task
```
check this  if it adds any value to MTS's goals -  it was in my email - 
 Let DSA run reads on its own  Allow writes (commit, push, add, checkout, merge, stash) on auto-run 0/50
off: click Run on each block
None selected 

Skip to content
Using Gmail with screen readers
1 of 4,949
Modeling for Fast Results: A Practical Guide to Building Trading Models That Work
Inbox

paperswithbacktest from Algo Trading & AI <edarchimbaud@substack.com> Unsubscribe
17:42 (14 minutes ago)
to me


Forwarded this email? Subscribe here for more
Modeling for Fast Results: A Practical Guide to Building Trading Models That Work
From data exploration and feature selection to a working Random Forest momentum model: the complete modeling pipeline for systematic traders.
paperswithbacktest
Oct 11
∙
Preview

 




READ IN APP
 
Hi there. Hope you’re doing well.

Over the past few articles, we’ve built up the foundations of a systematic trading workflow, from defining target variables (the thing you want to predict) to engineering signal variables (the features that might predict it). If you’ve been following along, you now have a clean dataset with well-constructed predictors and a target return or quintile to forecast.

This week, we tackle the hardest and most rewarding step: modeling. This is where you take your carefully prepared features and build the mathematical link between signals and returns. Get this right, and you have a strategy. Get it wrong, and you have an expensive illusion.

The good news? You don’t need to reinvent the wheel. The key is knowing which tools to reach for, when to use them, and, just as importantly, when to stop adding complexity. Let’s walk through the entire process, from data exploration to a working momentum model in Python.

Algo Trading & AI is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber.

Upgrade to paid
Why Exploration Comes Before Modeling
It’s tempting to jump straight to fitting a random forest or running a regression. But the most experienced quants always start with exploration. This unglamorous step is what separates models that generalize from models that overfit.

Exploration serves four purposes:

Detecting relationships between signal and target variables that may not be obvious from summary statistics

Reducing dimensionality by discarding features that carry no predictive signal

Identifying rare events: unusual market conditions that could dominate your model’s behavior

Guiding model selection: the shape of the data should inform whether you reach for a linear model or something more flexible

There are two main exploration techniques that every systematic trader should master.

Non-Parametric Analysis...
User's avatar
Continue reading this post for free in the Substack app
Claim my free post
Or upgrade your subscription. Upgrade to paid
 
Like
Comment
Restack
 
© 2026 Edouard d'Archimbaud
548 Market Street PMB 72296, San Francisco, CA 94104
Unsubscribe

Get the appStart writing
```
## uatvl0nb0izontyg64lf | 2026-10-11T16:09:15Z | requirement
```
When possible. Design DSA AI Bridge tasks such that multiple sessions can run in || and complete tasks  quickly. Make sure that their scope on NB and NUC are maintained!
```
## kvsh4c9zt1bvw26dhore | 2026-10-11T16:10:43Z | task
```
we have had changes in the way to improve AI health in MTS - I still see sessions doing starting rituals - is it expected/correct/optimized? If not fix as per our goals. 
```

## nwaa0hbbf0hrd0sk8qti | 2026-10-12T11:22:52Z | task
```
After the fixes, AI Bridge must be available on NB as well. Change the version number of the extension. 
AIBridge feedback - from DSA session MTS-2026-10-12-0952Z - 2026-10-12

F1. Multi-block count does not match what was sent.
    Result #1 note: "2 other AIRUN block(s) in the same reply were NOT run."
    Result #2 note: "4 other AIRUN block(s) in the same reply were NOT run."
    Both replies carried exactly one fenced AIRUN block. Either the detector
    counts non-block content as blocks (false positive) or it splits the one
    block on an internal delimiter. Either way the count is wrong.

F2. Half-run semantics. When multi-block is detected the bridge runs the
    first block and silently drops the rest. DSA cannot see from the result
    which commands actually ran and had already told the operator "one block".
    The first block can write state before the second is discovered missing.
    Better: reject the whole reply, run nothing, return error text naming the
    extra blocks. DSA then re-emits as one block.

F3. cmd: echoes only the first line of the block. For a five-line block the
    operator cannot verify the rest matched. Echo the full block under the
    existing byte cap, or include a hash of the block.

F4. The multi-block check runs AFTER the first block has executed. Move it
    before the run so no partial work lands.

F5. The warning is only in the result note. If the DSA session has already
    composed its next reply when the note arrives, the note is lost. Add
    structured fields to every result: blocks_seen (int), blocks_run (int),
    so DSA can assert blocks_run == 1 on every call.

F6. Keep the current [TRUNCATED...] + out_truncated pattern and extend it the
    same way. Consistent, machine-readable, no prose.

F7. "One block per reply" is in the bridge spec but the DSA session prompt
    (section 0.5) only says "One command per call". The bridge accepts many
    commands per block but one block per reply. Restate the bridge's actual
    rule in the DSA prompt: one AIRUN block per reply, many lines per block.
```
