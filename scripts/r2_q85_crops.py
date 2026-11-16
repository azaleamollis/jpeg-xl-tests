"""Follow-up 5: 2x zoom candidate crops at the q85 results for "building" (archives-ii) and "lake" (chisinau-zoo-lake).
No encoder is run. Inputs: the existing q85 run (results/round2/lossy_round2.csv -> files under work/round2/lossy) and the
working PNGs. Decoded PNGs used for the diffs are the existing decoded results of those encoded files (_dec.png).
New files are created in exclusive mode (nothing is overwritten). Stops if an input is missing."""
import sys, os, csv, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *
from PIL import ImageDraw, ImageFont

CD = os.path.join(R2, "crops")
CW, CH, SCALE, MIN_GAP, STRIDE = 180, 300, 2, 100, 10
IMGS = {"building": "archives-ii", "lake": "chisinau-zoo-lake"}
FMTS = ["jpeg", "webp", "avif", "jxl"]
KEY = {"jpeg": None, "webp": "WebP", "avif": "AVIF", "jxl": "JXL"}      # jpeg key chosen below
man = {r["file"].rsplit(".", 1)[0]: r for r in read_csv(os.path.join(ROOT, "manifest.csv"))}
r2 = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv"))}
m4 = {(r["image"], r["target"]): r for r in read_csv(os.path.join(R2, "extras_moz420.csv"))}


def need(path):
    if not os.path.exists(path):
        raise SystemExit(f"MISSING INPUT, stopping: {path}")
    return path


def xnew(path, img):
    with open(path, "xb") as f:
        img.save(f, format="PNG")


def gap(a, b):
    ax, ay = a[0], a[1]; bx, by = b[0], b[1]
    dx = max(0, bx - (ax + CW), ax - (bx + CW)); dy = max(0, by - (ay + CH), ay - (by + CH))
    return max(dx, dy)


