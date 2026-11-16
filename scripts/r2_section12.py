"""Follow-up 2: append section 12 to results/round2/results_round2.md (older text is not edited) and write variant_notes.md.
All numbers come from the CSVs."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

MD = os.path.join(R2, "results_round2.md")
txt = open(MD, encoding="utf-8").read()
if "\n## 12." in txt:
    raise SystemExit("section 12 already present")
n = lambda v: f"{int(v):,}"
rb = read_csv(os.path.join(R2, "moz_readback_all.csv"))
comb = read_csv(os.path.join(R2, "combined_lossy_v2.csv"))
lines = []
w = lines.append
w("\n## 12. Follow-up 2: corrections, baseline rule, new files\n")
w("Sections 1 to 11 above are unchanged by this section.\n")
w("### 12.1 Correction: MozJPEG default flags are not 4:2:0\n")
w("An earlier version of this report said MozJPEG's default output was 4:2:0 \"as verified by reading the files back\". That check had only looked at a q75 file. Section 11 already corrected the sentence; the full read-back of **every** recorded MozJPEG file (`results/round2/moz_readback_all.csv`, Pillow, no encoding) shows that with default flags the subsampling depends on the quality:\n")
by_q = {}
for r in rb:
    if r["kind"] in ("default-flag trial", "part A file (default flags)"):
        by_q.setdefault(int(r["quality"]), set()).add(r["subsampling"])
w("| default-flag quality | subsampling found | files read |\n|---|---|---|")
for q in sorted(by_q):
    k = sum(1 for r in rb if r["kind"] in ("default-flag trial", "part A file (default flags)") and int(r["quality"]) == q)
    w(f"| q{q} | {', '.join(sorted(by_q[q]))} | {k} |")
mixed = [q for q, s in by_q.items() if len(s) > 1]
w(f"\nAll files are progressive ({sum(r['progressive']=='yes' for r in rb)} of {len(rb)}). " + ("Qualities with more than one subsampling across files: " + ", ".join(f"q{q}" for q in sorted(mixed)) + ". " if mixed else "Each quality gave one subsampling across the files that share it. ") +
  f"Forced `-sample 2x2,1x1,1x1` files read back: {sum(r['kind']=='forced 4:2:0 trial' and r['subsampling']=='4:2:0' for r in rb)} of {sum(r['kind']=='forced 4:2:0 trial' for r in rb)} are 4:2:0.\n")
sel = {(r["image"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv")) if r["format"] == "MOZ"}
w("Subsampling of the default-flag MozJPEG cells that are in the main tables:\n")
w("| image | target | quality | bytes | subsampling read back |\n|---|---|---|---|---|")
for (img, t), r in sorted(sel.items(), key=lambda kv: (-int(kv[0][1]), IMAGES.index(kv[0][0]))):
    hit = [x for x in rb if x["image"] == img and x["kind"] == "default-flag trial" and x["target"] == t and x["quality"] == r["setting"]]
    w(f"| {img}.{EXT_OF[img]} | {t} | q{r['setting']} | {n(r['bytes'])} | {hit[0]['subsampling'] if hit else 'n/a'} |")
w("\nSo: the target-70 default-flag cells are 4:2:0 (except vscode-jxl-rs, which did not reach the target and whose closest trial, q89, is 4:2:2), and the target-85 default-flag cells are 4:4:4. The existing target-85 MozJPEG crops (`*_JPEG-MozJPEG_t85.png`) are therefore 4:4:4; they and `crops.csv` are kept unchanged.\n")
w("### 12.2 New baseline rule\n")
w("For the article tables the JPEG baseline per image and target is the **smaller file of libjpeg-turbo 4:2:0 and MozJPEG forced 4:2:0** (both reached the target for the four photographs). Default-flag MozJPEG results stay as measured in sections 2 to 4 but are not used as the baseline. Baselines chosen by `scripts/r2_article_tables.py`:\n")
D = {}
for r in comb:
    D[(r["image"].rsplit(".", 1)[0], r["target"], r["format"], r["variant"])] = r
w("| image | target | libjpeg-turbo 4:2:0 (bytes) | MozJPEG forced 4:2:0 (bytes) | baseline |\n|---|---|---|---|---|")
for t in ("70", "85"):
    for s in ("archives-ii", "bush-official-portrait", "chisinau-zoo-lake", "summer-tanager"):
        a = D[(s, t, LABEL["JPEG"], "4:2:0")]
        b = D[(s, t, LABEL["MOZ"], "4:2:0 forced")]
        base = "libjpeg-turbo 4:2:0" if int(a["bytes"]) < int(b["bytes"]) else "MozJPEG 4:2:0 (forced)"
        w(f"| {s}.{EXT_OF[s]} | {t} | {n(a['bytes'])} | {n(b['bytes'])} | {base} |")
w("\nvscode-jxl-rs and coaf-logo have no baseline (neither JPEG column reaches the target on the screenshot; no JPEG for coaf-logo).\n")
w("### 12.3 New files (follow-up 2; no existing file overwritten)\n")
for f, d in [("results/round2/moz_readback_all.csv", "subsampling / progressive flag of every recorded MozJPEG file"),
             ("results/round2/crops/crops_v2.csv", "all 22 old crop rows plus 6 new, with a `variant` column"),
             ("results/round2/crops/summer-tanager_JPEG-MozJPEG-420_t85.png, ..._t70.png", "MozJPEG forced 4:2:0"),
             ("results/round2/crops/vscode-jxl-rs_JPEG-libjpeg-turbo-444_t70.png, ..._t85.png", "libjpeg-turbo 4:4:4 (extra)"),
             ("results/round2/crops/vscode-jxl-rs_JPEG-MozJPEG-420_t70.png, ..._t85.png", "MozJPEG forced 4:2:0, target not reached, closest tried"),
             ("results/round2/combined_lossy_v2.csv", "74 rows: old rows plus 10 MozJPEG 4:2:0, 2 libjpeg-turbo 4:4:4, 2 JXL -d; columns include `variant` and `setting_type`"),
             ("results/round2/variant_notes.md", "what the `variant` column means per encoder"),
             ("results/round2/article_tables.md", "tables 1 to 5, generated by `scripts/r2_article_tables.py`"),
             ("results/round2/article_table1_lossy70.csv, article_table2_lossy85.csv, article_table3_screenshot_logo.csv, article_table3b_reference_lines.csv, article_table4_lossless.csv, article_table5_recompression.csv, article_scores_70.csv, article_scores_85.csv", "CSV copies and the score tables"),
             ("scripts/r2_followup_data.py, scripts/r2_article_tables.py, scripts/r2_section12.py", "the scripts that produced them")]:
    w(f"- `{f}`: {d}")
w("\nCrop checks: each new crop was decoded with Pillow from the recorded encoded file after its size was compared with the recorded bytes (0 mismatches); crop box rule unchanged (centre, 500x350, no resizing). Nothing was displayed. summer-tanager target 70, forced 4:2:0: same quality and bytes as the default-flag run (status in `crops_v2.csv` says whether the two files are byte-identical).\n")
w("### 12.4 Failed or deviating\n")
w("- Nothing failed; no search was re-run and no encoder was run in this follow-up (only Pillow decodes for the crops and read-backs).\n- `variant` values: libjpeg-turbo `4:2:0`, WebP `4:2:0` (lossy WebP is 4:2:0 by format), MozJPEG default `default`, MozJPEG forced `4:2:0 forced`, libjpeg-turbo extra `4:4:4`, AVIF and JXL `default`, JXL -d `distance (-d)`; details in `variant_notes.md`.\n- `combined_lossy_v2.csv` has one more column than requested (`setting_type`, quality or distance) as asked for the distance rows, and keeps `source`.\n- The old `results_round2.md` sections were not edited by this follow-up; the wrong "4:2:0 as verified" wording in section 9 had already been replaced in follow-up 1 (and section 11 added); that replacement is the only edit to older text and item 9 of section 10 does not mention it.\n")
open(MD, "a", encoding="utf-8", newline="\n").write("\n".join(lines))
notes = """# `variant` column in combined_lossy_v2.csv and crops_v2.csv

