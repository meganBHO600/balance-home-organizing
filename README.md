# Balance Home Organizing — website

The single reference for this project: what it is, how to build it, the brand
rules it follows, and what's still open.

Static, dependency-free recreation of balancehomeorganizing.com, built from the
`.dc.html` design prototypes in `design_handoff_balance_home_organizing/`.
Nine pages, no framework, no build step required to deploy.

```
site/                     ← deploy this directory
  index.html  services.html  process.html  about.html
  blog.html   blog-older.html  products.html  contact.html  join-our-team.html
  assets/css/styles.css   design system (tokens, components, responsive)
  assets/js/forms.js      form validation + submission handoff
  blog/                   37 post pages, one per post
  assets/img/             all imagery, local
  assets/img/posts/       blog thumbnails + in-post images
  assets/icons/           Instagram / Yelp / Google marks
content/posts.json        all 37 blog posts, full text
content/*.json            page content extracted from the prototypes
tools/                    build pipeline + verification tooling
design_handoff_.../       the received design handoff, unmodified
```

---

## 1. Working rules

### Always do first

- **Invoke the `frontend-design` skill before writing any frontend code — every
  session, no exceptions.**
- **Check `design_handoff_balance_home_organizing/assets/` before designing.** Use
  real assets wherever they exist; never substitute a placeholder for an asset
  that already exists. Never invent brand colours — take them from §4.

### Reference discipline

This is a **reference-provided** build. The `.dc.html` prototypes are the
reference for layout, spacing and copy; the live site is the reference for brand
identity (§4).

- **Match the reference — do not improve on it.** Match layout, spacing,
  typography and colour exactly.
- **Do not add sections, features, or content that are not in the reference.**
- Screenshot your output, compare against the reference, fix mismatches,
  re-screenshot. **Do at least two comparison rounds.** Stop only when no visible
  differences remain, or the user says so. **Do not stop after one pass.**
- When comparing, be specific: "heading is 32px but reference shows ~24px",
  "card gap is 16px but should be 24px" — not "looks close".
- Check every pass: spacing/padding, font size/weight/line-height, colours (exact
  hex), alignment, border-radius, shadows, image sizing.
- If there is ever no reference, design from scratch with high craft, per the
  guardrails below.

### Local server

- **Always serve on localhost — never screenshot a `file:///` URL.**
- If the server is already running, do not start a second instance.

### Craft guardrails

- **Colours** — never a default framework palette (indigo-500, blue-600 and
  friends). Everything derives from the brand tokens in §4.
- **Animations** — only animate `transform` and `opacity`. **Never
  `transition-all`.** Spring-style easing.
- **Interactive states** — every clickable element needs hover, focus-visible and
  active states. No exceptions.
- **Spacing** — intentional, consistent tokens (`--space-1..9`), never arbitrary
  values.
- **Images** — placeholder images (`https://placehold.co/`) only where no real
  asset exists. This project has real photography for everything.
- **Mobile-first responsive**, always.

Three standing guardrails **do not apply here**, because this brand overrides them:

| Guardrail | Why it does not apply |
|---|---|
| "Never use the same font for headings and body" | Montserrat throughout *is* the brand. Do not pair in a serif. |
| "Use layered, colour-tinted shadows" | The design is deliberately flat — hairline dividers only, no shadows. |
| "Layer radial gradients, add grain; treat images with `mix-blend-multiply`" | The brand calls for naturally lit, true-to-colour photography. No overlays or colour treatment. |

The standing output default of "a single `index.html` with Tailwind via CDN" also
does not apply: this is nine pages with its own token system and no Tailwind.

### Hard rules

- Do not add sections, features, or content not in the reference.
- Do not "improve" a reference design — match it.
- Do not stop after one screenshot pass.
- Do not use `transition-all`.
- Do not use a default framework blue/indigo as a primary colour.
- Do not fabricate content (§6).

---

## 2. Running and rebuilding

```bash
python3 tools/serve.py            # http://localhost:3000
./tools/build_all.sh              # regenerate site/ from content/
./tools/build_all.sh --with-blog  # also re-import every blog post from the live site
```

Content lives in `content/*.json`, not in the HTML. The pipeline steps run in
dependency order and must stay in that order — re-running `extract.py` alone
will wipe the resolved image URLs:

| Step | Script | What it does |
|---|---|---|
| 1 | `extract.py` | Prototypes → `content/*.json` (37 posts, 9 services, 9 products, 5 team, process steps) |
| 2 | `resolve_images.py` | Fills in images the prototype bundle referenced but never shipped, by reading each page's `og:image` from the live site. Cached in `content/_og_cache.json`. |
| 3 | `download_images.py` | Downloads every image into `site/assets/img/` and rewrites the JSON to local paths |
| 4 | `build.py` | Renders `site/*.html` and `site/blog/*.html` — shared nav/footer/head live here |

