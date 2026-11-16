"""Follow-up 7: append section 13 (decoder check) to results/round2/results_round2.md and mark deviation 3 as verified.
Numbers come from decoder_check.csv."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

MD = os.path.join(R2, "results_round2.md")
txt = open(MD, encoding="utf-8").read()
if "\n## 13." in txt:
    raise SystemExit("section 13 already present")
rows = read_csv(os.path.join(R2, "decoder_check.csv"))
ndiff = sum(int(r["differing_pixels"]) > 0 for r in rows if r["dims_match"] == "yes")
assert ndiff == 0 and all(r["dims_match"] == "yes" and r["size_match"] == "yes" for r in rows), "outcome is not 'identical' - section text must be rewritten"
pix = sum(int(r["differing_pixels"]) for r in rows); mx = max(int(r["max_channel_diff"]) for r in rows)
sub = {}
for r in rows:
    sub.setdefault(r["subsampling"], []).append(r)
vs = [r for r in rows if r["image"] == "vscode-jxl-rs"]
vs_pick = sorted([r for r in vs if r["target"] == "70" and r["kind"] == "default-flag trial" and r["quality"] in ("88", "89", "90", "91", "94")], key=lambda r: int(r["quality"]))
L = ["\n## 13. Follow-up 7: djpeg-static vs Pillow decode of the MozJPEG files\n",
     "**Outcome: identical.** All %d recorded MozJPEG files decode to exactly the same pixels with MozJPEG's own `djpeg-static` (default flags) as with Pillow: %d differing pixels in total, maximum per-channel difference %d, mean absolute difference 0, dimensions equal for every file, and every file's size matched its recorded bytes before decoding.\n" % (len(rows), pix, mx),
     "Evidence (`results/round2/decoder_check.csv`, `results/round2/decoder_check.md`):\n",
     "| subsampling | files | files with any differing pixel | max per-channel difference | qualities |\n|---|---|---|---|---|"]
for s in ("4:2:0", "4:2:2", "4:4:4"):
    g = sub[s]; qs = sorted({int(r["quality"]) for r in g})
    L.append(f"| {s} | {len(g)} | {sum(int(r['differing_pixels']) > 0 for r in g)} | {max(int(r['max_channel_diff']) for r in g)} | q{qs[0]}..q{qs[-1]} |")
L.append("\nThe vscode-jxl-rs target-70 default-flag trials around the jump are covered and identical, so their recorded scores stand:\n")
L.append("| file | subsampling | quality | differing pixels | max channel diff |\n|---|---|---|---|---|")
for r in vs_pick:
    L.append(f"| {r['file']} | {r['subsampling']} | q{r['quality']} | {r['differing_pixels']} | {r['max_channel_diff']} |")
L.append("\nBecause nothing differed, no cell was re-scored: every SSIMULACRA 2 score, quality setting, target status (reached / NOT REACHED) and closest-trial choice in this report is unchanged, including vscode-jxl-rs at target 70 (q89 68.93, q90 83.04).\n")
L.append("**Assumption now verified:** decoding MozJPEG output with Pillow instead of `djpeg-static` makes no difference to the decoded pixels for these files. Deviation 3 in section 10 is therefore a verified assumption; its wording was updated in place (the only edit to older text, because the old wording listed it among deviations and presented the choice as unchecked).\n")
L.append("What this does not cover: only the MozJPEG files were compared (the libjpeg-turbo baseline column was decoded with Pillow only, as in round 1, and was not compared with another decoder); only `djpeg-static` default flags were used (no fancy-upsampling off, no other IDCT); the 8 part-A files were never scored, so for them the Pillow side is a decode computed during the check, not a saved file; other decoders such as browsers were not tested.\n")
open(MD, "a", encoding="utf-8", newline="\n").write("\n".join(L))
# deviation 3: update wording in the report and in its source part
old = "  3. MozJPEG output is decoded with Pillow, not with MozJPEG's own `djpeg`."
new = "  3. *Verified assumption (section 13):* MozJPEG output is decoded with Pillow, not with MozJPEG's own `djpeg`; a later check of all 112 files showed pixel-identical results with `djpeg-static` (default flags)."
for p in (MD, os.path.join(ROOT, "scripts", "r2_report_parts", "method_limits.md")):
    t = open(p, encoding="utf-8").read()
    if old in t:
        open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
        print("updated deviation 3 in", os.path.relpath(p, ROOT))
log("followup7: python -I scripts/r2_section13.py -> section 13 appended to results_round2.md; deviation 3 reworded as verified assumption")
print("section 13 appended")
