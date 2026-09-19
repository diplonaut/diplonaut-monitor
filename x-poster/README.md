# Posting to @DiplonautHQ

Posts to X automatically from a queue, using the X API's pay-per-use billing (paid via
credits purchased in the X Developer Console -- roughly $0.015 per plain-text post). It
never invents or verifies anything itself: it only posts entries someone has already
added to `queue.json` with `"posted": false`.

## One-time setup

Already done: the app, OAuth 1.0a keys, GitHub secrets, and a paid credit balance are
all in place. If credits ever run out, add more in the X Developer Console under
Billing -> Credits -- posting will resume automatically once the balance is positive.

## Writing a new post

Write the post exactly as it should appear and add it to `queue.json` as `"text"`:

```json
{"text": "Canada raises proof of funds to CA$23,448, up from CA$20,635, according to IRCC.\nStill cheaper than one semester of room and board in most of the US.", "posted": false}
```

Rules, all of them non-negotiable:

- **Proper sentence case.** Capitalize the first word and every proper noun and
  acronym -- "UK," "US," "IRCC," "Canada," not "uk," "us," "canada." This is a news
  brief, not a text message.
- **No unexplained jargon.** If a term isn't something a general reader already knows
  (a visa category's specific name, an agency's internal shorthand), spell out what it
  means in a few words the first time it appears -- e.g. "the Graduate Route (its
  post-study work visa)" rather than just "the Graduate Route." A reader with zero
  background in immigration policy should still follow the post on one read.
- **Name the real source in prose, no links.** "according to the UK Home Office,"
  "per the College Board," "IRCC confirms." No claim goes out unattributed, and no
  post links out -- the source is a phrase, not a URL.
- **Under 280 characters** (the script truncates if not; check before adding).
- **The fact must hold up.** It has to be true and checkable on diplonaut.com, even
  though the post itself never links there.

Only **one queued post goes out per scheduled run** (`MAX_POSTS_PER_RUN` in
`post_to_x.py`), so a backlog trickles out over days instead of firing all at once.
The schedule is 3 times a day (07:00, 13:00, 19:00 UTC) -- edit the cron in
`.github/workflows/post-to-x.yml` to change the pace. Use **Actions -> Run workflow**
to post one immediately instead of waiting for the next scheduled slot.
