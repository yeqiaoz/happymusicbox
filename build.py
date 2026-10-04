#!/usr/bin/env python3
"""Build the Happy Music Box one-page site into site/.

Copy lives here (mirrored in content/home.md). Run from the repo root: python3 build.py
Needs Pillow. Source photos in assets/source/ (gitignored), so build from the Dropbox folder.
"""
import html, json, os, shutil
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets", "source")
OUT = os.path.join(ROOT, "site")
IMG = os.path.join(OUT, "img")

# [ASK] domain not chosen yet. With BASE_URL empty the build skips canonical/og:url/sitemap.
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
# While Shuai reviews the draft on github.io: keep it out of search. Set False at launch.
DRAFT = True

BIZ = {
    "name": "Happy Music Box",
    "email": "support@happymusicbox.com",  # [ASK] from Shuai's mockup; happymusicbox.com does not resolve yet
    "amazon_pink": "https://www.amazon.com/dp/B0HC9TPS27",
    "amazon_blue": "https://www.amazon.com/dp/B0HC9XZ8BC",
}
BUY = BIZ["amazon_pink"]

NAV = [
    ("#overview", "Overview"),
    ("#frequencies", "Solace Frequencies"),
    ("#light", "LED Light Modes"),
    ("#support", "Support"),
    ("#faq", "FAQ"),
]

# name -> (source file, crop box or None, pad-to-square, widths, alt)
IMAGES = {
    "cube": ("amz_7_41CuGnnAYqL.jpg", None, True, (1000, 560),
             "Happy Music Box, a soft white 3x3 cube speaker with a peach speaker grille and rainbow LED light between its squares"),
    "cube_lit": ("amz_0_31fGKr6jWbL.jpg", None, True, (560,),
                 "The cube glowing in pink, yellow, green and violet LED light"),
    "hand": ("amz_3_41NoBI5hh7L.jpg", (0, 60, 300, 467), False, (400,),
             "A hand holding the palm-sized cube, showing its soft silicone grid and the buttons on top"),
    "box": ("amz_4_41B998PrnfL.jpg", (0, 90, 500, 500), False, (500,),
            "What's in the box: the Happy Music Box speaker, its gift box, the manual and a USB cable"),
    "use_sleep": ("amz_1_51sZTOBUmcL.jpg", (10, 5, 140, 135), False, (260,),
                  "A woman asleep in bed with the cube glowing softly on the nightstand"),
    "use_meditate": ("amz_1_51sZTOBUmcL.jpg", (372, 8, 494, 130), False, (260,),
                     "A woman meditating cross-legged on a yoga mat"),
    "use_focus": ("amz_1_51sZTOBUmcL.jpg", (70, 160, 225, 315), False, (260,),
                  "Someone at a desk in the evening, holding the glowing cube"),
    "use_gift": ("amz_1_51sZTOBUmcL.jpg", (35, 338, 192, 495), False, (260,),
                 "Two people handing over a wrapped gift box"),
}


def esc(s):
    return html.escape(s, quote=True)


def ext(url, text, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(url)}"{c} target="_blank" rel="noopener">{text}</a>'


# ---------- images ----------

def process_images():
    os.makedirs(IMG, exist_ok=True)
    for name, (src, box, pad, widths, _) in IMAGES.items():
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, src))).convert("RGB")
        if box:
            im = im.crop(box)
        if pad:  # product shots touch the frame; give them white breathing room, square
            side = int(max(im.size) * 1.12)
            canvas = Image.new("RGB", (side, side), (255, 255, 255))
            canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2 + int(side * 0.02)))
            im = canvas
        for w in widths:
            r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            r.save(os.path.join(IMG, f"{name}-{w}.webp"), "WEBP", quality=84, method=6)


