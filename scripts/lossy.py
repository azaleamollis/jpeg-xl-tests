"""Step 1: lossy at matched SSIMULACRA 2 (target 70, +/-1). Usage: lossy.py <image-stem> [<image-stem> ...]
No timing is measured or recorded."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np
from PIL import Image

WORK = os.path.join(ROOT, "work"); RES = os.path.join(ROOT, "results")
OUT = os.path.join(WORK, "lossy"); TMP = os.path.join(WORK, "score_tmp")
TARGET, TOL, MAX_IT = 70.0, 1.0, 8
GRAY = 128           # fixed background for compositing alpha images before scoring (all formats)
# fixed settings (one per encoder)
SETTINGS = {
    "JPEG": "Pillow/libjpeg-turbo quality=Q, optimize=True (Huffman), baseline, 4:2:0 subsampling, no metadata",
    "WebP": "cwebp -q Q -m 4 -mt -metadata none",
    "AVIF": "avifenc -q Q -s 6 -j all -y 444 -d 8",
    "JXL":  "cjxl -q Q -e 7 --quiet",
}
ALPHA_IMAGES = {"coaf-logo"}


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


def encode(fmt, src, dst, q):
    if fmt == "JPEG":
        with Image.open(src) as im:
            im = im.convert("RGB")
            log(f"PIL.Image.save({dst}, JPEG, quality={q}, optimize=True, subsampling=4:2:0) from {src}")
            im.save(dst, format="JPEG", quality=q, optimize=True, subsampling=2, progressive=False)
    elif fmt == "WebP":
        run([CWEBP, "-q", q, "-m", 4, "-mt", "-metadata", "none", src, "-o", dst])
    elif fmt == "AVIF":
        run([AVIFENC, "-q", q, "-s", 6, "-j", "all", "-y", 444, "-d", 8, src, dst])
    elif fmt == "JXL":
        run([CJXL, src, dst, "-q", q, "-e", 7, "--quiet"])


def decode(fmt, src, dst):
    if fmt == "JPEG":
        with Image.open(src) as im:
            log(f"PIL.Image.open({src}).convert(RGB).save({dst})")
            im.convert("RGB").save(dst, format="PNG")
    elif fmt == "WebP":
        run([DWEBP, src, "-nodither", "-o", dst])
    elif fmt == "AVIF":
        run([AVIFDEC, src, dst])
    elif fmt == "JXL":
        run([DJXL, src, dst, "--quiet"])


def score(ref_arr, dist_arr, tag):
    os.makedirs(TMP, exist_ok=True)
    a = os.path.join(TMP, tag + "_ref.png"); b = os.path.join(TMP, tag + "_dist.png")
    Image.fromarray(composite(ref_arr), "RGB").save(a)
    Image.fromarray(composite(dist_arr), "RGB").save(b)
    p = run([SSIM2, a, b])
    return float(p.stdout.strip().split()[-1])


def search(stem, fmt):
    ref_png = os.path.join(WORK, stem + ".png")
    ref = load(ref_png)
    d = os.path.join(OUT, stem); os.makedirs(d, exist_ok=True)
    ext = {"JPEG": "jpg", "WebP": "webp", "AVIF": "avif", "JXL": "jxl"}[fmt]
    lo, hi = 1, 100
    trials = []
    for it in range(1, MAX_IT + 1):
        if lo > hi:
            break
        q = (lo + hi) // 2
        enc = os.path.join(d, f"{fmt}_q{q}.{ext}"); dec = os.path.join(d, f"{fmt}_q{q}_dec.png")
        encode(fmt, ref_png, enc, q)
        decode(fmt, enc, dec)
        dd = load(dec)
        if dd.shape[:2] != ref.shape[:2]:
            raise RuntimeError(f"dimension mismatch {stem} {fmt} q{q}: {dd.shape} vs {ref.shape}")
        if dd.shape[2] != ref.shape[2] and not (ref.shape[2] == 4 and fmt == "JPEG"):
            # e.g. decoder dropped/added alpha: keep going but note it
            if ref.shape[2] == 4 and dd.shape[2] == 3:
                raise RuntimeError(f"{fmt} decoded without alpha for {stem}")
            if ref.shape[2] == 3 and dd.shape[2] == 4:
                dd = dd[:, :, :3]
        s = score(ref, dd, f"{stem}_{fmt}")
        size = os.path.getsize(enc)
        trials.append(dict(image=stem, format=fmt, iteration=it, quality=q, score=f"{s:.4f}", bytes=size,
                           dims_match="yes"))
        print(f"  {stem} {fmt} it{it} q={q} score={s:.3f} bytes={size}", flush=True)
        if abs(s - TARGET) <= TOL:
            break
        if s > TARGET:
            hi = q - 1
        else:
            lo = q + 1
        # clean up non-final decodes later; keep all for audit
    ok = [t for t in trials if abs(float(t["score"]) - TARGET) <= TOL]
    if ok:
        best = ok[-1]; status = "reached"
    else:
        best = min(trials, key=lambda t: abs(float(t["score"]) - TARGET)); status = "NOT REACHED"
    return trials, dict(image=stem, format=fmt, quality=best["quality"], score=best["score"], bytes=best["bytes"],
                        status=status, iterations=len(trials))


def main():
    os.makedirs(OUT, exist_ok=True)
    final_p = os.path.join(RES, "lossy.csv"); trial_p = os.path.join(RES, "lossy_trials.csv")
    for stem in sys.argv[1:]:
        for fmt in ("JPEG", "WebP", "AVIF", "JXL"):
            if stem in ALPHA_IMAGES and fmt == "JPEG":
                final = dict(image=stem, format=fmt, quality="", score="", bytes="", status="SKIPPED (real transparency; JPEG has no alpha)", iterations=0)
                trials = []
            else:
                print(f"== {stem} {fmt}", flush=True)
                trials, final = search(stem, fmt)
            for path, rows in ((trial_p, trials), (final_p, [final])):
                if not rows:
                    continue
                new = not os.path.exists(path)
                with open(path, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    if new:
                        w.writeheader()
                    w.writerows(rows)
            print(f"  -> {final}", flush=True)


main()
