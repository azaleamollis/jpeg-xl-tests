"""Build 8-bit sRGB working PNGs (long edge <= 2000, Lanczos, never upscale) and provenance data.
Never writes to sources/."""
import sys, os, csv, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np, tifffile, imagecodecs as ic
import scipy.sparse as sp
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
SRC = os.path.join(ROOT, "sources"); WORK = os.path.join(ROOT, "work"); RES = os.path.join(ROOT, "results")
TARGET = 2000


def lanczos(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(np.abs(x) < 3, np.sinc(x) * np.sinc(x / 3.0), 0.0)


def weight_matrix(n_in, n_out):
    """Same geometry as Pillow's separable resampler (pixel centres, support scaled by the reduction factor)."""
    scale = n_in / n_out
    fscale = max(scale, 1.0)
    support = 3.0 * fscale
    rows, cols, vals = [], [], []
    for i in range(n_out):
        center = (i + 0.5) * scale
        lo = max(int(center - support + 0.5), 0)
        hi = min(int(center + support + 0.5), n_in)
        xs = np.arange(lo, hi)
        w = lanczos((xs - center + 0.5) / fscale)
        w = w / w.sum()
        rows.append(np.full(len(xs), i)); cols.append(xs); vals.append(w)
    return sp.csr_matrix((np.concatenate(vals).astype(np.float32), (np.concatenate(rows), np.concatenate(cols))),
                         shape=(n_out, n_in))


def resize_lanczos(arr, out_w, out_h):
    """arr: (H,W,C) integer array. float32 maths, rounded back to the SAME integer dtype (original bit depth)."""
    H, W, C = arr.shape
    Wy = weight_matrix(H, out_h); Wx = weight_matrix(W, out_w)
    mx = np.iinfo(arr.dtype).max
    out = np.empty((out_h, out_w, C), dtype=arr.dtype)
    for c in range(C):
        ch = arr[:, :, c].astype(np.float32)
        t = Wy @ ch
        r = (Wx @ t.T).T
        out[:, :, c] = np.clip(np.rint(r), 0, mx).astype(arr.dtype)
    return out


def block_stats(Y):
    """Mean absolute neighbour difference by position mod P, P in 8 (JPEG grid) and 7, 9 (controls)."""
    res = {}
    for axis, name in ((1, "H"), (0, "V")):
        d = np.abs(np.diff(Y, axis=axis))
        prof = d.mean(axis=0 if axis == 1 else 1, dtype=np.float64)
        for P in (7, 8, 9):
            m = np.array([prof[p::P].mean() for p in range(P)])
            ratios = []
            for p in range(P):
                others = np.delete(m, p).mean()
                ratios.append(m[p] / others if others > 0 else float("nan"))
            res[(name, P)] = (m, ratios)
    return res


def exif_meta(path):
    p = run([EXIFTOOL, "-json", "-a", "-G0", "-ee", path])
    return json.loads(p.stdout.lstrip("﻿"))[0]


def pick(meta, *names):
    vals = []
    for k, v in meta.items():
        if k.split(":", 1)[-1] in names:
            for x in (v if isinstance(v, list) else [v]):
                if str(x) not in vals:
                    vals.append(str(x))
    return vals


def nanmax(xs):
    xs = [x for x in xs if not math.isnan(x)]
    return max(xs) if xs else float("nan")


def main():
    files = sorted(os.listdir(SRC))
    prov, wc, detail = [], [], []
    for fn in files:
        t0 = time.time()
        p = os.path.join(SRC, fn)
        print(f"== {fn}", flush=True)
        meta = exif_meta(p)
        icc = None; alpha_info = "none"; extra_info = ""
        if fn.lower().endswith((".tif", ".tiff")):
            with tifffile.TiffFile(p) as tf:
                pg = tf.pages[0]
                arr = pg.asarray()
                tag = pg.tags.get("InterColorProfile")
                icc = bytes(tag.value) if tag is not None else None
                comp = pg.compression.name if hasattr(pg.compression, "name") else str(pg.compression)
                extra = pg.extrasamples
            assert arr.ndim == 3 and arr.shape[2] == 3 and not extra, (arr.shape, extra)
        else:
            with Image.open(p) as im:
                icc = im.info.get("icc_profile")
                extra_info = "png_info_keys=" + ",".join(sorted(im.info.keys()))
                arr = np.array(im)
                comp = "Deflate"
        H, W, C = arr.shape
        bits = arr.dtype.itemsize * 8
        orig_bytes = os.path.getsize(p)
        has_alpha = (C == 4)
        if has_alpha:
            a = arr[:, :, 3]
            opaque = float((a == 255).mean()); transp = float((a == 0).mean())
            alpha_info = (f"RGBA: opaque={opaque*100:.3f}% fully_transparent={transp*100:.3f}% "
                          f"partial={(1-opaque-transp)*100:.3f}%")
            if opaque == 1.0:
                arr = arr[:, :, :3]; C = 3; has_alpha = False
                alpha_info += " -> 100% opaque, alpha DROPPED"
            else:
                alpha_info += " -> real transparency, alpha KEPT"
        # ---- provenance: blockiness at ORIGINAL resolution (luma, 0..255 scale) ----
        rgb = arr[:, :, :3].astype(np.float32) * (255.0 / np.iinfo(arr.dtype).max)
        Y = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        del rgb
        bs = block_stats(Y); del Y
        r8 = {ax: nanmax(bs[(ax, 8)][1]) for ax in "HV"}
        ph8 = {ax: int(np.nanargmax(bs[(ax, 8)][1])) for ax in "HV"}
        r7 = {ax: nanmax(bs[(ax, 7)][1]) for ax in "HV"}; r9 = {ax: nanmax(bs[(ax, 9)][1]) for ax in "HV"}
        ratio8 = float(np.nanmean([r8["H"], r8["V"]]))
        ratio7 = float(np.nanmean([r7["H"], r7["V"]])); ratio9 = float(np.nanmean([r9["H"], r9["V"]]))
        gradmean = float(np.mean([bs[(ax, 8)][0].mean() for ax in "HV"]))
        # ---- working copy ----
        long_edge = max(W, H)
        if long_edge > TARGET:
            factor = long_edge / TARGET
            if W >= H:
                ow, oh = TARGET, max(1, round(H * TARGET / W))
            else:
                oh, ow = TARGET, max(1, round(W * TARGET / H))
            res = resize_lanczos(arr, ow, oh)       # at ORIGINAL bit depth
        else:
            factor = 1.0; ow, oh = W, H; res = arr
        icc_note = "none embedded -> assumed sRGB"
        if has_alpha:
            assert bits == 8
            out8 = res
        elif icc is not None:
            desc = ic.cms_info(icc).get("description")
            out8 = ic.cms_transform(np.ascontiguousarray(res), icc, ic.cms_profile("srgb"), colorspace="rgb",
                                    outcolorspace="rgb", outdtype=np.uint8, intent=ic.CMS.INTENT.RELATIVE_COLORIMETRIC)
            pt = res if bits == 8 else np.rint(res.astype(np.float32) * (255.0 / 65535.0)).astype(np.uint8)
            dd = np.abs(out8.astype(np.int16) - pt.astype(np.int16))
            icc_note = (f"embedded ICC '{desc}' -> converted to built-in sRGB (lcms2 {ic.cms_version()}), relative colorimetric; "
                        f"vs plain passthrough: max|diff|={int(dd.max())}, mean={float(dd.mean()):.3f}")
        else:
            out8 = res if bits == 8 else np.rint(res.astype(np.float32) * (255.0 / 65535.0)).astype(np.uint8)
        assert out8.dtype == np.uint8 and out8.shape[:2] == (oh, ow)
        name = os.path.splitext(fn)[0] + ".png"
        outp = os.path.join(WORK, name)
        Image.fromarray(np.ascontiguousarray(out8), "RGBA" if has_alpha else "RGB").save(outp, format="PNG", compress_level=6)
        with Image.open(outp) as chk:
            assert chk.size == (ow, oh) and chk.mode == ("RGBA" if has_alpha else "RGB")
        wbytes = os.path.getsize(outp)
        mk, md = pick(meta, "Make"), pick(meta, "Model")
        camera = (" ".join(mk + md) if not (mk and md and md[0].startswith(mk[0])) else md[0]) or "none recorded"
        sw = pick(meta, "Software", "CreatorTool", "HistorySoftwareAgent")
        hp = pick(meta, "HistoryParameters")
        jpegflags = [f"{k}={v}" for k, v in meta.items()
                     if any(s in k for s in ("History", "Derived", "Ingredient", "Software", "CreatorTool"))
                     and "jpeg" in json.dumps(v).lower()]
        if gradmean < 0.05 or math.isnan(ratio8):
            verdict = "unknown"
        elif ratio8 >= 1.05 and ratio8 > max(ratio7, ratio9) + 0.02:
            verdict = "suspicious"
        else:
            verdict = "clean"
        dims = f"{W}x{H}"
        prov.append(dict(file=fn, camera=camera, software="; ".join(sw) if sw else "none recorded", bit_depth=bits,
                         original_dimensions=dims, downscale_factor_to_2000px=f"{factor:.4f}", original_bytes=orig_bytes,
                         working_png_bytes=wbytes, blockiness_ratio=f"{ratio8:.4f}", verdict=verdict))
        wc.append(dict(file=name, source=fn, source_bit_depth=bits, compression=comp, icc=icc_note, alpha=alpha_info,
                       original_dimensions=dims, working_dimensions=f"{ow}x{oh}", downscale_factor=f"{factor:.6f}",
                       sha256=sha256(outp), original_bytes=orig_bytes, working_png_bytes=wbytes,
                       resample="Lanczos3 at source bit depth" if factor > 1 else "none (never upscale)", extra=extra_info))
        detail.append(dict(file=fn, compression=comp, camera=camera, software_tags="; ".join(sw),
                           history_parameters="; ".join(hp) or "none",
                           jpeg_mentions_in_history_or_software="; ".join(jpegflags) or "none found",
                           ratio8=f"{ratio8:.4f}", ratio7_control=f"{ratio7:.4f}", ratio9_control=f"{ratio9:.4f}",
                           best_phase_H=ph8["H"], best_phase_V=ph8["V"], ratio8_H=f"{r8['H']:.4f}", ratio8_V=f"{r8['V']:.4f}",
                           mean_abs_neighbour_diff_levels=f"{gradmean:.4f}",
                           phases8_H=" ".join(f"{x:.4f}" for x in bs[("H", 8)][0]),
                           phases8_V=" ".join(f"{x:.4f}" for x in bs[("V", 8)][0])))
        print(f"   {dims} -> {ow}x{oh} factor {factor:.4f}; {icc_note}; alpha: {alpha_info}; "
              f"ratio8={ratio8:.4f} (7:{ratio7:.4f} 9:{ratio9:.4f}) verdict={verdict}; {time.time()-t0:.0f}s", flush=True)
        del arr, res, out8

    def wcsv(path, rows):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    wcsv(os.path.join(RES, "provenance.csv"), prov)
    wcsv(os.path.join(RES, "working_copies.csv"), wc)
    wcsv(os.path.join(RES, "provenance_details.csv"), detail)


main()
