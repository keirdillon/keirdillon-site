#!/usr/bin/env python3
"""Generate responsive AVIF/WebP derivatives from the image masters.

Run locally when a master changes; the output is committed so the Vercel build
needs no image tooling:

    <venv>/bin/python tools/build_images.py

Masters in site-source/src/assets/ are never modified. Derivatives and a
manifest are written to site-source/src/assets-web/, which build.py copies into
dist/assets/img/ and uses to emit <picture> markup.

Requires: pillow, pillow-avif-plugin.
"""
from pathlib import Path
import hashlib, json, math, sys

from PIL import Image, ImageChops
import pillow_avif  # noqa: F401  (registers the AVIF plugin)

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ROOT / "site-source/src/assets"
OUT = ROOT / "site-source/src/assets-web"

# Rendered CSS width of each image at a range of viewport widths, measured in
# Chrome against the built site. Regenerate with tools/measure_images.js if the
# layout changes.
MEASURED = json.loads((Path(__file__).parent / "image-widths.json").read_text())

QUALITY = {"avif": 62, "webp": 80, "jpeg": 86}
# Quality floor. Anything below this is re-encoded at a higher setting until it
# clears the bar, so flat gradients and skies do not band.
TARGET_PSNR = 38.0
QUALITY_STEPS = [62, 68, 74, 80, 86]
MAX_DPR = 2          # 3x displays fall back to the 2x file; the extra bytes are not worth it
STEP = 1.4           # ratio between neighbouring srcset widths
# keir-editorial doubles as the Open Graph image, which wants >=1200px wide.
# That is a separate file: the <img> fallback stays sized for the layout.
OG_IMAGE = ("keir-editorial.jpg", 1600)


def sizes_attr(m):
    """Build a `sizes` value from the measured widths.

    Media conditions are evaluated left to right, so they run widest first.
    """
    def vw(viewports):
        return math.ceil(max(m[str(v)] / v for v in viewports) * 100)

    big = m["1728"]
    mid = max(m["1280"], m["1440"])
    return (
        f"(min-width: 1600px) {big}px, "
        f"(min-width: 1280px) {mid}px, "
        f"(min-width: 768px) {vw([768, 1024])}vw, "
        f"{vw([360, 390, 480, 640])}vw"
    )


def widths_for(m, natural):
    """A geometric ladder from the smallest 1x layout width to the largest 2x one.

    Steps of 1.4x keep every request within ~40% of what the layout actually
    needs. Merging near-duplicates instead would leave gaps big enough that a
    390px phone at DPR 2 gets handed the desktop file.
    """
    lo = int(math.ceil(min(m[str(v)] for v in (360, 390, 480))))
    hi = min(natural, int(math.ceil(max(m.values()) * MAX_DPR)))
    lo = max(160, min(lo, hi))

    ladder, w = [], lo
    while w < hi / STEP:
        ladder.append(int(round(w)))
        w *= STEP
    ladder.append(hi)
    return sorted({min(x, natural) for x in ladder})


def encode(im, path, fmt, quality=None):
    if fmt == "avif":
        im.save(path, "AVIF", quality=quality or QUALITY["avif"], speed=4)
    elif fmt == "webp":
        im.save(path, "WEBP", quality=quality or QUALITY["webp"], method=6)
    elif fmt == "png":
        im.save(path, "PNG", optimize=True)
    else:
        im.convert("RGB").save(path, "JPEG", quality=QUALITY["jpeg"], optimize=True, progressive=True)


def psnr(a, b):
    """Peak signal-to-noise ratio between the resized master and its AVIF."""
    a = a.convert("RGB"); b = b.convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size, Image.LANCZOS)
    hist = ImageChops.difference(a, b).histogram()
    total, sq = 0, 0
    for ch in range(3):
        for value, count in enumerate(hist[ch * 256:(ch + 1) * 256]):
            sq += value * value * count
            total += count
    mse = sq / total if total else 0
    return 99.0 if mse == 0 else 10 * math.log10(255 * 255 / mse)