- `4:2:0` (libjpeg-turbo): Pillow/libjpeg-turbo `subsampling=2` (4:2:0), baseline, as in round 1.
- `4:2:0` (WebP): cwebp lossy; lossy WebP is 4:2:0 by the format (background fact, not measured here; round 1 report says the same).
- `default` (MozJPEG): `cjpeg-static -quality Q`, no other flags. Subsampling then depends on quality (see section 12.1 and `moz_readback_all.csv`): 4:2:0 up to about q78, 4:2:2 around q81 to q89, 4:4:4 from q90 or q91 up in the files read back. These rows stay as measured but are not used as the JPEG baseline.
- `4:2:0 forced` (MozJPEG): `cjpeg-static -quality Q -sample 2x2,1x1,1x1`.
- `4:4:4` (libjpeg-turbo, vscode-jxl-rs only): Pillow `subsampling=0`.
- `default` (AVIF): the fixed round-1 setting `avifenc -q Q -s 6 -j all -y 444 -d 8`, i.e. 4:4:4 chroma was requested explicitly; the column says `default` only because no variant of it was run.
- `default` (JXL): `cjxl -q Q -e 7 --quiet`; no chroma-subsampling option was passed and none is varied; cjxl handles colour in its own way (lossy mode uses the XYB colour space), so there is no 4:2:0/4:4:4 setting to name.
- `distance (-d)` (JXL on coaf-logo): `cjxl -d D -e 7 --quiet`; `setting_type` = `distance` and `setting` holds D.
"""
open(os.path.join(R2, "variant_notes.md"), "x", encoding="utf-8", newline="\n").write(notes)
print("section 12 appended")
