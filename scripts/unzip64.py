import sys, os, struct, zipfile, zlib
sys.path.append(os.path.expandvars(r"%APPDATA%\Python\Python314\site-packages"))
import inflate64
src, dst = sys.argv[1], sys.argv[2]
zf = zipfile.ZipFile(src)
with open(src, "rb") as fp:
    for zi in zf.infolist():
        out = os.path.join(dst, zi.filename)
        if zi.is_dir():
            os.makedirs(out, exist_ok=True); continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        fp.seek(zi.header_offset)
        h = fp.read(30)
        n, m = struct.unpack("<HH", h[26:30])
        fp.seek(zi.header_offset + 30 + n + m)
        raw = fp.read(zi.compress_size)
        if zi.compress_type == 9:
            d = inflate64.Inflater(); data = d.inflate(raw)
        elif zi.compress_type == 8:
            data = zlib.decompress(raw, -15)
        else:
            data = raw
        assert len(data) == zi.file_size and (zlib.crc32(data) & 0xffffffff) == zi.CRC, zi.filename
        open(out, "wb").write(data)
print("ok")
