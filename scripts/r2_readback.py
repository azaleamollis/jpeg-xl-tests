"""Round 2 follow-up: read back chroma subsampling, progressive flag and first luminance quantisation values of selected
MozJPEG files (no encoding, no search). Pillow subsampling codes: 0 = 4:4:4, 1 = 4:2:2, 2 = 4:2:0."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2lib import *
from PIL import JpegImagePlugin
L = os.path.join(W2, "lossy"); Rc = os.path.join(W2, "recompress")
FILES = [("vscode-jxl-rs", 89, "target-70 trial", f"{L}/vscode-jxl-rs/MOZ_t70_q89.jpg"),
         ("vscode-jxl-rs", 90, "target-70 trial", f"{L}/vscode-jxl-rs/MOZ_t70_q90.jpg"),
         ("bush-official-portrait", 75, "part A file", f"{Rc}/bush-official-portrait_MOZ_q75.jpg"),
         ("bush-official-portrait", 90, "part A file", f"{Rc}/bush-official-portrait_MOZ_q90.jpg"),
         ("bush-official-portrait", 93, "target-85 result", f"{L}/bush-official-portrait/MOZ_t85_q93.jpg"),
         ("chisinau-zoo-lake", 90, "part A file", f"{Rc}/chisinau-zoo-lake_MOZ_q90.jpg"),
         ("chisinau-zoo-lake", 91, "target-85 result", f"{L}/chisinau-zoo-lake/MOZ_t85_q91.jpg")]
NAME = {0: "4:4:4", 1: "4:2:2", 2: "4:2:0"}
rows = []
for stem, q, what, p in FILES:
    with Image.open(p) as im:
        rows.append(dict(image=stem, quality=q, file_kind=what, subsampling=NAME.get(JpegImagePlugin.get_sampling(im), "other"),
                         progressive="yes" if im.info.get("progressive") else "no",
                         luma_quant_first8=" ".join(map(str, list(im.quantization[0])[:8])), bytes=os.path.getsize(p)))
path = os.path.join(R2, "moz_readback.csv")
if os.path.exists(path): os.remove(path)
append_csv(path, rows)
for r in rows: print(r)
