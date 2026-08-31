"""Import the live site's service detail pages and the consultation page.

These exist on balancehomeorganizing.com but were never in the design handoff.
This build replaces that site, so they have to come across too.
"""
import html, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content")
SITE = "https://balancehomeorganizing.com"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

SERVICE_SLUGS = [
    "kitchen-organization", "playroom-organizing", "closet-organization",
    "moving-organization", "home-office-organization", "garage-organization",
    "nursery-organization", "bedroom-bathroom-organizing",
]

def get(path):
    req = urllib.request.Request(SITE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")

def main_of(doc):
    m = re.search(r"<main[^>]*>(.*?)</main>", doc, re.S)
    core = m.group(1) if m else doc
    return re.sub(r"<(script|style)[^>]*>.*?</\1>", "", core, flags=re.S)

def txt(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

def paragraphs(core):
    out = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", core, re.S):
        t = txt(p)
        if t and t.lower() not in {"previous", "next"} and t not in out:
            out.append(t)
    return out

def images(core):
    urls = []
    for u in re.findall(r'data-src="([^"]+)"', core):
        u = u.split("?")[0]
        if "squarespace-cdn.com" in u and "memberAccountAvatars" not in u and u not in urls:
            urls.append(u)
    return urls

services = []
print("service detail pages:")
for slug in SERVICE_SLUGS:
    try:
        core = main_of(get("/services/" + slug))
    except Exception as e:
        print(f"  ! {slug}: {e}", file=sys.stderr); continue
    heads = [txt(h) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", core, re.S)] or \
            [txt(h) for h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", core, re.S)]
    paras = paragraphs(core)
    services.append({
        "slug": slug,
        "title": heads[0] if heads else slug.replace("-", " ").title(),
        "tagline": paras[0] if paras else "",
        "body": paras[1] if len(paras) > 1 else "",
        "images": images(core),
        "live_url": f"{SITE}/services/{slug}",
    })
    print(f"  {slug:<30} {len(images(core))} images  \"{(paras[0] if paras else '')[:44]}\"")
    time.sleep(0.35)

print("\nconsultation page:")
core = main_of(get("/consultation"))
paras = paragraphs(core)
heads = [txt(h) for h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", core, re.S)]
booking = [h for h in re.findall(r'href="([^"]+)"', core)
           if any(k in h.lower() for k in ("calendly", "acuity", "squarespace-scheduling",
                                           "appointment", "schedul", "mailto", "tel:"))]
consultation = {
    "title": heads[0] if heads else "Book a Virtual Consultation",
    "headings": heads,
    "paragraphs": paras,
    "booking_links": list(dict.fromkeys(booking)),
    "images": images(core),
    "live_url": SITE + "/consultation",
}
for h in heads: print(f"  h: {h}")
for p in paras: print(f"  p: {p[:110]}")
print(f"  booking links: {consultation['booking_links'] or 'none found'}")

json.dump(services, open(os.path.join(OUT, "services_detail.json"), "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
json.dump(consultation, open(os.path.join(OUT, "consultation.json"), "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print(f"\n{len(services)} service pages + consultation written to content/")

# --- localise the imagery -----------------------------------------------------
IMGDIR = os.path.join(ROOT, "site", "assets", "img", "services")
os.makedirs(IMGDIR, exist_ok=True)

def slugpart(url):
    base = os.path.basename(urllib.parse.urlparse(url).path)
    name, ext = os.path.splitext(urllib.parse.unquote(base))
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()[:36]
    return (name or "img"), (ext.lower() if ext.lower() in (".jpg", ".jpeg", ".png", ".webp") else ".jpg")

def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return True
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
            data = r.read()
        if len(data) < 512:
            raise ValueError("too small")
        open(dest, "wb").write(data)
        time.sleep(0.12)
        return True
    except Exception as e:
        print(f"  ! {url[:60]}: {e}", file=sys.stderr)
        return False

got = 0
for s in services:
    local = []
    for n, u in enumerate(s["images"]):
        nm, ext = slugpart(u)
        fname = f"{s['slug']}-{n}-{nm}{ext}"
        if download(u, os.path.join(IMGDIR, fname)):
            local.append("assets/img/services/" + fname); got += 1
    s["local_images"] = local
json.dump(services, open(os.path.join(OUT, "services_detail.json"), "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print(f"{got} service images downloaded to site/assets/img/services/")
