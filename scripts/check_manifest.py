import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import tifffile
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src = os.path.join(ROOT, "sources")
files = sorted(os.listdir(src))
rows = list(csv.DictReader(open(os.path.join(ROOT, "manifest.csv"), encoding="utf-8", newline="")))
mf = [r["file"] for r in rows]
out = []
out.append(f"sources entries: {files}")
out.append(f"manifest rows: {mf}")
out.append(f"in sources, not in manifest: {sorted(set(files)-set(mf))}")
out.append(f"in manifest, not in sources: {sorted(set(mf)-set(files))}")
img_ext = {".png", ".tif", ".tiff"}
out.append(f"non-image / unexpected entries in sources: {[f for f in files if os.path.splitext(f)[1].lower() not in img_ext or not os.path.isfile(os.path.join(src,f))]}")
out.append(f"duplicate manifest rows: {[f for f in set(mf) if mf.count(f)>1]}")
out.append("--- fields containing VERIFY / 'to verify' (case-insensitive), or status != ready:")
n = 0
for r in rows:
    for k, v in r.items():
        if v is not None and ("verify" in v.lower()):
            out.append(f"  {r['file']}.{k}: {v!r}"); n += 1
    if r["status"].strip().lower() != "ready":
        out.append(f"  {r['file']}.status = {r['status']!r}"); n += 1
    for k, v in r.items():
        if v is None or v.strip() == "":
            out.append(f"  {r['file']}.{k}: EMPTY"); n += 1
out.append(f"  total flagged: {n}")
out.append("--- manifest original_dimensions vs file header:")
for f in files:
    p = os.path.join(src, f)
    if f.lower().endswith((".tif", ".tiff")):
        with tifffile.TiffFile(p) as t:
            pg = t.pages[0]; w, h = pg.imagewidth, pg.imagelength
    else:
        with Image.open(p) as im: w, h = im.size
    m = next((r["original_dimensions"] for r in rows if r["file"] == f), None)
    out.append(f"  {f}: header {w}x{h}; manifest {m}; {'OK' if m == f'{w}x{h}' else 'MISMATCH'}")
out.append("--- raw bytes check of manifest encoding (summer-tanager title):")
raw = open(os.path.join(ROOT, "manifest.csv"), "rb").read()
out.append(f"  starts with BOM: {raw[:3]==b'\xef\xbb\xbf'}; title repr: {rows[1]['title']!r}")
open(os.path.join(ROOT, "results", "manifest_check.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
# hashes of sources (to prove they are unmodified at the end)
with open(os.path.join(ROOT, "results", "sources_sha256_before.txt"), "w") as f:
    for fn in files:
        f.write(f"{sha256(os.path.join(src, fn))}  {fn}\n")
print(open(os.path.join(ROOT, "results", "sources_sha256_before.txt")).read())
