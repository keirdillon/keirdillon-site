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
OG_IMAGE = "/assets/keir-editorial.jpg"       # 1600x900 master already shipped with the design
OG_IMAGE_SIZE = ("1600", "900")
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
RETIRED = {"/story": "/about", "/thinking": "/guides"}


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
        f'<meta property="og:image" content="{ORIGIN}{OG_IMAGE}">',
        f'<meta property="og:image:width" content="{OG_IMAGE_SIZE[0]}">',
        f'<meta property="og:image:height" content="{OG_IMAGE_SIZE[1]}">',
        '<meta property="og:image:alt" content="Keir Dillon, fractional CMO and founder of Dillon Agency">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{ORIGIN}{OG_IMAGE}">',
        ANALYTICS_SNIPPET,
    ]
    return "".join(bits)


ANALYTICS_SNIPPET = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>'
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
    f'gtag("js",new Date());gtag("config","{ANALYTICS_ID}");</script>'
)

CURRENT = {"html": ""}


def process_new_page(path, file_rel, production, asset_map):
    html = path.read_text(encoding="utf-8")
    html = rewrite_links(html, file_rel)
    for old, new in asset_map.items():
        html = html.replace(old, new)
    if production:
        html = normalise_trailing_slash(html)
    CURRENT["html"] = html
    html = html.replace("</head>", head_injection(clean_url(file_rel), production) + "</head>", 1)
    path.write_text(html, encoding="utf-8")


def process_legacy_page(path, production):
    html = path.read_text(encoding="utf-8")
    # Point the legacy chrome at the routes that replaced /story and /thinking.
    for old, new in RETIRED.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
    if production:
        if ANALYTICS_ID not in html:
            # /prompts never carried the tag; make analytics consistent across the site.
            html = html.replace("</head>", ANALYTICS_SNIPPET + "</head>", 1)
            log(f"  + analytics added to {path.relative_to(DIST)}")
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
def hash_assets(dist):
    """Content-hash the generated stylesheet and script so /assets/* can stay immutable."""
    mapping = {}
    for name in ("style.css", "site.js"):
        f = dist / "assets" / name
        digest = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
        stem, ext = name.rsplit(".", 1)
        new = f"{stem}.{digest}.{ext}"
        f.rename(dist / "assets" / new)
        mapping[f"/assets/{name}"] = f"/assets/{new}"
    return mapping


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

    built = build_source(production)

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(built, DIST)

    asset_map = hash_assets(DIST)
    new_pages = sorted(
        str(p.relative_to(DIST)) for p in DIST.rglob("*.html")
    )
    for rel in new_pages:
        process_new_page(DIST / rel, rel, production, asset_map)
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
