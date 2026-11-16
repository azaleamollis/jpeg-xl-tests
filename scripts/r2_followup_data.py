"""Follow-up 2, data part: (1) read back subsampling of every MozJPEG file recorded so far (no encoding, no search),
(2) crops_v2.csv + new crops, (3) combined_lossy_v2.csv. Existing result files are never overwritten (new files only)."""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *
from PIL import JpegImagePlugin
NAME = {0: "4:4:4", 1: "4:2:2", 2: "4:2:0"}
CD = os.path.join(R2, "crops")
KEY_OF = {LABEL["JPEG"]: "JPEG", LABEL["MOZ"]: "MOZ", LABEL["WebP"]: "WebP", LABEL["AVIF"]: "AVIF", LABEL["JXL"]: "JXL"}
VARIANT = {"JPEG": "4:2:0", "MOZ": "default", "WebP": "4:2:0", "AVIF": "default", "JXL": "default",
           "MOZ420": "4:2:0 forced", "JPEG444": "4:4:4", "JXLd": "distance (-d)"}


def new_only(path):
    if os.path.exists(path):
        raise SystemExit(f"refusing to overwrite existing {path}")


def sub_of(p):
    with Image.open(p) as im:
        return NAME.get(JpegImagePlugin.get_sampling(im), "other"), "yes" if im.info.get("progressive") else "no"


# ---------- (1) read-back of all MozJPEG files ----------
rb = []
for csvname, kind in (("lossy_trials_round2.csv", "default-flag trial"), ("extras_moz420_trials.csv", "forced 4:2:0 trial")):
    for r in read_csv(os.path.join(R2, csvname)):
        if r["format"] in ("MOZ", "MOZ420"):
            s, pr = sub_of(os.path.join(ROOT, r["encoded"]))
            rb.append(dict(image=r["image"], kind=kind, target=r["target"], quality=r["setting"], subsampling=s, progressive=pr,
                           bytes=os.path.getsize(os.path.join(ROOT, r["encoded"])), file=r["encoded"]))
for r in read_csv(os.path.join(R2, "recompression.csv")):
    pass
RC = os.path.join(W2, "recompress")
for stem in ("archives-ii", "bush-official-portrait", "chisinau-zoo-lake", "summer-tanager"):
    for q in (75, 90):
        p = os.path.join(RC, f"{stem}_MOZ_q{q}.jpg"); s, pr = sub_of(p)
        rb.append(dict(image=stem, kind="part A file (default flags)", target="", quality=q, subsampling=s, progressive=pr,
                       bytes=os.path.getsize(p), file=os.path.relpath(p, ROOT).replace("\\", "/")))
new_only(os.path.join(R2, "moz_readback_all.csv")); append_csv(os.path.join(R2, "moz_readback_all.csv"), rb)
log("followup2: read back subsampling of %d MozJPEG files with Pillow (no encoding)" % len(rb))

# ---------- (2) crops ----------
CW, CH = 500, 350
r1 = {(r["image"], r["format"]): r for r in read_csv(os.path.join(RES, "lossy.csv"))}
m420 = {(r["image"], r["target"]): r for r in read_csv(os.path.join(R2, "extras_moz420.csv"))}
ex = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "extras.csv"))}
r2 = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv"))}
problems = []
new_rows = []


def crop_from_encoded(rec, fname, stem, fmtlabel, variant, status):
    enc = os.path.join(ROOT, rec["encoded"])
    actual = os.path.getsize(enc)
    if actual != int(rec["bytes"]):
        problems.append(f"{fname}: recorded {rec['bytes']} B, file has {actual} B"); return
    log(f"followup2: PIL.Image.open({enc}).convert(RGB) -> crop 500x350 centre -> {fname}")
    with Image.open(enc) as im:
        arr = np.array(im.convert("RGB"))
    ref = load(os.path.join(WORK, stem + ".png"))
    if arr.shape[:2] != ref.shape[:2]:
        problems.append(f"{fname}: decoded dimensions differ"); return
    h, w = arr.shape[:2]; x0, y0 = (w - CW) // 2, (h - CH) // 2
    new_only(os.path.join(CD, fname))
    Image.fromarray(arr[y0:y0 + CH, x0:x0 + CW]).save(os.path.join(CD, fname), format="PNG")
    new_rows.append(dict(file=fname, source_image=stem + "." + EXT_OF[stem], format=fmtlabel, variant=variant, target=rec["target"],
                         setting=rec.get("setting", rec.get("quality")), score=rec["score"], bytes_full_encoded_file=actual,
                         crop_box=f"x={x0}..{x0 + CW - 1}, y={y0}..{y0 + CH - 1} (left={x0}, top={y0}, {CW}x{CH}) of {w}x{h}", status=status))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


