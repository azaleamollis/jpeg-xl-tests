"""Follow-up 6: 2x nearest-neighbour crops at fixed boxes: lake water1..3 and building facade (q85 results).
No encoder, no scoring: file paths, sizes and SSIMULACRA 2 values are read from crops_q85.csv (written by r2_q85_crops.py);
decoded PNGs are the existing ones saved when the encoded files were scored. New files only (exclusive create)."""
import sys, os, csv, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *
from PIL import ImageDraw, ImageFont

CD = os.path.join(R2, "crops")
CW, CH, SCALE = 180, 300, 2
FMTS = ["original", "jpeg", "webp", "avif", "jxl"]
JOBS = [  # (article name, project stem, [(box name, x, y)], overview file)
    ("lake", "chisinau-zoo-lake", [("water1", 250, 830), ("water2", 550, 830), ("water3", 850, 830)], "lake_q85_water_overview.png"),
    ("building", "archives-ii", [("facade", 1560, 1111)], "building_q85_facade_overview.png"),
]
prev = read_csv(os.path.join(CD, "crops_q85.csv"))


def xnew(path, img):
    with open(path, "xb") as f:
        img.save(f, format="PNG")


rows, newfiles = [], []
for art, stem, boxes, ovname in JOBS:
    info = {}
    for f in FMTS:
        r = [p for p in prev if p["image"] == art and p["format"] == f][0]       # same size / score / source file as before
        src = os.path.join(ROOT, r["source_encoded_file"])
        if not os.path.exists(src):
            raise SystemExit(f"MISSING INPUT, stopping: {src}")
        if os.path.getsize(src) != int(r["bytes_of_full_encoded_file"]):
            raise SystemExit(f"size mismatch {src}")
        dec = src if f == "original" else src.rsplit(".", 1)[0] + "_dec.png"
        if not os.path.exists(dec):
            raise SystemExit(f"MISSING INPUT, stopping: {dec}")
        info[f] = dict(row=r, src=src, dec=dec, arr=load(dec)[:, :, :3])
        print(f"{art}: {f:8s} encoded/source: {os.path.relpath(src, ROOT)}  | decoded PNG used: {os.path.relpath(dec, ROOT)}  | {r['bytes_of_full_encoded_file']} B, SSIMULACRA2 {r['ssimulacra2_of_full_image'] or '-'}")
    H, W = info["original"]["arr"].shape[:2]
    for name, x, y in boxes:
        assert x + CW <= W and y + CH <= H, (name, W, H)
        crops = {}
        for f in FMTS:
            c = Image.fromarray(info[f]["arr"][y:y + CH, x:x + CW]).resize((CW * SCALE, CH * SCALE), Image.NEAREST)
            crops[f] = c
            fn = f"{art}_q85_{name}_{f}.png"
            xnew(os.path.join(CD, fn), c); newfiles.append(fn)
            r = info[f]["row"]
            rows.append(dict(file=fn, image=art, candidate=name, format=f, crop_x=x, crop_y=y, crop_w=CW, crop_h=CH, scale=SCALE,
                             bytes_of_full_encoded_file=r["bytes_of_full_encoded_file"], ssimulacra2_of_full_image=r["ssimulacra2_of_full_image"],
                             source_encoded_file=r["source_encoded_file"]))
        o = np.asarray(crops["original"], dtype=np.float32)
        print(f"  {name} (x, y, w, h) = ({x}, {y}, {CW}, {CH}); mean abs diff to original on the 2x crops (0-255 scale): " +
              ", ".join(f"{f} {np.abs(np.asarray(crops[f], dtype=np.float32) - o).mean():.3f}" for f in FMTS[1:]))
    ov = Image.fromarray(info["original"]["arr"].copy())
    dr = ImageDraw.Draw(ov)
    font = ImageFont.load_default(size=48)
    for i, (name, x, y) in enumerate(boxes, 1):
        dr.rectangle([x, y, x + CW - 1, y + CH - 1], outline=(255, 0, 0), width=3)
        dr.text((x + 6, y + 4), str(i) if len(boxes) > 1 else name, fill=(255, 0, 0), font=font, stroke_width=2, stroke_fill=(255, 255, 255))
    xnew(os.path.join(CD, ovname), ov); newfiles.append(ovname)

with open(os.path.join(CD, "crops_q85_water.csv"), "x", newline="", encoding="utf-8") as f:
    w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w_.writeheader(); w_.writerows(rows)
newfiles.append("crops_q85_water.csv")
log(f"followup6: python -I scripts/r2_q85_water_crops.py -> {len(rows)} crops (lake water1-3, building facade) + 2 overviews + crops_q85_water.csv (no encoder, no scoring)")
zp = os.path.join(R2, "q85_water_crops.zip")
with zipfile.ZipFile(zp, "x", zipfile.ZIP_STORED) as z:
    for n_ in sorted(newfiles):
        z.write(os.path.join(CD, n_), arcname="crops/" + n_)
print(len(rows), "crops +", 2, "overviews + csv;", "zip:", os.path.relpath(zp, ROOT), os.path.getsize(zp), "bytes,", len(newfiles), "entries")
