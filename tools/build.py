"""Build the Balance Home Organizing site into site/*.html.

Shared chrome (head/nav/footer) lives here; repeating content (blog posts,
services, products, team, process steps) is rendered from content/*.json so the
35+ posts stay data, not hand-written markup.
"""
import datetime, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
SITE = os.path.join(ROOT, "site")

def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)

SERVICES     = load("services.json")
PRODUCTS     = load("products.json")
TEAM         = load("team.json")
STEPS        = load("process.json")
STEPS_HOME   = load("process_home.json")
IMAGES       = load("images.json")
BLOG         = load("posts.json")          # all 37 posts, newest first
SERVICE_PAGES= load("services_detail.json")
CONSULT      = load("consultation.json")
PER_PAGE     = 20

def e(s):
    return html.escape(s or "", quote=True)

def img(path, alt, **attrs):
    if not path:
        return ""
    extra = "".join(f' {k.replace("_", "-")}="{e(str(v))}"' for k, v in attrs.items())
    return f'<img src="{e(path)}" alt="{e(alt)}" loading="lazy" decoding="async"{extra} />'

# --- site chrome ------------------------------------------------------------

# The live site's nav omits Home — the logo carries it.
NAV_LINKS = [
    ("services.html",    "Services"),
    ("process.html",     "Process"),
    ("about.html",       "About"),
    ("blog.html",        "Blog"),
    ("products.html",    "Favorite Products"),
]

CONTACT = {
    "email": "megan@balancehomeorganizing.com",
    "phone_display": "760.571.9292",
    "phone_href": "tel:7605719292",
}

SOCIAL = [
    ("https://www.instagram.com/balancehomeorganizing/", "Instagram", "assets/icons/instagram.svg"),
    ("https://www.yelp.com/biz/balance-home-organizing-san-marcos", "Yelp", "assets/icons/yelp.svg"),
    ("https://g.page/balance-home-organizing?share", "Google Maps", "assets/icons/google.svg"),
]

def nav(current, overlay=False, prefix=""):
    cls = "nav nav--overlay" if overlay else "nav"
    out = [f'<nav class="{cls}" aria-label="Main">']
    out.append(f'<a href="{prefix}index.html" class="nav-brand" aria-label="Balance Home Organizing — home">'
               f'{img(prefix + IMAGES["logo"], "Balance Home Organizing")}</a>')
    out.append('<div class="nav-links">')
    for href, label in NAV_LINKS:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{prefix}{href}"{cur}>{label}</a>')
    out.append("</div>")
    cur = ' aria-current="page"' if current == "consultation.html" else ""
    out.append(f'<a href="{prefix}consultation.html" class="btn btn-primary"{cur}>Book Consultation</a>')
    out.append("</nav>")
    return "\n".join(out)

def footer(prefix=""):
    links = "".join(
        f'<a href="{prefix}{h}">{l}</a>' for h, l in [
            ("index.html", "Home"), ("services.html", "Services"),
            ("process.html", "Our Process"), ("products.html", "Products"),
            ("contact.html", "Contact Us"), ("join-our-team.html", "Join our Team"),
        ])
    social = "".join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="{l}">'
        f'<img src="{prefix}{i}" alt="" width="20" height="20" /></a>'
        for h, l, i in SOCIAL)
    return f"""<footer class="site-footer">
  <div class="site-footer__inner">
    <div style="max-width:320px">
      <div class="brand">Balance Home Organizing</div>
      <p>Professional Organizers in San Marcos, CA<br />Serving Greater San Diego County</p>
    </div>
    <div>
      <p>Location: San Marcos, CA<br />
         Phone: <a href="{CONTACT['phone_href']}">{CONTACT['phone_display']}</a><br />
         Email: <a href="mailto:{CONTACT['email']}">{CONTACT['email']}</a></p>
    </div>
    <nav class="footer-links" aria-label="Footer">{links}</nav>
    <div class="footer-social">{social}</div>
  </div>
</footer>"""

