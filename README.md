# JPEG XL Tests

This repository holds the test scripts, data and results behind an article to be published (link to come). It compares JPEG XL with JPEG, WebP and AVIF on file size, and measures decode speed in different browsers.

If you want to contribute, you can add decode-speed results from your own machine; see [Contributing speed-test results](#contributing-speed-test-results).

The tests were run in stages. Round 1 left a few points open, so round 2 added tests on some of them, a second JPEG encoder (MozJPEG) as an extra check, the quality 85 target, and the recompression test. Each stage was added on top of the earlier ones, and the earlier results were left unchanged.

| Part | What it covers | Where |
|---|---|---|
| **Round 1** | Provenance check, lossless sizes, lossy at SSIMULACRA 2 target 70 | [`results/results.md`](/results/results.md), `results/*.csv` |
| **Round 2** | JPEG recompression; lossy at targets 85 and 70 with a second JPEG encoder (MozJPEG); labelled extras; crop index; a combined table | [`results/round2/results_round2.md`](/results/round2/results_round2.md), [`results/round2/combined_lossy_v2.csv`](/results/round2/combined_lossy_v2.csv) (the original, without the extra variants, is [`combined_lossy.csv`](/results/round2/combined_lossy.csv)) |
| **Later extra** | Lossless JPEG XL on the screenshot and the logo at efforts 7, 9 and 10. It does not replace any main result. | [`results/round2/extras_jxl_effort.md`](/results/round2/extras_jxl_effort.md) (data in [`results/round2/extras_jxl_effort.csv`](/results/round2/extras_jxl_effort.csv)) |
| **Decode-speed test** | How long Chrome and Firefox take to decode the 108 final files (see "Decode-speed test" below) | Test page in [`speedtest/`](/speedtest/), results in [`results/speedtest/`](/results/speedtest/) |

## Image Credits and Licences

**Source images are not included**

The `sources/` folder is not part of this repository, as its size exceeds GitHub's upload limit. Every image is linked in [`manifest.csv`](/manifest.csv) (`source_url` column) and the SHA-256 of each file I used is in [`results/sources_sha256_before.txt`](/results/sources_sha256_before.txt) (identical to [`results/sources_sha256_after.txt`](/results/sources_sha256_after.txt); the scripts never write to `sources/`). Download them yourself, check the SHA-256, and put them in `sources/` under the file names in the manifest.

The images are referred to by their short names in the article.

| File | Short name | Title | Credit | Licence | Source |
|---|---|---|---|---| --- |
| bush-official-portrait.tif | portrait | Official portrait of President George W. Bush (blue tie), 14 Jan 2003 | Eric Draper (White House photographer) | Public domain in the US (work of a US federal employee, 17 U.S.C. section 105; per Commons) (more info on the website of the [Library of Congress](https://www.loc.gov/pictures/item/2011645073/)) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:President_Bush_poses_for_his_official_portrait_in_the_Roosevelt_Room_(blue_tie).tif) |
| summer-tanager.tif | bird | Summer tanager (Cardenal veranero / Tangara veranera), Río Oro, Santa Ana, San José, Costa Rica | Ernesto Fernandez Telleria | CC0 1.0 (own work) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Cardenal_veranero,_Tangara_veranera.tif) |
| archives-ii.tif | building | Archives II, National Archives facility, Maryland | Carol M. Highsmith | No known restrictions on publication (more info on the website of the [Library of Congress](https://hdl.loc.gov/loc.pnp/highsm.15000)) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Archives_II%2C_a_newer_research_and_storage_facility_of_the_National_Archives%2C_in_the_Maryland_suburbs_of_Washington%2C_D.C_LCCN2011633193.tif) |
| vscode-jxl-rs.png | screenshot | Screenshot of VS Code showing jxl-rs source (color.rs and blending.rs), 15 Oct 2026 | Anna M | Own screenshot; shows source code under BSD-3-Clause; (c) the JPEG XL Project Authors (no endorsement implied) | [GitHub](https://github.com/libjxl/jxl-rs) |
| coaf-logo.png | logo | Children of Armenia Fund (COAF) logo | COAF | CC0 1.0 (per the Commons uploader) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Children_of_Armenia_Fund_%28COAF%29_-_Logo_%28Transparent%29.png) |
| chisinau-zoo-lake.tif | lake | Lake in Chisinau Zoo (25 March 2023) | Iurie Nistor | CC0 1.0 (own work) |[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Lake_in_Chisinau_Zoo.tif) |
| dsoc-laser.tif | n/a | DSOC uplink laser at Table Mountain Facility, night view (PIA26662) | NASA/JPL-Caltech | Public domain (Commons licensing section: 'JPL and public domain'); JPL image-use policy allows use for any purpose (no endorsement implied) | [Wikimedia Commons (excl.)](https://commons.wikimedia.org/wiki/File:DSOC%E2%80%99s_Table_Mountain_Facility_Uplink_Laser_%E2%80%93_Infrared_vs_Visible_Light_(PIA26662).tiff) |

The seventh image (`dsoc-laser.tif`) is excluded from all tests. A check for earlier JPEG compression ([`scripts/prepare.py`](/scripts/prepare.py)) found a strong 8×8 block pattern aligned to the image origin (ratio 1.1022, against 1.0016–1.0092 for the other photos), which suggests it was JPEG-compressed before. That is likely but not proven, and no metadata says so. Its row is kept in the provenance table in [`results/results.md`](/results/results.md).

## Tool versions and fixed settings

| Tool | Version | Source and notes |
|---|---|---|
| cjxl, djxl | v0.12.0 (4128790, SSE2, Clang 22.1.3) | [libjxl v0.12.0 releases](https://github.com/libjxl/libjxl/releases) |
| ssimulacra2.exe | libjxl v0.12.0 | Shipped in `jxl-x64-windows-static.zip` (no `--version` flag; same release as cjxl/djxl) |
| avifenc, avifdec | 1.4.2 | [libavif v1.4.2 releases](https://github.com/AOMediaCodec/libavif/releases); dav1d 1.5.3 (decoder), aom 3.14.1 (encoder), libyuv 1924 |
| cwebp, dwebp | 1.6.0 | [libwebp 1.6.0](https://storage.googleapis.com/downloads.webmproject.org); libsharpyuv 0.4.2 |
| oxipng | 10.2.1 | [oxipng v10.2.1 releases](https://github.com/oxipng/oxipng/releases) |
| MozJPEG `cjpeg` | 4.0.3 (build 20210225) | `cjpeg-static.exe` from `mozjpeg-v4.0.3-win-x64.zip` (static/Release), [release page](https://github.com/mozilla/mozjpeg/releases/tag/v4.0.3); zip SHA-256 `c8db69b2bbf9cff05447e60454b55317f719d9793b9100597bfcd4682836f7ee`; no admin rights; extracted to `work/tools/mozjpeg/x` |
| libjpeg-turbo | 3.1.4.1 | Pillow's bundled libjpeg(-turbo) (jpg=8.0) |
| exiftool | 13.59 | [sourceforge.net/projects/exiftool](https://sourceforge.net/projects/exiftool) |
| Python | 3.14.8 | |
| Python libraries | numpy 2.5.4, scipy 1.18.1, tifffile 2026.10.15, imagecodecs 2026.10.10 (lcms2 2.19.0), Pillow 12.3.0 | |

Round 1 made the JPEGs with Pillow's libjpeg-turbo; round 2 added MozJPEG's `cjpeg-static`. MozJPEG 4.0.3 is the newest version with an official prebuilt Windows zip; newer tags (v4.1.1 to v4.1.5, the latest from October 2023) are source-only, and I did not build them, so they were not tested. They may compress slightly differently.

**MozJPEG input:** PPM (Portable Pixmap; a plain uncompressed image format) written by the scripts, because cjpeg does not read PNG. MozJPEG output was decoded with Pillow, the same decode path as the libjpeg-turbo column; a check of all 112 MozJPEG files showed pixel-identical results with MozJPEG's own `djpeg-static` (see [`results/round2/results_round2.md`](/results/round2/results_round2.md#13-follow-up-7-djpeg-static-vs-pillow-decode-of-the-mozjpeg-files), section 13).

Fixed encoder settings (same for every image):

| format | settings |
|---|---|
| JPEG (libjpeg-turbo, baseline) | Pillow `save(..., format="JPEG", quality=Q, optimize=True, subsampling=2 (4:2:0), progressive=False)`, no metadata |
| JPEG (MozJPEG 4.0.3, progressive) | `cjpeg-static -quality Q -outfile out.jpg in.ppm` (all other flags at MozJPEG defaults: progressive, optimised, trellis; chroma subsampling chosen by quality, see the MozJPEG section below; the article tables use the forced 4:2:0 variant instead); decoded with Pillow |
| WebP | `cwebp -q Q -m 4 -mt -metadata none`; decode `dwebp -nodither` |
| AVIF | `avifenc -q Q -s 6 -j all -y 444 -d 8`; decode `avifdec` |
| JXL | `cjxl -q Q -e 7 --quiet`; decode `djxl --quiet` |
| JXL lossless JPEG recompression (round 2 part A) | `cjxl in.jpg out.jxl -e 7 --quiet`, restore with `djxl out.jxl out.jpg --quiet` |
| scoring | libjxl 0.12.0 `ssimulacra2.exe` against the 8-bit sRGB working PNG; alpha images composited on gray 128 |

Lossy search: integer quality, binary search starting at 50, at most 8 iterations, stop at the first trial within the target
band (+/-1). If no trial lands in the band the cell is marked NOT REACHED and the closest trial is reported.

## How to re-run the tests

**The scripts were written for Python 3.14 on Windows** (with `numpy`, `scipy`, `tifffile`, `imagecodecs` and `pillow`), and they use Windows `.exe` tools. On another Python version, change `Python314` in line 2 of [`scripts/common.py`](/scripts/common.py) to match it; otherwise the scripts can't find the installed packages.

Before running them, download the tools listed in [`results/versions.txt`](/results/versions.txt) into `work/tools/`, unpacked into the subfolders named at the top of [`scripts/common.py`](/scripts/common.py) and [`scripts/r2lib.py`](/scripts/r2lib.py), and put the source images in `sources/`.

Then, from the project folder, run:

```
python -I scripts/check_manifest.py
python -I scripts/prepare.py                       # working PNGs in work/, provenance
python -I scripts/lossless.py <image-stem> ...     # round 1 lossless
python -I scripts/lossy.py <image-stem> ...        # round 1 lossy, target 70
python -I scripts/make_results.py                  # round 1 report
python -I scripts/r2_recompress.py                 # round 2 A
python -I scripts/r2_lossy.py main                 # round 2 B
python -I scripts/r2_lossy.py extras               # round 2 C
python -I scripts/r2_crops.py                      # round 2 D
python -I scripts/r2_combined.py                   # round 2 E
python -I scripts/r2_report.py                     # round 2 report
python -I scripts/r2_lossy.py moz420               # extra: MozJPEG with 4:2:0 forced
python -I scripts/r2_readback.py                   # follow-up 1: subsampling read-back of selected MozJPEG files
python -I scripts/r2_followup_data.py              # follow-up 2: read-back of all MozJPEG files, crops_v2.csv, combined_lossy_v2.csv
python -I scripts/r2_article_tables.py             # follow-up 2: results/round2/article_tables.md and CSV copies
python -I scripts/r2_section12.py                  # follow-up 2: appends section 12 to results_round2.md
python -I scripts/r2_bush_crops.py                 # follow-up 4: bush-official-portrait crops (adds rows to crops_v2.csv)
python -I scripts/r2_q85_crops.py                  # follow-up 5: 2x candidate crops, building and lake, target 85
python -I scripts/r2_q85_water_crops.py            # follow-up 6: 2x crops of the lake water and the building facade, target 85
python -I scripts/r2_decoder_check.py              # follow-up 7: djpeg-static vs Pillow decode of the MozJPEG files (decode only)
python -I scripts/r2_section13.py                  # follow-up 7: appends section 13 to results_round2.md
python -I scripts/r2_extra_effort.py               # extra: lossless JXL effort check (-e 7/9/10), compared with extras_jxl_effort.csv
```

-I runs Python in isolated mode; drop it if you get import errors.

## MozJPEG chroma subsampling

MozJPEG 4.0.3 (`cjpeg-static -quality Q`) picks its chroma subsampling from the quality setting. Reading back every recorded file
([`results/round2/moz_readback_all.csv`](/results/round2/moz_readback_all.csv)): 4:2:0 up to q78, 4:2:2 for q81 to q89, and 4:4:4 from q90 up. So with its default flags:

- at target 70 (q65 to q78), the files are 4:2:0;
- at target 85 (q91 to q94), the files are 4:4:4, so they are **not** comparable with the 4:2:0 formats.

For a like-for-like comparison I also ran MozJPEG with 4:2:0 forced, using `cjpeg-static -quality Q -sample 2x2,1x1,1x1`. Both
variants are in [`results/round2/combined_lossy_v2.csv`](/results/round2/combined_lossy_v2.csv) (`variant` column, explained in [`results/round2/variant_notes.md`](/results/round2/variant_notes.md)). The command, and a check
that every forced file reads back as 4:2:0, are in [`results/round2/results_round2.md`](/results/round2/results_round2.md).

### Which JPEG was the baseline

For each image and target, the JPEG baseline in the article is the smaller of libjpeg-turbo 4:2:0 (baseline JPEG) and MozJPEG
forced 4:2:0 (progressive JPEG). The `baseline_format` column in
[`results/round2/article_table1_lossy70.csv`](/results/round2/article_table1_lossy70.csv) and
[`article_table2_lossy85.csv`](/results/round2/article_table2_lossy85.csv) records which one it was ("forced" means 4:2:0 was forced, as above).

| article name | target 70 | target 85 |
|---|---|---|
| building | MozJPEG 4:2:0 (forced), q68 | MozJPEG 4:2:0 (forced), q94 |
| portrait | MozJPEG 4:2:0 (forced), q78 | MozJPEG 4:2:0 (forced), q95 |
| lake | MozJPEG 4:2:0 (forced), q78 | libjpeg-turbo 4:2:0, q94 |
| bird | MozJPEG 4:2:0 (forced), q65 | MozJPEG 4:2:0 (forced), q94 |

Two images need a different baseline:

- **vscode-jxl-rs:** neither 4:2:0 JPEG reached the target, so the baseline is the smaller 4:4:4 JPEG that did (libjpeg-turbo 4:4:4 at target 70, MozJPEG default flags at target 85).
- **coaf-logo:** it has no JPEG baseline (JPEG has no alpha), so its lossy sizes are compared with the optimized PNG.

## Article tables

These are the size comparisons behind the file-size sections of the article: the same images encoded in different formats at two lossy quality targets (SSIMULACRA 2 scores of 70 and 85), in lossless mode, and as lossless recompression of JPEGs. They cover six images and show file sizes only, with no timings, averages or rankings.

[`results/round2/article_tables.md`](/results/round2/article_tables.md) (and the CSV copies next to it) is generated by [`scripts/r2_article_tables.py`](/scripts/r2_article_tables.py) from
[`results/round2/combined_lossy_v2.csv`](/results/round2/combined_lossy_v2.csv), [`results/round2/moz_readback_all.csv`](/results/round2/moz_readback_all.csv), [`results/lossless.csv`](/results/lossless.csv), [`results/working_copies.csv`](/results/working_copies.csv) and
[`results/round2/recompression.csv`](/results/round2/recompression.csv); nothing in it is typed by hand.

Every external command the scripts ran is in [`results/commands.log`](results/commands.log) (the project folder's path on my machine is shown as `<project>`). A few round-1 setup helpers (`scripts/extract7z.py`,
`scripts/unzip64.py`, `scripts/probe*.py`, `scripts/showcmds.py`) are one-off utilities kept for completeness.

## Final files

[`final_files/`](/final_files/) collects the 108 final encoded files behind the article and the decode-speed test, in four folders (`lossy70/`,
`lossy85/`, `lossless/`, `recompress/`). [`final_files/manifest.csv`](/final_files/manifest.csv) lists every file (file name, group, image, format, encoder,
subsampling, setting, bytes, SHA-256, width and height, source path, the article table or chart that uses it, whether it is the
article's JPEG baseline, recorded SSIMULACRA 2 score), and [`final_files/REPORT.md`](final_files/REPORT.md) lists the cells that did not reach their target
and the checks that were made. Each file's byte size was checked against the recorded results, and the SHA-256 is in the manifest.

[`final_files/lossless/`](/final_files/lossless/) also shows what the encoders were given: each image's optimized PNG (the oxipng files) is pixel-identical
to the 8-bit sRGB working copy that every quality score is measured against (all 24 lossless files are marked `IDENTICAL` in
[`results/lossless.csv`](/results/lossless.csv)). The bytes, and so the SHA-256, differ from the working PNGs that [`scripts/prepare.py`](/scripts/prepare.py) writes, because oxipng
recompresses them.

## Crops

[`results/round2/crops/`](/results/round2/crops/) holds crops for comparing the formats side by side. They were made in four steps, each with its own script and index file. None of them runs an encoder, and the three follow-up scripts create new files in exclusive mode, so they never overwrite an existing file.

| Step | Images | What | Script | Index |
|---|---|---|---|---|
| Round 2, part D | summer-tanager, vscode-jxl-rs | 500x350 px crops at 100% from the centre of the image: the working copy and each format at targets 70 and 85 | `r2_crops.py` | `crops.csv`, `crops_v2.csv` |
| Follow-up 4 | bush-official-portrait | 240x280 px crops at 100%: the working copy and 6 encodings at targets 70 and 85 | `r2_bush_crops.py` | `crops_v2.csv` |
| Follow-up 5 | archives-ii ("building"), chisinau-zoo-lake ("lake") | three candidate crops each (180x300 px, shown 2x) at target 85 | `r2_q85_crops.py` | `crops_q85.csv`, `credits_q85.txt` |
| Follow-up 6 | building facade, lake water | more 2x crops at target 85 | `r2_q85_water_crops.py` | `crops_q85_water.csv` |

The `results/round2/crops/*_overview.png` files show a whole working copy. For the building and lake the crop positions are marked with numbered red boxes; the bush overview is only a resized copy (710x900 px). The overviews are large, about 22 MB together.

## Decode-speed test

A small timing of browser decoding. Like the rest of this repository, it is not a benchmark.

- **What is measured:** how long the browser takes to decode each of the 108 final files (`img.decode()` on a detached `Image`, one
  fresh object URL per measurement, timed with `performance.now()`). Each run has 2 warm-up rounds (discarded) and 15 measured rounds,
  with the file order shuffled in every round and a 25 ms pause between files. Per file the summary has the median, minimum, 90th
  percentile and coefficient of variation (CV).
- **Machine and browsers (my run):** Intel Celeron N4100, Windows 11 Home 23H2, plugged in, power mode "Best performance". Chrome 156
  (incognito) and Firefox 159 (private window), each run twice on 2026-10-28, with the browser restarted between runs.
- **Timer resolution:** Chrome's timer steps in 0.1 ms and Firefox's in 1 ms (`timer_granularity_ms` column). Rows with a median
  under 10 timer steps carry a `timer_coarse` flag; files with a CV over 15% carry `noisy`. The small `coaf-logo` files are the
  ones affected.
- **Files** (all in `speedtest/`, next to `results/`): `index.html` is the test page; it runs offline from `file://`, you choose the `final_files` folder with the
  picker, and it reads `manifest.csv` and checks each file's size. `analyze.html` combines several exported CSVs.
  `manifest.json` is a copy of the manifest for the fallback, and `README.md` has the steps.
- **Results:** one folder per machine in [`results/speedtest/`](/results/speedtest/). Mine is `celeron-n4100-windows-11_2026-10-28/`; contributed runs go in their own folders (see "Contributing speed-test results" below). Each folder has `decode_raw_*.csv` (every timing) and `decode_summary_*.csv` (per file, with ratios against the
  libjpeg-turbo and MozJPEG files, WebP, AVIF, PNG and the original JPEG, and each JPEG labelled baseline (SOF0) or progressive
  (SOF2)). File names contain the browser, date and time of the run.
- **Caveats:** my run covers one machine and two browsers (no Safari). `decode()` on a detached image measures decoding, not painting or layout.
  JPEG type matters: the libjpeg-turbo files are baseline and the MozJPEG files are progressive, which decode more slowly. The two
  runs per browser in my run agreed closely (median difference between runs: about 1.1% in Chrome and 0.6% in Firefox).

## About the scripts

All the scripts in `scripts/` and the pages in `speedtest/` were written by Claude Code (Anthropic's coding agent; model: Code Sonnet 5.5, Medium) and run locally. The numbers in the reports are produced by the scripts from the logged tool output, and the text of the reports was written by Claude Code too, as the notice at the top of each report says.

## Licence

Code and reports: MIT, see `LICENSE`. The source images keep their own licences (table above). The original source files are not included here; the encoded files in [`final_files/`](/final_files/) and the crops below are derived from their working copies (8-bit sRGB, long edge at most 2,000 px).

The files in [`results/round2/crops/`](/results/round2/crops/) are crops of the working copies and of their decoded results, plus overview images of whole working copies, for five of the images: archives-ii (no known restrictions on publication), bush-official-portrait (public domain in the US), chisinau-zoo-lake (CC0), summer-tanager (CC0) and vscode-jxl-rs (own screenshot, which shows BSD-3-Clause source code; see the manifest).

## Contributing speed-test results

Want to contribute? The best way to help is to add decode-speed results from other hardware and browsers. The test is a single web page that needs no install and takes about 10-15 minutes per browser. You can add your results by opening a pull request.

1. Run the test following steps 1 to 7 of [`speedtest/README.md`](/speedtest/README.md): Get the repo (clone it or download the ZIP) and open `speedtest/index.html` in the browser you want to test. Fill in the hardware and operating system _(CPU model, OS and version; the page will not start without it)_, pick the `final_files` folder and run the **Default** preset, twice per browser _(ideally restarting the browser in between)_, as in the results in this repository. Please plug the laptop in and use the best-performance power mode. Chrome and Firefox are the best match for the numbers in the article; Edge and Safari are welcome too. JPEG XL has to show as "decodes" in the format table, otherwise the run is not useful. The **Quick** preset is only a short trial run; please don't send those files.
2. Put the raw and summary CSV files of the Default runs into a new folder inside `results/speedtest/`, named for your CPU, your operating system and the date of your first run as `YYYY-MM-DD` (for example `results/speedtest/celeron-n4100-windows-11_2026-10-28/`), one folder per machine and submission. If that name is already taken, add `-2`. Without Git, you can use GitHub's "Add file" > "Upload files" on the web, which creates the pull request for you.
3. Open a pull request titled "Speed test: your CPU, your OS" that adds only that folder. Please don't change any other file.

I merge submissions that load in `speedtest/analyze.html` and have the hardware and operating system filled in. If you have a question about the test, start a discussion in the repo's Discussions tab.