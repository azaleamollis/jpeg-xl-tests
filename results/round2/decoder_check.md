# Decoder check: djpeg-static vs Pillow on the recorded MozJPEG files

Decode only: no encoder, search or scoring was run. Decoder: `djpeg-static.exe` (mozjpeg version 4.0.3 (build 20210225)), official prebuilt `mozjpeg-v4.0.3-win-x64.zip`, **default flags** (no `-nosmooth`, `-dct` or other switch). Exact command per file: `djpeg-static.exe -outfile dj.ppm <file>.jpg` (`-outfile` only names the output; the default output format is PPM, P6, 8-bit RGB, lossless). Pillow 12.3.0 with libjpeg-turbo 3.1.4.1 is the other decoder: `Image.open(f).convert('RGB')`. Both outputs are 8-bit RGB arrays compared pixel by pixel (difference in 0-255 levels; no conversion step is lossy).

Files: 112 (every recorded MozJPEG file: default-flag trials, forced 4:2:0 trials, and the 8 part-A files). Size check against recorded bytes before decoding: 0 mismatches.

Pillow reference: for the 104 search-trial files, the existing decoded PNG saved by the search (the file that was scored); for the 8 part-A files (never scored, no decoded PNG existed) a Pillow decode computed now.

## Summary by subsampling

| subsampling | files | dimensions all match | files with any differing pixel | total differing pixels | max per-channel difference | largest mean abs difference of a file | qualities covered |
|---|---|---|---|---|---|---|---|
| 4:2:0 | 83 | yes | 0 | 0 | 0 | 0.000000 | q50..q100 (13 values) |
| 4:2:2 | 11 | yes | 0 | 0 | 0 | 0.000000 | q81..q89 (3 values) |
| 4:4:4 | 18 | yes | 0 | 0 | 0 | 0.000000 | q90..q94 (5 values) |

Overall: 112 of 112 files are pixel-identical; 0 differ.

Per-file rows (width, height, dimension match, differing pixels, max difference, mean abs difference, subsampling, quality): `decoder_check.csv`.