ENC_LABEL = LABEL["MOZ"]
for t in ("85", "70"):
    rec = m420[("summer-tanager", t)]
    if t == "70":
        dflt = r2[("summer-tanager", "MOZ", "70")]
        same = sha(os.path.join(ROOT, rec["encoded"])) == sha(os.path.join(ROOT, dflt["encoded"]))
        st = (f"reached; identical to the default-flag MozJPEG run at this quality (q{dflt['setting']}, {int(dflt['bytes']):,} B; "
              + ("files byte-identical)" if same else "same size, SHA-256 differs)"))
    else:
        st = "reached"
    crop_from_encoded(rec, f"summer-tanager_JPEG-MozJPEG-420_t{t}.png", "summer-tanager", ENC_LABEL, VARIANT["MOZ420"], st)
for t in ("70", "85"):
    crop_from_encoded(ex[("vscode-jxl-rs", "JPEG444", t)], f"vscode-jxl-rs_JPEG-libjpeg-turbo-444_t{t}.png", "vscode-jxl-rs",
                      LABEL["JPEG"], VARIANT["JPEG444"], "reached")
for t in ("70", "85"):
    rec = m420[("vscode-jxl-rs", t)]
    crop_from_encoded(rec, f"vscode-jxl-rs_JPEG-MozJPEG-420_t{t}.png", "vscode-jxl-rs", ENC_LABEL, VARIANT["MOZ420"],
                      f"target not reached, closest tried (score {float(rec['score']):.2f})")
old = read_csv(os.path.join(CD, "crops.csv"))
out = []
for r in old:
    k = KEY_OF.get(r["format"])
    out.append(dict(file=r["file"], source_image=r["source_image"], format=r["format"], variant=VARIANT[k] if k else "",
                    target=r["target"], setting=r["setting"], score=r["score"], bytes_full_encoded_file=r["bytes_full_encoded_file"],
                    crop_box=r["crop_box"], status=r["status"]))
out += new_rows
new_only(os.path.join(CD, "crops_v2.csv")); append_csv(os.path.join(CD, "crops_v2.csv"), out)
print("crops: old", len(old), "new", len(new_rows), "problems", problems)

# ---------- (3) combined v2 ----------
rows = []
for r in read_csv(os.path.join(R2, "combined_lossy.csv")):
    k = KEY_OF[r["format"]]
    rows.append(dict(image=r["image"], target=r["target"], format=r["format"], variant=VARIANT[k], setting=r["quality_setting"],
                     setting_type="quality" if r["quality_setting"] else "", ssimulacra2_score=r["ssimulacra2_score"], bytes=r["bytes"],
                     status=r["status"], source=r["source"]))
st = lambda s: "reached" if s == "reached" else "NOT REACHED closest tried"
for r in read_csv(os.path.join(R2, "extras_moz420.csv")):
    rows.append(dict(image=r["image"] + "." + EXT_OF[r["image"]], target=r["target"], format=LABEL["MOZ"], variant=VARIANT["MOZ420"],
                     setting=r["setting"], setting_type="quality", ssimulacra2_score=r["score"], bytes=r["bytes"], status=st(r["status"]),
                     source="round 2 extra (follow-up)"))
for r in read_csv(os.path.join(R2, "extras.csv")):
    k = r["format"]
    rows.append(dict(image=r["image"] + "." + EXT_OF[r["image"]], target=r["target"], format=LABEL["JPEG"] if k == "JPEG444" else LABEL["JXL"],
                     variant=VARIANT[k], setting=r["setting"], setting_type="quality" if k == "JPEG444" else "distance",
                     ssimulacra2_score=r["score"], bytes=r["bytes"], status=st(r["status"]), source="round 2 extra"))
new_only(os.path.join(R2, "combined_lossy_v2.csv")); append_csv(os.path.join(R2, "combined_lossy_v2.csv"), rows)
print("combined_v2 rows", len(rows))
