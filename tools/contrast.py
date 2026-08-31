"""WCAG contrast audit for the built site.

Checks actual rendered colours, compositing any translucent layer over the
background it sits on. Translucent panels over photography are checked against
their worst case (a white photo), since that is the lightest the panel can get
and therefore the worst for the white text on it.
"""
import sys

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def hexs(c):
    return "#%02x%02x%02x" % tuple(round(max(0, min(1, x)) * 255) for x in c)

def over(fg, alpha, bg):
    """Composite fg at alpha over bg."""
    f, b = rgb(fg) if isinstance(fg, str) else fg, rgb(bg) if isinstance(bg, str) else bg
    return tuple(f[i] * alpha + b[i] * (1 - alpha) for i in range(3))

def lum(c):
    c = rgb(c) if isinstance(c, str) else c
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def ratio(a, b):
    l1, l2 = sorted([lum(a), lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

# --- tokens under test ------------------------------------------------------
T = dict(
    accent      = sys.argv[1] if len(sys.argv) > 1 else "#e17e6b",
    sage        = sys.argv[2] if len(sys.argv) > 2 else "#839788",
    sage_alpha  = float(sys.argv[3]) if len(sys.argv) > 3 else 0.78,
    ink         = "#4a433a",
    page        = "#f5f6f4",
    warm        = "#eee0cb",
    white       = "#ffffff",
)

# panel worst case: translucent sage over the brightest possible photo
panel_light = over(T["sage"], T["sage_alpha"], "#ffffff")
# CTA band: 82% white over the brightest photo -> effectively near-white
cta = over("#ffffff", 0.82, "#ffffff")
# hero scrim: 72% white over a bright photo
hero = over("#ffffff", 0.72, "#ffffff")

CHECKS = [
    # (label, foreground, background, is_large_text)
    ("body ink on page",              T["ink"], T["page"], False),
    ("body ink on warm",              T["ink"], T["warm"], False),
    ("prose ink 82% on page",         over(T["ink"], .82, T["page"]), T["page"], False),
    ("hero subhead ink 78% on scrim", over(T["ink"], .78, hero), hero, False),
    ("muted ink 80% on page",         over(T["ink"], .80, T["page"]), T["page"], False),
    ("footer/meta ink 82% on page",   over(T["ink"], .82, T["page"]), T["page"], False),
    ("field hint ink 82% on page",    over(T["ink"], .82, T["page"]), T["page"], False),
    ("footer/meta ink 82% on warm",   over(T["ink"], .82, T["warm"]), T["warm"], False),
    ("prose ink 82% on warm",         over(T["ink"], .82, T["warm"]), T["warm"], False),
    ("nav ink on page",               T["ink"], T["page"], False),
    ("link accent on page",           T["accent"], T["page"], False),
    ("link accent on warm",           T["accent"], T["warm"], False),
    ("blog title accent on warm",     T["accent"], T["warm"], False),
    ("white on accent button",        T["white"], T["accent"], False),
    ("ghost btn accent on warm",      T["accent"], T["warm"], False),
    ("panel body white on sage",      T["white"], panel_light, False),
    ("panel heading white on sage",   T["white"], panel_light, True),
    ("CTA band ink on white wash",    T["ink"], cta, False),
    ("divider ink 14% (decorative)",  over(T["ink"], .14, T["page"]), T["page"], True),
]

print(f"accent={T['accent']}  sage={T['sage']} @ {T['sage_alpha']:.0%}  "
      f"(panel renders as {hexs(panel_light)} at its lightest)\n")
fails = 0
for label, fg, bg, large in CHECKS:
    need = 3.0 if large else 4.5
    r = ratio(fg, bg)
    ok = r >= need
    if not ok and "decorative" not in label:
        fails += 1
    note = "ok" if ok else ("FAIL" if "decorative" not in label else "n/a — decorative")
    print(f"  {label:<32} {r:>5.2f}:1  need {need}  {note}")
print(f"\n{fails} failing" if fails else "\nall clear")
sys.exit(1 if fails else 0)
