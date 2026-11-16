"""Follow-up 7: djpeg-static (MozJPEG 4.0.3) vs Pillow decode of every recorded MozJPEG file. Decode only: no encoder, no search,
no scoring. New files only (decoder_check.csv, decoder_check.md). Pillow reference = the existing _dec.png saved by the search
(trial files); for the 8 part-A files no _dec.png exists, so the Pillow decode is computed now in memory (same call as before:
Image.open(f).convert('RGB'))."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

DJPEG = os.path.join(T, r"mozjpeg\x\static\Release\djpeg-static.exe")
TMPD = os.path.join(W2, "djpeg_tmp"); os.makedirs(TMPD, exist_ok=True)
rb = read_csv(os.path.join(R2, "moz_readback_all.csv"))
assert len(rb) == 112
rec_bytes = {}
for fn in ("lossy_trials_round2.csv", "extras_moz420_trials.csv"):
    for r in read_csv(os.path.join(R2, fn)):
        if r["format"] in ("MOZ", "MOZ420"):
            rec_bytes[r["encoded"]] = int(r["bytes"])
for r in read_csv(os.path.join(R2, "recompression.csv")):
    if "MozJPEG" in r["jpeg_encoder"]:
        stem = r["image"].split(".png")[0]
        rec_bytes[f"work/round2/recompress/{stem}_MOZ_q{r['jpeg_quality']}.jpg"] = int(r["original_jpeg_bytes"])
ver = subprocess.run([DJPEG, "-version"], capture_output=True, text=True)
version = (ver.stdout + ver.stderr).strip()
log(f"followup7: djpeg-static -version -> {version}")
out, size_mismatch = [], []
for r in rb:
    rel = r["file"]
    path = os.path.join(ROOT, rel)
    rb_ = rec_bytes[rel]; act = os.path.getsize(path)
    if act != rb_:
        size_mismatch.append((rel, rb_, act))
    ppm = os.path.join(TMPD, "dj.ppm")
    if os.path.exists(ppm):
        os.remove(ppm)
    run([DJPEG, "-outfile", ppm, path])                                  # default flags only; default output = PPM (P6, 8-bit RGB)
    with Image.open(ppm) as im:
        assert im.format == "PPM" and im.mode == "RGB", (im.format, im.mode)
        dj = np.array(im)
    dec = path.rsplit(".", 1)[0] + "_dec.png"
    if os.path.exists(dec):
        pil = load(dec)[:, :, :3]; refkind = "existing _dec.png (Pillow)"
    else:
        with Image.open(path) as im:
            pil = np.array(im.convert("RGB"))
        refkind = "Pillow decode computed now (no _dec.png existed)"
    dims_ok = dj.shape == pil.shape
    if dims_ok:
        d = np.abs(dj.astype(np.int16) - pil.astype(np.int16))
        ndiff, mx, mean = int((d.max(axis=2) > 0).sum()), int(d.max()), float(d.mean())
    else:
        ndiff = mx = mean = ""
    out.append(dict(file=rel, image=r["image"], kind=r["kind"], target=r["target"], quality=r["quality"], subsampling=r["subsampling"],
                    recorded_bytes=rb_, actual_bytes=act, size_match="yes" if act == rb_ else "NO",
                    djpeg_width=dj.shape[1], djpeg_height=dj.shape[0], pillow_width=pil.shape[1], pillow_height=pil.shape[0],
                    dims_match="yes" if dims_ok else "NO", differing_pixels=ndiff, max_channel_diff=mx,
                    mean_abs_diff=f"{mean:.6f}" if dims_ok else "", pillow_reference=refkind))
if os.path.exists(os.path.join(TMPD, "dj.ppm")):
    os.remove(os.path.join(TMPD, "dj.ppm"))
cp = os.path.join(R2, "decoder_check.csv")
with open(cp, "x", newline="", encoding="utf-8") as f:
    import csv
    w_ = csv.DictWriter(f, fieldnames=list(out[0].keys())); w_.writeheader(); w_.writerows(out)

# ---- md ----
by = {}
for o in out:
    by.setdefault(o["subsampling"], []).append(o)
L = []
w = L.append
w("# Decoder check: djpeg-static vs Pillow on the recorded MozJPEG files\n")
w(f"Decode only: no encoder, search or scoring was run. Decoder: `djpeg-static.exe` ({version}), official prebuilt `mozjpeg-v4.0.3-win-x64.zip`, **default flags** (no `-nosmooth`, `-dct` or other switch). Exact command per file: `djpeg-static.exe -outfile dj.ppm <file>.jpg` (`-outfile` only names the output; the default output format is PPM, P6, 8-bit RGB, lossless). Pillow 12.3.0 with libjpeg-turbo 3.1.4.1 is the other decoder: `Image.open(f).convert('RGB')`. Both outputs are 8-bit RGB arrays compared pixel by pixel (difference in 0-255 levels; no conversion step is lossy).\n")
w(f"Files: {len(out)} (every recorded MozJPEG file: default-flag trials, forced 4:2:0 trials, and the 8 part-A files). Size check against recorded bytes before decoding: {len(size_mismatch)} mismatches" + (": " + "; ".join(f"{a} recorded {b} B, file {c} B" for a, b, c in size_mismatch) if size_mismatch else ".") + "\n")
w("Pillow reference: for the " + str(sum(o['pillow_reference'].startswith('existing') for o in out)) + " search-trial files, the existing decoded PNG saved by the search (the file that was scored); for the " + str(sum(o['pillow_reference'].startswith('Pillow') for o in out)) + " part-A files (never scored, no decoded PNG existed) a Pillow decode computed now.\n")
w("## Summary by subsampling\n")
w("| subsampling | files | dimensions all match | files with any differing pixel | total differing pixels | max per-channel difference | largest mean abs difference of a file | qualities covered |\n|---|---|---|---|---|---|---|---|")
for s in ("4:2:0", "4:2:2", "4:4:4"):
    g = by.get(s, [])
    if not g:
        continue
    dm = all(o["dims_match"] == "yes" for o in g)
    nd = [o for o in g if o["dims_match"] == "yes" and o["differing_pixels"] > 0]
    qs = sorted({int(o["quality"]) for o in g})
    w(f"| {s} | {len(g)} | {'yes' if dm else 'NO'} | {len(nd)} | {sum(o['differing_pixels'] for o in g if o['dims_match']=='yes'):,} | {max(o['max_channel_diff'] for o in g if o['dims_match']=='yes')} | {max(float(o['mean_abs_diff']) for o in g if o['dims_match']=='yes'):.6f} | q{qs[0]}..q{qs[-1]} ({len(qs)} values) |")
tot = [o for o in out if o["dims_match"] == "yes" and o["differing_pixels"] > 0]
w(f"\nOverall: {len(out) - len(tot)} of {len(out)} files are pixel-identical; {len(tot)} differ.\n")
if tot:
    w("## Files that differ\n")
    w("| file | subsampling | quality | differing pixels | max channel diff | mean abs diff |\n|---|---|---|---|---|---|")
    for o in sorted(tot, key=lambda o: -o["differing_pixels"]):
        w(f"| {o['file']} | {o['subsampling']} | q{o['quality']} | {o['differing_pixels']:,} | {o['max_channel_diff']} | {o['mean_abs_diff']} |")
    w("")
w("Per-file rows (width, height, dimension match, differing pixels, max difference, mean abs difference, subsampling, quality): `decoder_check.csv`.")
with open(os.path.join(R2, "decoder_check.md"), "x", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
log(f"followup7: python -I scripts/r2_decoder_check.py -> decoder_check.csv/.md ({len(out)} files, {len(tot)} differ, {len(size_mismatch)} size mismatches); decode only")
print("\n".join(L))