def page(filename, title, description, body, current, warm=False, overlay_nav=False, prefix=""):
    body_cls = ' class="theme-warm"' if warm else ""
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(title)}</title>
<meta name="description" content="{e(description)}" />
<link rel="icon" href="{prefix}{IMAGES.get('favicon', 'assets/img/favicon.ico')}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" />
<link rel="stylesheet" href="{prefix}assets/css/styles.css" />
</head>
<body{body_cls}>
<a class="skip-link" href="#main">Skip to content</a>
{nav(current, overlay_nav, prefix) if not overlay_nav else ""}
<main id="main">
{body}
</main>
{footer(prefix)}
<script src="{prefix}assets/js/forms.js" defer></script>
</body>
</html>
"""
    dest = os.path.join(SITE, filename)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(doc)
    return filename

# --- shared sections --------------------------------------------------------

def cta_band(prefix=""):
    return f"""<section class="cta-band">
  <figure>{img(prefix + IMAGES['cta-jars'], '', style='object-position:center')}</figure>
  <div class="cta-band__inner">
    <h2>Let&rsquo;s Get Organized!</h2>
    <p>Book a free, virtual 30 minute consultation to discuss your needs and goals!</p>
    <a href="{prefix}contact.html" class="btn btn-primary">Get Started</a>
  </div>
</section>"""

def step_rows(steps):
    out = []
    for s in steps:
        cta = ""
        if s.get("cta"):
            href = {"./Services.dc.html": "services.html",
                    "./Contact.dc.html": "contact.html",
                    "./About.dc.html": "about.html"}.get(s["cta_href"], "contact.html")
            cta = f'<a href="{href}" class="btn btn-primary">{e(s["cta"])}</a>'
        out.append(f"""<div class="panel-row">
  <figure>{img(s['local_image'], s['alt'])}</figure>
  <div class="panel">
    <h3>{e(s['title'])}</h3>
    <p>{e(s['body'])}</p>
    {cta}
  </div>
</div>""")
    return "\n".join(out)

def post_date(p):
    return datetime.datetime.utcfromtimestamp(p["published_ms"] / 1000)

def post_url(p, prefix=""):
    return f'{prefix}blog/{p["slug"]}.html'

def blog_grid(posts, prefix=""):
    cards = []
    for p in posts:
        thumb = p.get("local_thumb")
        figure = (f'<figure>{img(prefix + thumb, p["title"])}</figure>' if thumb
                  else '<figure aria-hidden="true"></figure>')
        cards.append(f"""<a href="{post_url(p, prefix)}">
  {figure}
  <h2>{e(p['title'])}</h2>
</a>""")
    return f'<div class="post-grid">\n{chr(10).join(cards)}\n</div>'

def term_slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "untagged"

def collect_terms():
    tags, cats = {}, {}
    for p in BLOG:
        for t in p.get("tags") or []:
            tags.setdefault(t, []).append(p)
        for c in p.get("categories") or []:
            cats.setdefault(c, []).append(p)
    return tags, cats

TAGS, CATEGORIES = collect_terms()

def terms_block(p):
    links = []
    for kind, key in (("category", "categories"), ("tag", "tags")):
        for t in p.get(key) or []:
            links.append(f'<a href="{kind}/{term_slug(t)}.html">{e(t)}</a>')
    return f'<p class="post__terms">{"".join(links)}</p>' if links else ""

def build_archives():
    n = 0
    for kind, terms in (("tag", TAGS), ("category", CATEGORIES)):
        for term, items in sorted(terms.items()):
            body = f"""<div class="wrap">
  <hr class="hr" />
  <section class="section--tight">
    <p class="archive__kicker">{kind.capitalize()}</p>
    <h1 class="archive__title">{e(term)}</h1>
    <p class="archive__count">{len(items)} post{'s' if len(items) != 1 else ''}</p>
    {blog_grid(items, prefix='../../')}
    <div class="pager"><a href="../../blog.html" class="btn btn-ghost">&larr; All tips</a></div>
  </section>
