import sys, os, subprocess, datetime, hashlib, shlex
sys.path.append(os.path.expandvars(r"%APPDATA%\Python\Python314\site-packages"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "commands.log")
T = os.path.join(ROOT, "work", "tools")
CJXL = os.path.join(T, r"libjxl\x64\x64-windows-static\bin\cjxl.exe")
DJXL = os.path.join(T, r"libjxl\x64\x64-windows-static\bin\djxl.exe")
SSIM2 = os.path.join(T, r"libjxl\x64\x64-windows-static\bin\ssimulacra2.exe")
AVIFENC = os.path.join(T, r"libavif\x\avifenc.exe")
AVIFDEC = os.path.join(T, r"libavif\x\avifdec.exe")
CWEBP = os.path.join(T, r"libwebp\x\libwebp-1.6.0-windows-x64\bin\cwebp.exe")
DWEBP = os.path.join(T, r"libwebp\x\libwebp-1.6.0-windows-x64\bin\dwebp.exe")
EXIFTOOL = os.path.join(T, r"exiftool\x\exiftool-13.59_64\exiftool.exe")
OXIPNG = os.path.join(T, r"oxipng\x\oxipng-10.2.1-x86_64-pc-windows-msvc\oxipng.exe")

def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {line}\n")

def run(args, check=True, **kw):
    args = [str(a) for a in args]
    log(subprocess.list2cmdline(args))
    p = subprocess.run(args, capture_output=True, text=True, **kw)
    if check and p.returncode != 0:
        raise RuntimeError(f"exit {p.returncode}: {subprocess.list2cmdline(args)}\n{p.stdout}\n{p.stderr}")
    return p

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
