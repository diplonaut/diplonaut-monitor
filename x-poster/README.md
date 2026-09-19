# Posting to @DiplonautHQ

Posts to X automatically from a queue, using the X API's pay-per-use billing (paid via
credits purchased in the X Developer Console -- roughly $0.015 per plain-text post). It
never invents or verifies anything itself: it only posts entries someone has already
added to `queue.json` with `"posted": false`.

## One-time setup

Already done: the app, OAuth 1.0a keys, GitHub secrets, and a paid credit balance are
all in place. If credits ever run out, add more in the X Developer Console under
Billing -> Credits -- posting will resume automatically once the balance is positive.

## Adding a new post to the queue

Posts are plain text -- no links -- but every post names its source in the sentence
itself, journalist-style: "according to the UK Home Office," "per the College Board,"
"IRCC confirms." No claim goes out unattributed. Write the post exactly as it should
appear and add it to `queue.json`:

```json
{"text": "canada raises proof of funds to CA$23,448 (up from CA$20,635), according to IRCC\nstill cheaper than one semester of room and board in most of the us", "posted": false}
```

- Keep it under 280 characters (script truncates if not).
- `\n` for a line break within the post.
- Name the actual source (the agency, ministry, or report) somewhere in the text --
  not as a link, just as a phrase, the way a news article would attribute a claim.
- The fact itself must still be true and checkable on diplonaut.com -- the account
  never links to prove it, but it always has to hold up if someone checks.

Only **one queued post goes out per scheduled run** (`MAX_POSTS_PER_RUN` in
`post_to_x.py`), so a backlog trickles out over days instead of firing all at once.
The schedule is 3 times a day (07:00, 13:00, 19:00 UTC) -- edit the cron in
`.github/workflows/post-to-x.yml` to change the pace. Use **Actions -> Run workflow**
to post one immediately instead of waiting for the next scheduled slot.