def logo_png(size):
    """App-icon version of the logo: terracotta rounded square with a white waveform."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.24, fill=(224, 115, 88, 255))
    heights = [0.16, 0.3, 0.22, 0.46, 0.62, 0.4, 0.54, 0.3, 0.2, 0.12]
    bw, gap = s * 0.04, s * 0.032
    x0 = (s - (len(heights) * bw + (len(heights) - 1) * gap)) / 2
    for i, h in enumerate(heights):
        x = x0 + i * (bw + gap)
        d.rounded_rectangle((x, s / 2 - s * h / 2, x + bw, s / 2 + s * h / 2), radius=bw / 2, fill="white")
    return im.resize((size, size), Image.LANCZOS)


def write_icons():
    logo_png(180).save(os.path.join(IMG, "apple-touch-icon.png"))
    logo_png(192).save(os.path.join(IMG, "icon-192.png"))
    logo_png(48).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    # Social share card: cream ground, product centered
    og = Image.new("RGB", (1200, 630), (251, 245, 233))
    cube = Image.open(os.path.join(SRC, IMAGES["cube"][0])).convert("RGB")
    cube.thumbnail((640, 560))
    og.paste(cube, ((1200 - cube.width) // 2, (630 - cube.height) // 2))
    og.save(os.path.join(IMG, "og.jpg"), quality=86)


def pic(name, w, cls="", eager=False, sizes=None):
    _, _, _, widths, alt = IMAGES[name]
    widths = sorted(widths)
    srcset = ", ".join(f"img/{name}-{x}.webp {x}w" for x in widths)
    big = widths[-1]
    with Image.open(os.path.join(IMG, f"{name}-{big}.webp")) as im:
        iw, ih = im.size
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="img/{name}-{big}.webp" srcset="{srcset}" sizes="{sizes or f"{w}px"}" '
            f'width="{iw}" height="{ih}" alt="{esc(alt)}" {load} decoding="async">')


# ---------- icons (inline SVG, stroke = currentColor) ----------

ICON = {
    "meditate": '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="10" r="4.5"/><path d="M24 15v13M24 19c-4 0-6 3-9 7l-3 4M24 19c4 0 6 3 9 7l3 4M10 38c4-4 9-5 14-5s10 1 14 5M15 32c3 2 6 3 9 3s6-1 9-3"/></svg>',
    "bulb": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M17 27a10 10 0 1 1 14 0c-2 2-3 4-3 6h-8c0-2-1-4-3-6zM20 37h8M21 41h6M24 3v4M8 18H4M44 18h-4M12 7l3 3M36 7l-3 3"/></svg>',
    "hand": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 5c3 5 6 8 6 12a6 6 0 0 1-12 0c0-4 3-7 6-12zM4 34l7-6c2-1 4-1 6 0l7 3h6a2.5 2.5 0 0 1 0 5h-8M30 36l9-6a2.5 2.5 0 0 1 3 4l-10 8c-2 1-4 2-6 2H14l-6 2"/></svg>',
    "wave": '<svg viewBox="0 0 48 28" aria-hidden="true"><path d="M2 8c7-6 13-6 22 0s15 6 22 0M2 16c7-6 13-6 22 0s15 6 22 0M2 24c7-6 13-6 22 0s15 6 22 0"/></svg>',
    "leaf": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M10 38C8 22 18 10 38 10c0 20-12 30-28 28zM10 38 28 20"/></svg>',
    "heart": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 40S6 29 6 17a9 9 0 0 1 18-3 9 9 0 0 1 18 3c0 12-18 23-18 23z"/><path d="M15 23h4l2-4 3 8 3-6 2 2h4"/></svg>',
    "people": '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="16" cy="15" r="5"/><circle cx="32" cy="15" r="5"/><path d="M6 36c0-6 4-10 10-10s10 4 10 10M22 36c0-6 4-10 10-10s10 4 10 10"/></svg>',
    "arrow": '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 10h13M11 5l5 5-5 5"/></svg>',
}

LOGO = ('<a class="logo" href="#overview" aria-label="Happy Music Box home">'
        '<span class="logo-mark" aria-hidden="true">' + "".join(f"<i style=\"height:{h}%\"></i>" for h in (18, 34, 24, 52, 70, 44, 60, 34, 22, 14)) + '</span>'
        '<span class="logo-word">Happy<br>Music Box</span></a>')

WAVES = ('<svg class="deco deco-{pos}" viewBox="0 0 220 60" aria-hidden="true">'
         '<path d="M0 40c30-26 60-26 90 0s60 26 90 0 40-20 40-20"/>'
         '<path d="M0 48c30-26 60-26 90 0s60 26 90 0 40-20 40-20"/>'
         '<path d="M0 56c30-26 60-26 90 0s60 26 90 0 40-20 40-20"/></svg>')

STARS = '<span class="stars" aria-label="5 out of 5 stars">★★★★★</span>'


# ---------- copy ----------

FEATURES = [
    ("meditate", "Mindful Frequencies",
     "Preloaded 432Hz, 528Hz, and 639Hz tracks promote deep sleep, meditation, and focus."),
    ("bulb", "Ambient Lighting",
     "7 smooth LED color transitions to set a calming mood for bedtime or evening study."),
    ("hand", "Soft-Touch Design",
     "Soft silicone casing with a modern grid pattern that fits seamlessly into any room setup."),
]

FREQS = [
    ("leaf", "432 Hz", "Natural Harmony", "Grounding &amp; calm", "peach"),
    ("heart", "528 Hz", "Love &amp; Miracles", "Healing &amp; harmony", "mint"),
    ("people", "639 Hz", "Connection", "Relationships &amp; unity", "lilac"),
]

USES = [("use_sleep", "Sleep"), ("use_meditate", "Meditate"), ("use_focus", "Focus"), ("use_gift", "Gift")]

SPECS = [
    ("Size", "3 × 3 × 3 inches, palm-sized"),
    ("Weight", "12.8 oz"),
    ("Sounds", "Built-in 432Hz, 528Hz and 639Hz tracks, plus Bluetooth streaming from your phone"),
    ("Stereo", "Pair two units together for wider stereo sound"),
    ("Light", "7 LED colors with multiple dynamic light modes"),
    ("Battery", "1600mAh, up to 4 hours of playback"),
    ("Finish", "Soft-touch silicone with a 3×3 textured grid"),
    ("Colors", "Pink, Blue"),
]

IN_BOX = ["Happy Music Box speaker", "User manual", "USB cable", "Ready-to-gift box"]

FAQ = [
    ("Do I need my phone to use it?",
     "No. The 432Hz, 528Hz and 639Hz tracks are built in, so you can tap to play straight away. "
     "Your phone is only needed if you want to stream your own music over Bluetooth."),
    ("How long does the battery last?",
     "Up to 4 hours of playback from the built-in 1600mAh battery. Recharge it with the included USB cable."),
    ("Can I connect two of them?",
     "Yes. Two Happy Music Box speakers can be paired together for a wider, more immersive stereo sound."),
    ("How big is it?",
     "3 × 3 × 3 inches and 12.8 oz, small enough for a nightstand, a desk, or your bag."),
    ("What colors does it come in?",
     "Pink and Blue. Both are sold on Amazon."),
    ("Where do I go for returns or a replacement?",
     "If you bought on Amazon, start a return or replacement from your Amazon order. "
     f"For anything else, email us at {BIZ['email']}."),
]


# ---------- page ----------

def head():
    title = "Happy Music Box | Portable Sound Machine & Bluetooth Speaker"
    desc = ("A palm-sized sound machine and Bluetooth speaker with built-in 432Hz, 528Hz and 639Hz tracks, "
            "7 LED light modes and a soft-touch silicone finish. Available on Amazon in Pink and Blue.")
    canon = ""
    og_url = ""
    og_img = "img/og.jpg"
    if BASE_URL:
        canon = f'<link rel="canonical" href="{BASE_URL}/">'
        og_url = f'<meta property="og:url" content="{BASE_URL}/">'
        og_img = f"{BASE_URL}/img/og.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{'<meta name="robots" content="noindex">' if DRAFT else ""}
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{canon}
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_img}">
{og_url}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF5E9">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(schema(), ensure_ascii=False)}</script>
</head>"""


