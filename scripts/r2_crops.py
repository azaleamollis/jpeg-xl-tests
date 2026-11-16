"""Round 2, part D: 500x350 crops at 100% (no resizing), centre of the image: x0=(W-500)//2, y0=(H-350)//2.
The box rule was fixed before any image was looked at. Crops are saved, never displayed."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

CW, CH = 500, 350
STEMS = ["summer-tanager", "vscode-jxl-rs"]
FILE_FMT = {"JPEG": "JPEG-libjpeg-turbo", "MOZ": "JPEG-MozJPEG", "WebP": "WebP", "AVIF": "AVIF", "JXL": "JXL"}
r1 = {(r["image"], r["format"]): r for r in read_csv(os.path.join(RES, "lossy.csv"))}
r2 = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv"))}
CD = os.path.join(R2, "crops"); os.makedirs(CD, exist_ok=True)
rows = []; problems = []


def crop_save(arr, name):
    h, w = arr.shape[:2]
    x0, y0 = (w - CW) // 2, (h - CH) // 2
    Image.fromarray(arr[y0:y0 + CH, x0:x0 + CW]).save(os.path.join(CD, name), format="PNG")
    return f"x={x0}..{x0 + CW - 1}, y={y0}..{y0 + CH - 1} (left={x0}, top={y0}, {CW}x{CH}) of {w}x{h}"


for stem in STEMS:
    ref = load(os.path.join(WORK, stem + ".png"))
    box = crop_save(ref, f"{stem}_original.png")
    rows.append(dict(file=f"{stem}_original.png", source_image=stem + "." + EXT_OF[stem], format="original (working PNG)",
                     target="", setting="", score="", bytes_full_encoded_file="", crop_box=box, status="original"))
    for t in (85, 70):
        for fmt in ("JPEG", "MOZ", "WebP", "AVIF", "JXL"):
            if t == 70 and fmt != "MOZ":
                r = r1[(stem, fmt)]
                q = r["quality"]
                enc = os.path.join(WORK, "lossy", stem, f"{fmt}_q{q}.{ {'JPEG':'jpg','WebP':'webp','AVIF':'avif','JXL':'jxl'}[fmt] }")
                setting, sc, rb, status = q, r["score"], int(r["bytes"]), r["status"]
                src_note = "round 1"
            else:
                r = r2[(stem, fmt, str(t))]
                enc = os.path.join(ROOT, r["encoded"])
                setting, sc, rb, status = r["setting"], r["score"], int(r["bytes"]), r["status"]
                src_note = "round 2"
            dec = enc.rsplit(".", 1)[0] + "_dec.png"
            actual = os.path.getsize(enc)
            if actual != rb:
                problems.append(f"{stem} {fmt} t{t}: recorded {rb} bytes but file has {actual}")
            arr = load(dec)
            if arr.shape[:2] != ref.shape[:2]:
                problems.append(f"{stem} {fmt} t{t}: decoded dimensions differ")
            name = f"{stem}_{FILE_FMT[fmt]}_t{t}.png"
            b = crop_save(arr, name)
            label = "reached" if status == "reached" else f"target not reached, closest tried (score {float(sc):.2f})"
            rows.append(dict(file=name, source_image=stem + "." + EXT_OF[stem], format=LABEL[fmt], target=t, setting=setting,
                             score=sc, bytes_full_encoded_file=actual, crop_box=b, status=label))
append_csv(os.path.join(CD, "crops.csv"), rows) if not os.path.exists(os.path.join(CD, "crops.csv")) else None
print("rows", len(rows)); print("PROBLEMS:", problems)
