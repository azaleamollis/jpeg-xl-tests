# final_files report

Generated 2026-10-28 12:35 from results/, results/round2/ and work/ (read-only). Nothing was encoded, scored or decoded; widths/heights come from file headers.

## Files per group

| Group | Files |
|---|---|
| lossy70 | 25 |
| lossy85 | 27 |
| lossless | 24 |
| recompress | 32 |
| **Total** | **108** |

Lossy groups by format:

- lossy70 : AVIF 6, JPEG-libjpeg-turbo-420 4, JPEG-libjpeg-turbo-444 1, JPEG-MozJPEG-420 4, JXL 5, WebP 5
- lossy85 : AVIF 6, JPEG-libjpeg-turbo-420 4, JPEG-libjpeg-turbo-444 1, JPEG-MozJPEG-420 4, JPEG-MozJPEG-default 1, JXL 6, JXL-distance 1, WebP 4

## Skipped cells (did not reach target, or not encoded)

- lossy70 / coaf-logo / JPEG: SKIPPED (real transparency; JPEG has no alpha)
- lossy70 / coaf-logo / JXL: NOT REACHED (closest tried q21, 7328 bytes, score 78.6437)
- lossy70 / vscode-jxl-rs / JPEG: NOT REACHED (closest tried q99, 588194 bytes, score 64.8935)
- lossy70 / vscode-jxl-rs / WebP: NOT REACHED (closest tried q97, 270816 bytes, score 59.9660)
- lossy85 / summer-tanager / WebP: NOT REACHED (closest tried setting 95, 473088 bytes, score 86.0983)
- lossy85 / vscode-jxl-rs / JPEG: NOT REACHED (closest tried setting 99, 588194 bytes, score 64.8935)
- lossy85 / vscode-jxl-rs / WebP: NOT REACHED (closest tried setting 97, 270816 bytes, score 59.9660)
- lossy70 / coaf-logo / JXLd (extras.csv): NOT REACHED (closest tried setting 9.995, 7042 bytes, score 77.1869)
- lossy70 / vscode-jxl-rs / MozJPEG 4:2:0 (extras_moz420.csv): NOT REACHED (closest tried q100, 604348 bytes, score 64.8341)
- lossy85 / vscode-jxl-rs / MozJPEG 4:2:0 (extras_moz420.csv): NOT REACHED (closest tried q100, 604348 bytes, score 64.8341)

## Unverified or mismatched files

None. Every collected file exists, its byte size equals the recorded value, and (where an article table cites it) equals the article table value and setting.

## Article table cells with no collected file

None: every cell marked "reached" in article tables 1, 2, 3 and 3b has a collected file.

## Recorded files deliberately not collected

- lossy_round2.csv MOZ (default flags) archives-ii t85 work/round2/lossy/archives-ii/MOZ_t85_q91.jpg (693898 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) bush-official-portrait t85 work/round2/lossy/bush-official-portrait/MOZ_t85_q93.jpg (1258553 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) chisinau-zoo-lake t85 work/round2/lossy/chisinau-zoo-lake/MOZ_t85_q91.jpg (1557579 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) summer-tanager t85 work/round2/lossy/summer-tanager/MOZ_t85_q94.jpg (457870 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) archives-ii t70 work/round2/lossy/archives-ii/MOZ_t70_q68.jpg (222701 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) bush-official-portrait t70 work/round2/lossy/bush-official-portrait/MOZ_t70_q78.jpg (259281 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) chisinau-zoo-lake t70 work/round2/lossy/chisinau-zoo-lake/MOZ_t70_q78.jpg (659910 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) summer-tanager t70 work/round2/lossy/summer-tanager/MOZ_t70_q65.jpg (90750 bytes, reached): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossy_round2.csv MOZ (default flags) vscode-jxl-rs t70 work/round2/lossy/vscode-jxl-rs/MOZ_t70_q89.jpg (274726 bytes, NOT REACHED): article tables use the forced-4:2:0 MozJPEG files from extras_moz420.csv instead
- lossless.csv coaf-logo WebP variant 'exact' (5524 bytes, IDENTICAL): article table 4 uses the default variant

