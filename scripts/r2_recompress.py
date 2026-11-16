"""Round 2, part A: lossless JPEG recompression (cjxl default, -e 7) and byte-exact restore check.
JPEGs are made by this script from the working PNGs (not camera or CDN files)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

STEMS = ["archives-ii", "bush-official-portrait", "chisinau-zoo-lake", "summer-tanager"]
D = os.path.join(W2, "recompress"); os.makedirs(D, exist_ok=True); os.makedirs(R2, exist_ok=True)
rows = []
for stem in STEMS:
    src = os.path.join(WORK, stem + ".png")
    for enc_key in ("JPEG", "MOZ"):
        for q in (75, 90):
            base = os.path.join(D, f"{stem}_{enc_key}_q{q}")
            jpg, jxl, back = base + ".jpg", base + ".jxl", base + "_restored.jpg"
            encode(enc_key, src, jpg, q)
            # cjxl default JPEG input => lossless JPEG recompression (jbrd box); only -e 7 and --quiet given
            run([CJXL, jpg, jxl, "-e", 7, "--quiet"])
            run([DJXL, jxl, back, "--quiet"])
            h1, h2 = sha256(jpg), sha256(back)
            ob, jb = os.path.getsize(jpg), os.path.getsize(jxl)
            rows.append(dict(image=stem + ".png (working copy)", jpeg_encoder=LABEL[enc_key], jpeg_quality=q,
                             original_jpeg_bytes=ob, jxl_bytes=jb, saving_percent=f"{(1 - jb / ob) * 100:.2f}",
                             sha256_match="yes" if h1 == h2 else "FAILED", sha256_original=h1, sha256_restored=h2))
            print(rows[-1], flush=True)
append_csv(os.path.join(R2, "recompression.csv"), rows)
