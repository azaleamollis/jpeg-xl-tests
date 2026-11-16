"""Follow-up 4: comparison crops for bush-official-portrait (box left=566, top=566, 240x280 of the 1577x2000 working copy)
from the EXISTING encoded files, both targets. Decoders only (no encoder), new files in exclusive-create mode, rows appended
to crops_v2.csv (existing rows untouched)."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

STEM = "bush-official-portrait"
L0, T0, CW, CH = 566, 566, 240, 280
CD = os.path.join(R2, "crops")
V2 = os.path.join(CD, "crops_v2.csv")
FILE_FMT = {"JPEG": "JPEG-libjpeg-turbo", "MOZ": "JPEG-MozJPEG", "MOZ420": "JPEG-MozJPEG-420", "WebP": "WebP", "AVIF": "AVIF", "JXL": "JXL"}
VARIANT = {"JPEG": "4:2:0", "MOZ": "default", "MOZ420": "4:2:0 forced", "WebP": "4:2:0", "AVIF": "default", "JXL": "default"}
LAB = {"JPEG": LABEL["JPEG"], "MOZ": LABEL["MOZ"], "MOZ420": LABEL["MOZ"], "WebP": LABEL["WebP"], "AVIF": LABEL["AVIF"], "JXL": LABEL["JXL"]}
TMP = os.path.join(W2, "bush_crop_tmp"); os.makedirs(TMP, exist_ok=True)
missing, problems, rows = [], [], []

existing = read_csv(V2)
if any(r["file"].startswith(STEM) for r in existing):
    raise SystemExit("bush rows already present in crops_v2.csv")
ref = load(os.path.join(WORK, STEM + ".png"))
H, W = ref.shape[:2]
assert (W, H) == (1577, 2000) and L0 + CW <= W and T0 + CH <= H
box = f"x={L0}..{L0 + CW - 1}, y={T0}..{T0 + CH - 1} (left={L0}, top={T0}, {CW}x{CH}) of {W}x{H}"


def save_crop(arr, name):
    path = os.path.join(CD, name)
    with open(path, "xb") as f:                       # exclusive create: never overwrites
        Image.fromarray(arr[T0:T0 + CH, L0:L0 + CW]).save(f, format="PNG")


r1 = {(r["image"], r["format"]): r for r in read_csv(os.path.join(RES, "lossy.csv"))}
r2 = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv"))}
m4 = {(r["image"], r["target"]): r for r in read_csv(os.path.join(R2, "extras_moz420.csv"))}
EXTN = {"JPEG": "jpg", "WebP": "webp", "AVIF": "avif", "JXL": "jxl"}


def record(key, t):
    """(encoded path, quality, score, recorded bytes, status) from the existing result files."""
    if key == "MOZ420":
        r = m4[(STEM, t)]; return os.path.join(ROOT, r["encoded"]), r["setting"], r["score"], int(r["bytes"]), r["status"]
    if t == "70" and key != "MOZ":
        r = r1[(STEM, key)]; q = r["quality"]
        return os.path.join(WORK, "lossy", STEM, f"{key}_q{q}.{EXTN[key]}"), q, r["score"], int(r["bytes"]), r["status"]
    r = r2[(STEM, key, t)]; return os.path.join(ROOT, r["encoded"]), r["setting"], r["score"], int(r["bytes"]), r["status"]


name = f"{STEM}_original.png"
save_crop(ref, name)
rows.append(dict(file=name, source_image=STEM + ".tif", format="original (working PNG)", variant="", target="", setting="", score="",
                 bytes_full_encoded_file="", crop_box=box, status="original"))
for t in ("85", "70"):
    for key in ("JPEG", "MOZ", "MOZ420", "WebP", "AVIF", "JXL"):
        enc, q, sc, rb, st = record(key, t)
        if not os.path.exists(enc):
            missing.append(enc); continue
        actual = os.path.getsize(enc)
        if actual != rb:
            problems.append(f"{key} t{t}: recorded {rb} B, file {actual} B"); continue
        fk = "MOZ" if key == "MOZ420" else key
        dec = os.path.join(TMP, f"{key}_t{t}_dec.png")
        if os.path.exists(dec):
            os.remove(dec)                                    # scratch file made by this script only
        decode("JPEG" if key in ("JPEG", "MOZ", "MOZ420") else key, enc, dec)
        arr = load(dec)
        if arr.shape[:2] != (H, W):
            problems.append(f"{key} t{t}: decoded dimensions {arr.shape[:2]}"); continue
        old_dec = enc.rsplit(".", 1)[0] + "_dec.png"
        same_as_old = os.path.exists(old_dec) and np.array_equal(load(old_dec)[:, :, :3], arr[:, :, :3])
        name = f"{STEM}_{FILE_FMT[key]}_t{t}.png"
        save_crop(arr, name)
        label = "reached" if st == "reached" else f"target not reached, closest tried (score {float(sc):.2f})"
        rows.append(dict(file=name, source_image=STEM + ".tif", format=LAB[key], variant=VARIANT[key], target=t, setting=q, score=sc,
                         bytes_full_encoded_file=actual, crop_box=box, status=label))
        print(f"{name}: q{q} score {sc} {actual} B; fresh decode == existing decoded PNG: {same_as_old}")
append_csv(V2, rows)
log(f"followup4: bush-official-portrait comparison crops {box} -> {len(rows)} PNGs in results/round2/crops + {len(rows)} rows appended to crops_v2.csv (decoders only)")
print("rows added", len(rows), "missing", missing, "problems", problems)