MozJPEG default vs forced 4:2:0 at target 70 (same quality, checked by SHA-256):

- archives-ii: MOZ_t70 (222701 bytes) vs MOZ420_t70 (222701 bytes): byte-identical = True
- bush-official-portrait: MOZ_t70 (259281 bytes) vs MOZ420_t70 (259281 bytes): byte-identical = True
- chisinau-zoo-lake: MOZ_t70 (659910 bytes) vs MOZ420_t70 (659910 bytes): byte-identical = True
- summer-tanager: MOZ_t70 (90750 bytes) vs MOZ420_t70 (90750 bytes): byte-identical = True

## Which JPEG was the article baseline

From the `baseline_format` column of article tables 1 and 2. Both JPEG files are collected in every cell where both reached; `is_article_jpeg_baseline` in manifest.csv marks the baseline. Subsampling was verified from each JPEG header (see manifest).

| Table | Image | Target | Baseline | Baseline bytes |
|---|---|---|---|---|
| Table 1 (lossy 70) | archives-ii | 70 | JPEG MozJPEG 4:2:0 (forced) | 222701 |
| Table 1 (lossy 70) | bush-official-portrait | 70 | JPEG MozJPEG 4:2:0 (forced) | 259281 |
| Table 1 (lossy 70) | chisinau-zoo-lake | 70 | JPEG MozJPEG 4:2:0 (forced) | 659910 |
| Table 1 (lossy 70) | summer-tanager | 70 | JPEG MozJPEG 4:2:0 (forced) | 90750 |
| Table 2 (lossy 85) | archives-ii | 85 | JPEG MozJPEG 4:2:0 (forced) | 616304 |
| Table 2 (lossy 85) | bush-official-portrait | 85 | JPEG MozJPEG 4:2:0 (forced) | 851306 |
| Table 2 (lossy 85) | chisinau-zoo-lake | 85 | JPEG libjpeg-turbo 4:2:0 | 1513762 |
| Table 2 (lossy 85) | summer-tanager | 85 | JPEG MozJPEG 4:2:0 (forced) | 341612 |

Table 3 (vscode-jxl-rs, coaf-logo) has no JPEG baseline: for vscode-jxl-rs neither 4:2:0 JPEG reached either target, and coaf-logo JPEG was skipped (real transparency). The 4:4:4 libjpeg-turbo JPEG and the default-flag MozJPEG file are the reference lines in Table 3b, not baselines.

## Header dimension consistency

For every image, all collected files (lossy, lossless, recompression) report identical width x height in their headers.

## Things I could not check

- SSIMULACRA 2 scores and the "reached" statuses are taken from the CSVs as recorded; nothing was re-scored or decoded (by instruction).
- Round-1 lossy files (lossy70) have no `encoded` path in lossy.csv; they were located as work/lossy/<image>/<Format>_q<quality>.<ext> and accepted only because the byte size equals the recorded `bytes` exactly.
- WebP chroma subsampling (4:2:0) and AVIF 4:4:4 are the settings/format properties recorded in variant_notes.md; they were not read back from the files. JPEG subsampling was read from the headers.
- WebP lossy dimensions come from the VP8 frame header and JPEG XL dimensions from the codestream size header; AVIF from the ispe box. Cross-file consistency (above) is the only check on these parsers.
- `working_png` sizes in article table 4 refer to the working-copy PNGs, not an encoded output; they are not collected.
- The article text/charts themselves are not in this folder; "behind the article" is taken to mean the cells of article tables 1-5.
- coaf-logo lossless WebP: the article table 4 value (5518) is the default encode, whose RGB under fully transparent pixels differs from the source (visible pixels identical). The `exact` variant (5524 bytes) exists but is not in table 4.