def schema():
    product = {
        "@context": "https://schema.org", "@type": "Product",
        "name": "Happy Music Box Portable Bluetooth Speaker & Sound Machine",
        "brand": {"@type": "Brand", "name": BIZ["name"]},
        "description": "Palm-sized sound machine and Bluetooth speaker with built-in 432Hz, 528Hz and 639Hz tracks, "
                       "7 LED light modes and a soft-touch silicone finish.",
        "image": [f"{BASE_URL}/img/cube-1000.webp" if BASE_URL else "img/cube-1000.webp"],
        "color": ["Pink", "Blue"],
        "weight": {"@type": "QuantitativeValue", "value": 12.8, "unitCode": "ONZ"},
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }
    return [product, faq]


def header():
    nav = '<span aria-hidden="true">|</span>'.join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    return f"""<header class="top">
  {WAVES.format(pos="tr")}{WAVES.format(pos="bl")}
  {LOGO}
  <nav class="nav" aria-label="Sections">{nav}</nav>
  {ext(BUY, "Buy on Amazon", "btn")}
</header>"""


def hero():
    return f"""<section class="hero" id="overview">
  <div class="hero-light" aria-hidden="true"></div>
  <h1><span class="h1-wave">{ICON["wave"]}</span>Find Your Rhythm: Ambient Sound &amp; Light Therapy</h1>
  <p class="lede">A 3x3" geometric sound companion loaded with 432Hz, 528Hz, and 639Hz solace frequencies and 7 soft LED ambient modes.</p>
  <div class="stage">
    <div class="spot" aria-hidden="true"></div>
    {pic("cube", 330, "cube", eager=True, sizes="(max-width: 560px) 74vw, 330px")}
    {ext(BUY, "Available on Amazon " + ICON["arrow"], "pill")}
  </div>
</section>"""


