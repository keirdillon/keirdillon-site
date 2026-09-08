# Shared design files: handoff to the Dillon Agency session

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

## What the agency session should do

1. **Do not overwrite.** Diff first. If the agency session has its own edits to
   `fonts.css` or `brand.css`, merge these changes into them.
2. `style.css` and `visual.css` are unchanged here — if they differ on the agency
   side, that divergence came from the agency work, and this project should
   probably take it rather than the other way round.
3. Copy `site-source/src/fonts/*.woff2` and adjust the five URLs if the publish
   path differs.
4. Update `docs/DESIGN-MANIFEST.json` on both sides once reconciled, so the
   hashes agree again.
5. Tell this project if the agency build needs different font paths — it is a
   one-line change here.

## Unrelated, but needed before keirdillon.com can launch

The personal site links to five agency URLs. Three currently 404 and are the
launch blocker on this side:

| URL | Status | Linked from |
|---|---|---|
| `https://dillonagency.co/` | 200 | every page footer |
| `https://dillonagency.co/approach/` | 200 | `/approach` |
| `https://dillonagency.co/fractional-cmo/` | **404** | `/approach` |
| `https://dillonagency.co/advisor-marketing/` | **404** | `/tools` |
| `https://dillonagency.co/selected-work/coastal-wealth/` | **404** | `/about`, `/guides`, `/selected-work` |

Note the trailing slashes. dillonagency.co currently 308-redirects `/path/` to
`/path`; if that stays, these links each cost a redirect hop. Either serve them
at the trailing-slash form, or tell this project and the five links get rewritten
without it.