</div>"""
            page(f"blog/{kind}/{term_slug(term)}.html",
                 f"{term} — Balance Home Organizing",
                 f"Organizing tips tagged {term} from Balance Home Organizing.",
                 body, "blog.html", warm=True, prefix="../../")
            n += 1
    return n

def build_post(p, newer, older):
    d = post_date(p)
    nav_links = []
    if newer:
        nav_links.append(f'<a href="{newer["slug"]}.html" rel="prev">&larr; {e(newer["title"])}</a>')
    if older:
        nav_links.append(f'<a href="{older["slug"]}.html" rel="next">{e(older["title"])} &rarr;</a>')
    adjacent = ('<nav class="post-nav" aria-label="More posts">' + "".join(nav_links) + "</nav>") if nav_links else ""
    body = f"""<article class="post">
  <header class="post__header">
    <p class="post__meta"><time datetime="{d.strftime('%Y-%m-%d')}">{d.strftime('%B %-d, %Y')}</time>
      {'&middot; ' + e(p['author']) if p.get('author') else ''}</p>
    <h1>{e(p['title'])}</h1>
  </header>
  <div class="post__body">
{p['body_clean'].replace('%ROOT%', '../')}
  </div>
  {terms_block(p)}
  <p class="post__back"><a href="../blog.html">&larr; All tips</a></p>
  {adjacent}
</article>

{cta_band(prefix='../')}"""
    return page(f"blog/{p['slug']}.html",
                f"{p['title']} — Balance Home Organizing",
                (p.get("excerpt") or p["title"])[:180],
                body, "blog.html", prefix="../")

# --- pages ------------------------------------------------------------------

def build_home():
    body = f"""<section class="hero" style="position:relative;width:100%;min-height:760px;overflow:hidden">
  <div style="position:absolute;inset:0">{img(IMAGES['home-hero'], 'Organized home interior')}</div>
  <div style="position:absolute;inset:0;background:rgba(255,255,255,0.72)"></div>
  {nav('index.html', overlay=True)}
  <div style="position:relative;max-width:900px;margin:0 auto;padding:clamp(60px,10vh,120px) var(--edge) 0;text-align:center">
    <h1 style="font-size:clamp(34px,4.6vw,58px);line-height:1.18">Is your home clutter causing you stress?</h1>
    <p style="font-size:17px;max-width:56ch;margin:var(--space-4) auto 0;color:color-mix(in srgb, var(--color-text) 82%, transparent)">We are a team of professional organizers, located in San Diego, dedicated to bringing balance and simplicity in your home through organized living.</p>
    <div style="display:flex;gap:var(--space-3);flex-wrap:wrap;justify-content:center;margin-top:var(--space-6)">
      <a href="services.html" class="btn btn-primary">See Services</a>
    </div>
  </div>
</section>

<div class="wrap">
  <hr class="hr" />

  <section class="panel-row" style="margin-block:var(--space-2)">
    <figure>{img(IMAGES['home-help'], 'Organized living room')}</figure>
    <div class="panel panel--wide">
      <h2>We are here to help&hellip;</h2>
      <p>We understand the struggle and commitment it takes to become organized, that&rsquo;s why we&rsquo;re here to help. We want the process of getting organized to be a meaningful and stress-free experience.</p>
    </div>
  </section>

  <hr class="hr" />

  <section class="section">
    <h2 class="section__title">Our Process</h2>
    {step_rows(STEPS_HOME)}
  </section>
</div>

{cta_band()}"""
    return page("index.html", "Balance Home Organizing — Professional Home Organizers in San Diego County",
                "Professional home organizers in San Marcos, CA, serving greater San Diego County. "
                "Book a free virtual consultation to bring balance and simplicity to your home.",
                body, "index.html", overlay_nav=True)

def build_services():
    detail = {d["slug"]: d for d in SERVICE_PAGES}
    tiles = []
    for s in SERVICES:
        slug = s["href"].rstrip("/").split("/")[-1]
        href = f"services/{slug}.html" if slug in detail else s["href"]
        ext = "" if slug in detail else ' target="_blank" rel="noopener"'
        tiles.append(f"""<a href="{e(href)}"{ext} class="center">
  <figure>{img(s['local_image'], s['alt'])}</figure>
  <span class="tile-label">{e(s['title'])}</span>
</a>""")
    body = f"""<div class="wrap">
  <section class="section">
    <h1 class="visually-hidden">Services</h1>
    <div class="circle-grid">
{chr(10).join(tiles)}
    </div>
  </section>