The blog runs separately (`--with-blog`) because it hits the live site 37+ times:

| Step | Script | What it does |
|---|---|---|
| a | `fetch_posts.py` | Enumerates every post via Squarespace's JSON API, then **scrapes each rendered page** for the body |
| b | `clean_posts.py` | Strips Squarespace markup to semantic HTML, localises images, rewrites live-site links to internal ones |
| c | `verify_posts.py` | Re-fetches every live post and compares word counts — catches silent content loss |

To edit one-off copy (hero, About, Contact), edit `tools/build.py`. To add a
service or product, add a record to the relevant `content/*.json` and rebuild.

### The blog

All 37 posts now live in this site — full text, images and all — at
`site/blog/<slug>.html`. Nothing links back to Squarespace any more.

Two things are worth knowing if you re-import:

- **The JSON API's `body` field is incomplete.** Squarespace product and summary
  blocks live outside it. One post came through at 78 words instead of 508.
  `fetch_posts.py` therefore scrapes the rendered page, not the API body.
- **`verify_posts.py` is the safety net.** It re-fetches every live post and
  compares word counts; it exits non-zero if anything imported short. It caught a
  parser bug that was silently truncating posts at the first inline SVG.

Post pages carry the real publish date and author (29 Megan Mossuto, 8 Mike
Simpson), previous/next navigation in date order, and a link back to the listing.
Listing pages stay 20 + 17 to match the live pagination.

---

## 3. The verification loop

**Always serve on localhost — never screenshot a `file:///` URL.**
Node and Puppeteer are not installed on this machine; headless Chrome covers it
with no dependencies.

```bash
python3 tools/serve.py &                                  # the build, :3000
./tools/refsite.sh &                                      # the reference, :3001
tools/shot.sh http://localhost:3000/index.html "temporary screenshots/new-home.png"
tools/shot.sh http://localhost:3001/Home.dc.html "temporary screenshots/ref-home.png"
```

Then read both PNGs back with the Read tool and diff them specifically —
"heading is 32px but reference shows ~24px", not "looks close". **Do at least two
comparison rounds.** Stop only when no visible differences remain.

`tools/refsite.sh` exists because the prototypes ship broken: they load a
design-system stylesheet and a `support.js` that are not in the bundle, plus 33
local images that are missing. It substitutes the rebuilt `styles.css` and the
resolved images so the reference actually renders.

**Mobile:** `--window-size` does *not* emulate a mobile viewport — it renders
desktop-wide and crops, which will make a correct page look broken. Use the
iframe harness instead:

```bash
cp tools/frame.html site/_frame.html
tools/shot.sh "http://localhost:3000/_frame.html?p=index.html" "temporary screenshots/m-home.png" 420 2200
rm site/_frame.html
```

`tools/probe.html` reports any element overflowing a 390px viewport — the
reliable way to confirm there's no horizontal scroll.

**Contrast:** `python3 tools/contrast.py` audits every text/background pair,
compositing translucent layers over what sits behind them. It exits non-zero on
any failure, so it can gate a build.

---

## 4. Source of truth

**Where anything disagrees, the live site wins** on brand identity — palette,
typography, nav, and which pages use the warm background. The prototypes win on
redesigned layout, structure and copy. `BrandGuidelines.dc.html` is unreliable on
both counts; check it against the live site before trusting it.

Read off the live site's compiled theme CSS and screenshots:

| | Live site | Handoff doc said | Prototypes said |
|---|---|---|---|
| Font | **Montserrat** (heading, body, meta) | Work Sans | Work Sans |
| | | BrandGuidelines said Poppins | |
| Heading weight | **400**, letter-spacing 0 | 400 | 600 on the Home hero |
| Accent | **`#E17E6B`** terracotta | Salmon `#E0A899` | `#E0A899` |
| Ink | **`#4A433A`** | `#26332F` | `#26332F` |
| Page background | **`#F5F6F4`** | `#FFFFFF` | `#FFFFFF` |
| Warm background | **`#EEE0CB`**, blog only | `#ECE1CD`, blog only | also on Products |
| Sage | **`#839788`** | `#9AAB89` | `#9AAB89` |
| Emerald `#1F6361` | **not in the theme at all** | "primary" | used for links |
| Nav | **no Home link** | Home first | Home first |
| Active nav item | **underline** | emerald | no indication |
| Links | **terracotta, underlined** | emerald | emerald, no underline |

---

## 5. Design system

### Logo

`assets/img/logo.png` — a layered square monogram: three offset outlined squares
behind a serif "B". Keep clear space around it equal to the mark's own width.
**Never recolor the squares or fill them solid.** 32×32 with `object-fit:contain`
in the nav.

### Palette