rows, picked_info = [], {}
for art, stem in IMGS.items():
    # ---- 1. pick the five files ----
    work_png = need(os.path.join(WORK, stem + ".png"))
    cand = {}   # jpeg candidates from the q85 run: libjpeg-turbo 4:2:0 and MozJPEG forced 4:2:0 (the established baseline rule)
    for k, rec in (("libjpeg-turbo 4:2:0", r2[(stem, "JPEG", "85")]), ("MozJPEG forced 4:2:0", m4[(stem, "85")])):
        cand[k] = rec
    jname = min(cand, key=lambda k: int(cand[k]["bytes"]))
    jrec = cand[jname]
    sel = {"original": dict(path=work_png, bytes=os.path.getsize(work_png), score="", label="working copy PNG (8-bit sRGB)"),
           "jpeg": dict(path=need(os.path.join(ROOT, jrec["encoded"])), bytes=int(jrec["bytes"]), score=jrec["score"], label=f"JPEG {jname} q{jrec['setting']}")}
    for f in ("webp", "avif", "jxl"):
        rec = r2[(stem, KEY[f], "85")]
        sel[f] = dict(path=need(os.path.join(ROOT, rec["encoded"])), bytes=int(rec["bytes"]), score=rec["score"], label=f"{KEY[f]} q{rec['setting']}")
    print(f"=== {art} ({stem})")
    for f in ["original"] + FMTS:
        s = sel[f]
        actual = os.path.getsize(s["path"])
        if actual != s["bytes"]:
            raise SystemExit(f"size mismatch {s['path']}: recorded {s['bytes']}, file {actual}")
        s["dec"] = s["path"] if f == "original" else need(s["path"].rsplit(".", 1)[0] + "_dec.png")
        print(f"  {f:8s} {s['label']:34s} {os.path.relpath(s['path'], ROOT)}  {actual:,} B  SSIMULACRA2={s['score'] or '-'}")
    # ---- 2. choose regions ----
    ref = load(work_png)[:, :, :3].astype(np.float32)
    H, W = ref.shape[:2]
    D = []
    for f in FMTS:
        dec = load(sel[f]["dec"])[:, :, :3].astype(np.float32)
        assert dec.shape == ref.shape, (stem, f)
        D.append(np.abs(dec - ref).mean(axis=2))
    D = np.stack(D)                                  # 4 x H x W : per-pixel mean abs difference to the original
    spread = D.max(axis=0) - D.min(axis=0)           # how much the four formats disagree at each pixel
    ii = np.pad(spread.astype(np.float64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    ys = np.arange(0, H - CH + 1, STRIDE); xs = np.arange(0, W - CW + 1, STRIDE)
    Y, X = np.meshgrid(ys, xs, indexing="ij")
    win = (ii[Y + CH, X + CW] - ii[Y, X + CW] - ii[Y + CH, X] + ii[Y, X]) / (CW * CH)
    order = np.dstack(np.unravel_index(np.argsort(-win, axis=None), win.shape))[0]
    chosen = []
    for yi, xi in order:
        box = (int(xs[xi]), int(ys[yi]))
        if all(gap(box, c) >= MIN_GAP for c in chosen):
            chosen.append(box)
        if len(chosen) == 3:
            break
    assert len(chosen) == 3
    boxes = [(x, y, CW, CH) for x, y in chosen]
    for n, (x, y, w, h) in enumerate(boxes, 1):
        reg = (slice(y, y + h), slice(x, x + w))
        print(f"  candidate {n}: (x, y, w, h) = ({x}, {y}, {w}, {h}); mean format-spread {spread[reg].mean():.3f}; mean abs diff to original: " +
              ", ".join(f"{f} {D[i][reg].mean():.3f}" for i, f in enumerate(FMTS)))
    # ---- 3. crops ----
    for n, (x, y, w, h) in enumerate(boxes, 1):
        for f in ["original"] + FMTS:
            arr = load(sel[f]["dec"])[:, :, :3]
            crop = Image.fromarray(arr[y:y + h, x:x + w]).resize((w * SCALE, h * SCALE), Image.NEAREST)
            name = f"{art}_q85_cand{n}_{f}.png"
            xnew(os.path.join(CD, name), crop)
            rows.append(dict(file=name, image=art, candidate=n, format=f, crop_x=x, crop_y=y, crop_w=w, crop_h=h, scale=SCALE,
                             bytes_of_full_encoded_file=sel[f]["bytes"], ssimulacra2_of_full_image=sel[f]["score"],
                             source_encoded_file=os.path.relpath(sel[f]["path"], ROOT).replace("\\", "/")))
    # ---- 4. overview ----
    ov = Image.fromarray(load(work_png)[:, :, :3])
    dr = ImageDraw.Draw(ov)
    font = ImageFont.load_default(size=48)
    for n, (x, y, w, h) in enumerate(boxes, 1):
        dr.rectangle([x, y, x + w - 1, y + h - 1], outline=(255, 0, 0), width=3)
        dr.text((x + 6, y + 4), str(n), fill=(255, 0, 0), font=font, stroke_width=2, stroke_fill=(255, 255, 255))
    xnew(os.path.join(CD, f"{art}_q85_overview.png"), ov)
    picked_info[art] = (stem, boxes, sel)

# ---- 5. csv ----
csv_path = os.path.join(CD, "crops_q85.csv")
with open(csv_path, "x", newline="", encoding="utf-8") as f:
    w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w_.writeheader(); w_.writerows(rows)

# ---- 6. credits ----
unk = lambda v: v.strip() if v and v.strip() else "UNKNOWN"
with open(os.path.join(CD, "credits_q85.txt"), "x", encoding="utf-8", newline="\n") as f:
    f.write("Credits for the two source photos used in the q85 crops (taken from manifest.csv, the source of the README credits table).\n\n")
    for art, (stem, boxes, sel) in picked_info.items():
        m = man[stem]
        f.write(f"{art} ({m['file']})\n  title:   {unk(m['title'])}\n  author:  {unk(m['credit'])}\n  source:  {unk(m['source_url'])}\n  license: {unk(m['license'])}\n\n")

log(f"followup5: python -I scripts/r2_q85_crops.py -> {len(rows)} crops + 2 overviews + crops_q85.csv + credits_q85.txt in results/round2/crops (no encoder)")
# ---- zip of the q85 deliverables ----
zp = os.path.join(R2, "q85_crops.zip")
names = sorted([r["file"] for r in rows] + [f"{a}_q85_overview.png" for a in IMGS] + ["crops_q85.csv", "credits_q85.txt"])
with zipfile.ZipFile(zp, "x", zipfile.ZIP_STORED) as z:
    for n_ in names:
        z.write(os.path.join(CD, n_), arcname="crops/" + n_)
print("files:", len(rows), "crops + 2 overviews + csv + credits; zip:", os.path.relpath(zp, ROOT), os.path.getsize(zp), "bytes,", len(names), "entries")
