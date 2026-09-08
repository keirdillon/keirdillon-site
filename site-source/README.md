# Keir Dillon: complete website source

September 2026 / Two-brand architecture edition

This package belongs to **https://keirdillon.com**. It contains 14 complete pages, editable source, local image masters, embedded fonts, styling, scripts, review output, production-reference output, verification, and a project-specific Claude Code handoff. It is independently buildable and does not need the other project folder.

## Start here

1. Open `keir-dillon-website.html` to review the complete website in one self-contained HTML file. Internal navigation and the three advisor tools work in that file. Links to the other brand and email/LinkedIn use their external destinations.
2. Read `CLAUDE-CODE-HANDOFF.md` inside this package and use it in the matching existing Claude Code project.
3. Read `docs/BRAND-ARCHITECTURE.md` and `docs/ROUTE-MAP.csv` before changing the existing site.

This is a complete new source package, not an export of the existing live repository. Existing resources, contact providers, analytics, verification files, redirects, and legal/privacy pages must be preserved or deliberately merged. Do not unzip over your project root and replace files blindly.

## One current source of truth

- `src/pages.py`: every page’s content and metadata. This is the public-copy authority.
- `src/components.py`: photo and contact helpers.
- `src/fonts.css`, `src/style.css`, `src/visual.css`, `src/brand.css`: complete shared Rams design; identical copies in the companion project.
- `src/assets.json` and `src/assets/`: local image masters, provenance, dimensions, and byte hashes.
- `src/site.js`: menus, standalone navigation, copy actions, and supported interactions.
- `src/tools.js`: deterministic advisor tools; no AI/API calls or data storage.
- `site.json`: this brand’s domain, peer domain, review origins, navigation, and output filename.
- `build.py`: dependency-free Python static builder. Python 3.9+; no pip/npm install required to build.
- `verify.py`: structural, asset, JavaScript, and metadata checks. Node is used only for JavaScript verification.
- `build_vercel.py`: optional environment-aware Vercel build adapter.
- `vercel.example.json`: candidate settings to merge into the existing project, not an instruction to replace its configuration.

## Review build

Run `python3 build.py` from this package root. It emits `dist/` and `keir-dillon-website.html`. Review pages are deliberately noindex,nofollow with a disallow-all robots.txt. This is an indexing signal, not access control.

The single-file review embeds all images and fonts and can therefore be large. The multipage build shares local assets across routes. Original image bytes and the approved framing are preserved. If generating optimized production derivatives later, retain the masters and check the crops at the actual breakpoints.

## Production build

After confirming the actual production origin, run:

`python3 build.py --production https://keirdillon.com`

This builds `dist/` with indexable pages, correct-domain canonicals, a sitemap, robots.txt, Open Graph text metadata, and linked Person/Organization/WebSite/page structured data. The standalone review remains noindex. No new social-sharing image was created; retain an existing appropriate one during the migration if present.

The bundled `dist-production/` is a production-reference build for https://keirdillon.com. Rebuild it after any source change using `python3 build.py --production https://keirdillon.com --output dist-production`. It is supplied for review and integration, not automatically deployed to your domain.

Only `dist/` (or the deliberately selected final public output) should be served. The source root contains internal handoff and architecture documents. Never make the whole package root the public output directory.

## Vercel integration

Use the existing project and GitHub connection. The example config runs `python3 build_vercel.py` and serves `dist/`. The adapter checks VERCEL_ENV: production uses this project’s confirmed domain; previews stay noindex. Verify Python availability and the real project’s build setup in the Vercel preview. A framework conversion is not required. The existing application may instead retain its own build and incorporate this design/content.

Do not promote a noindex preview artifact unchanged to production. The production release needs the production-mode build and final metadata checks. Merge the existing sitemap and preserve current public resources/verification files in the final output. The builder replaces its generated output directory, so any retained routes must become part of the build or be copied into the final output by the integration step.

## Verification and remaining integration

Run `python3 verify.py`. Optionally use `--peer-project /absolute/path/to/the/other/package` to check cross-site routes and identical design files. `verification.json` records the checks actually completed. Browser layout, clipboard/download/mail-client behavior, existing production integrations, and live search indexing have not been verified by this package.

Both current public sites publish keir@dillonagency.co; this is the contact destination. The email button opens the user’s email application, and a copy-address fallback is provided. A working old form/provider can be retained during integration. There is no backend submission, newsletter signup, analytics, membership, payment service, or AI API installed in this source.

The two websites have distinct content ownership. Keep Keir’s full story and advisor resources on his personal domain; keep detailed services and firm engagement scope at Dillon Agency. The agency’s Coastal Wealth page describes scope, not measured results or an endorsement.
