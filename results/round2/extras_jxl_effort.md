# JPEG XL lossless: effort setting check (vscode-jxl-rs, coaf-logo)

Data: `extras_jxl_effort.csv`. Nothing existing was changed; the encoded files were written to a scratch folder, not to `work/`.

## What was run

- Input: the working PNGs `work/vscode-jxl-rs.png` (1920x1080, 8-bit RGB, 235,612 bytes) and `work/coaf-logo.png` (1024x146, 8-bit RGBA, 14,206 bytes).
- Encoder: cjxl 0.12.0 (`work/tools/libjxl`), `-d 0 -e N --quiet`; for `-e 10` also `--allow_expert_options`. No other settings.
- Decode: djxl 0.12.0 to PNG, then compared with the working PNG pixel by pixel (all four ARGB channels, including RGB under alpha=0). Every one of the six decodes had 0 differing pixels.
- Reproduction: the new `-e 7` files are byte-identical (same SHA-256) to the existing `work/lossless/<image>/JXL.jxl` files (165,312 and 5,136 bytes).

## Results (bytes, and % of the oxipng PNG)

| Image | oxipng PNG | WebP lossless (existing) | JXL -e 7 | JXL -e 9 | JXL -e 10 |
|---|---|---|---|---|---|
| vscode-jxl-rs | 136,172 (100%) | 77,882 (57.2%) | 165,312 (121.4%) | 155,332 (114.1%) | 103,956 (76.3%) |
| coaf-logo | 6,622 (100%) | 5,518 (83.3%) | 5,136 (77.6%) | 4,759 (71.9%) | 3,593 (54.3%) |


## Caveats

- WebP is the existing default lossless result (`-lossless -z 6 -m 4`); for coaf-logo that default differs from the source only in RGB under fully transparent pixels (see `results/lossless.csv`; the `exact` variant is 5,524 bytes). No new WebP or PNG encodes were made.
- Only effort was varied. Other lossless cjxl options were not tried.
