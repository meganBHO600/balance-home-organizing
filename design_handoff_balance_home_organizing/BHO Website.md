# Handoff: Balance Home Organizing — Website Redesign

## Overview
A full marketing site redesign for Balance Home Organizing (professional home organizers, San Marcos/San Diego, CA), recreating and modernizing balancehomeorganizing.com. Covers Home, Services, Our Process, About, Blog (+ older posts), Favorite Products, Contact, and Join Our Team.

## About the Design Files
The files in this bundle are **design references built in HTML** — high-fidelity prototypes showing the intended look, layout, and content, not production code to copy directly. The task is to **recreate these HTML designs in the target codebase's environment** (React, Vue, static site generator, CMS theme, etc.) using its established patterns and libraries — or, if no environment exists yet, choose the most appropriate framework and implement the designs there.

## Fidelity
**High-fidelity (hifi).** Colors, typography, spacing, copy, and imagery are final/near-final. Recreate pixel-close using the codebase's own component/styling system, not by embedding this HTML.

## Brand Guide

### Logo
`assets/logo.png` (included in this bundle) — a layered square monogram: three offset outlined squares behind a serif "B", in Emerald on a white/transparent ground. Keep clear space around it equal to the mark's own width. Never recolor the squares or fill them solid.

### Color palette
| Name | Hex | Usage |
|---|---|---|
| Emerald (primary) | `#1F6361` | Buttons (ghost/outline), links, nav active state, headings accents |
| Emerald 600 | `#17504E` | Hover state for emerald elements |
| Emerald 700 | `#123F3D` | Link default color, darker accents |
| Emerald 300 | `#BCD6D4` | Light tints |
| Emerald 100 | `#E6F0EF` | Very light backgrounds |
| Sage | `#9AAB89` | Secondary accents, tags |
| Salmon | `#E0A899` | Primary CTA button fill ("Book Consultation", "Shop All", "Send"), hover `#D3927F` |
| Ink / text | `#26332F` | Body copy, headings (used at ~80–82% opacity via `color-mix` for secondary text) |
| Page background (default) | `#FFFFFF` | Home, Services, Process, About, Products, Contact, Join Our Team |
| Page background (warm) | `#ECE1CD` | Blog & Blog Older Posts pages only |

Max 2 background colors per the system: white (default) and warm beige (blog only). Divider/hairline color: design-system `--color-divider` token (light neutral gray).

### Typography
Single family throughout: **Work Sans** (Google Fonts, weights 400/500/600/700).
- H1 (page hero): `clamp(34px, 4–4.4vw, 48–54px)`, weight 400, line-height ~1.1
- H2 (section heads): 20–24px, weight 400
- Card/tile titles: 18–22px, weight 400, often in Salmon on Blog tiles
- Body copy: 15.5–17px, line-height 1.6–1.7, Ink at ~80–82% opacity
- Nav links: default size, weight 400/500, uppercase small kicker labels use 13px, letter-spacing 0.06–0.12em, uppercase
- Button label: uppercase, weight 600, letter-spacing 0.04em

### Imagery
Real client-space photography, naturally lit, true-to-color. Hero/section imagery runs full-bleed rectangular (no boxed/matted frames). Product tiles (Favorite Products page) show plain product cutouts on white, no card border/background — label + "→" arrow beneath, no frame.

### Voice
Warm, encouraging, plain-spoken. Short sentences, first-person plural ("we"). Speaks to stress/overwhelm directly, then offers a calm, concrete next step. No emoji.

### Components
- **Primary button**: Salmon fill `#E0A899`, white uppercase text, weight 600, letter-spacing 0.04em, hover darkens to `#D3927F`. No rounded-corner pill styling beyond the design system's default radius.
- **Nav**: Logo mark + text links (Home, Services, Process, About, Blog, Favorite Products) + primary button ("Book Consultation") right-aligned, on every page.
- **Footer**: 4 columns — brand blurb, contact info (location/phone/email), sitemap link list (Home, Services, Our Process, Products, Contact Us, Join our Team), social icons (Instagram, Yelp, Google).

