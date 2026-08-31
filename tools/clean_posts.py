"""Turn Squarespace's post bodies into clean semantic HTML and localise their images.

Squarespace wraps every paragraph in layers of layout divs with inline styles,
lazy-load attributes and srcsets. None of that survives; what is kept is the
prose, headings, lists, links, and figures.
"""
import html, json, os, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "content", "posts.json")
IMGDIR = os.path.join(ROOT, "site", "assets", "img", "posts")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# balancehomeorganizing.com links inside post bodies become internal links —
# this build is replacing that site. %ROOT% is substituted with the correct
# relative prefix when the page is rendered.
LOCAL = {
    "": "index.html", "/": "index.html",
    "/about": "about.html", "/services": "services.html",
    "/our-process": "process.html", "/products": "products.html",
    "/contact": "contact.html", "/consultation": "contact.html",
    "/join-our-team": "join-our-team.html", "/tips": "blog.html",
}
SLUGS = set()

def map_href(href):
    """Map a live-site URL to its local equivalent.

    Returns (href, mode) where mode is "external", "internal", or "unwrap".
    Anything on balancehomeorganizing.com with no local equivalent is unwrapped
    — the link text stays, the dead link goes. Squarespace hashtag archives are
    the main case; this build has no tag pages.
    """
    if not href.startswith(("http://", "https://")):
        return href, "internal"
    m = re.match(r"https?://(?:www\.)?balancehomeorganizing\.com(/[^?#]*)?", href)
    if not m:
        return href, "external"
    path = (m.group(1) or "/").rstrip("/")
    if path.startswith("/tips/"):
        slug = path.split("/tips/", 1)[1]
        return (f"%ROOT%blog/{slug}.html", "internal") if slug in SLUGS else (href, "unwrap")
    if path.startswith("/services/"):
        # no per-service pages in this build yet — send readers to the index
        return "%ROOT%services.html", "internal"
    if path in LOCAL:
        return "%ROOT%" + LOCAL[path], "internal"
    return href, "unwrap"

KEEP = {"p","h2","h3","h4","h5","ul","ol","li","strong","em","b","i","a",
        "br","blockquote","figure","figcaption","img","hr"}
UNWRAP = {"div","span","section","article","header","footer","main","font","small","u"}
DROP = {"style","script","svg","noscript","button","form","iframe"}
VOID = {"br","img","hr"}
DEMOTE = {"h1":"h2"}

class Cleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack, self.dropped, self.images = [], [], [], []
    def handle_startendtag(self, tag, attrs):
        # self-closing: never opens a region, so it must not push onto `dropped`
        if tag in DROP:
            return
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in DROP:
            self.dropped.append(tag); return
        if self.dropped: return
        tag = DEMOTE.get(tag, tag)
        if tag in UNWRAP: return
        if tag not in KEEP: return
        if tag == "img":
            src = a.get("data-src") or a.get("data-image") or a.get("src") or ""
            src = src.split("?")[0]
            if not src.startswith("http"): return
            self.images.append(src)
            alt = (a.get("alt") or "").strip()
            self.out.append(f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" decoding="async" />')
            return
        if tag == "a":
            href = (a.get("href") or "").strip()
            # some posts have Amazon embed code pasted into the link field, which
            # yields an href that is itself markup — drop the link, keep the text
            if not href or not re.match(r"^(https?://|/|#|mailto:|tel:)", href):
                self.out.append("<a-skip>"); self.stack.append("a-skip"); return
            href, mode = map_href(href)
            if mode == "unwrap":
                self.out.append("<a-skip>"); self.stack.append("a-skip"); return
            rel = ' target="_blank" rel="noopener"' if mode == "external" else ""
            self.out.append(f'<a href="{html.escape(href)}"{rel}>')
            self.stack.append("a"); return
        self.out.append(f"<{tag}>")
        if tag not in VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if self.dropped:
            # Unwind to and including the matching open tag. SVG children such as
            # <path> open without ever closing, so requiring an exact top-of-stack
            # match would leave the region open and swallow the rest of the post.
            if tag in self.dropped:
                while self.dropped and self.dropped.pop() != tag:
                    pass
            return
        tag = DEMOTE.get(tag, tag)
        if tag in UNWRAP or tag in VOID or tag not in KEEP: return
        if self.stack and self.stack[-1] == "a-skip" and tag == "a":
            self.stack.pop(); self.out.append("</a-skip>"); return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop(); self.out.append(f"</{tag}>")
    def handle_data(self, data):
        if self.dropped: return
        if data.strip() or (self.out and not self.out[-1].endswith(">")):
            self.out.append(html.escape(data, quote=False))
    def result(self):
        while self.stack:
            self.out.append(f"</{self.stack.pop()}>")
        s = "".join(self.out)
        s = re.sub(r"[ \t ]+", " ", s)
        s = re.sub(r"<p>\s*</p>", "", s)
        s = re.sub(r"<(h[2-5])>\s*</\1>", "", s)
        s = re.sub(r"<figure>\s*</figure>", "", s)
        s = s.replace("<a-skip>", "").replace("</a-skip>", "")
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()

def slugpart(url):
    base = os.path.basename(urllib.parse.urlparse(url).path)
    name, ext = os.path.splitext(urllib.parse.unquote(base))
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()[:40]
    return name or "img", (ext.lower() if ext.lower() in (".jpg",".jpeg",".png",".webp",".gif") else ".jpg")

def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return True
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
        if len(data) < 512: raise ValueError(f"too small ({len(data)}b)")
        open(dest, "wb").write(data); time.sleep(0.12)
        return True
    except Exception as e:
        print(f"  ! {url[:70]}: {e}", file=sys.stderr)
        return False

posts = json.load(open(POSTS, encoding="utf-8"))
SLUGS.update(p["slug"] for p in posts)
os.makedirs(IMGDIR, exist_ok=True)
seen, failed, total_imgs = {}, [], 0

for i, p in enumerate(posts):
    p["title"] = re.sub(r"\s+", " ", p["title"]).strip()
    c = Cleaner(); c.feed(p["body_html"]); body = c.result()
    for url in c.images:
        total_imgs += 1
        if url in seen: continue
        name, ext = slugpart(url)
        fname = f"{i:02d}-{name}{ext}"
        if fetch(url, os.path.join(IMGDIR, fname)):
            seen[url] = "%ROOT%assets/img/posts/" + fname
        else:
            failed.append(url)
    for url, local in seen.items():
        body = body.replace(f'src="{html.escape(url)}"', f'src="{local}"')
    # any image that could not be downloaded is dropped rather than left hotlinking
    body = re.sub(r'<img src="https?://[^"]*"[^>]*/>', "", body)
    # the listing thumbnail
    if p.get("thumb"):
        turl = p["thumb"].split("?")[0]
        name, ext = slugpart(turl)
        tname = f"thumb-{i:02d}-{name}{ext}"
        p["local_thumb"] = ("assets/img/posts/" + tname) if fetch(turl, os.path.join(IMGDIR, tname)) else None
    else:
        p["local_thumb"] = None
    p["body_clean"] = body
    p["words"] = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", body)))
    del p["body_html"]

json.dump(posts, open(POSTS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"{len(posts)} posts cleaned")
print(f"  body images: {total_imgs} refs, {len(seen)} unique downloaded, {len(failed)} failed")
print(f"  thumbnails : {sum(1 for p in posts if p.get('local_thumb'))}/{len(posts)}")
print(f"  words: min {min(p['words'] for p in posts)}, median "
      f"{sorted(p['words'] for p in posts)[len(posts)//2]}, max {max(p['words'] for p in posts)}")
thin=[p['title'] for p in posts if p['words']<80]
if thin: print(f"  thin posts ({len(thin)}): {thin}")
