"""
Dudiver Music Audio Converter
- Archivo individual (menu contextual): converter.exe "file.mp3" --format FLAC
- Carpeta completa  (menu contextual): converter.exe "folder"  --batch --format FLAC
- GUI (abrir directamente):            converter.exe
"""

import sys, os, subprocess, threading, shutil, re
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ─────────────────────────────────────────────────────────────────────────────
# Formatos
# ─────────────────────────────────────────────────────────────────────────────
FORMATS = {
    "FLAC":    {"ext": ".flac", "args": ["-c:a","flac","-compression_level","8"],         "label": "FLAC (sin perdida)"},
    "WAV24":   {"ext": ".wav",  "args": ["-c:a","pcm_s24le"],                              "label": "WAV 24-bit (sin perdida)"},
    "WAV16":   {"ext": ".wav",  "args": ["-c:a","pcm_s16le"],                              "label": "WAV 16-bit (calidad CD)"},
    "AIFF":    {"ext": ".aiff", "args": ["-c:a","pcm_s24be"],                              "label": "AIFF (sin perdida)"},
    "MP3_320": {"ext": ".mp3",  "args": ["-c:a","libmp3lame","-b:a","320k","-q:a","0"],  "label": "MP3 320k"},
    "MP3_VBR": {"ext": ".mp3",  "args": ["-c:a","libmp3lame","-q:a","0"],                 "label": "MP3 VBR V0"},
    "AAC":     {"ext": ".m4a",  "args": ["-c:a","aac","-b:a","256k"],                     "label": "AAC / M4A 256k"},
    "OGG":     {"ext": ".ogg",  "args": ["-c:a","libvorbis","-q:a","10"],                 "label": "OGG Vorbis"},
    "OPUS":    {"ext": ".opus", "args": ["-c:a","libopus","-b:a","256k"],                 "label": "OPUS 256k"},
    "WMA":     {"ext": ".wma",  "args": ["-c:a","wmav2","-b:a","320k"],                   "label": "WMA 320k"},
}

DISPLAY_NAMES = {
    "FLAC":    ("FLAC",       "Sin perdida · Maxima calidad",       True),
    "WAV24":   ("WAV 24-bit", "Sin perdida · Estudio profesional",  True),
    "WAV16":   ("WAV 16-bit", "Sin perdida · Calidad CD",           True),
    "AIFF":    ("AIFF",       "Sin perdida · Mac / Pro Tools",      True),
    "MP3_320": ("MP3 320k",   "Alta calidad · 320 kbps CBR",        False),
    "MP3_VBR": ("MP3 VBR V0", "Alta calidad · VBR variable",        False),
    "AAC":     ("AAC / M4A",  "Alta calidad · 256 kbps",            False),
    "OGG":     ("OGG Vorbis", "Open source · Alta calidad",         False),
    "OPUS":    ("OPUS",       "Maxima eficiencia moderna",           False),
    "WMA":     ("WMA",        "Windows Media Audio · 320k",          False),
}

AUDIO_EXTS = {".mp3",".wav",".flac",".ogg",".m4a",".aiff",".aif",
              ".wma",".opus",".aac",".ape",".mka",".alac",".webm"}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_ffmpeg() -> str | None:
    base = Path(sys.executable).parent if getattr(sys,"frozen",False) else Path(__file__).parent
    for name in ("ffmpeg.exe","ffmpeg"):
        p = base / name
        if p.exists(): return str(p)
    return shutil.which("ffmpeg")


def auto_name(folder: Path, stem: str, ext: str) -> Path:
    c = folder / (stem + ext)
    if not c.exists(): return c
    n = 1
    while True:
        c = folder / f"{stem} {n}{ext}"
        if not c.exists(): return c
        n += 1


def auto_name_dir(parent: Path, name: str) -> Path:
    c = parent / name
    if not c.exists(): return c
    n = 1
    while True:
        c = parent / f"{name} {n}"
        if not c.exists(): return c
        n += 1


