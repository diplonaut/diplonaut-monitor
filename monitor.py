"""Diplonaut official-source monitor.

Runs twice a day (see .github/workflows/monitor.yml). For each official source it
fingerprints the page text, or queries the US Federal Register API, compares with the
previous run, and reports what changed. It never publishes anything: every change is a
candidate that a person verifies before the comparator is updated.
"""
import hashlib, html, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
STATUS = os.path.join(HERE, "status.json")
REPORT = os.path.join(HERE, "report.md")
UA = "Mozilla/5.0 (compatible; DiplonautMonitor/1.1; +https://diplonaut.com)"

def fetch(url, timeout=30):
    if url.startswith("file://"):
        return open(url[7:], encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en,fr;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")

def page_text(raw):
    """Visible text only: drop scripts, styles, navigation and footers, then normalise spacing."""
    raw = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", " ", raw)
    main = re.search(r"(?is)<main\b.*?</main>", raw)
    raw = main.group(0) if main else raw
    text = html.unescape(re.sub(r"(?s)<[^>]+>", "\n", raw))
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    return [l for l in lines if l]


FX = os.path.join(HERE, "fx.json")
FX_CODES = ["USD", "GBP", "CHF", "CAD", "AUD", "DKK", "SEK", "JPY", "KRW"]

def ecb_rates():
    """European Central Bank daily reference rates (1 EUR = x units), converted to 'value of 1 unit in EUR'."""
    xml = fetch("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")
    day = re.search(r"time=['\"](\d{4}-\d{2}-\d{2})['\"]", xml)
    rates = dict(re.findall(r"currency=['\"]([A-Z]{3})['\"]\s+rate=['\"]([0-9.]+)['\"]", xml))
    to_eur = {"EUR": 1.0}
    for code in FX_CODES:
        if code in rates and float(rates[code]) > 0:
            to_eur[code] = round(1 / float(rates[code]), 6)
    return {"date": day.group(1) if day else None, "source": "European Central Bank euro reference rates", "to_eur": to_eur}

def fingerprint(lines):
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()

def federal_register(terms, since):
    """New documents mentioning student-visa terms from DHS or the State Department."""
    found = {}
    for term in terms:
        q = urllib.parse.urlencode([
            ("conditions[term]", term),
            ("conditions[agencies][]", "homeland-security-department"),
            ("conditions[agencies][]", "state-department"),
            ("conditions[publication_date][gte]", since),
            ("order", "newest"), ("per_page", "20"),
            ("fields[]", "title"), ("fields[]", "html_url"), ("fields[]", "publication_date"),
            ("fields[]", "type"), ("fields[]", "document_number")])
        data = json.loads(fetch("https://www.federalregister.gov/api/v1/documents.json?" + q))
        for d in data.get("results", []):
            found[d["document_number"]] = d
    return list(found.values())

def main():
    now = datetime.now(timezone.utc)
    cfg = json.load(open(os.path.join(HERE, "sources.json"), encoding="utf-8"))
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    changes, failures, ok = [], [], 0
    for s in cfg["sources"]:
        prev = state.get(s["id"], {})
        try:
            if s["type"] == "federal_register":
                since = prev.get("since", now.strftime("%Y-%m-01"))
                seen = set(prev.get("seen", []))
                docs = federal_register(s["terms"], since)
                new = [d for d in docs if d["document_number"] not in seen]
                if prev and new:
                    for d in new:
                        changes.append({"source": s["id"], "dest": s["dest"], "name": s["name"],
                                        "title": d["title"], "url": d["html_url"],
                                        "date": d["publication_date"], "kind": d["type"]})
                state[s["id"]] = {"since": since, "seen": sorted(seen | {d["document_number"] for d in docs})[-500:],
                                  "checked": now.isoformat()}
            else:
                lines = page_text(fetch(s["url"]))
                fp = fingerprint(lines)
                if prev.get("fp") and prev["fp"] != fp:
                    old = set(prev.get("lines", []))
                    added = [l for l in lines if l not in old][:12]
                    removed = [l for l in prev.get("lines", []) if l not in set(lines)][:12]
                    changes.append({"source": s["id"], "dest": s["dest"], "name": s["name"],
                                    "url": s["url"], "added": added, "removed": removed})
                state[s["id"]] = {"fp": fp, "lines": lines[:3000], "checked": now.isoformat()}
            ok += 1
        except Exception as e:  # a failing source is reported, never silently skipped
            failures.append({"source": s["id"], "name": s["name"], "url": s.get("url", "Federal Register API"),
                             "error": f"{type(e).__name__}: {e}"[:200]})
    fx_date = None
    try:
        fx = ecb_rates()
        if len(fx["to_eur"]) > 5:
            json.dump(fx, open(FX, "w", encoding="utf-8"), indent=1)
            fx_date = fx["date"]
    except Exception as e:
        failures.append({"source": "ecb-fx", "name": "European Central Bank exchange rates", "url": "https://www.ecb.europa.eu", "error": f"{type(e).__name__}: {e}"[:200]})
    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    status = {"last_scan_utc": now.strftime("%Y-%m-%dT%H:%MZ"), "sources_total": len(cfg["sources"]),
              "sources_ok": ok, "sources_failed": len(failures),
              "pending_changes": len(changes), "fx_date": fx_date, "destinations": sorted({s["dest"] for s in cfg["sources"]})}
    json.dump(status, open(STATUS, "w", encoding="utf-8"), indent=1)
    out = [f"# Official-source scan, {now:%d %B %Y %H:%M} UTC", "",
           f"{ok} of {len(cfg['sources'])} sources checked. {len(changes)} possible change(s). {len(failures)} source(s) unreachable.", ""]
    for c in changes:
        out.append(f"## {c['dest']}: {c.get('title') or c['name']}")
        out.append(f"Source: {c['url']}")
        for l in c.get("added", []): out.append(f"+ {l}")
        for l in c.get("removed", []): out.append(f"- {l}")
        out.append("")
    if failures:
        out.append("## Sources that could not be checked")
        out += [f"- {f['name']} ({f['url']}): {f['error']}" for f in failures]
    out += ["", "Verify each change on the official page before updating the comparator."]
    open(REPORT, "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
