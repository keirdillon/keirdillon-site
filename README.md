# keirdillon.com

Personal site for Keir Dillon — fractional CMO for wealth management firms and
founder of Dillon Agency. Story, perspective, selected work, advisor resources
and a concise "Work with me" page.

Detailed firm services, delivery and commercial engagements live on the companion
site, **dillonagency.co**. Each substantial piece has one primary home; the other
site summarises and links.

## Layout

```
build.py        Publish build. Runs the source package, overlays the preserved
                legacy routes, writes robots.txt/sitemap.xml, injects analytics,
                favicon and social metadata. Output: dist/
vercel.json     Build command, output dir, clean URLs, redirects, headers, CSP
site-source/    Source package for the current site (September 2026 edition).
                Internal — never served.
  src/pages.py    public copy authority for the 14 new pages
  src/*.css       fonts, base, visual and brand layers (shared design with
                  dillonagency.co — change both together)
  src/tools.js    the three advisor tools (pure functions, no network)
  src/site.js     nav, copy and download behaviour
  src/assets/     image masters + assets.json provenance
  site.json       domain, peer domain, nav, descriptor, contact address
  docs/           brand architecture, route map, asset and proof notes
public/         Preserved legacy public routes, copied verbatim into dist/
  resources/**    Positioning Blueprint, Sniff Test hub + 4 audience variants + PDFs
  prompts/**      prompt library
  style.css       legacy stylesheet (used only by the pages above)
  main.js         legacy script (used only by the pages above)
  googlea8f86105fc6a4cb6.html   Google Search Console verification
  The_Positioning_Blueprint.pdf
dist/           Generated. Git-ignored. The only thing Vercel serves.
new-website/    Incoming ZIP + extraction. Git-ignored, never deployed.
```

Only `dist/` is published, so `site-source/`, `public/` sources, docs and handoff
material are never reachable as URLs.

## Build

```bash
python3 build.py               # preview build: noindex, no analytics
python3 build.py --production  # production build for https://keirdillon.com
python3 -m http.server -d dist # quick local look (no clean URLs)
```

On Vercel the build command is `python3 build.py`; `VERCEL_ENV=production`
switches on indexing, canonicals, sitemap, social metadata and analytics, so
preview deployments stay unindexed automatically.

Set `PEER_PREVIEW_ORIGIN` to point cross-brand links at a Dillon Agency preview
instead of the live agency domain.

## Routes

| URL | Source |
|---|---|
| `/`, `/about`, `/approach`, `/selected-work` | site-source |
| `/tools`, `/tools/client-brief`, `/tools/presence-check`, `/tools/content-plan` | site-source |
| `/guides` + 3 guides, `/the-operators-room`, `/contact` | site-source |
| `/resources`, `/resources/positioning-blueprint`, `/resources/audit` (+4 variants) | public/ |
| `/prompts`, `/prompts/positioning` | public/ |
| `/story` → `/about`, `/thinking` → `/guides` | 301 in vercel.json |

## Integrations

- Analytics: GA4 `G-THTL2M1JL2`, production builds only.
- Google Search Console: `/googlea8f86105fc6a4cb6.html` (also served at the
  extensionless path by `cleanUrls`).
- Contact: `mailto:keir@dillonagency.co` plus a copy-address fallback. No form
  backend, no data collection.
- The advisor tools run entirely in the browser; nothing is transmitted or stored.