def features():
    cols = "".join(f"""
    <div class="feat">
      <span class="feat-icon">{ICON[i]}</span>
      <h2>{t}</h2>
      <p>{d}</p>
    </div>""" for i, t, d in FEATURES)
    return f'<section class="feats">{cols}\n</section>'


def voices():
    # Only real reviews here. As of Oct 3, 2026 the Amazon listing has one (5★, Sept 7, 2026).
    return f"""<section class="voices">
  <div class="reviews">
    <h2 class="script">What our users are saying</h2>
    <div class="cards">
      <figure class="review">
        <figcaption><span class="avatar" aria-hidden="true">YZ</span><span><b>Y.Z.</b>{STARS}</span></figcaption>
        <blockquote>“Super easy to use, and the audio is so calming. Really great product—even our cats are fans!”</blockquote>
        <small>Verified purchase on Amazon</small>
      </figure>
      {ext(BUY + "#customerReviews", "Read reviews on Amazon " + ICON["arrow"], "review review-more")}
    </div>
  </div>
  <div class="glow" role="img" aria-label="Animation of the cube's LED colors cycling">
    <div class="glow-bars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <span class="glow-tag">7 LED light modes</span>
  </div>
</section>"""


def frequencies():
    cards = "".join(f"""
    <div class="freq freq-{tint}">
      <span class="freq-icon">{ICON[i]}</span>
      <strong>{hz}</strong>
      <span class="freq-name">{name}</span>
      <span class="freq-sub">{sub}</span>
    </div>""" for i, hz, name, sub, tint in FREQS)
    uses = "".join(f"""
      <figure>{pic(n, 200, sizes="(max-width: 560px) 44vw, 200px")}<figcaption>{t}</figcaption></figure>""" for n, t in USES)
    return f"""<section class="band" id="frequencies">
  <h2 class="sec">Solace Frequencies</h2>
  <p class="sec-lede">Preloaded with 432Hz, 528Hz and 639Hz frequency tracks for meditation, mindfulness, and creating a calming atmosphere.</p>
  <p class="chip">No phone needed: tap to relax instantly</p>
  <div class="freqs">{cards}
  </div>
  <h3 class="sub">Relax, focus &amp; sleep</h3>
  <div class="uses">{uses}
  </div>
</section>"""