def notify(title: str, body: str):
    body_safe  = body.replace('"',"'").replace('\n',' ')
    title_safe = title.replace('"',"'")
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$n=New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon=[System.Drawing.SystemIcons]::Information;"
        "$n.Visible=$true;"
        f'$n.ShowBalloonTip(5000,"{title_safe}","{body_safe}",'
        "[System.Windows.Forms.ToolTipIcon]::Info);"
        "Start-Sleep -s 5;$n.Dispose()"
    )
    subprocess.Popen(
        ["powershell","-WindowStyle","Hidden","-NonInteractive","-Command",script],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,"CREATE_NO_WINDOW") else 0,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def probe(ffmpeg: str, path: str) -> dict:
    try:
        r = subprocess.run([ffmpeg,"-i",path], capture_output=True, text=True, timeout=10)
        out = r.stderr
        info = {k:"—" for k in ("codec","duration","bitrate","hz")}
        m = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", out)
        if m: info["duration"] = m.group(1)
        m = re.search(r"bitrate: (\d+) kb/s", out)
        if m: info["bitrate"] = f"{m.group(1)} kbps"
        m = re.search(r"Audio: (\w+).*?,\s*(\d+) Hz", out)
        if m: info["codec"] = m.group(1).upper(); info["hz"] = f"{m.group(2)} Hz"
    except Exception:
        info = {k:"—" for k in ("codec","duration","bitrate","hz")}
    return info


def get_duration_s(ffmpeg: str, path: str) -> float | None:
    try:
        r = subprocess.run([ffmpeg,"-i",path], capture_output=True, text=True, timeout=10)
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
        if m:
            return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# MODO SILENCIOSO — archivo individual
# ─────────────────────────────────────────────────────────────────────────────

def convert_silent(input_file: str, format_key: str):
    ffmpeg = find_ffmpeg()
    inp = Path(input_file)
    fmt = FORMATS[format_key]
    if not ffmpeg:
        notify("Dudiver Music Audio Converter","❌ FFmpeg no encontrado. Reinstala la aplicacion.")
        return
    out = auto_name(inp.parent, inp.stem, fmt["ext"])
    notify("Dudiver Music Audio Converter", f"⏳ Convirtiendo: {inp.name}  →  {fmt['label']}...")
    cmd = [ffmpeg,"-i",str(inp),"-y"] + fmt["args"] + [str(out)]
    result = subprocess.run(cmd, capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,"CREATE_NO_WINDOW") else 0)
    if result.returncode == 0:
        notify("Dudiver Music Audio Converter", f"✅ {out.name}  ·  {os.path.getsize(out)/1_048_576:.1f} MB")
    else:
        notify("Dudiver Music Audio Converter", f"❌ Error convirtiendo {inp.name}")


# ─────────────────────────────────────────────────────────────────────────────
# MODO BATCH — convierte toda una carpeta
# ─────────────────────────────────────────────────────────────────────────────

