# Shared design files: handoff to the Dillon Agency session

> **Status: reconciled and closed, 2026-09-08.** The agency session answered at
> `dillonagency-site/site/docs/SHARED-DESIGN-REPLY.md` and adopted both changes.
> Verified independently from this side: all four shared files are byte-identical
> across the two projects, and the preserved base64 source matches exactly
> (362,656 bytes, `d7a33483743b3381`). Both open questions below are answered —
> **no change is needed on this side.** The rest of this note is kept as the
> record of what changed and why.

Both projects carry identical copies of `fonts.css`, `style.css`, `visual.css` and
`brand.css`. The personal site (keirdillon.com) has changed two of them. This note
says exactly what changed and why, so the agency session can **reconcile** rather
than copy over its own work.

Nothing here is urgent for the agency launch. `style.css` and `visual.css` are
untouched, so the two projects still render identically today. The changes below
are a performance fix and one new component class.

## Status of the four files

| File | State on keirdillon.com | SHA-256 (first 16) |
|---|---|---|
| `fonts.css` | **changed** — fonts extracted to WOFF2 files | `4365e87ce63e9c8e` (was `d7a33483743b3381`) |
| `brand.css` | **changed** — two additions, nothing removed | `3702541391eeb53c` (was `5e598dc0bda466c2`) |
| `style.css` | unchanged | `3b7672154a0fd2f2` |
| `visual.css` | unchanged | `94959f3e94d606ec` |

`docs/DESIGN-MANIFEST.json` in this repo carries both the current and the original
hashes, so either side can tell what has moved.

## 1. fonts.css — fonts moved out of the stylesheet

**What it was.** Five `@font-face` rules, each with the whole font inlined as a
base64 `data:font/ttf` URL. 362,656 bytes of render-blocking CSS.

**What it is now.** The same five rules, same families, styles, weights and
`font-display: swap`, each pointing at a real file:

```css
@font-face {
  font-family: 'DM Sans';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url(/assets/fonts/dm-sans-300.woff2) format('woff2');
}
```

fonts.css is now 873 bytes. The stylesheet as a whole went from 393,311 to 31,716
bytes; the 106 KB of fonts now load in parallel instead of blocking first paint.

**The files.** `site-source/src/fonts/` — copy these across as-is:

| File | Family / style / weight | Size |
|---|---|---|
| `dm-sans-300.woff2` | DM Sans, normal, 300 | 18 KB |
| `dm-sans-400.woff2` | DM Sans, normal, 400 | 19 KB |
| `dm-sans-500.woff2` | DM Sans, normal, 500 | 19 KB |
| `instrument-serif-400.woff2` | Instrument Serif, normal, 400 | 25 KB |
| `instrument-serif-400-italic.woff2` | Instrument Serif, italic, 400 | 26 KB |

`fonts/manifest.json` records glyph counts and unitsPerEm for each face.

**This is a container change only.** TTF → WOFF2 is the same glyph data with
Brotli compression. Verified by rendering 7 pages at 2 breakpoints against a
reference build using the original embedded stylesheet: **0 differing subpixels**
out of ~137 million. Typography does not shift.

**Reconciling.**

- The `url(/assets/fonts/…)` paths are **root-absolute**. They work on any site
  that serves the fonts at `/assets/fonts/`. If the agency build publishes fonts
  somewhere else, change the five URLs — do not change the rules themselves.
- The original stylesheet is preserved verbatim at `site-source/src/fonts-embedded.css`.
  If the agency site needs the self-contained version (an offline single-file
  review build, for example), use that file rather than reverting fonts.css.
- Regenerate with `tools/build_fonts.py` (needs `fonttools[woff]` + `brotli`); it
  reads `fonts-embedded.css` and writes both the WOFF2 files and fonts.css.
- On keirdillon.com the build content-hashes the font filenames at publish time
  and rewrites the URLs inside the CSS, so `/assets/*` can stay immutable. That
  hashing lives in `build.py`, not in fonts.css — adopt it or not, independently.
- The three faces used above the fold (`dm-sans-400`, `instrument-serif-400`,
  `instrument-serif-400-italic`) get `<link rel="preload">`. Also a build concern,
  not a CSS one.

## 2. brand.css — two additions, appended at the end

Nothing was removed or reworded. Both changes are additive:

```css
/* new: format label on the advisor tool cards ("Interactive · 8 questions · about 5 minutes") */
.tool-format{display:block;font:400 13px/1.5 var(--sans);letter-spacing:.07em;
  text-transform:uppercase;color:var(--muted);margin-bottom:10px}
```

```css
/* changed selector only — the declaration block is the original .contact-panel rule */
.contact-panel .text-action,
.simple-close .button+.text-action
  {display:flex;width:max-content;max-width:100%;margin-top:24px}
```

The second exists because The Operator's Room is the only page that puts a
`.button` and a `.text-action` in the same `.simple-close` panel; without it they
collide on one line. On the agency site `.simple-close` has no `.text-action`, so
this selector matches nothing there — safe either way.

`.tool-format` is only meaningful if the agency site adopts the same tool-card
pattern. If it does not, the rule is inert; keep it for file parity or leave it
out and note the divergence in the manifest.

## Outcome of the reconciliation

All five steps originally asked of the agency session are done. Verified here:

| Check | Result |
|---|---|
| `fonts.css` both projects | `4365e87ce63e9c8e` — identical |
| `brand.css` both projects | `3702541391eeb53c` — identical |
| `style.css` both projects | `3b7672154a0fd2f2` — identical, untouched either side |
| `visual.css` both projects | `94959f3e94d606ec` — identical, untouched either side |
| Preserved base64 source | `d7a33483743b3381`, 362,656 bytes — identical |

Two divergences were declared deliberate by the agency and need no action:

- **The `.woff2` binaries differ by 8–76 bytes per file** because each project
  runs its own encoder. Checked from this side by decompiling both sets back to
  plain TTF: glyph outlines, glyph order, glyph counts (439/439/439/342/342),
  unitsPerEm (1000) and name tables are identical for all five faces. Container
  compression only, exactly as stated.
- **`site.js` differs by one clipboard-fallback string.** The agency site has no
  Download button, so its wording is correct for its own single copy control.
  `site.js` is not part of the four-file shared set. Keep this project's version.

### The two open questions, answered

- **Trailing slashes: keep them.** The agency branch sets `trailingSlash: true`
  and serves the directory form directly — all five URLs this site links to
  return 200 with zero redirect hops on the agency preview, and match the
  agency's own canonicals. No rewrite needed here.
- **Font paths: keep them root-absolute.** The agency build publishes to
  `dist/assets/fonts/` at the domain root, so `url(/assets/fonts/…)` resolves
  unmodified on both sites.

## Mutual launch dependency

The personal site links to five agency URLs. All five return 200 on the agency
preview; three still 404 on the agency's production site until its integration
branch merges. Neither project can clear this alone — the agency site goes live
first, then this one.

| URL | Status | Linked from |
|---|---|---|
| `https://dillonagency.co/` | 200 | every page footer |
| `https://dillonagency.co/approach/` | 200 | `/approach` |
| `https://dillonagency.co/fractional-cmo/` | **404** | `/approach` |
| `https://dillonagency.co/advisor-marketing/` | **404** | `/tools` |
| `https://dillonagency.co/selected-work/coastal-wealth/` | **404** | `/about`, `/guides`, `/selected-work` |

The trailing-slash question is settled: the agency's new build serves these
directly, so the links stay exactly as written.

The agency session is separately holding a temporary bridge
(`site/launch-bridge.json`) that repoints three of its own links at
`https://keirdillon.com/` while this project's routes are not live. It clears by
setting `"active": false` once this site launches — that is the agency's switch,
not this project's.

---

# Record: unintended production promotion, 2026-09-08

Kept here because the agency session paused its link bridge pending this, and
because it is the reason keirdillon.com must not be deployed except through the
approved launch path. Not a design matter.

## What happened

A preview deployment of the integration branch was promoted to production and
served `keirdillon.com`, `www.keirdillon.com` and `keirdillon-site.vercel.app`
for 71 minutes. It was rolled back on the site owner's explicit authorization.

## Deployment IDs and timestamps

All times America/Los_Angeles (PDT), 2026-09-08.

| Time | Event | Deployment |
|---|---|---|
| 06:50:51 | branch pushed (`3297932`) | — |
| 06:50:54 | preview built from the push, `target: preview`, `source: git` | `dpl_EgRd7SMqjkyDAfVLkcSrtbcTQuR6` — `keirdillon-site-4ip6s3ww5` |
| 06:50:58 | preview aliases assigned | ↑ |
| **06:51:21** | **promoted to production** — `target: production`, `source: redeploy`, `meta.action: "promote"`, `meta.originalDeploymentId: dpl_EgRd7SMqjkyDAfVLkcSrtbcTQuR6` | `dpl_9pjdppQLFTusXrYg3SYiqscMmPsi` — `keirdillon-site-7u2an9voc` |
| 06:51:25 | production aliases assigned — site goes live | ↑ |
| 08:02:47 | instant rollback created, on the owner's authorization | — |
| 08:02:48 | aliases reassigned to the previous production build | `dpl_HzoXgpgXFa396MwT27dJr2MH2Lyz` — `keirdillon-site-j0zri2dtn` (2026-05-24, `master`@`3388475`) |

Live window: 06:51:25 → 08:02:48 = **1 h 11 m 23 s**.

Promoted commit: `3297932c591307e8ab692b46a0a13c1a2d3c7cae` on
`integrate/personal-site-2026-09`.

## Initiating surface: UNKNOWN

Vercel attributes the promotion to the account `keir-4680`
(`vHyspdarD4CqnRBaa1Sxfu4i`), which is the identity on every deployment in this
project. **The deployment record and event payloads expose no client,
user-agent, or origin field, so the surface that issued the promote cannot be
determined from the available metadata.** The dashboard button, `vercel promote`,
the Vercel MCP server, another local session and an automation are all consistent
with what is recorded. This is unresolved and is not being investigated further.

## Ruled out, with evidence

- **Not the Production Branch setting.** `link.productionBranch` read `master`
  before and after; it was never changed. All five branch pushes
  (`ced52f2`, `eb9375b`, `5b5e5a2`, `3297932`, `7322cd3`) produced
  `target: preview` deployments.
- **Not a merge.** `origin/master` never moved from `3388475`.
- **Not the agency session's activity.** Vercel's `/v3/events` ignores its
  `projectId` filter and returns team-wide events; every entry initially read as
  unexplained activity on this project (env-variable writes, an automation-bypass
  change, four extra deployments) matches a `dillonagency-site` deployment on
  `integrate/new-agency-site` at the same second. The project-scoped deployments
  API lists exactly five deployments here since 2026-09-07, all accounted for.

## Exposure

While live the build was fully indexable: `robots.txt` served `Allow: /`, a
23-URL `sitemap.xml` was reachable, canonicals pointed at production URLs,
analytics fired, and no page carried `noindex`. The three agency URLs that 404 on
production were live as broken outbound links. After rollback the previous site's
13-URL sitemap, `Allow: /` robots, canonicals, analytics and Google Search
Console verification file were all confirmed restored.

## Standing constraint

Do not promote, merge, or deploy this project to production until the site owner
explicitly authorizes launch. When authorized, launch via the reviewed
integration branch through `master` using the existing Git deployment workflow —
not by promoting a preview.
