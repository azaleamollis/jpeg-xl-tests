"""Round 2 extra: lossless JXL effort check (cjxl -d 0 -e 7 / 9 / 10) on vscode-jxl-rs and coaf-logo, with the oxipng and WebP
reference rows taken from results/lossless.csv. No timing is measured or recorded.
The CSV is built in memory and compared with results/round2/extras_jxl_effort.csv: if identical nothing is rewritten, if different
nothing is written and the script exits 1 (it never overwrites). Encoded files go to a scratch folder outside work/.
Commands are written to results/commands.log only when the encode/decode checks pass and the CSV matches."""
import sys, os, csv, io, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
# common.py hard-codes ROOT (the author's original folder). Re-point it, and every path derived from it, to the tree this script
# lives in, before r2lib / lossless are imported (they copy the values with `from common import *`). common.py is not modified.
_old_root, _new_root = common.ROOT, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _n, _v in list(vars(common).items()):
    if isinstance(_v, str) and _v.startswith(_old_root):
        setattr(common, _n, _new_root + _v[len(_old_root):])
from r2lib import *

_argv = sys.argv
sys.argv = [_argv[0]]            # lossless.py runs main() at import time; with no image arguments its loop does nothing
import lossless as LL            # noqa: E402  (provides load() and compare(); not modified)
sys.argv = _argv

OUTCSV = os.path.join(R2, "extras_jxl_effort.csv")
FIELDS = ["image", "codec", "setting", "bytes", "pct_of_oxipng_png", "mismatched_pixels", "sha256", "same_file_as_existing_result", "note"]
STEMS = ["vscode-jxl-rs", "coaf-logo"]
EFFORTS = [(7, []), (9, []), (10, ["--allow_expert_options"])]

cmds = []
_real_log = common.log
common.log = cmds.append          # collect command lines; written to commands.log only after everything matches

ll = read_csv(os.path.join(RES, "lossless.csv"))


def ref_row(stem, fmt):
    r = [x for x in ll if x["image"] == stem and x["format"] == fmt and x["variant"] == "default"][0]
    return int(r["bytes"])


pct = lambda b, base: f"{b / base * 100:.1f}"
rows = []
failures = []
with tempfile.TemporaryDirectory(prefix="r2_effort_") as scratch:
    for stem in STEMS:
        src = os.path.join(WORK, stem + ".png")
        ref_mode, ref = LL.load(src)
        base = ref_row(stem, "PNG (oxipng)")
        rows.append(dict(image=stem, codec="PNG (oxipng)", setting="existing result", bytes=base, pct_of_oxipng_png="100.0",
                         mismatched_pixels="", sha256="", same_file_as_existing_result="", note="from results/lossless.csv"))
        wb = ref_row(stem, "WebP")
        rows.append(dict(image=stem, codec="WebP", setting="existing lossless default", bytes=wb, pct_of_oxipng_png=pct(wb, base),
                         mismatched_pixels="", sha256="", same_file_as_existing_result="", note="from results/lossless.csv"))
        for e, extra in EFFORTS:
            enc = os.path.join(scratch, f"{stem}_e{e}.jxl"); dec = os.path.join(scratch, f"{stem}_e{e}_dec.png")
            run([CJXL, src, enc, "-d", 0, "-e", e, "--quiet", *extra])
            run([DJXL, enc, dec, "--quiet"])
            dmode, darr = LL.load(dec)
            status, n, note = LL.compare(ref, dmode, darr)
            h = sha256(enc)
            same = ""
            if e == 7:
                same = str(h == sha256(os.path.join(WORK, "lossless", stem, "JXL.jxl")))
                if same != "True":
                    failures.append(f"{stem} -e 7: SHA-256 {h} differs from work/lossless/{stem}/JXL.jxl")
            if status != "IDENTICAL":
                failures.append(f"{stem} -e {e}: {status}, {n} pixels, {note}")
            size = os.path.getsize(enc)
            rows.append(dict(image=stem, codec="JXL", setting=" ".join(["cjxl -d 0 -e", str(e), *extra]), bytes=size,
                             pct_of_oxipng_png=pct(size, base), mismatched_pixels=n, sha256=h, same_file_as_existing_result=same, note=""))
            print(f"  {stem} -e {e}: {status} {size} B sha256 {h[:16]}...", flush=True)

common.log = _real_log
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
w.writeheader(); w.writerows(rows)
new = buf.getvalue().encode("utf-8")
if os.path.exists(OUTCSV):
    old = open(OUTCSV, "rb").read()
    if old != new:
        failures.append("generated CSV differs from the existing results/round2/extras_jxl_effort.csv")
        print("--- existing"); print(old.decode("utf-8", "replace")); print("--- generated"); print(new.decode("utf-8", "replace"))
else:
    with open(OUTCSV, "xb") as f:
        f.write(new)
if failures:
    print("STOP - differences found (nothing written, commands.log not touched):")
    for f_ in failures:
        print("  -", f_)
    sys.exit(1)
for c in cmds:
    log(c)
log("r2_extra_effort: python -I scripts/r2_extra_effort.py -> results/round2/extras_jxl_effort.csv byte-identical to the existing file; -e 7 files SHA-256 equal to work/lossless/<image>/JXL.jxl")
print("MATCH: generated CSV is byte-identical to the existing file; -e 7 SHA-256 equal to work/lossless/<image>/JXL.jxl")
