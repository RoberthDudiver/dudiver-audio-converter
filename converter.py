"""
Dudiver Music Audio Converter
- Modo silencioso (desde menu contextual): converter.exe "archivo.mp3" --format FLAC
- Modo GUI (abrir directamente):           converter.exe
"""

import sys
import os
import subprocess
import threading
import shutil
import re
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ---------------------------------------------------------------------------
# Formatos
# ---------------------------------------------------------------------------
FORMATS = {
    "FLAC":       {"ext": ".flac", "args": ["-c:a", "flac", "-compression_level", "8"],          "label": "FLAC (sin perdida)"},
    "WAV24":      {"ext": ".wav",  "args": ["-c:a", "pcm_s24le"],                                 "label": "WAV 24-bit (sin perdida)"},
    "WAV16":      {"ext": ".wav",  "args": ["-c:a", "pcm_s16le"],                                 "label": "WAV 16-bit (calidad CD)"},
    "AIFF":       {"ext": ".aiff", "args": ["-c:a", "pcm_s24be"],                                 "label": "AIFF (sin perdida)"},
    "MP3_320":    {"ext": ".mp3",  "args": ["-c:a", "libmp3lame", "-b:a", "320k", "-q:a", "0"],  "label": "MP3 320k"},
    "MP3_VBR":    {"ext": ".mp3",  "args": ["-c:a", "libmp3lame", "-q:a", "0"],                  "label": "MP3 VBR V0"},
    "AAC":        {"ext": ".m4a",  "args": ["-c:a", "aac", "-b:a", "256k"],                      "label": "AAC / M4A 256k"},
    "OGG":        {"ext": ".ogg",  "args": ["-c:a", "libvorbis", "-q:a", "10"],                  "label": "OGG Vorbis"},
    "OPUS":       {"ext": ".opus", "args": ["-c:a", "libopus", "-b:a", "256k"],                  "label": "OPUS 256k"},
    "WMA":        {"ext": ".wma",  "args": ["-c:a", "wmav2", "-b:a", "320k"],                    "label": "WMA 320k"},
}

# Nombres para mostrar en GUI
DISPLAY_NAMES = {
    "FLAC":    ("FLAC",       "Sin perdida · Maxima calidad",      True),
    "WAV24":   ("WAV 24-bit", "Sin perdida · Estudio profesional", True),
    "WAV16":   ("WAV 16-bit", "Sin perdida · Calidad CD",          True),
    "AIFF":    ("AIFF",       "Sin perdida · Mac / Pro Tools",     True),
    "MP3_320": ("MP3 320k",   "Alta calidad · 320 kbps CBR",       False),
    "MP3_VBR": ("MP3 VBR V0", "Alta calidad · VBR variable",       False),
    "AAC":     ("AAC / M4A",  "Alta calidad · 256 kbps",           False),
    "OGG":     ("OGG Vorbis", "Open source · Alta calidad",        False),
    "OPUS":    ("OPUS",       "Maxima eficiencia moderna",          False),
    "WMA":     ("WMA",        "Windows Media Audio · 320k",         False),
}


# ---------------------------------------------------------------------------
# Helpers comunes
# ---------------------------------------------------------------------------

def find_ffmpeg() -> str | None:
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    for name in ("ffmpeg.exe", "ffmpeg"):
        p = base / name
        if p.exists():
            return str(p)
    return shutil.which("ffmpeg")


def auto_name(folder: Path, stem: str, ext: str) -> Path:
    """Devuelve ruta sin colision: 'song.flac', 'song 1.flac', 'song 2.flac'..."""
    candidate = folder / (stem + ext)
    if not candidate.exists():
        return candidate
    n = 1
    while True:
        candidate = folder / f"{stem} {n}{ext}"
        if not candidate.exists():
            return candidate
        n += 1