def light():
    return f"""<section class="band" id="light">
  <div class="zig">
    <div class="zig-img">{pic("cube_lit", 380, "fade", sizes="(max-width: 760px) 80vw, 380px")}</div>
    <div class="zig-txt">
      <h2 class="sec">LED Light Modes</h2>
      <p>Choose from 7 LED colors and multiple dynamic light modes to match your mood, your décor or the moment. Soft color glows through the cube's grid while your music or frequency track plays.</p>
    </div>
  </div>
  <div class="zig rev">
    <div class="zig-img">{pic("hand", 300, "rounded", sizes="(max-width: 760px) 70vw, 300px")}</div>
    <div class="zig-txt">
      <h3 class="sub left">Gentle, soft-touch design</h3>
      <ul class="ticks">
        <li>Soothing tactile experience</li>
        <li>Unique 3×3 textured grid design</li>
        <li>Durable, long-lasting silicone</li>
        <li>Comfortable grip with anti-slip protection</li>
      </ul>
    </div>
  </div>
</section>"""


def support():
    rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in SPECS)
    box = "".join(f"<li>{x}</li>" for x in IN_BOX)
    return f"""<section class="band" id="support">
  <h2 class="sec">Support</h2>
  <div class="support">
    <div class="card">
      <h3 class="sub left">What's in the box</h3>
      {pic("box", 460, "boxshot", sizes="(max-width: 760px) 86vw, 460px")}
      <ul class="ticks">{box}</ul>
    </div>
    <div class="card">
      <h3 class="sub left">Specs</h3>
      <table class="specs">{rows}</table>
      <div class="colors">
        {ext(BIZ["amazon_pink"], '<span class="dot pink"></span>Shop Pink', "btn ghost")}
        {ext(BIZ["amazon_blue"], '<span class="dot blue"></span>Shop Blue', "btn ghost")}
      </div>
      <p class="help">Questions? Email <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a>.</p>
    </div>
  </div>
</section>"""


def faq():
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    return f"""<section class="band" id="faq">
  <h2 class="sec">FAQ</h2>
  <div class="faq">{items}</div>
</section>"""


def footer():
    return f"""<footer class="foot">
  <p>© 2026 Happy Music Box. Contact: <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a> ·
     <a href="mailto:{BIZ["email"]}?subject=Partnership">Contact for Partnership</a></p>
  <p class="legal">Happy Music Box is an independent wellness brand. Amazon and the Amazon logo are trademarks of Amazon.com, Inc.</p>
</footer>"""


def page():
    return "\n".join([
        head(), "<body>", '<div class="sheet">', header(), "<main>",
        hero(), features(), voices(), frequencies(), light(), support(), faq(),
        "</main>", footer(), "</div>", "</body></html>",
    ])


def page_404():
    return "\n".join([
        head().replace("<title>", '<meta name="robots" content="noindex"><title>Page not found · '), "<body>", '<div class="sheet">', header(),
        '<main class="band nf"><h1>Page not found</h1><p><a class="btn" href="./">Back to Happy Music Box</a></p></main>',
        footer(), "</div></body></html>",
    ])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    process_images()
    write_icons()
    shutil.copy(os.path.join(ROOT, "templates", "style.css"), os.path.join(OUT, "style.css"))
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(page())
    with open(os.path.join(OUT, "404.html"), "w") as f:
        f.write(page_404())
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    if BASE_URL:
        with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    f"<url><loc>{BASE_URL}/</loc></url></urlset>\n")
        with open(os.path.join(OUT, "robots.txt"), "w") as f:
            f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"built 1 page → {OUT}  BASE_URL={BASE_URL or '(unset)'}")


if __name__ == "__main__":
    main()
