import sys, os, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy, scipy, tifffile, imagecodecs as ic, PIL, PIL.features as f
L = []
def tool(name, args):
    p = run(args, check=False)
    out = (p.stdout + p.stderr).strip().splitlines()
    L.append(f"{name}: " + " | ".join(l.strip() for l in out[:8] if l.strip()))
tool("cjxl", [CJXL, "--version"]); tool("djxl", [DJXL, "--version"])
tool("ssimulacra2 (libjxl tools build, from the same libjxl v0.12.0 release package)", [SSIM2, "--help"]) if False else None
tool("avifenc", [AVIFENC, "--version"]); tool("avifdec", [AVIFDEC, "--version"])
tool("cwebp", [CWEBP, "-version"]); tool("dwebp", [DWEBP, "-version"])
tool("exiftool", [EXIFTOOL, "-ver"]); tool("oxipng", [OXIPNG, "--version"])
L.append("ssimulacra2.exe: shipped in jxl-x64-windows-static.zip of libjxl v0.12.0 (no --version flag; same release as cjxl/djxl)")
L.append(f"python: {platform.python_version()} ({platform.system()})")
L.append(f"numpy {numpy.__version__}; scipy {scipy.__version__}; tifffile {tifffile.__version__}; imagecodecs {ic.__version__} (lcms2 {ic.cms_version()}); Pillow {PIL.__version__}")
L.append(f"JPEG encoder: Pillow's bundled libjpeg(-turbo): jpg={f.version('jpg')}, libjpeg_turbo={f.check_feature('libjpeg_turbo')} {f.version('libjpeg_turbo')}")
L.append("Not used: ImageMagick/cjpeg (ImageMagick portable 7z needs a BCJ2 extractor that is not available here; no cjpeg build available without admin/choco)")
L.append("Downloaded sources: libjxl v0.12.0 (github.com/libjxl/libjxl releases), libavif v1.4.2 (github.com/AOMediaCodec/libavif releases), libwebp 1.6.0 (storage.googleapis.com/downloads.webmproject.org), exiftool 13.59 (sourceforge.net/projects/exiftool), oxipng v10.2.1 (github.com/oxipng/oxipng releases)")
open(os.path.join(ROOT, "results", "versions.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