def notify(title: str, body: str):
    """Notificacion de Windows via PowerShell (sin dependencias extra)."""
    body_safe = body.replace('"', "'").replace('\n', ' ')
    title_safe = title.replace('"', "'")
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
        ["powershell", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", script],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def probe(ffmpeg: str, path: str) -> dict:
    try:
        r = subprocess.run([ffmpeg, "-i", path], capture_output=True, text=True, timeout=10)
        out = r.stderr
        info = {k: "—" for k in ("codec", "duration", "bitrate", "hz")}
        m = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", out)
        if m: info["duration"] = m.group(1)
        m = re.search(r"bitrate: (\d+) kb/s", out)
        if m: info["bitrate"] = f"{m.group(1)} kbps"
        m = re.search(r"Audio: (\w+).*?,\s*(\d+) Hz", out)
        if m: info["codec"] = m.group(1).upper(); info["hz"] = f"{m.group(2)} Hz"
    except Exception:
        info = {k: "—" for k in ("codec", "duration", "bitrate", "hz")}
    return info


def get_duration_s(ffmpeg: str, path: str) -> float | None:
    try:
        r = subprocess.run([ffmpeg, "-i", path], capture_output=True, text=True, timeout=10)
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
        if m:
            return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# MODO SILENCIOSO — desde el menu contextual
# ---------------------------------------------------------------------------

def convert_silent(input_file: str, format_key: str):
    """Convierte sin GUI. Solo notificaciones de Windows."""
    ffmpeg = find_ffmpeg()
    inp = Path(input_file)
    fmt = FORMATS[format_key]

    if not ffmpeg:
        notify("Dudiver Music Audio Converter",
               "❌ FFmpeg no encontrado. Reinstala la aplicacion.")
        return

    out = auto_name(inp.parent, inp.stem, fmt["ext"])

    notify("Dudiver Music Audio Converter",
           f"⏳ Convirtiendo: {inp.name}  →  {fmt['label']}...")

    cmd = [ffmpeg, "-i", str(inp), "-y"] + fmt["args"] + [str(out)]
    result = subprocess.run(cmd, capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)

    if result.returncode == 0:
        size_mb = os.path.getsize(out) / 1_048_576
        notify("Dudiver Music Audio Converter",
               f"✅ {out.name}  ·  {size_mb:.1f} MB")
    else:
        notify("Dudiver Music Audio Converter",
               f"❌ Error convirtiendo {inp.name}")


# ---------------------------------------------------------------------------
# MODO GUI — ventana completa (cuando el usuario abre el .exe directamente)
# ---------------------------------------------------------------------------

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
        self.fmt_var = ctk.StringVar(value="FLAC")
        self.converting = False
        self.ffmpeg = find_ffmpeg()

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
        x = (self.winfo_screenwidth() - W) // 2
        y = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{x}+{y}")

    def _build(self):
        PAD = 14

        # Cabecera
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
        row.pack(fill="x", padx=10, pady=(10, 6))
        row.grid_columnconfigure(0, weight=1)
        self.lbl_file = ctk.CTkLabel(row, text="Ningun archivo seleccionado",
                                     text_color="gray", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_file.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(row, text="Examinar…", command=self._browse,
                      width=110, height=28).grid(row=0, column=1, padx=(8, 0))

        info_bg = ctk.CTkFrame(f_inp, fg_color="#111827", corner_radius=6)
        info_bg.pack(fill="x", padx=10, pady=(0, 10))
        for c in range(4): info_bg.grid_columnconfigure(c, weight=1)
        self._info: dict[str, ctk.CTkLabel] = {}
        for i, (lbl, key) in enumerate([("Codec","codec"),("Duracion","duration"),
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
        for idx, (key, (name, desc, lossless)) in enumerate(DISPLAY_NAMES.items()):
            r, c = divmod(idx, COLS)
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
        f_out.pack(fill="x", padx=PAD, pady=(PAD, 0))
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
        self._prog_bar.pack(fill="x", padx=PAD, pady=(PAD, 0))
        self._prog_bar.set(0)
        self._lbl_prog = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self._lbl_prog.pack(pady=(2, 0))

        # Boton
        self.btn_conv = ctk.CTkButton(self, text="⚡  Convertir", command=self._start,
                                      height=46, font=ctk.CTkFont(size=16, weight="bold"),
                                      fg_color="#2563eb", hover_color="#1d4ed8")
        self.btn_conv.pack(fill="x", padx=PAD, pady=PAD)

    def _browse(self):
        p = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.ogg *.m4a *.aiff *.aif "
                                 "*.wma *.opus *.aac *.ape *.alac *.mka *.webm"),
                       ("Todos", "*.*")])
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
                for k, v in self._info.items()
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

    def _start(self):
        if self.converting: return
        if not self.input_file:
            messagebox.showerror("Sin archivo", "Selecciona un archivo de audio primero."); return
        if not self.ffmpeg:
            messagebox.showerror("FFmpeg", "ffmpeg.exe no encontrado."); return

        fmt_key = self.fmt_var.get()
        fmt = FORMATS[fmt_key]
        inp = Path(self.input_file)
        stem = inp.stem + ("_16bit" if fmt_key == "WAV16" else "")
        out = auto_name(Path(self.output_dir), stem, fmt["ext"])

        self.converting = True
        self.btn_conv.configure(state="disabled", text="Convirtiendo…")
        self._prog_bar.set(0)
        self._lbl_prog.configure(text="Iniciando…", text_color="gray")

        threading.Thread(target=self._convert_bg,
                         args=(str(inp), str(out), fmt, fmt_key), daemon=True).start()

    def _convert_bg(self, inp, out, fmt, fmt_key):
        dur = get_duration_s(self.ffmpeg, inp)
        cmd = [self.ffmpeg, "-i", inp, "-y"] + fmt["args"] + [out]
        try:
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                    text=True, encoding="utf-8", errors="replace")
            time_re = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            for line in proc.stderr:
                if dur:
                    m = time_re.search(line)
                    if m:
                        cur = int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
                        pct = min(cur/dur, 1.0)
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
        self.btn_conv.configure(state="normal", text="⚡  Convertir")
        self._prog_bar.set(1.0)
        mb = os.path.getsize(out)/1_048_576
        self._lbl_prog.configure(text=f"✅  {Path(out).name}  ({mb:.1f} MB)", text_color="#22c55e")
        if messagebox.askyesno("¡Listo!", f"Formato: {fmt_name}\nArchivo: {Path(out).name}\nTamaño: {mb:.1f} MB\n\n¿Abrir carpeta?"):
            os.startfile(str(Path(out).parent))

    def _err(self, msg):
        self.converting = False
        self.btn_conv.configure(state="normal", text="⚡  Convertir")
        self._prog_bar.set(0)
        self._lbl_prog.configure(text="❌  Error", text_color="#ef4444")
        messagebox.showerror("Error", msg)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    # Modo silencioso: converter.exe "file.mp3" --format FLAC
    if len(args) >= 3 and args[1] == "--format":
        convert_silent(args[0], args[2])
        return

    # Modo GUI (con o sin archivo inicial)
    input_file = args[0] if args else None
    App(input_file=input_file).mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback, tempfile
        log = os.path.join(tempfile.gettempdir(), "DudiverConverter_error.txt")
        with open(log, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        try:
            import tkinter as tk
            from tkinter import messagebox as mb
            tk.Tk().withdraw()
            mb.showerror("Error", f"{e}\n\nLog: {log}")
        except Exception:
            pass
