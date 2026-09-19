# Posting to @DiplonautHQ

Posts to X automatically from a queue, using the free API tier (write-only, 1,500
posts/month, $0 cost). It never invents or verifies anything itself: it only posts
entries someone has already added to `queue.json` with `"posted": false`.

## One-time setup (you do this part; Claude cannot)

1. Go to [developer.x.com](https://developer.x.com) and sign up for a developer account
   using the @DiplonautHQ account.
2. Create a Project and an App inside it.
3. In the App's settings, under **User authentication settings**, turn on OAuth 1.0a and
   set permissions to **Read and Write**.
4. Under **Keys and tokens**, generate:
   - API Key and API Key Secret
   - Access Token and Access Token Secret (make sure these are generated *after* you set
     permissions to Read and Write, or they'll be read-only)
5. In the `diplonaut-monitor` GitHub repository, go to **Settings → Secrets and variables
   → Actions → New repository secret**, and add four secrets with these exact names:
   - `X_API_KEY`
   - `X_API_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_SECRET`

   Paste each value directly into GitHub's secret field. Never paste these into a chat
   with Claude or anywhere else — they let anyone post as @DiplonautHQ.
6. Go to **Actions → Post verified changes to X → Run workflow** to test it. It should
   post the first queued item and print "Posted: ..." with no errors. That confirms the
   credentials work, and the schedule takes over from there.

## Adding a new post to the queue

Posts are plain text now -- no links, no source attribution, no flag/date formatting.
Just write the post exactly as it should appear, in the account's voice, and add it to
`queue.json`:

```json
{"text": "canada raises proof of funds to CA$23,448 (up from CA$20,635)\nstill cheaper than one semester of room and board in most of the us", "posted": false}
```

- Keep it under 280 characters (script truncates if not).
- `\n` for a line break within the post.
- The fact itself must still be true and checkable on diplonaut.com -- the account never
  links to prove it, but it always has to hold up if someone checks.

Only **one queued post goes out per scheduled run** (`MAX_POSTS_PER_RUN` in
`post_to_x.py`), so a backlog trickles out over days instead of firing all at once.
The schedule is 3 times a day (07:00, 13:00, 19:00 UTC) -- edit the cron in
`.github/workflows/post-to-x.yml` to change the pace. A push to `queue.json` does
**not** trigger an immediate post anymore, to keep the pace controlled by the schedule;
use **Actions → Run workflow** if you want one out sooner.
