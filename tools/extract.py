"""Extract structured content from the .dc.html design prototypes into content/*.json.

The prototypes are the source of truth for copy, links and imagery. Parsing them
beats hand-transcription: 35 blog posts, 9 services and 9 product tiles.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "design_handoff_balance_home_organizing", "pages")
OUT = os.path.join(ROOT, "content")

def read(name):
    with open(os.path.join(PAGES, name), encoding="utf-8") as f:
        return f.read()

def unesc(s):
    return html.unescape(s or "").strip()

ANCHOR = re.compile(r'<a\s+href="([^"]+)"(.*?)</a>', re.S)
IMG = re.compile(r'<img\s+src="([^"]+)"[^>]*?alt="([^"]*)"', re.S)
HEADING = re.compile(r'<h[23][^>]*>(.*?)</h[23]>', re.S)
SPAN = re.compile(r'<span[^>]*>(.*?)</span>', re.S)
TAGS = re.compile(r'<[^>]+>')

def text(s):
    return unesc(TAGS.sub("", s))

def tiles(src, heading_re, require_image=True):
    """Every anchor in the doc that wraps a label (and usually an <img>)."""
    out = []
    for href, body in ANCHOR.findall(src):
        label = heading_re.search(body)
        if not label:
            continue
        m = IMG.search(body)
        if m is None and require_image:
            continue
        out.append({
            "href": href,
            "image": m.group(1) if m else None,
            "alt": unesc(m.group(2)) if m else "",
            "title": text(label.group(1)).replace(" →", "").replace("→", "").strip(),
        })
    return out

# --- blog -------------------------------------------------------------------
def posts(name):
    src = read(name)
    # Only the post grid: anchors pointing at /tips/
    return [t for t in tiles(src, HEADING, require_image=False)
            if "/tips/" in t["href"]]

# --- services ---------------------------------------------------------------
services = [t for t in tiles(read("Services.dc.html"), SPAN)
            if "/services/" in t["href"]]

# --- products ---------------------------------------------------------------
products = [t for t in tiles(read("Products.dc.html"), HEADING)
            if "amazon.com" in t["href"] and "/shop/balancehomeorganizing/\"" not in t["href"]]
products = [p for p in products if p["title"]]

# --- team -------------------------------------------------------------------
about = read("About.dc.html")
team = []
grid = about.split('About the Team', 1)[1].split('</section>', 1)[0]
for b in grid.split('<div style="text-align:center">')[1:]:
    m = IMG.search(b)
    h = re.search(r'<h3[^>]*>(.*?)</h3>', b, re.S)
    p = re.search(r'<p[^>]*>(.*?)</p>', b, re.S)
    if m and h:
        team.append({"image": m.group(1), "alt": unesc(m.group(2)),
                     "name": text(h.group(1)), "role": text(p.group(1)) if p else ""})

# --- process steps (from Process.dc.html, the canonical four) ---------------
def parse_steps(doc):
    steps = []
    for blk in re.findall(r'<figure[^>]*><img\s+src="([^"]+)"\s+alt="([^"]*)"[^>]*></figure>\s*<div style="position:absolute(.*?)</div>', doc, re.S):
        img, alt, body = blk
        h = re.search(r'<h3[^>]*>(.*?)</h3>', body, re.S)
        p = re.search(r'<p[^>]*>(.*?)</p>', body, re.S)
        a = re.search(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', body, re.S)
        if h:
            steps.append({"image": img, "alt": unesc(alt), "title": text(h.group(1)),
                          "body": text(p.group(1)) if p else "",
                          "cta_href": a.group(1) if a else "", "cta": text(a.group(2)) if a else ""})
    return steps

steps = parse_steps(read("Process.dc.html"))
home_steps = parse_steps(read("Home.dc.html"))

os.makedirs(OUT, exist_ok=True)
data = {"services.json": services, "products.json": products,
        "team.json": team, "process.json": steps,
        "process_home.json": home_steps}
for fname, payload in data.items():
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"{fname}: {len(payload)}")
