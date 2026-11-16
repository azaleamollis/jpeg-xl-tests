"""Step 2: lossless. Usage: lossless.py <image-stem> ... ; lossless = identical to the 8-bit working PNG.
No timing is measured or recorded."""
import sys, os, csv, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np
from PIL import Image

WORK = os.path.join(ROOT, "work"); RES = os.path.join(ROOT, "results"); OUT = os.path.join(WORK, "lossless")

# variant name -> (format, extension, encode-args builder)
SETTINGS = {
    "PNG (oxipng)": "oxipng -o 4 --strip safe",
    "WebP": "cwebp -lossless -z 6 -m 4 -mt -metadata none  [+ -exact variant if RGB under alpha=0 differs]",
    "AVIF": "avifenc --lossless -s 6 -j all  [8-bit, 4:4:4, identity matrix]",
    "JXL": "cjxl -d 0 -e 7 --quiet  [+ --keep_invisible=1 variant if RGB under alpha=0 differs]",
}


def load(path):
    with Image.open(path) as im:
        im.load()
        mode = im.mode
        if mode not in ("RGB", "RGBA") and not mode.startswith("I;16") and mode != "I":
            # e.g. oxipng may store a palette/greyscale PNG: expand to RGB(A) for the pixel comparison
            im = im.convert("RGBA" if ("A" in mode or "transparency" in im.info) else "RGB")
        return mode, np.array(im)


def compare(ref, dmode, dec):
    """Return (status, mismatched_pixels, note). ref: working PNG array (H,W,3|4)."""
    if dec.dtype != np.uint8:
        return "FAILED", -1, f"decoded dtype {dec.dtype} (mode {dmode})"
    if dec.ndim != 3 or dec.shape[:2] != ref.shape[:2]:
        return "FAILED", -1, f"shape {dec.shape} vs {ref.shape}"
    rc, dc = ref.shape[2], dec.shape[2]
    if rc == 4 and dc == 3:
        return "FAILED", -1, "decoder output has no alpha channel"
    if rc == 3 and dc == 4:
        if not (dec[:, :, 3] == 255).all():
            return "FAILED", -1, "decoder output has non-opaque alpha for an opaque source"
        dec = dec[:, :, :3]
    if (ref == dec).all():
        return "IDENTICAL", 0, ""
    diff = (ref != dec).any(axis=2)
    n = int(diff.sum())
    if rc == 4:
        a_same = (ref[:, :, 3] == dec[:, :, 3]).all()
        diff_under_transparent = int((diff & (ref[:, :, 3] == 0)).sum())
        if a_same and diff_under_transparent == n:
            return "RGB_UNDER_ALPHA0_DIFFERS", n, (f"alpha identical; all {n} differing pixels are fully transparent "
                                                 f"(alpha=0), only their RGB values differ; visible pixels identical")
    return "FAILED", n, f"{n} pixels differ"


def enc_dec(fmt, variant, src, d, stem):
    """returns (encoded path, decoded path)."""
    tag = fmt.split()[0] + (("_" + variant) if variant else "")
    if fmt.startswith("PNG"):
        enc = os.path.join(d, f"{tag}.png")
        run([OXIPNG, "-o", 4, "--strip", "safe", "--out", enc, src])
        return enc, enc
    if fmt == "WebP":
        enc = os.path.join(d, f"{tag}.webp"); dec = os.path.join(d, f"{tag}_dec.png")
        extra = ["-exact"] if variant == "exact" else []
        run([CWEBP, "-lossless", "-z", 6, "-m", 4, "-mt", "-metadata", "none", *extra, src, "-o", enc])
        run([DWEBP, enc, "-nodither", "-o", dec])
        return enc, dec
    if fmt == "AVIF":
        enc = os.path.join(d, f"{tag}.avif"); dec = os.path.join(d, f"{tag}_dec.png")
        run([AVIFENC, "--lossless", "-s", 6, "-j", "all", src, enc])
        run([AVIFDEC, enc, dec])
        return enc, dec
    if fmt == "JXL":
        enc = os.path.join(d, f"{tag}.jxl"); dec = os.path.join(d, f"{tag}_dec.png")
        extra = ["--keep_invisible=1"] if variant == "keep_invisible" else []
        run([CJXL, src, enc, "-d", 0, "-e", 7, "--quiet", *extra])
        run([DJXL, enc, dec, "--quiet"])
        return enc, dec


def main():
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(RES, "lossless.csv")
    for stem in sys.argv[1:]:
        src = os.path.join(WORK, stem + ".png")
        ref_mode, ref = load(src)
        assert ref_mode in ("RGB", "RGBA")
        d = os.path.join(OUT, stem); os.makedirs(d, exist_ok=True)
        rows = []
        for fmt in ("PNG (oxipng)", "WebP", "AVIF", "JXL"):
            variants = [""]
            while variants:
                v = variants.pop(0)
                try:
                    enc, dec = enc_dec(fmt, v, src, d, stem)
                    dmode, darr = load(dec)
                    status, n, note = compare(ref, dmode, darr)
                    size = os.path.getsize(enc)
                except Exception as e:
                    status, n, note, size = "FAILED", -1, f"{type(e).__name__}: {str(e)[:300]}", ""
                if status == "FAILED":
                    size_out = ""     # never report a size as lossless for a failure
                    note = (note + f" (encoded file was {size} bytes, not reported as lossless)") if size != "" else note
                else:
                    size_out = size
                rows.append(dict(image=stem, format=fmt, variant=v or "default", bytes=size_out, status=status,
                                 mismatched_pixels=n, note=note))
                print(f"  {stem} {fmt} [{v or 'default'}] {status} bytes={size_out} {note}", flush=True)
                if status == "RGB_UNDER_ALPHA0_DIFFERS" and not v:
                    if fmt == "WebP": variants.append("exact")
                    if fmt == "JXL": variants.append("keep_invisible")
        new = not os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            if new:
                w.writeheader()
            w.writerows(rows)


main()
