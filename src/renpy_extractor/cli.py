import argparse

from .jobs import find_archives, run_job
from .rpa import list_archive


def _parse_exts(s):
    if not s:
        return None
    return {e.strip().lower() if e.strip().startswith(".") else "." + e.strip().lower()
            for e in s.split(",") if e.strip()} or None


def main(argv=None):
    ap = argparse.ArgumentParser(prog="renpy-extractor",
                                 description="Ekstrak arsip RPA dari game Ren'Py")
    ap.add_argument("source", nargs="?", help="folder game atau file .rpa (kosong = GUI)")
    ap.add_argument("-o", "--output", default="extracted")
    ap.add_argument("-l", "--list", action="store_true", help="hanya tampilkan isi arsip")
    ap.add_argument("-d", "--decompile", action="store_true", help="decompile .rpyc via unrpyc")
    ap.add_argument("-e", "--ext", help="filter ekstensi, mis. .png,.ogg")
    args = ap.parse_args(argv)

    if not args.source:
        from .gui import run_gui
        run_gui()
        return
    if args.list:
        for a in find_archives(args.source):
            ver, files = list_archive(a)
            print(f"== {a} [{ver}] ==")
            for n in files:
                print("  ", n)
        return
    run_job(args.source, args.output, args.decompile, _parse_exts(args.ext), print)


if __name__ == "__main__":
    main()