</div>"""
    return page("services.html", "Services — Balance Home Organizing",
                "Kitchen, pantry, playroom, closet, moving, home office, garage, nursery and "
                "bedroom organizing services across San Diego County.",
                body, "services.html")

def build_process():
    body = f"""<div class="wrap">
  <div style="position:relative;margin-inline:calc(-1 * var(--edge));width:calc(100% + 2 * var(--edge));aspect-ratio:16/7;overflow:hidden">
    {img(IMAGES['process-hero'], 'Organized shelving', style='position:absolute;inset:0')}
    <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-bottom:18%">
      <h1 style="font-size:clamp(30px,3.6vw,40px);line-height:1.1;color:var(--color-text)">Our Process</h1>
    </div>
  </div>

  <section style="padding-block:clamp(64px,15vw,220px) var(--space-7);max-width:900px;margin:0 auto;text-align:center">
    <h2 style="font-size:clamp(26px,2.8vw,32px)">Why Hire Professional Organizers?</h2>
    <p class="muted" style="font-size:16.5px;margin-top:var(--space-4)">Whether you were born with the organizing gene or not; getting organized can be time consuming and overwhelming. A professional organizer is an unbiased and non judgmental person to assess your organizing goals and challenges. Once these are identified, our team will commit to helping you reach your unique goals to create balance in your day-to-day life.</p>
    <p style="font-size:22px;font-style:italic;color:color-mix(in srgb, var(--color-text) 55%, transparent);margin-top:var(--space-7)">The hardest part is getting started&hellip;</p>
  </section>

  <hr class="hr" />

  <section class="section--tight">
    {step_rows(STEPS)}
  </section>

  <hr class="hr" />
</div>

{cta_band()}"""
    return page("process.html", "Our Process — Balance Home Organizing",
                "Four steps: choose a space, schedule a free virtual consultation, make a plan, "
                "and our team organizes.",
                body, "process.html")

def build_about():
    members = []
    for m in TEAM:
        members.append(f"""<div class="center">
  <figure>{img(m['local_image'], m['alt'])}</figure>
  <h3>{e(m['name'])}</h3>
  <p class="role">{e(m['role'])}</p>
</div>""")
    body = f"""<div class="wrap">
  <section class="section">
    <h2 class="section__title">About the Team</h2>
    <div class="circle-grid team-grid">
{chr(10).join(members)}
    </div>
  </section>

  <hr class="hr" />

  <section class="section split">
    <figure style="margin:0;width:100%;aspect-ratio:4/5;overflow:hidden">
      {img(IMAGES['about-founder'], 'Megan Mossuto, founder', style='object-fit:contain')}
    </figure>
    <div class="prose">
      <h1 style="font-size:clamp(30px,3.6vw,40px);line-height:1.12;margin-bottom:var(--space-4)">About Balance Home</h1>
      <p>Megan Mossuto is the Owner &amp; Organizer of Balance Home Organizing, a professional home organization company. After many years of the 9-to-5 career in sales, Megan decided to pursue her true passion of connecting and helping others through home organization. Now, Megan and her team are helping clients throughout San Diego County.</p>
      <p>Organizing a client&rsquo;s home is so much more than just beautifying the space and making it look &lsquo;Pinterest&rsquo; worthy. It&rsquo;s about creating an environment that gives people permission to let go of the things they don&rsquo;t enjoy anymore. No matter the season of life you&rsquo;re in, we want to help you be your most productive self. We pride ourselves in understanding our clients&rsquo; unique needs and creating systems that work for their day-to-day life.</p>
      <p>We truly feel honored that our team is a trusted, reliable and professional home organization company throughout San Diego County.</p>
      <p>Let us help you achieve your organizing goals.</p>
    </div>
  </section>
</div>"""
    return page("about.html", "About — Balance Home Organizing",
                "Meet Megan Mossuto and the Balance Home Organizing team, professional home "
                "organizers serving San Diego County.",
                body, "about.html")

def build_blog():
    body = f"""<div class="wrap">
  <hr class="hr" />
  <section class="section--tight">
    <h1 class="visually-hidden">Organizing tips</h1>
    {blog_grid(BLOG[:PER_PAGE])}
    <div class="pager">
      <a href="blog-older.html" class="btn btn-ghost">Older Posts</a>
    </div>
  </section>