Shipped values are the live site's colours **darkened to clear WCAG AA** (see
§8). Both are kept as tokens so the relationship stays visible:

| Token | Shipped | Live site | Usage |
|---|---|---|---|
| `--color-accent` | `#B23B24` | `#E17E6B` | CTA fill, links, blog tile titles |
| `--color-accent-600` | `#94311E` | `#DA6049` | hover |
| `--color-accent-700` | `#7F2A1A` | — | active |
| `--color-sage` | `#637668` | `#839788` | overlay panels, opaque |
| `--color-text` | `#4A433A` | same | body copy and headings |
| `--color-bg` | `#F5F6F4` | same | all pages except the two blog pages |
| `--color-bg-warm` | `#EEE0CB` | same | Blog and Blog Older Posts only |

Secondary text is ink at 82% (the lowest opacity that clears 4.5:1 on both
backgrounds). Divider: ink at 14%.

### Typography

**Montserrat throughout** — headings, body and meta. Heading and body weight both
400, letter-spacing 0.

- H1: `clamp(34px, 4–4.6vw, 48–58px)`, weight 400, line-height 1.1–1.18
- H2: 20–30px, weight 400 · Card/tile titles: 18–22px, weight 400
- Body: 15.5–17px, line-height 1.6–1.7 · Nav: 15px
- Uppercase kickers: 13px, letter-spacing 0.06–0.12em
- Button label: uppercase, weight 600, letter-spacing 0.04em

### Components

- **Primary button** — accent fill, white uppercase text, weight 600,
  letter-spacing 0.04em, `white-space:nowrap`.
- **Nav** — logo + Services, Process, About, Blog, Favorite Products, with
  "Book Consultation" pushed right. **No Home link** (the logo carries home).
  Current page is marked with an underline.
- **Footer** — four columns: brand blurb; contact; sitemap (Home, Services, Our
  Process, Products, Contact Us, Join our Team); social icons.
- **Links** — accent, underlined.
- **Spacing** — `--space-1..9` = 4/8/12/16/24/32/48/64/96. Edge gutter
  `clamp(20px, 5vw, 72px)`, content max-width 1200px.
- **Radius** — `--radius` 4px, `--radius-lg` 10px on figures and panels.
- **Shadows** — none. Flat, with hairline dividers.

### Imagery

Real client-space photography, naturally lit, true-to-colour. Hero and section
imagery full-bleed rectangular, never boxed or matted. Service and team photos in
circle crops. Product tiles are plain cutouts — no card border, no fill, no frame.

---

## 6. Content rules — non-negotiable

- **No fabricated content, ever.** No invented testimonials, client names,
  before/after claims, stats, credentials, team bios, or blog posts. If real
  content isn't available, leave the section out.
- **All 37 blog posts are real** (20 + 17), with their real titles and links.
- **No invented pricing.** The CTA is "Book Consultation", not a price.
- **Real contact details only:** megan@balancehomeorganizing.com, 760.571.9292,
  San Marcos, CA. Service areas per the Contact page.
- **"We" language** — a team, not a solo practice. Megan is named in the About bio.
- **No emoji**, anywhere.
- **Voice:** warm, encouraging, plain-spoken. Short sentences. Name the
  stress directly, then offer a calm, concrete next step. No hype, no jargon.
- **Amazon links are affiliate links** — keep them intact, open in a new tab.

---

## 7. Pages

1. **Home** — full-bleed hero + white scrim, "We are here to help" sage panel,
   four process steps, CTA band.
2. **Services** — 9-tile circle grid. No hero intro.
3. **Our Process** — hero, "Why Hire Professional Organizers?", four steps, CTA band.
4. **About** — team grid (5), founder bio.
5. **Blog** — 20 post tiles, warm background, "Older Posts".
6. **Blog Older Posts** — 17 tiles, "Newer Posts".
7. **Favorite Products** — hero + Shop All, 9 affiliate category tiles.
8. **Contact** — intro + details, form with Yes/No radio.
9. **Join Our Team** — hiring flyer, bullets, form.

Nav links are standard same-site navigation. External links open in a new tab
with `rel="noopener"`. Every clickable element has hover, focus-visible and
active states. Reduced motion is respected.

---

## 8. What was verified

- 46 pages, 186 internal references, **0 broken**; 366 images, **0 missing alt**.
- All 37 blog posts verified against their live pages at 100–105% of body text.
- Every page: one `<h1>`, `lang="en"`, a `<title>`, a skip link.
- Desktop screenshot-diffed at 1440px against the prototypes, two rounds.
  Corrections found and fixed: panel-row gaps, footer offset, footer link colour,
  Process hero spacing, blog pager (centred, not spread), and the Home/Process
  step-copy difference.
