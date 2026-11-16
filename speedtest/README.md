# Decode-speed test

> The pages in this folder and these notes were written with Claude Code (Anthropic's coding agent).

Plain HTML/JS, no install, no server. Open the pages by double-clicking (file://).

## Steps

1. Plug the laptop in, set the operating system's power mode to best performance (or the nearest equivalent), close all other apps and tabs.
2. Open `speedtest/index.html` in the browser you want to test (the article's results use Chrome and Firefox). Fill in the hardware and operating system (the page leaves it empty and will not start without it), check the browser version, and choose the power source and mode.
3. Click *Choose Folder* and pick `final_files/` (the folder that contains `manifest.csv`). Wait until it says all files were read and verified, and check the format support table (JPEG XL must say "decodes").
4. Optional: preset **Quick** (1 warm-up, 5 measured rounds) → *Start run*, only as a short trial to check that everything works. Do not use its CSVs in the analysis.
5. Preset **Default** (2 warm-up, 15 measured rounds) → *Start run*. Do not touch the machine. Download the raw and summary CSVs when it finishes.
6. Repeat steps 2–5 in every other browser you want to test. `analyze.html` labels Chrome, Firefox, Edge and Safari; anything else is grouped as "Other".
7. Run each browser **twice** (two Default runs per browser, ideally after a restart of the browser). Keep every CSV; file names contain browser, date, time and preset.
8. Open `speedtest/analyze.html`, load all the **raw** CSVs of the Default runs (and optionally the summary CSVs for the baseline/progressive JPEG labels), and copy the plain-text summary. Do not load Quick-preset files: they would be mixed into the medians. Load the files of one machine at a time, because the page combines all loaded runs of the same browser.
9. To share your results, follow "Contributing speed-test results" in the main README.

## Notes

- Each measurement: Blob with the right MIME type → fresh object URL → detached `new Image()` → `img.decode()` timed with `performance.now()` → URL revoked. Blob creation happens before the timer starts.
- A stopped run is discarded and cannot be exported. If the tab is hidden during a run, the page warns that the run is untrustworthy.
- `analyze.html` labels the browser family as Chrome, Firefox, Edge or Safari (from the browser field and the user-agent text) and groups anything else as "Other". Each family gets its own columns; the extra "Firefox / Chrome" column appears only when both are loaded.
- If `manifest.csv` cannot be read, the page tries `manifest.json` (fetch is usually blocked on file://, so it then asks you to pick `speedtest/manifest.json` manually).
- In the raw CSV the `format` column holds the specific variant (for example `JPEG-MozJPEG-420`, `JXL-recompressed-from-...`), not just `JPEG`.
- Timer precision depends on the browser; the page shows the observed granularity and flags files whose median is under 10× that step as `timer_coarse`.