class BatchApp(ctk.CTk):

    COLORS = {"pending":"#6b7280", "converting":"#3b82f6",
               "done":"#22c55e",   "error":"#ef4444"}
    W, H = 700, 600

    def __init__(self, folder: str, format_key: str):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.src_folder  = Path(folder)
        self.current_fmt = format_key
        self.ffmpeg      = find_ffmpeg()
        self.cancelled   = False
        self._running    = False
        self.out_dir     = None

        # Archivos de audio en la carpeta (no recursivo)
        self.files: list[Path] = sorted(
            [f for f in self.src_folder.iterdir()
             if f.is_file() and f.suffix.lower() in AUDIO_EXTS],
            key=lambda x: x.name.lower()
        )

        self.title("Dudiver Music Audio Converter")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(560, 480)
        self.resizable(True, True)

        self._build()
        self._update_dest()
        self._center()
        self.lift(); self.focus_force()
        self.attributes("-topmost", True)
        self.after(300, lambda: self.attributes("-topmost", False))

        if not self.ffmpeg:
            messagebox.showerror("FFmpeg no encontrado",
                "No se encontro ffmpeg.exe.\nColoca ffmpeg.exe junto al programa.")
            return

        if not self.files:
            messagebox.showinfo("Sin archivos",
                "No se encontraron archivos de audio en la carpeta seleccionada.")
            self.destroy(); return

    # ── helpers de formato ─────────────────────────────────────────────────────
    @staticmethod
    def _key_to_option(key: str) -> str:
        return f"{DISPLAY_NAMES[key][0]}  —  {FORMATS[key]['label']}"

    @staticmethod
    def _option_to_key(option: str) -> str:
        for k in FORMATS:
            if BatchApp._key_to_option(k) == option:
                return k
        return "FLAC"

    def _update_dest(self, *_):
        disp = DISPLAY_NAMES[self.current_fmt][0]
        preview = self.src_folder.parent / f"{self.src_folder.name} [{disp}]"
        self._lbl_dest.configure(text=str(preview))

    def _on_fmt_change(self, selection: str):
        self.current_fmt = self._option_to_key(selection)
        self._update_dest()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.W) // 2
        y = (self.winfo_screenheight() - self.H) // 2
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

    def _build(self):
        PAD = 14

        # ── Cabecera ──────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="#1c3a5e", corner_radius=0)
        hdr.pack(fill="x", side="top")
        ctk.CTkLabel(hdr, text="🎵  Dudiver Music Audio Converter · Conversión en lote",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=10)

        # ── Botones — pack desde el FONDO primero para que siempre sean visibles ──
        self._btn_row = ctk.CTkFrame(self, fg_color="transparent")
        self._btn_row.pack(fill="x", padx=PAD, pady=(8, PAD), side="bottom")
        self._btn_row.grid_columnconfigure(0, weight=1)
        self._btn_row.grid_columnconfigure(1, weight=1)
        self._btn_row.grid_columnconfigure(2, weight=1)

        self._btn_left = ctk.CTkButton(
            self._btn_row, text="✕  Cerrar", command=self.destroy,
            fg_color="#374151", hover_color="#4b5563",
            height=42, font=ctk.CTkFont(size=13))
        self._btn_left.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self._btn_right = ctk.CTkButton(
            self._btn_row, text="▶  Iniciar conversión", command=self._start_batch,
            fg_color="#2563eb", hover_color="#1d4ed8",
            height=42, font=ctk.CTkFont(size=13, weight="bold"))
        self._btn_right.grid(row=0, column=1, sticky="ew", padx=(6, 6))

        # Tercer botón — oculto hasta que termina la conversión
        self._btn_new = ctk.CTkButton(
            self._btn_row, text="📁  Otra carpeta", command=self._new_folder,
            fg_color="#6d28d9", hover_color="#5b21b6",
            height=42, font=ctk.CTkFont(size=13))
        self._btn_new.grid(row=0, column=2, sticky="ew", padx=(6, 0))
        self._btn_new.grid_remove()   # oculto al inicio

        # ── Info carpeta ──────────────────────────────────────────────
        info = ctk.CTkFrame(self)
        info.pack(fill="x", padx=PAD, pady=(PAD, 0), side="top")
        info.grid_columnconfigure(1, weight=1)

        # Carpeta
        ctk.CTkLabel(info, text="Carpeta:", font=ctk.CTkFont(size=11),
                     text_color="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 3))
        self._lbl_folder = ctk.CTkLabel(info, text=str(self.src_folder),
                     font=ctk.CTkFont(size=11), anchor="w", text_color="white")
        self._lbl_folder.grid(row=0, column=1, sticky="ew", padx=6, pady=(8, 3))

        # Formato — selector desplegable
        ctk.CTkLabel(info, text="Formato:", font=ctk.CTkFont(size=11),
                     text_color="gray").grid(row=1, column=0, sticky="w", padx=10, pady=(0, 3))

        fmt_options = [self._key_to_option(k) for k in FORMATS]
        self._fmt_menu = ctk.CTkOptionMenu(
            info,
            values=fmt_options,
            command=self._on_fmt_change,
            width=340, height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#1e3a5f",
            button_color="#2563eb",
            button_hover_color="#1d4ed8",
            dropdown_font=ctk.CTkFont(size=11),
        )
        self._fmt_menu.set(self._key_to_option(self.current_fmt))
        self._fmt_menu.grid(row=1, column=1, sticky="w", padx=6, pady=(0, 3))

        # Destino
        ctk.CTkLabel(info, text="Destino:", font=ctk.CTkFont(size=11),
                     text_color="gray").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))
        self._lbl_dest = ctk.CTkLabel(info, text="", font=ctk.CTkFont(size=11),
                                      anchor="w", text_color="#86efac")
        self._lbl_dest.grid(row=2, column=1, sticky="ew", padx=6, pady=(0, 8))

        # ── Progreso global ───────────────────────────────────────────
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.pack(fill="x", padx=PAD, pady=(PAD, 0), side="top")

        self._lbl_prog = ctk.CTkLabel(
            prog_frame, text=f"0 / {len(self.files)} archivos",
            font=ctk.CTkFont(size=12), text_color="gray", anchor="w")
        self._lbl_prog.pack(fill="x", pady=(0, 4))

        self._prog_bar = ctk.CTkProgressBar(prog_frame, height=8)
        self._prog_bar.pack(fill="x")
        self._prog_bar.set(0)

        # ── Lista de archivos — ocupa el espacio restante ─────────────
        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=PAD, pady=(PAD, 4))
        self._scroll.grid_columnconfigure(0, weight=1)

        self._rows: list[dict] = []
        for i, f in enumerate(self.files):
            row_frame = ctk.CTkFrame(self._scroll,
                                     fg_color="#1e293b" if i % 2 == 0 else "#0f172a",
                                     corner_radius=4)
            row_frame.pack(fill="x", pady=1)
            row_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row_frame, text=f.name, anchor="w",
                         font=ctk.CTkFont(size=11)).grid(
                             row=0, column=0, sticky="ew", padx=8, pady=3)

            lbl_status = ctk.CTkLabel(row_frame, text="⏳ Pendiente",
                                      text_color=self.COLORS["pending"],
                                      font=ctk.CTkFont(size=10), width=130, anchor="e")
            lbl_status.grid(row=0, column=1, padx=8, pady=3)
            self._rows.append({"status": lbl_status})

    def _set_row(self, idx: int, icon: str, color: str, text: str):
        self._rows[idx]["status"].configure(text=f"{icon} {text}", text_color=color)

    def _start_batch(self):
        if self._running:
            return
        self._running = True

        # Crear carpeta de salida ahora que sabemos el formato final
        disp = DISPLAY_NAMES[self.current_fmt][0]
        out_name = f"{self.src_folder.name} [{disp}]"
        self.out_dir = auto_name_dir(self.src_folder.parent, out_name)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._lbl_dest.configure(text=str(self.out_dir))

        # Cambiar estado de botones
        self._btn_new.grid_remove()
        self._btn_right.configure(state="disabled", text="⏳  Convirtiendo…",
                                  fg_color="#374151", hover_color="#374151")
        self._btn_left.configure(text="✕  Cancelar", command=self._cancel,
                                 fg_color="#dc2626", hover_color="#b91c1c")
        self._fmt_menu.configure(state="disabled")

        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        fmt   = FORMATS[self.current_fmt]
        total = len(self.files)
        done  = 0
        errors = 0

        for i, f in enumerate(self.files):
            if self.cancelled:
                self.after(0, self._set_row, i, "⏹", "#6b7280", "Cancelado")
                continue

            self.after(0, self._set_row, i, "🔄", self.COLORS["converting"], "Convirtiendo…")
            self.after(0, self._lbl_prog.configure,
                       {"text": f"{done} / {total} archivos  ·  {f.name}"})

            out = auto_name(self.out_dir, f.stem, fmt["ext"])
            cmd = [self.ffmpeg, "-i", str(f), "-y"] + fmt["args"] + [str(out)]
            try:
                r = subprocess.run(cmd, capture_output=True,
                                   creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,"CREATE_NO_WINDOW") else 0)
                if r.returncode == 0:
                    done += 1
                    mb = os.path.getsize(out) / 1_048_576
                    self.after(0, self._set_row, i, "✅", self.COLORS["done"], f"{mb:.1f} MB")
                else:
                    errors += 1
                    self.after(0, self._set_row, i, "❌", self.COLORS["error"], "Error")
            except Exception as e:
                errors += 1
                self.after(0, self._set_row, i, "❌", self.COLORS["error"], str(e)[:30])

            self.after(0, self._prog_bar.set, (i + 1) / total)

        if self.cancelled:
            self.after(0, self._lbl_prog.configure,
                       {"text": f"Cancelado · {done} de {total} completados", "text_color": "#f59e0b"})
            self.after(0, self._btn_left.configure,
                       {"text": "✕  Cerrar", "command": self.destroy,
                        "fg_color": "#374151", "hover_color": "#4b5563"})
        else:
            self.after(0, self._finish, done, errors, total)

    def _finish(self, done: int, errors: int, total: int):
        self._prog_bar.set(1.0)
        if errors == 0:
            self._lbl_prog.configure(
                text=f"✅  {done} / {total} archivos convertidos correctamente",
                text_color="#22c55e")
        else:
            self._lbl_prog.configure(
                text=f"⚠️  {done} OK · {errors} errores de {total} archivos",
                text_color="#f59e0b")
        self._btn_left.configure(text="✕  Cerrar", command=self.destroy,
                                 fg_color="#374151", hover_color="#4b5563", state="normal")
        self._btn_right.configure(state="normal", text="📂  Abrir carpeta",
                                  command=self._open_out,
                                  fg_color="#15803d", hover_color="#166534")
        self._btn_new.grid()   # mostrar botón "Otra carpeta"

    def _cancel(self):
        self.cancelled = True
        self._btn_left.configure(state="disabled", text="Cancelando…")

    def _open_out(self):
        os.startfile(str(self.out_dir))

    def _new_folder(self):
        """Selecciona una nueva carpeta y reinicia la ventana sin cerrarla."""
        folder = filedialog.askdirectory(title="Seleccionar otra carpeta de audio")
        if not folder:
            return

        # Resetear estado interno
        self.src_folder  = Path(folder)
        self.cancelled   = False
        self._running    = False
        self.out_dir     = None

        self.files = sorted(
            [f for f in self.src_folder.iterdir()
             if f.is_file() and f.suffix.lower() in AUDIO_EXTS],
            key=lambda x: x.name.lower()
        )

        if not self.files:
            messagebox.showinfo("Sin archivos",
                "No se encontraron archivos de audio en esa carpeta.")
            return

        # Actualizar etiquetas
        self._lbl_folder.configure(text=str(self.src_folder))
        self._update_dest()
        self._prog_bar.set(0)
        self._lbl_prog.configure(
            text=f"0 / {len(self.files)} archivos", text_color="gray")

        # Reconstruir lista de archivos
        for w in self._scroll.winfo_children():
            w.destroy()
        self._rows = []
        for i, f in enumerate(self.files):
            row_frame = ctk.CTkFrame(self._scroll,
                                     fg_color="#1e293b" if i % 2 == 0 else "#0f172a",
                                     corner_radius=4)
            row_frame.pack(fill="x", pady=1)
            row_frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row_frame, text=f.name, anchor="w",
                         font=ctk.CTkFont(size=11)).grid(
                             row=0, column=0, sticky="ew", padx=8, pady=3)
            lbl_status = ctk.CTkLabel(row_frame, text="⏳ Pendiente",
                                      text_color=self.COLORS["pending"],
                                      font=ctk.CTkFont(size=10), width=130, anchor="e")
            lbl_status.grid(row=0, column=1, padx=8, pady=3)
            self._rows.append({"status": lbl_status})

        # Resetear botones al estado inicial
        self._fmt_menu.configure(state="normal")
        self._btn_new.grid_remove()
        self._btn_left.configure(text="✕  Cerrar", command=self.destroy,
                                 fg_color="#374151", hover_color="#4b5563", state="normal")
        self._btn_right.configure(text="▶  Iniciar conversión", command=self._start_batch,
                                  fg_color="#2563eb", hover_color="#1d4ed8", state="normal")


