#!/usr/bin/env python3
"""Extract the base64 TTFs embedded in fonts.css into real WOFF2 files.

Run locally when the design's fonts change; the output is committed so the
Vercel build needs no font tooling:

    <venv>/bin/python tools/build_fonts.py

Reads site-source/src/fonts-embedded.css (the original, kept verbatim as the
master), writes site-source/src/fonts/*.woff2 plus a rewritten
site-source/src/fonts.css that points at /assets/fonts/.

Family, style and weight are carried through untouched — only the container
format changes (TTF -> WOFF2, which is the same glyph data, Brotli-compressed).

Requires: fonttools[woff], brotli.
"""
from pathlib import Path
import base64, io, json, re, sys

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site-source/src"
EMBEDDED = SRC / "fonts-embedded.css"
OUT_CSS = SRC / "fonts.css"
OUT_DIR = SRC / "fonts"

FACE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
DATA = re.compile(r"url\(data:font/([a-z0-9+-]+);base64,([A-Za-z0-9+/=]+)\)\s*format\('([^']+)'\)")


def prop(block, name):
    m = re.search(rf"{name}\s*:\s*([^;]+);", block)
    return m.group(1).strip() if m else None


def slug(family, style, weight):
    return f"{family.strip().strip(chr(39)).lower().replace(' ', '-')}-{weight}{'-italic' if style == 'italic' else ''}"


def main():
    css = EMBEDDED.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.woff2"):
        old.unlink()

    faces, rules, before, after = [], [], 0, 0
    for block in FACE.findall(css):
        family = prop(block, "font-family")
        style = prop(block, "font-style") or "normal"
        weight = prop(block, "font-weight") or "400"
        display = prop(block, "font-display") or "swap"

        m = DATA.search(block)
        if not m:
            raise SystemExit("expected one embedded font per @font-face block")
        raw = base64.b64decode(m.group(2))

        font = TTFont(io.BytesIO(raw))
        name = slug(family, style, weight) + ".woff2"
        font.flavor = "woff2"
        font.save(OUT_DIR / name)
        size = (OUT_DIR / name).stat().st_size

        # unitsPerEm and the name table confirm we carried the same face over.
        real_family = next((r.toUnicode() for r in font["name"].names if r.nameID == 1), "?")
        faces.append({
            "file": name, "family": family, "style": style, "weight": weight,
            "name_table_family": real_family,
            "glyphs": font["maxp"].numGlyphs,
            "upem": font["head"].unitsPerEm,
            "ttf_bytes": len(raw), "woff2_bytes": size,
        })
        before += len(raw)
        after += size

        rules.append(
            "@font-face {\n"
            f"  font-family: {family};\n"
            f"  font-style: {style};\n"
            f"  font-weight: {weight};\n"
            f"  font-display: {display};\n"
            f"  src: url(/assets/fonts/{name}) format('woff2');\n"
            "}\n"
        )
        print(f"{family:20s} {style:7s} {weight:4s} -> {name:34s} "
              f"{len(raw)/1024:7.0f}KB TTF -> {size/1024:6.0f}KB WOFF2  "
              f"({font['maxp'].numGlyphs} glyphs, upem {font['head'].unitsPerEm}, "
              f"name table: {real_family})")

    OUT_CSS.write_text("".join(rules), encoding="utf-8")
    (OUT_DIR / "manifest.json").write_text(json.dumps(faces, indent=1) + "\n")

    print(f"\nfonts.css {len(css)/1024:.0f}KB (base64 TTF) -> "
          f"{OUT_CSS.stat().st_size} bytes CSS + {after/1024:.0f}KB WOFF2 "
          f"(from {before/1024:.0f}KB of TTF, {len(faces)} faces)")


if __name__ == "__main__":
    sys.exit(main())
