# Posting to @DiplonautHQ

This pipeline is for **one thing only: fresh, verified official rule changes** the
monitor detects -- the kind where posting promptly actually matters. Everything else
(cost comparisons, domestic tuition stats, anything compiled rather than breaking) gets
posted by hand through X's normal interface, which is free. Paying ~$0.015 a post only
makes sense when speed has real value; static facts don't need it.

## What goes in the automated queue

Only entries tied to a change the monitor just confirmed -- something that happened
recently and is worth posting the moment it's verified. Add it to `queue.json` as
`"text": "...", "posted": false`, following the same rules as always: proper sentence
case, no unexplained jargon, the source named in prose, no links, neutral tone (no
emotionally-loaded emoji or editorializing words -- see prior notes on this if unsure).

## What gets posted manually instead

Comparisons, cost stats, "stay or go" content, and anything else compiled from research
rather than a live monitor detection. Write it, check it against the same style rules,
and post it yourself on X whenever convenient -- no queue entry, no cost. Claude can
still draft this content on request; it just doesn't go through this pipeline.

## One-time setup

Already done: the app, OAuth 1.0a keys, GitHub secrets, and a paid credit balance are
all in place. If credits ever run out, add more in the X Developer Console under
Billing -> Credits.

Only **one queued post goes out per scheduled run** (`MAX_POSTS_PER_RUN` in
`post_to_x.py`), so if several fresh changes land at once they trickle out over days
rather than firing all at once. The schedule is 3 times a day (07:00, 13:00, 19:00 UTC)
-- it simply does nothing on a run with an empty queue, at no cost. Use
**Actions -> Run workflow** to post one immediately instead of waiting.
