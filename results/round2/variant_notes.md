# `variant` column in combined_lossy_v2.csv and crops_v2.csv

- `4:2:0` (libjpeg-turbo): Pillow/libjpeg-turbo `subsampling=2` (4:2:0), baseline, as in round 1.
- `4:2:0` (WebP): cwebp lossy; lossy WebP is 4:2:0 by the format (background fact, not measured here; round 1 report says the same).
- `default` (MozJPEG): `cjpeg-static -quality Q`, no other flags. Subsampling then depends on quality (see section 12.1 and `moz_readback_all.csv`): 4:2:0 up to about q78, 4:2:2 around q81 to q89, 4:4:4 from q90 or q91 up in the files read back. These rows stay as measured but are not used as the JPEG baseline.
- `4:2:0 forced` (MozJPEG): `cjpeg-static -quality Q -sample 2x2,1x1,1x1`.
- `4:4:4` (libjpeg-turbo, vscode-jxl-rs only): Pillow `subsampling=0`.
- `default` (AVIF): the fixed round-1 setting `avifenc -q Q -s 6 -j all -y 444 -d 8`, i.e. 4:4:4 chroma was requested explicitly; the column says `default` only because no variant of it was run.
- `default` (JXL): `cjxl -q Q -e 7 --quiet`; no chroma-subsampling option was passed and none is varied; cjxl handles colour in its own way (lossy mode uses the XYB colour space), so there is no 4:2:0/4:4:4 setting to name.
- `distance (-d)` (JXL on coaf-logo): `cjxl -d D -e 7 --quiet`; `setting_type` = `distance` and `setting` holds D.
