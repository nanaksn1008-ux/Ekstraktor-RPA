import queue
import threading
from pathlib import Path

from .cli import _parse_exts
from .jobs import run_job


def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    root = tk.Tk()
    root.title("Ren'Py Extractor")
    root.geometry("720x480")
    q = queue.Queue()

    src_var, out_var, ext_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
    dec_var = tk.BooleanVar(value=False)

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)
    frm.columnconfigure(1, weight=1)

    def set_src(p):
        if p:
            src_var.set(p)
            if not out_var.get():
                out_var.set(str(Path(p).parent / "extracted"))

    ttk.Label(frm, text="Sumber:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=src_var).grid(row=0, column=1, sticky="ew", padx=5)
    ttk.Button(frm, text="Folder",
               command=lambda: set_src(filedialog.askdirectory(title="Folder game"))
               ).grid(row=0, column=2)
    ttk.Button(frm, text="File",
               command=lambda: set_src(filedialog.askopenfilename(
                   filetypes=[("RPA", "*.rpa *.rpi"), ("Semua", "*.*")]))
               ).grid(row=0, column=3, padx=(4, 0))

    ttk.Label(frm, text="Output:").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Entry(frm, textvariable=out_var).grid(row=1, column=1, sticky="ew", padx=5)
    ttk.Button(frm, text="Pilih",
               command=lambda: out_var.set(filedialog.askdirectory() or out_var.get())
               ).grid(row=1, column=2)

    ttk.Label(frm, text="Filter ext:").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=ext_var).grid(row=2, column=1, sticky="ew", padx=5)
    ttk.Label(frm, text="mis. .png,.ogg (kosong = semua)").grid(
        row=2, column=2, columnspan=2, sticky="w")

    ttk.Checkbutton(frm, text="Decompile .rpyc -> .rpy (butuh unrpyc di vendor/)",
                    variable=dec_var).grid(row=3, column=1, sticky="w", pady=6)

    log_box = scrolledtext.ScrolledText(frm, height=16, state="disabled")
    log_box.grid(row=5, column=0, columnspan=4, sticky="nsew")
    frm.rowconfigure(5, weight=1)

    def poll():
        while not q.empty():
            log_box.configure(state="normal")
            log_box.insert("end", q.get() + "\n")
            log_box.see("end")
            log_box.configure(state="disabled")
        root.after(100, poll)

    def start():
        if not src_var.get() or not out_var.get():
            messagebox.showwarning("Kurang data", "Isi sumber dan folder output.")
            return
        btn.configure(state="disabled")

        def work():
            try:
                run_job(src_var.get(), out_var.get(), dec_var.get(),
                        _parse_exts(ext_var.get()), q.put)
            finally:
                root.after(0, lambda: btn.configure(state="normal"))
        threading.Thread(target=work, daemon=True).start()

    btn = ttk.Button(frm, text="Ekstrak", command=start)
    btn.grid(row=4, column=1, sticky="w", pady=6)

    poll()
    root.mainloop()
