"""Diplonaut X (Twitter) poster.

Posts verified rule changes to @DiplonautHQ. It never invents or verifies anything itself:
it only posts entries that a person has already added to queue.json with "posted": false,
using the X API v2 free tier (write-only, 1,500 posts/month, no cost). Runs on a schedule
via .github/workflows/post-to-x.yml.

Required GitHub repository secrets (Settings -> Secrets and variables -> Actions):
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
These come from a X Developer Portal app with "Read and Write" permission (OAuth 1.0a).
Never paste these values into chat, a file Claude can read, or anywhere but GitHub's own
secret fields.
"""
import hashlib, hmac, json, os, random, string, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "queue.json")
API_URL = "https://api.x.com/2/tweets"
SITE = "https://diplonaut.com"

FLAG = {  # ISO 3166-1 alpha-2 by destination id, for the regional-indicator flag emoji
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU", "de": "DE", "fr": "FR", "nl": "NL",
    "ie": "IE", "be": "BE", "ch": "CH", "at": "AT", "dk": "DK", "se": "SE", "jp": "JP", "kr": "KR",
}
SRC_NAME = {
    "gov.uk": "UK Home Office", "canada.ca": "IRCC, Canada", "federalregister.gov": "Federal Register",
    "whitehouse.gov": "White House", "state.gov": "US State Department", "studyinthestates.dhs.gov": "DHS",
    "enseignementsup-recherche.gouv.fr": "French Higher Education Ministry", "service-public.fr": "Service-Public.fr",
    "diplo.de": "German Federal Foreign Office", "ind.nl": "IND, Netherlands", "irishimmigration.ie": "Irish Immigration Service",
    "belgium.be": "Belgian Foreign Affairs", "ibz.be": "Belgian Immigration Office", "studyaustralia.gov.au": "Australian Government",
    "migration.gv.at": "Austrian government", "oead.at": "OeAD, Austria", "nyidanmark.dk": "SIRI, Denmark",
    "migrationsverket.se": "Swedish Migration Agency", "moj.go.jp": "Immigration Services Agency, Japan",
    "korea.kr": "Korean government", "immigration.go.kr": "Korea Ministry of Justice", "sem.admin.ch": "Swiss SEM",
}

def flag_emoji(dest):
    cc = FLAG.get(dest)
    if not cc:
        return "\U0001F310"  # globe, if a destination has no mapping yet
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in cc)

def src_name(url):
    host = urllib.parse.urlparse(url).netloc.replace("www.", "")
    for k, v in SRC_NAME.items():
        if k in host:
            return v
    return host

def fmt_date(iso):
    import datetime
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day} {d.strftime('%b')} {d.year}"
    except Exception:
        return iso

def build_text(change):
    # New voice: plain text, no links, no source attribution -- just the fact, deadpan.
    # A queue entry can set "text" directly for full control over the joke/phrasing.
    if change.get("text"):
        return change["text"][:280]
    # Fallback for older-style entries that only have title/date/src/dest.
    flag = flag_emoji(change["dest"])
    date = fmt_date(change.get("date", ""))
    when = f"from {date}" if change.get("upcoming") else date
    text = f'{flag} {change["title"]} ({when}).'
    return text[:280]

def oauth1_header(method, url, params, api_key, api_secret, token, token_secret):
    oauth = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }
    all_params = {**oauth, **params}
    enc = lambda s: urllib.parse.quote(str(s), safe="~")
    param_str = "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(all_params.items()))
    base = "&".join([method.upper(), enc(url), enc(param_str)])
    signing_key = f"{enc(api_secret)}&{enc(token_secret)}"
    signature = hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    import base64
    oauth["oauth_signature"] = base64.b64encode(signature).decode()
    return "OAuth " + ", ".join(f'{enc(k)}="{enc(v)}"' for k, v in sorted(oauth.items()))

def post_tweet(text, api_key, api_secret, token, token_secret):
    header = oauth1_header("POST", API_URL, {}, api_key, api_secret, token, token_secret)
    body = json.dumps({"text": text}).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST",
                                  headers={"Authorization": header, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

MAX_POSTS_PER_RUN = 1  # trickle the queue out over days rather than dumping it all at once

def main():
    api_key = os.environ["X_API_KEY"]; api_secret = os.environ["X_API_SECRET"]
    token = os.environ["X_ACCESS_TOKEN"]; token_secret = os.environ["X_ACCESS_SECRET"]
    queue = json.load(open(QUEUE, encoding="utf-8"))
    posted_any = False
    posted_this_run = 0
    for change in queue:
        if change.get("posted"):
            continue
        if posted_this_run >= MAX_POSTS_PER_RUN:
            break
        text = build_text(change)
        try:
            result = post_tweet(text, api_key, api_secret, token, token_secret)
            change["posted"] = True
            change["posted_at"] = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
            change["tweet_id"] = result.get("data", {}).get("id")
            print("Posted:", text.replace("\n", " | "))
            posted_any = True
            posted_this_run += 1
        except Exception as e:
            print("FAILED to post:", change.get("title"), "-", f"{type(e).__name__}: {e}")
    if posted_any:
        json.dump(queue, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        print("Nothing new in the queue.")

if __name__ == "__main__":
    main()
