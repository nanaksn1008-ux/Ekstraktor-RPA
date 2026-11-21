"""Pencarian arsip, salin script lepas, decompile .rpyc, dan job utama."""
import shutil
import subprocess
import sys
from pathlib import Path

from .rpa import extract_archive

ROOT = Path(__file__).resolve().parents[2]  # root repo (saat dijalankan dari source)


def find_archives(src):
    src = Path(src)
    if src.is_file():
        return [src]
    return sorted(p for p in src.rglob("*") if p.suffix.lower() in {".rpa", ".rpi"})


def find_unrpyc():
    for cand in (ROOT / "vendor" / "unrpyc.py",
                 ROOT / "vendor" / "unrpyc" / "unrpyc.py",
                 Path.cwd() / "unrpyc.py"):
        if cand.exists():
            return [sys.executable, str(cand)]
    exe = shutil.which("unrpyc")
    return [exe] if exe else None


def copy_loose_scripts(src, outdir, log):
    src = Path(src)
    if not src.is_dir():
        return
    n = 0
    for p in src.rglob("*"):
        if p.suffix.lower() in {".rpy", ".rpyc", ".rpym", ".rpymc"}:
            dest = Path(outdir) / p.relative_to(src)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            n += 1
    if n:
        log(f"Menyalin {n} file script lepas (.rpy/.rpyc)")


def decompile(outdir, log):
    cmd = find_unrpyc()
    if not cmd:
        log("unrpyc tidak ditemukan. Taruh unrpyc.py di folder vendor/ "
            "(https://github.com/CensoredUsername/unrpyc) lalu ulangi.")
        return
    rpycs = [str(p) for p in Path(outdir).rglob("*.rpyc")]
    if not rpycs:
        log("Tidak ada file .rpyc untuk di-decompile.")
        return
    log(f"Decompile {len(rpycs)} file .rpyc dengan unrpyc ...")
    for i in range(0, len(rpycs), 50):
        r = subprocess.run(cmd + rpycs[i:i + 50], capture_output=True, text=True)
        if r.stdout.strip():
            log(r.stdout.strip())
        if r.returncode != 0 and r.stderr.strip():
            log(r.stderr.strip())


def run_job(src, outdir, do_decompile=False, only_ext=None, log=print):
    archives = find_archives(src)
    if not archives:
        log("Tidak ada file .rpa/.rpi ditemukan.")
    total = 0
    for a in archives:
        try:
            total += extract_archive(a, outdir, log, only_ext)
        except Exception as e:
            log(f"  ! gagal {a.name}: {e}")
    copy_loose_scripts(src, outdir, log)
    if do_decompile:
        decompile(outdir, log)
    log(f"Selesai. Total {total} file dari {len(archives)} arsip -> {outdir}")
    return total
