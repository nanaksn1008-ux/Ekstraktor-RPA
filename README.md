# Ren'Py Extractor

Ekstrak arsip `.rpa` (RPA-2.0 / 3.0 / 3.2 / 4.0) dari game Ren'Py, dengan GUI dan CLI.
Tanpa dependensi eksternal. Opsional: decompile `.rpyc` -> `.rpy` via [unrpyc](https://github.com/CensoredUsername/unrpyc).

## Instalasi

```bash
git clone https://github.com/<USERNAME>/renpy-extractor.git
cd renpy-extractor
pip install -e .
```

## Pemakaian

```bash
renpy-extractor                        # buka GUI
renpy-extractor "Game/game" -o hasil   # ekstrak semua .rpa di folder
renpy-extractor game/archive.rpa -l    # lihat isi arsip
renpy-extractor "Game/game" -e .png,.ogg
renpy-extractor "Game/game" -d         # + decompile .rpyc (butuh vendor/unrpyc.py)
```

Tanpa instalasi: `PYTHONPATH=src python -m renpy_extractor ...`

## Build .exe (opsional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --paths src -n RenpyExtractor src/renpy_extractor/__main__.py
```

## Struktur

```
src/renpy_extractor/   kode utama (rpa, jobs, cli, gui)
tests/                 unit test
vendor/                taruh unrpyc.py di sini (opsional)
.github/workflows/     CI
```

## Batasan

- RPA-1.0 (`.rpi` + `.rpa` lama) dan arsip yang tertanam di `.exe` belum didukung.
- Index arsip dibaca dengan unpickler terbatas dan path traversal diblokir.

## Catatan hukum

Gunakan hanya pada game milik sendiri atau untuk modding/terjemahan yang diizinkan pengembangnya.

## Lisensi

MIT
