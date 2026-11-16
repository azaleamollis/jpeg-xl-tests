"""Round 2, parts B and C: lossy searches at SSIMULACRA 2 targets 85 / 70 (+/-1). Resumable (skips finished cells).
Usage: r2_lossy.py main | extras"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *

mode = sys.argv[1]
jobs = []   # (stem, fmt, target, continuous)
if mode == "main":
    for stem in IMAGES:
        for fmt in ("JPEG", "MOZ", "WebP", "AVIF", "JXL"):
            if stem in ALPHA_IMAGES and fmt in ("JPEG", "MOZ"):
                continue
            jobs.append((stem, fmt, 85, False))
    for stem in IMAGES:
        if stem not in ALPHA_IMAGES:
            jobs.append((stem, "MOZ", 70, False))      # target 70: only the new encoder; others reuse round 1
elif mode == "extras":
    for t in (70, 85):
        jobs.append(("vscode-jxl-rs", "JPEG444", t, False))
        jobs.append(("coaf-logo", "JXLd", t, True))

elif mode == "moz420":
    for t in (70, 85):
        for stem in IMAGES:
            if stem not in ALPHA_IMAGES:
                jobs.append((stem, "MOZ420", t, False))

final_p = os.path.join(R2, {"main": "lossy_round2.csv", "extras": "extras.csv", "moz420": "extras_moz420.csv"}[mode])
trial_p = os.path.join(R2, {"main": "lossy_trials_round2.csv", "extras": "extras_trials.csv", "moz420": "extras_moz420_trials.csv"}[mode])
os.makedirs(OUT2, exist_ok=True)
done = {(r["image"], r["format"], r["target"]) for r in read_csv(final_p)}
for stem, fmt, t, cont in jobs:
    if (stem, fmt, str(t)) in done:
        continue
    print(f"== {stem} {fmt} target {t}", flush=True)
    trials, final = search(stem, fmt, t, cont)
    append_csv(trial_p, trials); append_csv(final_p, [final])
    print("  ->", final, flush=True)
print("ALL DONE", flush=True)
