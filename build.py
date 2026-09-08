#!/usr/bin/env python3
"""Publish build for keirdillon.com.

Composes the final public output in ``dist/`` from two sources:

  site-source/   the September 2026 personal-site source package (build.py + src/)
  public/        preserved legacy public routes (resources, prompts, PDFs,
                 Google verification, legacy stylesheet/script)

Nothing outside ``dist/`` is served, so the source package, its docs and the
handoff files never become public URLs.

Usage
    python3 build.py                      preview build   (noindex, no analytics)
    python3 build.py --production         production build (indexable, analytics)

On Vercel the build command is ``python3 build.py`` and VERCEL_ENV=production
selects the production build automatically.
"""
from pathlib import Path
from html import escape
import argparse, hashlib, json, os, posixpath, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "site-source"
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

SITE = json.loads((SOURCE / "site.json").read_text(encoding="utf-8"))
ORIGIN = SITE["domain"]                       # https://keirdillon.com  (confirmed production host)
ANALYTICS_ID = "G-THTL2M1JL2"                 # existing GA4 property, preserved from the previous site
# Open Graph image, generated alongside the responsive derivatives.
_OG = json.loads((ROOT / "site-source/src/assets-web/manifest.json").read_text())["keir-editorial.jpg"]["og"]
OG_IMAGE = "/assets/img/" + _OG["file"]
OG_IMAGE_SIZE = (str(_OG["w"]), str(_OG["h"]))
# Faces used in the first screenful of nearly every page.
PRELOAD_FONTS = ["dm-sans-400.woff2", "instrument-serif-400.woff2", "instrument-serif-400-italic.woff2"]
FAVICON = (
    "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E"
    "%3Ccircle%20cx='16'%20cy='16'%20r='16'%20fill='%238C6840'/%3E%3C/svg%3E"
)

# Legacy routes that stay published, with the lastmod already recorded for them.
LEGACY_ROUTES = [
    ("/resources", "2026-05-20"),
    ("/resources/positioning-blueprint", "2026-05-20"),
    ("/resources/audit", "2026-05-24"),
    ("/resources/audit/financial-advisor", "2026-05-24"),
    ("/resources/audit/the-firm", "2026-05-24"),
    ("/resources/audit/financial-leadership", "2026-05-24"),
    ("/resources/audit/outside-financial-services", "2026-05-24"),
    ("/prompts", "2026-04-26"),
    ("/prompts/positioning", "2026-04-26"),
]

# Retired legacy pages -> their replacement, kept in step with vercel.json.
# The label moves with the link so the legacy chrome does not send visitors to a
# page called something else.
RETIRED = {"/story": "/about", "/thinking": "/guides"}
RETIRED_LABELS = {">Story<": ">My story<", ">Thinking<": ">Field notes<"}


