# Diplonaut official-source monitor

Scans the official decision-makers behind the comparator every 3 hours (00:00, 03:00, 06:00 … 21:00 UTC) and opens a review task whenever something changes. It never publishes on its own: every change is verified on the official page first.

## The update rule

1. **Scan:** automatically, every 3 hours, every source in `sources.json` (immigration services, ministries, the White House, the State Department, and the US Federal Register through its public API).
2. **Flag:** any change opens a GitHub issue labeled *review*, showing the lines added and removed and the link to the official page.
3. **Verify:** open the official page and confirm the change. Never publish from news reports alone.
4. **Publish:**
   - *Same day* for anything affecting visa eligibility or entry, or taking effect within 30 days.
   - *Within 48 hours* for everything else.
   - Add it to the comparator's change log with its official source link; the homepage's "Latest official updates" follows automatically.
5. **Close** the issue with a note: published, or "not a rule change" (for example, a page redesign).

The homepage shows two separate facts, so it never overstates: when sources were last **scanned** (automatic) and when a rule change was last **verified** (by a person).

Each run also saves the European Central Bank's daily euro reference rates to `fx.json`, used for the comparator's currency conversions.

## Adding a destination

Add entries to `sources.json` with the official page to watch (for example the immigration service's student page and its news page). The next run records a baseline; changes are flagged from the run after.