</div>"""
    return page("blog.html", "Tips — Balance Home Organizing",
                "Organizing tips, product picks and practical guides from the Balance Home "
                "Organizing team.",
                body, "blog.html", warm=True)

def build_blog_older():
    body = f"""<div class="wrap">
  <hr class="hr" />
  <section class="section--tight">
    <h1 class="visually-hidden">Organizing tips — older posts</h1>
    {blog_grid(BLOG[PER_PAGE:])}
    <div class="pager">
      <a href="blog.html" class="btn btn-ghost">&larr; Newer Posts</a>
    </div>
  </section>
</div>"""
    return page("blog-older.html", "Tips, older posts — Balance Home Organizing",
                "Earlier organizing tips and guides from the Balance Home Organizing team.",
                body, "blog.html", warm=True)

def build_products():
    tiles = []
    for p in PRODUCTS:
        tiles.append(f"""<a href="{e(p['href'])}" target="_blank" rel="noopener">
  <figure>{img(p['local_image'], p['alt'])}</figure>
  <h2>{e(p['title'])} &rarr;</h2>
</a>""")
    body = f"""<div class="wrap">
  <section class="section split split--center">
    <div>
      <h1 style="font-size:clamp(34px,4vw,48px);line-height:1.12">Shop Our Favorite Products</h1>
      <p class="muted" style="font-size:17px;margin-top:var(--space-4)">Searching for the best in class organizing products? Check out our Amazon Affiliate Store. When you click and shop, we receive a commission.</p>
      <a href="https://www.amazon.com/shop/balancehomeorganizing/" target="_blank" rel="noopener" class="btn btn-primary" style="margin-top:var(--space-5)">Shop All</a>
    </div>
    <figure style="margin:0;width:100%;aspect-ratio:4/3;overflow:hidden">
      {img(IMAGES['products-hero'], 'Organized kitchen shelves')}
    </figure>
  </section>

  <hr class="hr" />

  <section class="section">
    <div class="product-grid">
{chr(10).join(tiles)}
    </div>
  </section>
</div>"""
    return page("products.html", "Favorite Products — Balance Home Organizing",
                "Our favorite organizing products, by category, in the Balance Home Organizing "
                "Amazon affiliate store.",
                body, "products.html")

def build_service_pages():
    order = [d["slug"] for d in SERVICE_PAGES]
    for i, d in enumerate(SERVICE_PAGES):
        gallery = "".join(
            f'<figure>{img("../" + u, d["title"] + " organizing")}</figure>'
            for u in d.get("local_images", []))
        nxt = SERVICE_PAGES[(i + 1) % len(SERVICE_PAGES)]
        body = f"""<article class="service">
  <header class="service__header">
    <h1>{e(d['title'])}</h1>
    <p class="service__tagline">{e(d['tagline'])}</p>
  </header>
  <p class="service__body">{e(d['body'])}</p>
  <p><a href="../consultation.html" class="btn btn-primary">Get Started</a></p>
  <div class="service__gallery">{gallery}</div>
  <nav class="post-nav" aria-label="More services">
    <a href="../services.html">&larr; All services</a>
    <a href="{nxt['slug']}.html" rel="next">{e(nxt['title'])} &rarr;</a>
  </nav>
</article>

{cta_band(prefix='../')}"""
        page(f"services/{d['slug']}.html",
             f"{d['title']} organizing — Balance Home Organizing",
             d["tagline"] or f"{d['title']} organizing in San Diego County.",
             body, "services.html", prefix="../")
    return len(SERVICE_PAGES)

def build_consultation():
    paras = CONSULT.get("paragraphs", [])
    lead = "".join(f"<p>{e(t)}</p>" for t in paras[:2])
    rest = "".join(f"<p>{e(t)}</p>" for t in paras[2:])
    body = f"""<div class="wrap consult">
  <h1>{e(CONSULT.get('title', 'Book a Virtual Consultation'))}</h1>
  <div class="consult__lead">{lead}</div>
  <p><a href="mailto:{CONTACT['email']}?subject=Virtual%20consultation" class="btn btn-primary">Email us to book</a></p>
  <div class="consult__details">{rest}</div>
  <p class="consult__alt">Prefer a form? <a href="contact.html">Send us a message</a>.</p>