def resize(im, w):
    if w >= im.width:
        return im
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def main():
    assets = json.loads((ROOT / "site-source/src/assets.json").read_text())
    by_file = {a["file"]: key for key, a in assets.items()}

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*"):
        if old.is_file():
            old.unlink()

    manifest, before, after = {}, 0, 0
    for filename, measured in sorted(MEASURED.items()):
        master = MASTERS / filename
        im = Image.open(master)
        has_alpha = im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 255
        im = im.convert("RGBA" if has_alpha else "RGB")

        stem = master.stem
        ladder = widths_for(measured, im.width)
        entry = {
            "key": by_file.get(filename, stem),
            "master": filename,
            "master_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
            "natural": [im.width, im.height],
            "alpha": has_alpha,
            "sizes": sizes_attr(measured),
            "avif": [], "webp": [],
        }

        # Pick the lowest quality that clears TARGET_PSNR on the largest width,
        # then use it for every width of this image.
        probe = resize(im, ladder[-1])
        tmp = OUT / f".probe-{stem}.avif"
        q_avif, measured_psnr = QUALITY_STEPS[-1], 0.0
        for q in QUALITY_STEPS:
            encode(probe, tmp, "avif", q)
            measured_psnr = psnr(probe, Image.open(tmp))
            if measured_psnr >= TARGET_PSNR:
                q_avif = q
                break
        tmp.unlink(missing_ok=True)
        q_webp = QUALITY["webp"] + (q_avif - QUALITY["avif"]) // 2

        for w in ladder:
            r = resize(im, w)
            for fmt, q in (("avif", q_avif), ("webp", q_webp)):
                name = f"{stem}-{w}.{fmt}"
                encode(r, OUT / name, fmt, q)
                entry[fmt].append({"file": name, "w": w, "bytes": (OUT / name).stat().st_size})
        entry["quality"] = {"avif": q_avif, "webp": q_webp}

        # One fallback for the few browsers without WebP. Sized for the largest
        # 1x layout width rather than the top of the ladder: it is a safety net,
        # not the image most people receive.
        fb_w = min(im.width, measured["1728"])
        fb_ext = "png" if has_alpha else "jpg"
        fb_name = f"{stem}-{fb_w}.{fb_ext}"
        encode(resize(im, fb_w), OUT / fb_name, "png" if has_alpha else "jpeg")
        # Never ship a "derivative" heavier than the master it came from.
        if fb_w == im.width and master.suffix.lower() in (".jpg", ".jpeg") \
                and master.stat().st_size <= (OUT / fb_name).stat().st_size:
            (OUT / fb_name).write_bytes(master.read_bytes())
        entry["fallback"] = {"file": fb_name, "w": fb_w, "bytes": (OUT / fb_name).stat().st_size}
        entry["fallback_height"] = round(im.height * fb_w / im.width)

        if filename == OG_IMAGE[0]:
            og_w = min(im.width, OG_IMAGE[1])
            og_name = f"{stem}-og-{og_w}.jpg"
            resize(im, og_w).convert("RGB").save(
                OUT / og_name, "JPEG", quality=80, optimize=True, progressive=True)
            entry["og"] = {"file": og_name, "w": og_w,
                           "h": round(im.height * og_w / im.width),
                           "bytes": (OUT / og_name).stat().st_size}
            after += entry["og"]["bytes"]
            print(f"{'':24s} + Open Graph image {og_name} {entry['og']['bytes']/1024:.0f}KB")

        manifest[filename] = entry
        before += master.stat().st_size
        after += entry["fallback"]["bytes"] + sum(v["bytes"] for v in entry["avif"] + entry["webp"])

        entry["psnr"] = round(measured_psnr, 1)
        widest_avif = entry["avif"][-1]
        print(
            f"{filename:24s} {im.width}x{im.height} -> {len(ladder)} widths {ladder} "
            f"| master {master.stat().st_size/1024:7.0f}KB "
            f"| avif@{widest_avif['w']} {widest_avif['bytes']/1024:6.0f}KB "
            f"| fallback {entry['fallback']['bytes']/1024:6.0f}KB"
            f"| avif q{q_avif} PSNR {entry['psnr']}dB"
        )

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"\nmasters {before/1024/1024:.2f} MB -> all derivatives {after/1024/1024:.2f} MB "
          f"({len(manifest)} images)")


if __name__ == "__main__":
    sys.exit(main())