def log(msg):
    print(f"[build] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# 1. Build the supplied source package
# --------------------------------------------------------------------------- #
def build_source(production):
    cmd = [sys.executable, "build.py"]
    if production:
        cmd += ["--production", ORIGIN]
    else:
        # Previews link to the live agency site by default; PEER_PREVIEW_ORIGIN can point
        # at the agency's own preview when the two are being reviewed together.
        cmd += ["--peer-origin", os.environ.get("PEER_PREVIEW_ORIGIN") or SITE["peer_domain"]]
    subprocess.run(cmd, cwd=SOURCE, check=True)
    return SOURCE / "dist"


# --------------------------------------------------------------------------- #
# 2. HTML post-processing
# --------------------------------------------------------------------------- #
def clean_url(file_rel):
    """dist-relative HTML file path -> the URL it is served at (cleanUrls, no trailing slash)."""
    if file_rel == "index.html":
        return "/"
    if file_rel.endswith("/index.html"):
        return "/" + file_rel[: -len("/index.html")]
    return "/" + file_rel[: -len(".html")] if file_rel.endswith(".html") else "/" + file_rel


def rewrite_links(html, file_rel):
    """Relative in-build links become root-absolute clean URLs.

    The supplied build emits ``../about/index.html`` style hrefs. The site is served
    with cleanUrls + trailingSlash:false (the existing project configuration), so
    those are resolved once here instead of costing every visitor a 308.
    """
    here = posixpath.dirname(file_rel)

    def resolve(target):
        joined = posixpath.normpath(posixpath.join(here, target)) if here else posixpath.normpath(target)
        return clean_url(joined)

    def sub_attr(m):
        attr, value = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|tel:|data:|#|/)", value):
            return m.group(0)
        base, _, frag = value.partition("#")
        if base.endswith(".html"):
            out = resolve(base)
        else:  # assets/style.css, ../assets/keir-current.jpg
            out = "/" + posixpath.normpath(posixpath.join(here, base)) if here else "/" + posixpath.normpath(base)
        return f'{attr}="{out}{"#" + frag if frag else ""}"'

    html = re.sub(r'\b(href|src)="([^"]+)"', sub_attr, html)
    # Absolute self-links written into the copy resolve inside the current deployment.
    html = re.sub(r'(<a\b[^>]*?href=")' + re.escape(ORIGIN) + r'(/[^"]*)"', r'\1\2"', html)
    return html


def normalise_trailing_slash(html):
    """`https://keirdillon.com/about/` -> `https://keirdillon.com/about` in canonicals,
    og:url, sitemap locs and the JSON-LD @id graph. The bare origin is left intact."""
    return re.sub(r"(" + re.escape(ORIGIN) + r"/[A-Za-z0-9\-/]+)/(?=[\"#<])", r"\1", html)


def head_injection(url, production):
    """Favicon always; analytics, social cards and the OG image only in production."""
    bits = [f'<link rel="icon" href="{FAVICON}">', '<meta name="theme-color" content="#FAF8F4">']
    if not production:
        return "".join(bits)
    title = re.search(r"<title>(.*?)</title>", CURRENT["html"], re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', CURRENT["html"])
    title = title.group(1) if title else SITE["brand"]
    desc = desc.group(1) if desc else ""
    bits += [
        social_image_tags(),
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        ANALYTICS_SNIPPET,
    ]
    return "".join(bits)


def social_image_tags():
    return (
        f'<meta property="og:image" content="{ORIGIN}{OG_IMAGE}">'
        f'<meta property="og:image:width" content="{OG_IMAGE_SIZE[0]}">'
        f'<meta property="og:image:height" content="{OG_IMAGE_SIZE[1]}">'
        '<meta property="og:image:alt" content="Keir Dillon, fractional CMO and founder of Dillon Agency">'
        f'<meta name="twitter:image" content="{ORIGIN}{OG_IMAGE}">'
    )


ANALYTICS_SNIPPET = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>'
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
    f'gtag("js",new Date());gtag("config","{ANALYTICS_ID}");</script>'
)

CURRENT = {"html": ""}


def process_new_page(path, file_rel, production, asset_map, font_map):
    html = path.read_text(encoding="utf-8")
    html = rewrite_links(html, file_rel)
    html, image_preload = to_picture(html, clean_url(file_rel))
    for old, new in asset_map.items():
        html = html.replace(old, new)
    if production:
        html = normalise_trailing_slash(html)
    CURRENT["html"] = html

    preload = "".join(
        f'<link rel="preload" as="font" type="font/woff2" '
        f'href="{font_map[f"/assets/fonts/{name}"]}" crossorigin>'
        for name in PRELOAD_FONTS if f"/assets/fonts/{name}" in font_map
    ) + image_preload
    html = html.replace("</head>", preload + head_injection(clean_url(file_rel), production) + "</head>", 1)
    path.write_text(html, encoding="utf-8")


def process_legacy_page(path, production):
    html = path.read_text(encoding="utf-8")
    # Point the legacy chrome at the routes that replaced /story and /thinking.
    for old, new in RETIRED.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
    for old, new in RETIRED_LABELS.items():
        html = html.replace(old, new)
    if production:
        if ANALYTICS_ID not in html:
            # /prompts never carried the tag; make analytics consistent across the site.
            html = html.replace("</head>", ANALYTICS_SNIPPET + "</head>", 1)
            log(f"  + analytics added to {path.relative_to(DIST)}")
        if "og:image" not in html:
            # These pages already declare summary_large_image but shipped no image.
            html = html.replace("</head>", social_image_tags() + "</head>", 1)
    else:
        html = re.sub(r'<meta name="robots"[^>]*>', "", html)
        html = html.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
        html = html.replace(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>', ""
        )
        html = re.sub(r'gtag\("config", "' + ANALYTICS_ID + r'"\);', "", html)
    path.write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------- #
# 3. Compose dist/
# --------------------------------------------------------------------------- #
IMAGES = json.loads((SOURCE / "src/assets-web/manifest.json").read_text(encoding="utf-8"))


def check_masters():
    """The derivatives are generated offline and committed; make drift loud."""
    stale = []
    for filename, e in IMAGES.items():
        master = SOURCE / "src/assets" / filename
        if not master.exists():
            stale.append(filename + " (master missing)")
        elif hashlib.sha256(master.read_bytes()).hexdigest() != e["master_sha256"]:
            stale.append(filename + " (master changed)")
    if stale:
        raise SystemExit(
            "Image derivatives are out of date: " + ", ".join(stale)
            + "\nRe-run tools/build_images.py and commit site-source/src/assets-web/."
        )


def srcset(entries):
    return ", ".join(f"/assets/img/{v['file']} {v['w']}w" for v in entries)


def to_picture(html, page_url):
    """Swap each <img> for a <picture> with AVIF and WebP sources.

    Every attribute the design set — alt, width/height, loading, decoding,
    fetchpriority — is carried through to the fallback <img> unchanged, so
    framing, aspect ratio and loading priority are untouched.
    """
    preloads = []

    def one(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        e = IMAGES.get(posixpath.basename(src))
        if not e:
            return tag
        rest = re.sub(r'\ssrc="[^"]+"', "", tag)[len("<img"):].rstrip("/>").strip()
        fb = f"/assets/img/{e['fallback']['file']}"
        if 'fetchpriority="high"' in tag:
            preloads.append(
                '<link rel="preload" as="image" type="image/avif" '
                f'imagesrcset="{escape(srcset(e["avif"]), quote=True)}" '
                f'imagesizes="{escape(e["sizes"], quote=True)}" fetchpriority="high">'
            )
        return (
            "<picture>"
            f'<source type="image/avif" srcset="{escape(srcset(e["avif"]), quote=True)}" '
            f'sizes="{escape(e["sizes"], quote=True)}">'
            f'<source type="image/webp" srcset="{escape(srcset(e["webp"]), quote=True)}" '
            f'sizes="{escape(e["sizes"], quote=True)}">'
            f'<img src="{fb}" {rest}>'
            "</picture>"
        )

    html = re.sub(r"<img\b[^>]*>", one, html)
    return html, "".join(preloads)


def hashed(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    stem, ext = path.name.rsplit(".", 1)
    new = f"{stem}.{digest}.{ext}"
    path.rename(path.with_name(new))
    return new


def hash_assets(dist):
    """Content-hash everything under /assets/ so the immutable cache header is safe.

    Fonts are hashed first because the stylesheet references them; the CSS is
    hashed afterwards so its own hash covers the rewritten URLs.
    """
    fonts = {}
    for f in sorted((dist / "assets/fonts").glob("*.woff2")):
        fonts[f"/assets/fonts/{f.name}"] = f"/assets/fonts/{hashed(f)}"

    css = dist / "assets/style.css"
    text = css.read_text(encoding="utf-8")
    for old, new in fonts.items():
        text = text.replace(old, new)
    css.write_text(text, encoding="utf-8")

    mapping = {}
    for name in ("style.css", "site.js"):
        f = dist / "assets" / name
        mapping[f"/assets/{name}"] = f"/assets/{hashed(f)}"
    return mapping, fonts


def write_sitemap(dist, pages):
    entries = [(clean_url(p), None) for p in pages] + LEGACY_ROUTES
    body = "".join(
        f"<url><loc>{ORIGIN if url != '/' else ORIGIN + '/'}{'' if url == '/' else url}</loc>"
        + (f"<lastmod>{mod}</lastmod>" if mod else "")
        + "</url>"
        for url, mod in entries
    )
    (dist / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + "</urlset>",
        encoding="utf-8",
    )
    return len(entries)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", action="store_true", help="Indexable build for " + ORIGIN)
    args = ap.parse_args()
    production = args.production or os.environ.get("VERCEL_ENV") == "production"

    log(f"origin={ORIGIN} production={production} python={sys.version.split()[0]}")

    check_masters()
    built = build_source(production)

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(built, DIST)

    # Serve the responsive derivatives and the extracted WOFF2 faces; the image
    # masters and the base64 stylesheet stay in the repo as source only.
    (DIST / "assets/img").mkdir(parents=True, exist_ok=True)
    derived = 0
    for f in sorted((SOURCE / "src/assets-web").iterdir()):
        if f.suffix in (".avif", ".webp", ".jpg", ".png"):
            shutil.copyfile(f, DIST / "assets/img" / f.name)
            derived += 1
    (DIST / "assets/fonts").mkdir(parents=True, exist_ok=True)
    for f in sorted((SOURCE / "src/fonts").glob("*.woff2")):
        shutil.copyfile(f, DIST / "assets/fonts" / f.name)
    dropped = 0
    for filename in IMAGES:
        master = DIST / "assets" / filename
        if master.exists():
            master.unlink()
            dropped += 1
    log(f"images: {derived} derivatives, {dropped} masters left undeployed; "
        f"fonts: {len(PRELOAD_FONTS)} preloaded of "
        f"{len(list((SOURCE / 'src/fonts').glob('*.woff2')))}")

    asset_map, font_map = hash_assets(DIST)
    new_pages = sorted(
        str(p.relative_to(DIST)) for p in DIST.rglob("*.html")
    )
    for rel in new_pages:
        process_new_page(DIST / rel, rel, production, asset_map, font_map)
    log(f"new pages: {len(new_pages)}")

    # Overlay the preserved legacy routes. Never overwrite a page from the new build.
    copied, skipped = 0, []
    for src in sorted(PUBLIC.rglob("*")):
        if src.is_dir() or src.name == ".DS_Store":
            continue
        rel = src.relative_to(PUBLIC)
        dest = DIST / rel
        if dest.exists():
            skipped.append(str(rel))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        if dest.suffix == ".html" and rel.name != "googlea8f86105fc6a4cb6.html":
            process_legacy_page(dest, production)
        copied += 1
    log(f"legacy files: {copied} copied" + (f", {len(skipped)} skipped (collision: {skipped})" if skipped else ""))

    if production:
        count = write_sitemap(DIST, new_pages)
        (DIST / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n", encoding="utf-8"
        )
        log(f"sitemap: {count} urls; robots: indexable")
    else:
        (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        for f in ("sitemap.xml",):
            (DIST / f).unlink(missing_ok=True)
        log("robots: disallow all (preview stays unindexed)")

    total = sum(1 for p in DIST.rglob("*") if p.is_file())
    log(f"done: {total} files in {DIST}")


if __name__ == "__main__":
    main()
