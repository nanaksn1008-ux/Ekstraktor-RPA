"""Parser dan extractor arsip RPA (RPA-2.0 / 3.0 / 3.2 / 4.0)."""
import codecs
import io
import pickle
import zlib
from pathlib import Path


class _SafeUnpickler(pickle.Unpickler):
    """Index RPA hanya berisi dict/list/tuple/int/bytes. Semua class/fungsi
    ditolak agar arsip berbahaya tidak bisa mengeksekusi kode."""

    def find_class(self, module, name):
        # Pickle Python 3 menyimpan bytes (mis. prefix b"") lewat _codecs.encode.
        # Aman: hanya dipakai untuk mengubah str -> bytes.
        if (module, name) == ("_codecs", "encode"):
            return codecs.encode
        if module in ("builtins", "__builtin__") and name == "bytes":
            return bytes
        raise pickle.UnpicklingError(f"Objek tidak diizinkan: {module}.{name}")


def read_index(f):
    """Baca header + index. Return (versi, {nama: [(offset, length, prefix)]})."""
    f.seek(0)
    line = f.readline(256)
    if not line.startswith(b"RPA-"):
        raise ValueError("Bukan arsip RPA yang valid")
    parts = line.decode("ascii", "replace").split()
    version = parts[0]
    offset = int(parts[1], 16)
    key = 0
    for p in parts[2:]:  # 3.0: satu key, 3.2: beberapa key (XOR)
        key ^= int(p, 16)

    f.seek(offset)
    raw = zlib.decompress(f.read())
    idx = _SafeUnpickler(io.BytesIO(raw), encoding="bytes").load()

    files = {}
    for name, entries in idx.items():
        if isinstance(name, bytes):
            name = name.decode("utf-8", "replace")
        norm = []
        for e in entries:
            off, length = e[0] ^ key, e[1] ^ key
            prefix = e[2] if len(e) > 2 else b""
            if isinstance(prefix, str):
                prefix = prefix.encode("latin-1")
            norm.append((off, length, prefix))
        files[name] = norm
    return version, files


def list_archive(path):
    with open(path, "rb") as f:
        return read_index(f)


def extract_archive(path, outdir, log=print, only_ext=None):
    """Ekstrak satu arsip. Return jumlah file yang ditulis."""
    outdir = Path(outdir).resolve()
    count = 0
    with open(path, "rb") as f:
        version, files = read_index(f)
        log(f"[{version}] {Path(path).name}: {len(files)} file")
        for name, entries in files.items():
            if only_ext and Path(name).suffix.lower() not in only_ext:
                continue
            dest = (outdir / name).resolve()
            if outdir not in dest.parents:  # cegah path traversal
                log(f"  ! dilewati (path tidak aman): {name}")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as out:
                for off, length, prefix in entries:
                    f.seek(off)
                    out.write(prefix + f.read(length))
            count += 1
    log(f"  -> {count} file diekstrak")
    return count
