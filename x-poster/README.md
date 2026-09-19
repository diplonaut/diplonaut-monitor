# Posting to @DiplonautHQ

Posts verified rule changes to X automatically, using the free API tier (write-only,
1,500 posts/month, $0 cost). It never verifies anything itself: it only posts entries
someone has already added to `queue.json` with `"posted": false`.

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
6. Go to **Actions → Post verified changes to X → Run workflow** to test it. With an
   empty queue (all entries already marked posted), it should run and print "Nothing new
   in the queue," with no errors. That confirms the credentials work.

## Adding a new change to post

Whenever a change is verified and added to diplonaut.com's Live changes feed, add the
same entry to `queue.json` with `"posted": false`:

```json
{"date":"2026-11-30","dest":"uk","upcoming":true,"title":"UK raises the student living-cost requirement","src":"https://www.gov.uk/..."}
```

- `dest`: the two-letter destination id used elsewhere in the monitor (`uk`, `us`, `ca`, `fr`, `de`, `au`, `jp`, `kr`, `nl`, `ie`, `be`, `ch`, `at`, `dk`, `se`)
- `upcoming`: `true` if the change hasn't taken effect yet (posts as "from [date]"), omit or `false` if it already has
- `src`: the official source link

The next scheduled run (every 3 hours) or an immediate push to `queue.json` will post it
and mark it `"posted": true` automatically.
