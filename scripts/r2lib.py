"""Round 2 shared helpers (reuses round 1's common.py and the same fixed encoder settings).
No timing is measured or recorded."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np
from PIL import Image

WORK = os.path.join(ROOT, "work"); RES = os.path.join(ROOT, "results")
R2 = os.path.join(RES, "round2"); W2 = os.path.join(WORK, "round2")
OUT2 = os.path.join(W2, "lossy"); TMP2 = os.path.join(W2, "score_tmp"); PPM = os.path.join(W2, "ppm")
CJPEG = os.path.join(T, r"mozjpeg\x\static\Release\cjpeg-static.exe")
GRAY = 128
MAX_IT = 8
TOL = 1.0
ALPHA_IMAGES = {"coaf-logo"}
IMAGES = ["archives-ii", "bush-official-portrait", "chisinau-zoo-lake", "summer-tanager", "vscode-jxl-rs", "coaf-logo"]
EXT_OF = {"archives-ii": "tif", "bush-official-portrait": "tif", "chisinau-zoo-lake": "tif",
          "summer-tanager": "tif", "vscode-jxl-rs": "png", "coaf-logo": "png"}

# column labels (JPEG baseline label kept exactly as in round 1)
LABEL = {
    "JPEG": "JPEG (libjpeg-turbo, baseline)",
    "MOZ": "JPEG (MozJPEG 4.0.3, progressive)",
    "WebP": "WebP (cwebp 1.6.0)",
    "AVIF": "AVIF (avifenc 1.4.2, aom 3.14.1)",
    "JXL": "JXL (cjxl 0.12.0)",
    "MOZ420": "JPEG (MozJPEG 4.0.3, progressive, 4:2:0 forced)",
    "JPEG444": "JPEG (libjpeg-turbo, baseline, 4:4:4)",
    "JXLd": "JXL (cjxl 0.12.0, -d distance)",
}
EXT = {"JPEG": "jpg", "MOZ": "jpg", "MOZ420": "jpg", "WebP": "webp", "AVIF": "avif", "JXL": "jxl", "JPEG444": "jpg", "JXLd": "jxl"}


def load(path):
    with Image.open(path) as im:
        im.load()
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.mode or "transparency" in im.info else "RGB")
        return np.array(im)


def composite(a):
    if a.shape[2] == 3:
        return a
    al = a[:, :, 3:4].astype(np.float32) / 255.0
    return np.rint(a[:, :, :3] * al + GRAY * (1 - al)).astype(np.uint8)


def pillow_jpeg(src, dst, q, subsampling=2):
    """Round-1 setting: Pillow/libjpeg-turbo, optimize=True, baseline; subsampling 2 = 4:2:0 (0 = 4:4:4)."""
    with Image.open(src) as im:
        im = im.convert("RGB")
        log(f"PIL.Image.save({dst}, JPEG, quality={q}, optimize=True, subsampling={'4:2:0' if subsampling == 2 else '4:4:4'}, progressive=False) from {src}")
        im.save(dst, format="JPEG", quality=q, optimize=True, subsampling=subsampling, progressive=False)


def moz_jpeg(src, dst, q, force420=False):
    """MozJPEG cjpeg with its default flags: only -quality Q (defaults: progressive, optimized Huffman, trellis, 4:2:0)."""
    os.makedirs(PPM, exist_ok=True)
    ppm = os.path.join(PPM, "tmp.ppm")
    with Image.open(src) as im:
        a = np.array(im.convert("RGB"))
    h, w = a.shape[:2]
    log(f"write PPM {ppm} ({w}x{h}) from {src} (numpy, for cjpeg input)")
    with open(ppm, "wb") as f:
        f.write(b"P6\n%d %d\n255\n" % (w, h)); f.write(a.tobytes())
    run([CJPEG, "-quality", q] + (["-sample", "2x2,1x1,1x1"] if force420 else []) + ["-outfile", dst, ppm])


def encode(fmt, src, dst, v):
    if fmt == "JPEG":
        pillow_jpeg(src, dst, v, 2)
    elif fmt == "JPEG444":
        pillow_jpeg(src, dst, v, 0)
    elif fmt == "MOZ":
        moz_jpeg(src, dst, v)
    elif fmt == "MOZ420":
        moz_jpeg(src, dst, v, True)
    elif fmt == "WebP":
        run([CWEBP, "-q", v, "-m", 4, "-mt", "-metadata", "none", src, "-o", dst])
    elif fmt == "AVIF":
        run([AVIFENC, "-q", v, "-s", 6, "-j", "all", "-y", 444, "-d", 8, src, dst])
    elif fmt == "JXL":
        run([CJXL, src, dst, "-q", v, "-e", 7, "--quiet"])
    elif fmt == "JXLd":
        run([CJXL, src, dst, "-d", v, "-e", 7, "--quiet"])
    else:
        raise ValueError(fmt)


def decode(fmt, src, dst):
    if fmt in ("JPEG", "MOZ", "MOZ420", "JPEG444"):
        with Image.open(src) as im:
            log(f"PIL.Image.open({src}).convert(RGB).save({dst})")
            im.convert("RGB").save(dst, format="PNG")
    elif fmt == "WebP":
        run([DWEBP, src, "-nodither", "-o", dst])
    elif fmt == "AVIF":
        run([AVIFDEC, src, dst])
    elif fmt in ("JXL", "JXLd"):
        run([DJXL, src, dst, "--quiet"])


def score(ref_arr, dist_arr, tag):
    os.makedirs(TMP2, exist_ok=True)
    a = os.path.join(TMP2, tag + "_ref.png"); b = os.path.join(TMP2, tag + "_dist.png")
    Image.fromarray(composite(ref_arr), "RGB").save(a)
    Image.fromarray(composite(dist_arr), "RGB").save(b)
    p = run([SSIM2, a, b])
    return float(p.stdout.strip().split()[-1])


def append_csv(path, rows):
    if not rows:
        return
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if new:
            w.writeheader()
        w.writerows(rows)


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmtv(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def search(stem, fmt, target, continuous=False):
    """Round-1 method. Integer quality: binary search lo=1..hi=100, first trial 50, at most 8 iterations, stop at the
    first trial within target +/- 1. continuous=True (JXLd only): bisection on cjxl -d in [0.1, 15.0] (8 iterations,
    value rounded to 3 decimals), higher d = lower score."""
    ref_png = os.path.join(WORK, stem + ".png")
    ref = load(ref_png)
    d = os.path.join(OUT2, stem); os.makedirs(d, exist_ok=True)
    ext = EXT[fmt]
    if continuous:
        lo, hi = 0.1, 15.0
    else:
        lo, hi = 1, 100
    trials = []
    for it in range(1, MAX_IT + 1):
        if continuous:
            q = round((lo + hi) / 2, 3)
        else:
            if lo > hi:
                break
            q = (lo + hi) // 2
        tag = f"{fmt}_t{target}_{'d' if continuous else 'q'}{fmtv(q)}"
        enc = os.path.join(d, tag + "." + ext); dec = os.path.join(d, tag + "_dec.png")
        encode(fmt, ref_png, enc, q)
        decode(fmt, enc, dec)
        dd = load(dec)
        if dd.shape[:2] != ref.shape[:2]:
            raise RuntimeError(f"dimension mismatch {stem} {fmt} {q}: {dd.shape} vs {ref.shape}")
        if ref.shape[2] == 4 and dd.shape[2] == 3 and fmt not in ("JPEG", "MOZ", "MOZ420", "JPEG444"):
            raise RuntimeError(f"{fmt} decoded without alpha for {stem}")
        if ref.shape[2] == 3 and dd.shape[2] == 4:
            dd = dd[:, :, :3]
        s = score(ref, dd, f"{stem}_{fmt}_t{target}")
        size = os.path.getsize(enc)
        trials.append(dict(image=stem, format=fmt, target=target, iteration=it, setting=fmtv(q), score=f"{s:.4f}",
                           bytes=size, dims_match="yes", encoded=os.path.relpath(enc, ROOT).replace("\\", "/")))
        print(f"  {stem} {fmt} t{target} it{it} v={fmtv(q)} score={s:.3f} bytes={size}", flush=True)
        if abs(s - target) <= TOL:
            break
        if continuous:
            if s > target: lo = q
            else: hi = q
        else:
            if s > target: hi = q - 1
            else: lo = q + 1
    ok = [t for t in trials if abs(float(t["score"]) - target) <= TOL]
    if ok:
        best = ok[-1]; status = "reached"
    else:
        best = min(trials, key=lambda t: abs(float(t["score"]) - target)); status = "NOT REACHED"
    return trials, dict(image=stem, format=fmt, target=target, setting=best["setting"], score=best["score"],
                        bytes=best["bytes"], status=status, iterations=len(trials), encoded=best["encoded"])
