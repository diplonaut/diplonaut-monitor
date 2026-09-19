# Posting to @DiplonautHQ

Fully automated. Everything -- fresh monitor-detected changes and researched
comparisons/stats alike -- goes through this queue and posts on schedule, using the X
API's pay-per-use billing (paid via credits in the X Developer Console, roughly $0.015
a plain-text post; a thread costs one charge per part). At the current pace this runs
about $0.50-$1/month -- cheap enough that manual posting isn't worth the time it costs.

## Two entry types

**Single post:**
```json
{"text": "Canada raises proof of funds to CA$23,448, up from CA$20,635, according to IRCC.\nStill cheaper than one semester of room and board in most of the US.", "posted": false}
```

**Thread** (a connected reply chain -- use for a story with real depth, like a court
case or a multi-part policy change). All parts post together in one run, chained as
replies, and count as a single item against `MAX_POSTS_PER_RUN`:
```json
{"thread": ["First tweet text.", "Second tweet text, posted as a reply to the first.", "Third tweet, replying to the second."], "posted": false}
```

## Writing rules (apply to every part of every entry)

- **Proper sentence case.** Capitalize the first word and every proper noun and
  acronym -- "UK," "US," "IRCC," not "uk," "us," "irc." This is a news brief, not a
  text message.
- **Specific, not vague.** Name the actual before-and-after figures and the effective
  date when there's a rule change -- "rose from £524 to £558, effective April 8,
  2026," not "the fee went up." Verify these, don't estimate them.
- **No unexplained jargon.** Spell out an unfamiliar term in a few words the first
  time it appears, so a reader with zero background can still follow it on one read.
- **Name the real source in prose, no links.** "according to the UK Home Office,"
  "per the College Board," "DOJ says." No claim goes out unattributed, and no post
  links out -- the source is a phrase, not a URL.
- **Neutral tone, no emotionally-loaded emoji or editorializing words.** No skulls,
  no sarcastic winks, no "unfortunately." State the fact plainly; a dry observational
  aside is fine ("that's not a fee increase, that's a subscription tier upgrade"), a
  claim about someone's intent or state of mind is not, unless a court or official
  source actually said it. Let the numbers carry the weight.
- **Under 280 characters per part** (the script truncates single posts if not; check
  thread parts yourself since they aren't truncated automatically).
- **The fact must hold up.** True and checkable on diplonaut.com or the named source,
  even though the post itself never links there.

## Pace

One queue item goes out per scheduled run (`MAX_POSTS_PER_RUN` in `post_to_x.py`) --
a thread counts as one item regardless of how many parts it has. The schedule runs
once a day at 14:00 UTC; edit the cron in `.github/workflows/post-to-x.yml` to change
it. Use **Actions -> Run workflow** to post the next item immediately instead of
waiting. A run with an empty queue does nothing, at no cost.

When the queue runs low, ask Claude to research and verify a fresh batch -- the same
process used to build this one: real sources, real dates, real before/after figures.
