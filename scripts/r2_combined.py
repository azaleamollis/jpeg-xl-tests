"""Round 2, part E: combined_lossy.csv from round 1 (lossy.csv, target 70) and round 2 (lossy_round2.csv). Measured values only."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

r1 = {(r["image"], r["format"]): r for r in read_csv(os.path.join(RES, "lossy.csv"))}
r2 = {(r["image"], r["format"], r["target"]): r for r in read_csv(os.path.join(R2, "lossy_round2.csv"))}
rows = []


def add(stem, target, fmt, r):
    st = r["status"]
    if st.startswith("SKIPPED"):
        status = "skipped"
        rows.append(dict(image=stem + "." + EXT_OF[stem], target=target, format=LABEL[fmt], quality_setting="",
                         ssimulacra2_score="", bytes="", status=status, source="round 1" if "quality" in r else "round 2"))
        return
    status = "reached" if st == "reached" else "NOT REACHED closest tried"
    rows.append(dict(image=stem + "." + EXT_OF[stem], target=target, format=LABEL[fmt],
                     quality_setting=r.get("quality", r.get("setting")), ssimulacra2_score=r["score"], bytes=r["bytes"],
                     status=status, source="round 1" if "quality" in r else "round 2"))


for stem in IMAGES:
    for t in (85, 70):
        for fmt in ("JPEG", "MOZ", "WebP", "AVIF", "JXL"):
            if stem in ALPHA_IMAGES and fmt in ("JPEG", "MOZ"):
                rows.append(dict(image=stem + "." + EXT_OF[stem], target=t, format=LABEL[fmt], quality_setting="",
                                 ssimulacra2_score="", bytes="", status="skipped", source="round 2" if (fmt == "MOZ" or t == 85) else "round 1"))
                continue
            if t == 70 and fmt != "MOZ":
                add(stem, t, fmt, r1[(stem, fmt)])
            else:
                add(stem, t, fmt, r2[(stem, fmt, str(t))])
with open(os.path.join(R2, "combined_lossy.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