</div>

{cta_band()}"""
    return page("consultation.html",
                "Book a Virtual Consultation — Balance Home Organizing",
                "Book a free 30-minute virtual consultation with Balance Home Organizing.",
                body, "consultation.html")

def build_404():
    body = """<div class="wrap consult" style="text-align:center">
  <h1>We couldn&rsquo;t find that page</h1>
  <div class="consult__lead">
    <p>The link may be out of date, or the page may have moved when we rebuilt the site.</p>
  </div>
  <p style="display:flex;gap:var(--space-3);justify-content:center;flex-wrap:wrap;margin-top:var(--space-6)">
    <a href="/index.html" class="btn btn-primary">Go to the homepage</a>
    <a href="/blog.html" class="btn btn-ghost">Browse organizing tips</a>
  </p>
</div>"""
    return page("404.html", "Page not found — Balance Home Organizing",
                "That page could not be found.", body, "")

def build_contact():
    body = f"""<div class="wrap split" style="padding-block:var(--space-8)">
  <div>
    <p style="font-size:15px;font-style:italic;font-weight:700;margin-bottom:var(--space-4)">Have a question?</p>
    <h1 style="font-size:clamp(38px,4.6vw,52px);line-height:1.08;margin-bottom:var(--space-6)">Get in touch.</h1>
    <p class="muted" style="line-height:1.7;margin-bottom:var(--space-8)">Balance Home Organizing was founded by Megan, a professional organizer for Southern California. We are located in San Marcos, California just north of San Diego. Whether you need more information or you just have a question, feel free to check us out or send us a question below.</p>
    <h2 style="font-size:24px;margin-bottom:var(--space-5)">Contact Details</h2>
    <p class="muted" style="margin-bottom:var(--space-4)">Organizing Service Areas:</p>
    <p class="muted" style="line-height:1.7;margin-bottom:var(--space-6)">San Diego, Temecula, San Marcos, Vista, Oceanside, Carlsbad, Leucadia, Encinitas, Solana Beach, Del Mar, and Rancho Santa Fe</p>
    <p class="muted" style="line-height:1.8;margin-bottom:var(--space-3)">Email: <a href="mailto:{CONTACT['email']}" style="color:var(--color-salmon);text-decoration:underline">{CONTACT['email']}</a></p>
    <p class="muted" style="line-height:1.8">Phone Number: <a href="{CONTACT['phone_href']}">760-571-9292</a></p>
  </div>

  <form class="form" data-form="contact" novalidate>
    <div>
      <span class="field-label field-label--group">Name</span>
      <div class="field-pair">
        <div>
          <label class="field-label" for="fname">First Name <span class="field-hint">(required)</span></label>
          <input class="input" id="fname" name="first_name" type="text" autocomplete="given-name" required />
        </div>
        <div>
          <label class="field-label" for="lname">Last Name <span class="field-hint">(required)</span></label>
          <input class="input" id="lname" name="last_name" type="text" autocomplete="family-name" required />
        </div>
      </div>
    </div>
    <div>
      <label class="field-label" for="email">Email <span class="field-hint">(required)</span></label>
      <input class="input" id="email" name="email" type="email" autocomplete="email" required />
    </div>
    <div>
      <label class="field-label" for="phone">Phone Number</label>
      <input class="input" id="phone" name="phone" type="tel" autocomplete="tel" />
    </div>
    <div>
      <label class="field-label" for="zip">Zip Code</label>
      <input class="input" id="zip" name="zip" type="text" autocomplete="postal-code" inputmode="numeric" />
    </div>
    <fieldset style="border:0;padding:0;margin:0">
      <legend class="field-label" style="padding:0">Have you worked with an organizer in the past?</legend>
      <div class="radio-set">
        <label><input class="radio" type="radio" name="past_organizer" value="yes" />Yes</label>
        <label><input class="radio" type="radio" name="past_organizer" value="no" />No</label>
      </div>
    </fieldset>
    <div>
      <label class="field-label" for="message">Message <span class="field-hint">(required)</span></label>
      <textarea class="input" id="message" name="message" rows="5" required></textarea>
    </div>
    <p class="form-status" role="status" hidden></p>
    <button type="submit" class="btn btn-primary" style="align-self:start;padding:12px 28px">Send</button>
  </form>