## Screens / Views

### 1. Home
Hero (headline + subhead + CTA + image), value props, services teaser, process teaser, testimonial/CTA band, footer.

### 2. Services
Hero intro, grid/list of service offerings with icons or photos, each with title + short description, CTA to book consultation.

### 3. Our Process
Step-by-step process (numbered steps), each with heading + description, supporting imagery.

### 4. About
Founder bio (Megan), team photos, mission/voice copy, service-area list.

### 5. Blog (`Blog.dc.html`)
Grid of post tiles (title, author, date, thumbnail), most-recent-first, 20 posts total, "Older Posts" link → **Blog Older Posts** (`BlogOlder.dc.html`) with the next 15 posts and a "Newer Posts" link back. Tiles: 4:3 image, uppercase byline/date meta, title in Salmon.

### 6. Favorite Products (`Products.dc.html`)
Hero: headline + copy + "Shop All" button (left), kitchen-shelf photo (right), side-by-side ~5:7 column split. Below: grid of Amazon-affiliate category tiles — plain product cutout image (no card frame/background), label text + "→" arrow, links open in new tab.

### 7. Contact (`Contact.dc.html`)
Two-column: left = "Have a question?" kicker (italic, bold, 15px) + "Get in touch." H1 + intro paragraph + "Contact Details" (service areas, email, phone). Right = form: Name (First/Last side by side), Email, Phone Number, Zip Code, "Have you worked with an organizer in the past?" (Yes/No radio), Message, "Send" button (Salmon).

### 8. Join Our Team (`JoinOurTeam.dc.html`)
Two-column: left = hiring flyer image (`assets/hiring-flyer.jpg` — "Balance Home is Hiring! We're Looking For You!" graphic). Right = "Our Team is Growing!" H1, intro copy + bullet-style list (Organizing / Helping others / Making a difference / Enjoys working with a hardworking team), "Send us a message for more details!" line, then a form: First/Last Name, Email, Phone, Message, "Send" button.

## Interactions & Behavior
- All nav links are standard same-site navigation (no SPA transitions assumed).
- External links (Amazon affiliate store, Instagram, Yelp, Google Maps) open in a new tab (`target="_blank" rel="noopener"`).
- Forms (Contact, Join Our Team) are presentation-only in the prototype (`onsubmit="event.preventDefault()"`) — wire to real form handling (e.g. email service, CRM) in production.
- Button hover: Salmon `#E0A899` → `#D3927F`.
- Link hover: Emerald 700 → Emerald.
- No modals, no client-side routing state, no loading/error states defined — add per the target stack's form-submission UX.

## State Management
No complex state. Forms need: field values, required-field validation (First Name, Last Name, Email, Message marked required), submit/success/error handling.

## Design Tokens
- Spacing scale used: `--space-2` through `--space-8` (design-system tokens — use the target codebase's own 8-step spacing scale if porting).
- Border radius: minimal/none — flat rectangular imagery and buttons.
- Shadows: none used; the design is flat with hairline dividers only.

## Assets
- `assets/logo.png` — brand mark, included in this bundle.
- `assets/hiring-flyer.jpg` — Join Our Team hero graphic, included.
- All other photography is sourced from the live balancehomeorganizing.com site (Squarespace CDN URLs) or Unsplash stock photography referenced directly by URL in the HTML — replace with licensed/owned assets before production launch.

## Files
Reference HTML files copied into this bundle (`pages/`):
- `Home.dc.html`
- `Services.dc.html`
- `Process.dc.html`
- `About.dc.html`
- `Blog.dc.html`
- `BlogOlder.dc.html`
- `Products.dc.html`
- `Contact.dc.html`
- `JoinOurTeam.dc.html`
- `BrandGuidelines.dc.html` — standalone visual brand reference page

Each `.dc.html` file is self-contained (inline styles) and can be opened directly in a browser to view the reference design.