- Mobile verified at a true 390px viewport — `scrollWidth` 375, no overflow.
- Forms tested headlessly: empty submit is blocked and names the missing field;
  a valid submit hands off to the mail client.
- **Contrast: every text/background pair clears WCAG AA** (`tools/contrast.py`).

The live site's own palette failed AA badly — terracotta links 2.62:1, blog
titles 2.18:1, white-on-button 2.84:1, white on the translucent sage panels
2.33:1, all against a 4.5:1 minimum. Fixed by darkening the accent to `#B23B24`,
darkening the sage to `#637668` and making the panels opaque (so contrast no
longer depends on the photo behind them), and raising secondary text from 70% to
82% ink. Lowest ratio on the site is now 4.56:1.

---

## 9. Deviations from the prototypes

1. **Responsive rules are new.** The prototypes are fixed-width with no media
   queries. Breakpoints at 900px and 720px: sage panels stop being absolutely
   positioned and sit under their image, split layouts stack, nav links drop to a
   second row.
2. **The design-system layer was rebuilt** — `_ds/classical-….css` is not in the
   bundle. `styles.css` reconstructs the `--space-*` scale, `--radius-*`,
   `--color-divider` and `.nav`/`.btn`/`.hr`/`.input`. Values are inferred from
   usage, so they are a judgement call.
3. **Social icons are newly drawn** — the three SVGs were referenced but never shipped.
4. **Interactive states added** — focus-visible, active, reduced-motion.
5. **Colours darkened for accessibility** — see §8.

---

## 10. Open items

1. **Form submission is not wired.** Both forms validate, then open the visitor's
   mail client with the message prefilled, and say so. To send server-side, add
   `data-endpoint="https://…"` to the `<form>` in `build.py`; `forms.js` will POST
   the fields as JSON. Needs spam protection either way.
2. **Image licensing.** All 73 images came from the live site or Unsplash URLs it
   references. Client photography is fine; confirm or replace anything Unsplash-sourced.
3. **Hosting and DNS.** The live site is on Squarespace. Deploy target and
   cutover plan undecided.
4. **Per-service pages do not exist yet.** The live site has nine of them
   (`/services/kitchen-organization` and so on) and the Services tiles still link
   out to them — 9 links, the only ones left pointing at Squarespace. They need
   importing the same way the blog was before this can replace the live site.
5. **Footer layout differs from the live site.** The live footer is a large brand
   name with contact beneath and a right-aligned sitemap; the prototypes use four
   columns. Built the prototype's version — footer layout is redesign territory.

### Requested, not yet built

- **Design adjustments** — Megan reviewed and approved the site for launch, with
  refinements to follow. No specifics captured yet.
- **Project-timing question on the contact form** — a radio group asking when the
  visitor wants to start (the existing "worked with an organizer before" radio is
  the pattern to copy). Needs: the option wording from Megan, the field added in
  `tools/build.py`, and `project_timing` added to the contact form's `fields`
  list in `src/index.js` so it appears in the email.

### Notes on the imported blog

- Squarespace **hashtag archive links** inside post bodies (`/blog/hashtags/…`)
  were unwrapped — the text stays, the link goes, since this build has no tag
  pages. Add tag pages if you want them back.
- One post had **Amazon embed code pasted into a link field**, producing an
  `href` that was itself an `<iframe>`. That link is dropped and the text kept;
  it is broken on the live site too.
- **In-post links to `/services/<x>`** point at the Services index for now, since
  the per-service pages do not exist yet (see above).
- Post bodies keep the client's own wording exactly, including the occasional
  emoji. The no-emoji rule in §6 governs copy we write, not published posts.

### Handoff doc corrections

`design_handoff_balance_home_organizing/BHO Website.md` is the received handoff,
kept unmodified. It is wrong in these places:

- Post count is **37** (20 + 17), not 35 (20 + 15).
- Blog tiles have **no byline or date** — image and title only.
- Services has **no hero intro**, just the circle grid.
- Home has **no services teaser and no testimonials**.
- About has **no service-area list** (that lives on Contact).
- Font, palette, and nav are wrong throughout — see §4.
- It claims each `.dc.html` "can be opened directly in a browser". It cannot; see §3.

---

## Rollback: restoring Squarespace

If the cutover needs reverting, set these DNS records back in Cloudflare
(they are the Squarespace originals, captured before the switch):

```
A     @    198.185.159.144    DNS only
A     @    198.185.159.145    DNS only
A     @    198.49.23.144      DNS only
A     @    198.49.23.145      DNS only
CNAME www  ext-cust.squarespace.com   DNS only
```

Remove the Worker's custom domain first, then re-add these. Propagation is
about 10 minutes. This only works while the Squarespace subscription is still
within its paid period.

**Do not touch MX or TXT records** — those are Google Workspace and are not part
of any website change.
