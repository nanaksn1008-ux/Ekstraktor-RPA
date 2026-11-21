import pickle
import tempfile
import unittest
import zlib
from pathlib import Path

from renpy_extractor.rpa import extract_archive, list_archive


def build_rpa3(path, files, key=0xDEADBEEF, prefix=b""):
    header_len = len(f"RPA-3.0 {0:016x} {key:08x}\n")
    body, index, pos = b"", {}, header_len
    for name, data in files.items():
        index[name.encode()] = [((pos) ^ key, len(data) ^ key, prefix)]
        body += data
        pos += len(data)
    idx = zlib.compress(pickle.dumps(index, protocol=2))
    with open(path, "wb") as f:
        f.write(f"RPA-3.0 {pos:016x} {key:08x}\n".encode())
        f.write(body)
        f.write(idx)


class RpaTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            files = {"images/a.png": b"\x89PNGdata", "script.rpyc": b"RENPY RPC2"}
            build_rpa3(d / "t.rpa", files)
            ver, idx = list_archive(d / "t.rpa")
            self.assertEqual(ver, "RPA-3.0")
            self.assertEqual(set(idx), set(files))
            n = extract_archive(d / "t.rpa", d / "out", log=lambda *_: None)
            self.assertEqual(n, 2)
            for name, data in files.items():
                self.assertEqual((d / "out" / name).read_bytes(), data)

    def test_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            build_rpa3(d / "t.rpa", {"../evil.txt": b"x"})
            n = extract_archive(d / "t.rpa", d / "out", log=lambda *_: None)
            self.assertEqual(n, 0)
            self.assertFalse((d / "evil.txt").exists())

    def test_malicious_pickle_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            evil = zlib.compress(pickle.dumps(print, protocol=2))
            hdr = b"RPA-3.0 %016x %08x\n" % (len(b"RPA-3.0 " + b"0" * 16 + b" " + b"0" * 8 + b"\n"), 0)
            (d / "e.rpa").write_bytes(hdr + evil)
            with self.assertRaises(Exception):
                list_archive(d / "e.rpa")


if __name__ == "__main__":
    unittest.main()