</div>"""
    return page("contact.html", "Contact — Balance Home Organizing",
                "Get in touch with Balance Home Organizing in San Marcos, CA. Serving San Diego, "
                "Carlsbad, Encinitas, Oceanside and more.",
                body, "contact.html")

def build_join():
    body = f"""<div class="wrap split" style="padding-block:var(--space-8)">
  <figure style="margin:0;width:100%;aspect-ratio:3/4;overflow:hidden">
    {img(IMAGES['hiring-flyer'], "Balance Home is hiring. We're looking for you.")}
  </figure>

  <div>
    <h1 style="font-size:clamp(34px,4vw,48px);line-height:1.1;margin-bottom:var(--space-5)">Our Team is Growing!</h1>
    <p style="margin-bottom:var(--space-2)">If you or someone you know loves . . . .</p>
    <ul style="list-style:none;padding:0;margin:0 0 var(--space-5)">
      <li>* Organizing</li>
      <li>* Helping others</li>
      <li>* Making a difference</li>
      <li>* Enjoys working with a hardworking team</li>
    </ul>
    <p style="margin-bottom:var(--space-6)">Send us a message for more details!</p>

    <form class="form" data-form="join" novalidate>
      <div>
        <span class="field-label field-label--group">Name</span>
        <div class="field-pair">
          <div>
            <label class="field-label" for="jfname">First Name <span class="field-hint">(required)</span></label>
            <input class="input" id="jfname" name="first_name" type="text" autocomplete="given-name" required />
          </div>
          <div>
            <label class="field-label" for="jlname">Last Name <span class="field-hint">(required)</span></label>
            <input class="input" id="jlname" name="last_name" type="text" autocomplete="family-name" required />
          </div>
        </div>
      </div>
      <div>
        <label class="field-label" for="jemail">Email <span class="field-hint">(required)</span></label>
        <input class="input" id="jemail" name="email" type="email" autocomplete="email" required />
      </div>
      <div>
        <label class="field-label" for="jphone">Phone</label>
        <input class="input" id="jphone" name="phone" type="tel" autocomplete="tel" />
      </div>
      <div>
        <label class="field-label" for="jmessage">Message <span class="field-hint">(required)</span></label>
        <textarea class="input" id="jmessage" name="message" rows="5" required></textarea>
      </div>
      <p class="form-status" role="status" hidden></p>
      <button type="submit" class="btn btn-primary" style="align-self:start;padding:12px 28px">Send</button>
    </form>
  </div>
</div>"""
    return page("join-our-team.html", "Join Our Team — Balance Home Organizing",
                "Balance Home Organizing is hiring professional organizers in San Diego County.",
                body, "")

if __name__ == "__main__":
    os.makedirs(SITE, exist_ok=True)
    built = [build_home(), build_services(), build_process(), build_about(),
             build_blog(), build_blog_older(), build_products(),
             build_contact(), build_join(), build_consultation(), build_404()]
    for b in built:
        size = os.path.getsize(os.path.join(SITE, b))
        print(f"  {b:<22} {size:>7,} bytes")

    n_archives = build_archives()
    print(f"  blog/tag|category      {n_archives} archive pages")

    n_services = build_service_pages()
    print(f"  services/*.html        {n_services} service pages")

    for i, p in enumerate(BLOG):
        build_post(p, BLOG[i - 1] if i else None,
                   BLOG[i + 1] if i + 1 < len(BLOG) else None)
    print(f"  blog/*.html            {len(BLOG)} post pages")
    print(f"\n{len(built) + len(BLOG) + n_services + n_archives} pages built into site/")