# ─────────────────────────────────────────────────────────────────────────────
# MODO GUI — ventana principal (abrir directamente)
# ─────────────────────────────────────────────────────────────────────────────

W, H = 620, 618

class App(ctk.CTk):

    def __init__(self, input_file: str | None = None):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Dudiver Music Audio Converter")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)

        self.input_file: str | None = None
        self.output_dir: str | None = None
        self.fmt_var    = ctk.StringVar(value="FLAC")
        self.converting = False
        self.ffmpeg     = find_ffmpeg()

        self._build()
        self._center()
        self.lift(); self.focus_force()
        self.attributes("-topmost", True)
        self.after(300, lambda: self.attributes("-topmost", False))

        if not self.ffmpeg:
            messagebox.showerror("FFmpeg no encontrado",
                "No se encontro ffmpeg.exe.\n\nColoca ffmpeg.exe junto al programa.")
        if input_file and Path(input_file).exists():
            self._load(input_file)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - W) // 2
        y = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{x}+{y}")

    def _build(self):
        PAD = 14

        hdr = ctk.CTkFrame(self, fg_color="#1c3a5e", corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🎵  Dudiver Music Audio Converter",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(hdr, text="FFmpeg · lossless & lossy",
                     font=ctk.CTkFont(size=11), text_color="#90b8d8").pack(side="right", padx=16)

        # Archivo entrada
        f_inp = ctk.CTkFrame(self)
        f_inp.pack(fill="x", padx=PAD, pady=(PAD, 0))
        row = ctk.CTkFrame(f_inp, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(10,6))
        row.grid_columnconfigure(0, weight=1)
        self.lbl_file = ctk.CTkLabel(row, text="Ningun archivo seleccionado",
                                     text_color="gray", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_file.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(row, text="Examinar…", command=self._browse,
                      width=110, height=28).grid(row=0, column=1, padx=(8,0))

        info_bg = ctk.CTkFrame(f_inp, fg_color="#111827", corner_radius=6)
        info_bg.pack(fill="x", padx=10, pady=(0,10))
        for c in range(4): info_bg.grid_columnconfigure(c, weight=1)
        self._info: dict[str, ctk.CTkLabel] = {}
        for i,(lbl,key) in enumerate([("Codec","codec"),("Duracion","duration"),
                                       ("Bitrate","bitrate"),("Sample rate","hz")]):
            ctk.CTkLabel(info_bg, text=lbl, text_color="#6b7280",
                         font=ctk.CTkFont(size=10)).grid(row=0, column=i, padx=10, pady=(6,1))
            v = ctk.CTkLabel(info_bg, text="—", font=ctk.CTkFont(size=11, weight="bold"))
            v.grid(row=1, column=i, padx=10, pady=(1,6))
            self._info[key] = v

        # Formato
        ctk.CTkLabel(self, text="Formato de salida",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=PAD, pady=(PAD,4))
        fmt_frame = ctk.CTkFrame(self)
        fmt_frame.pack(fill="x", padx=PAD)
        COLS = 3
        for idx,(key,(name,desc,lossless)) in enumerate(DISPLAY_NAMES.items()):
            r,c = divmod(idx, COLS)
            cell = ctk.CTkFrame(fmt_frame, fg_color="transparent")
            cell.grid(row=r, column=c, sticky="w", padx=6, pady=2)
            ctk.CTkRadioButton(cell, text=name, variable=self.fmt_var, value=key,
                               font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            badge = "🔒" if lossless else "🔊"
            ctk.CTkLabel(cell, text=f"{badge} {desc}",
                         font=ctk.CTkFont(size=9), text_color="#6b7280").pack(anchor="w", padx=22)
        for c in range(COLS): fmt_frame.grid_columnconfigure(c, weight=1)

        # Destino
        f_out = ctk.CTkFrame(self)
        f_out.pack(fill="x", padx=PAD, pady=(PAD,0))
        row_out = ctk.CTkFrame(f_out, fg_color="transparent")
        row_out.pack(fill="x", padx=10, pady=8)
        row_out.grid_columnconfigure(1, weight=1)
        self.same_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(row_out, text="Misma carpeta que el original",
                        variable=self.same_var, command=self._toggle_out,
                        font=ctk.CTkFont(size=11)).grid(row=0, column=0, sticky="w")
        self.lbl_out = ctk.CTkLabel(row_out, text="", text_color="gray",
                                    font=ctk.CTkFont(size=10), anchor="w")
        self.lbl_out.grid(row=0, column=1, sticky="ew", padx=(12,0))
        self.btn_out = ctk.CTkButton(row_out, text="Cambiar…", command=self._browse_out,
                                     width=90, height=26, state="disabled")
        self.btn_out.grid(row=0, column=2, padx=(8,0))

        # Progreso
        self._prog_bar = ctk.CTkProgressBar(self, height=6)
        self._prog_bar.pack(fill="x", padx=PAD, pady=(PAD,0))
        self._prog_bar.set(0)
        self._lbl_prog = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self._lbl_prog.pack(pady=(2,0))

        # Botones
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=PAD, pady=PAD)
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)

        self.btn_conv = ctk.CTkButton(btns, text="⚡  Convertir archivo",
                                      command=self._start, height=46,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      fg_color="#2563eb", hover_color="#1d4ed8")
        self.btn_conv.grid(row=0, column=0, sticky="ew", padx=(0,5))

        ctk.CTkButton(btns, text="📂  Convertir carpeta",
                      command=self._browse_batch, height=46,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      fg_color="#15803d", hover_color="#166534").grid(
                          row=0, column=1, sticky="ew", padx=(5,0))

    def _browse(self):
        p = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[("Audio","*.mp3 *.wav *.flac *.ogg *.m4a *.aiff *.aif "
                                "*.wma *.opus *.aac *.ape *.alac *.mka *.webm"),
                       ("Todos","*.*")])
        if p: self._load(p)

    def _load(self, path: str):
        self.input_file = path
        name = Path(path).name
        self.lbl_file.configure(text=name[:70]+("…" if len(name)>70 else ""), text_color="white")
        self.output_dir = str(Path(path).parent)
        self._show_out()
        if self.ffmpeg:
            threading.Thread(target=lambda: self.after(0, lambda: [
                v.configure(text=probe(self.ffmpeg, path)[k])
                for k,v in self._info.items()
            ]), daemon=True).start()

    def _toggle_out(self):
        if self.same_var.get():
            self.btn_out.configure(state="disabled")
            if self.input_file:
                self.output_dir = str(Path(self.input_file).parent)
                self._show_out()
        else:
            self.btn_out.configure(state="normal")

    def _browse_out(self):
        d = filedialog.askdirectory(title="Carpeta de destino")
        if d: self.output_dir = d; self._show_out()

    def _show_out(self):
        d = self.output_dir or ""
        self.lbl_out.configure(text=d[:55]+("…" if len(d)>55 else ""))

    def _browse_batch(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de audio")
        if not folder: return
        fmt_key = self.fmt_var.get()
        self.withdraw()
        BatchApp(folder=folder, format_key=fmt_key).mainloop()
        self.deiconify()

    def _start(self):
        if self.converting: return
        if not self.input_file:
            messagebox.showerror("Sin archivo","Selecciona un archivo de audio primero."); return
        if not self.ffmpeg:
            messagebox.showerror("FFmpeg","ffmpeg.exe no encontrado."); return
        fmt_key = self.fmt_var.get()
        fmt  = FORMATS[fmt_key]
        inp  = Path(self.input_file)
        stem = inp.stem + ("_16bit" if fmt_key=="WAV16" else "")
        out  = auto_name(Path(self.output_dir), stem, fmt["ext"])
        self.converting = True
        self.btn_conv.configure(state="disabled", text="Convirtiendo…")
        self._prog_bar.set(0)
        self._lbl_prog.configure(text="Iniciando…", text_color="gray")
        threading.Thread(target=self._convert_bg, args=(str(inp),str(out),fmt,fmt_key), daemon=True).start()

    def _convert_bg(self, inp, out, fmt, fmt_key):
        dur  = get_duration_s(self.ffmpeg, inp)
        cmd  = [self.ffmpeg,"-i",inp,"-y"] + fmt["args"] + [out]
        try:
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                    text=True, encoding="utf-8", errors="replace")
            tre  = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            for line in proc.stderr:
                if dur:
                    m = tre.search(line)
                    if m:
                        cur = int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
                        pct = min(cur/dur,1.0)
                        self.after(0, self._set_prog, pct, f"{int(pct*100)}%")
            proc.wait()
            if proc.returncode == 0:
                self.after(0, self._done, out, DISPLAY_NAMES[fmt_key][0])
            else:
                self.after(0, self._err, "FFmpeg termino con error.")
        except Exception as e:
            self.after(0, self._err, str(e))

    def _set_prog(self, v, txt):
        self._prog_bar.set(v); self._lbl_prog.configure(text=txt)

    def _done(self, out, fmt_name):
        self.converting = False
        self.btn_conv.configure(state="normal", text="⚡  Convertir archivo")
        self._prog_bar.set(1.0)
        mb = os.path.getsize(out)/1_048_576
        self._lbl_prog.configure(text=f"✅  {Path(out).name}  ({mb:.1f} MB)", text_color="#22c55e")
        if messagebox.askyesno("¡Listo!", f"Formato: {fmt_name}\nArchivo: {Path(out).name}\nTamaño: {mb:.1f} MB\n\n¿Abrir carpeta?"):
            os.startfile(str(Path(out).parent))

    def _err(self, msg):
        self.converting = False
        self.btn_conv.configure(state="normal", text="⚡  Convertir archivo")
        self._prog_bar.set(0)
        self._lbl_prog.configure(text="❌  Error", text_color="#ef4444")
        messagebox.showerror("Error", msg)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    # Modo silencioso archivo: exe "file.mp3" --format FLAC
    if len(args) >= 3 and args[1] == "--format":
        convert_silent(args[0], args[2])
        return

    # Modo batch carpeta: exe "folder" --batch --format FLAC
    if len(args) >= 4 and args[1] == "--batch" and args[2] == "--format":
        BatchApp(folder=args[0], format_key=args[3]).mainloop()
        return

    # GUI
    input_file = args[0] if args else None
    App(input_file=input_file).mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback, tempfile
        log = os.path.join(tempfile.gettempdir(), "DudiverConverter_error.txt")
        with open(log,"w",encoding="utf-8") as f:
            f.write(traceback.format_exc())
        try:
            import tkinter as tk
            from tkinter import messagebox as mb
            tk.Tk().withdraw()
            mb.showerror("Error", f"{e}\n\nLog: {log}")
        except Exception:
            pass
