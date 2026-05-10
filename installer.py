"""
Dudiver Music Audio Converter - Installer
Doble clic para instalar. No requiere admin.
"""
import sys, os, shutil, winreg, subprocess, time, ctypes
from pathlib import Path

APP_NAME    = "Dudiver Music Audio Converter"
MENU_KEY    = "DudiverMusicConverter"
INSTALL_DIR = Path(os.environ["LOCALAPPDATA"]) / "DudiverMusicConverter"

FORMATS_FILE = [
    ("FLAC",    "a FLAC  (sin perdida)"),
    ("WAV24",   "a WAV 24-bit  (sin perdida)"),
    ("WAV16",   "a WAV 16-bit  (calidad CD)"),
    ("AIFF",    "a AIFF  (sin perdida)"),
    ("MP3_320", "a MP3 320k"),
    ("MP3_VBR", "a MP3 VBR V0"),
    ("AAC",     "a AAC / M4A"),
    ("OGG",     "a OGG Vorbis"),
    ("OPUS",    "a OPUS"),
    ("WMA",     "a WMA"),
]

FORMATS_FOLDER = [
    ("FLAC",    "Convertir todo a FLAC  (sin perdida)"),
    ("WAV24",   "Convertir todo a WAV 24-bit"),
    ("WAV16",   "Convertir todo a WAV 16-bit"),
    ("MP3_320", "Convertir todo a MP3 320k"),
    ("MP3_VBR", "Convertir todo a MP3 VBR V0"),
    ("AAC",     "Convertir todo a AAC / M4A"),
    ("OGG",     "Convertir todo a OGG Vorbis"),
    ("OPUS",    "Convertir todo a OPUS"),
]

def say(msg): print(msg, flush=True)

def make_ico(src: Path, dst: Path) -> bool:
    try:
        from PIL import Image
        img = Image.open(src).convert("RGBA")
        sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
        imgs = [img.resize(s, Image.LANCZOS) for s in sizes]
        imgs[0].save(dst, format="ICO", sizes=sizes, append_images=imgs[1:])
        return True
    except Exception:
        return False

def del_key(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as k:
            while True:
                try:
                    child = winreg.EnumKey(k, 0)
                    del_key(root, path + "\\" + child)
                except OSError:
                    break
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass

def reg_set(root, path, values: dict):
    with winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE) as k:
        for name, val in values.items():
            winreg.SetValueEx(k, name, 0, winreg.REG_SZ, val)

def install():
    # Fuente: junto al instalador
    if getattr(sys, "frozen", False):
        src = Path(sys.executable).parent
    else:
        src = Path(__file__).parent / "dist"

    exe_src    = src / "DudiverConverter.exe"
    ffmpeg_src = src / "ffmpeg.exe"
    icon_src   = src / "icon.png"
    ico_src    = src / "icon.ico"

    if not exe_src.exists():
        say(f"ERROR: No se encuentra {exe_src}")
        input("Presiona Enter para salir...")
        sys.exit(1)

    # ── 1. Copiar archivos ────────────────────────────────────────────
    say(f"[1/3] Copiando archivos a {INSTALL_DIR} ...")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exe_src, INSTALL_DIR / "DudiverConverter.exe")
    if ffmpeg_src.exists():
        shutil.copy2(ffmpeg_src, INSTALL_DIR / "ffmpeg.exe")

    # Icono
    ico_dst = INSTALL_DIR / "icon.ico"
    if ico_src.exists():
        shutil.copy2(ico_src, ico_dst)
    elif icon_src.exists():
        if not make_ico(icon_src, ico_dst):
            ico_dst = INSTALL_DIR / "DudiverConverter.exe"
    else:
        ico_dst = INSTALL_DIR / "DudiverConverter.exe"
    say("      OK")

    exe_path = str(INSTALL_DIR / "DudiverConverter.exe")
    ico_str  = f'"{ico_dst}",0'
    hkcu     = winreg.HKEY_CURRENT_USER

    # ── Limpiar entradas viejas ───────────────────────────────────────
    old_paths = [
        f"SOFTWARE\\Classes\\SystemFileAssociations\\.mp3\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\SystemFileAssociations\\.wav\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\SystemFileAssociations\\.flac\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.mp3\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.wav\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.flac\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.ogg\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.m4a\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.wma\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.opus\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.aac\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.ape\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\.mka\\shell\\{MENU_KEY}",
        f"SOFTWARE\\Classes\\SystemFileAssociations\\audio\\shell\\DudiverTest",
    ]
    for p in old_paths:
        del_key(hkcu, p)

    # ── 2. Menu contextual para archivos de audio ─────────────────────
    # SystemFileAssociations\audio\shell\ cubre todos los formatos de audio
    # igual que hacen Play y Enqueue del sistema operativo
    say("[2/3] Registrando menu contextual (archivos de audio)...")
    base = f"SOFTWARE\\Classes\\SystemFileAssociations\\audio\\shell\\{MENU_KEY}"
    del_key(hkcu, base)
    reg_set(hkcu, base, {"MUIVerb": APP_NAME, "SubCommands": "", "Icon": ico_str})

    for idx, (key, label) in enumerate(FORMATS_FILE):
        sub = f"{base}\\shell\\{idx:02d}_{key}"
        reg_set(hkcu, sub, {"MUIVerb": label})
        reg_set(hkcu, sub + "\\command", {"": f'"{exe_path}" "%1" --format {key}'})
    say("      OK")

    # ── 3. Menu contextual para carpetas ──────────────────────────────
    say("[3/3] Registrando menu contextual (carpetas)...")
    for dir_type in ("Directory", "Directory\\Background"):
        dbase = f"SOFTWARE\\Classes\\{dir_type}\\shell\\{MENU_KEY}"
        del_key(hkcu, dbase)
        reg_set(hkcu, dbase, {"MUIVerb": APP_NAME, "SubCommands": "", "Icon": ico_str})
        arg = "%V" if dir_type == "Directory\\Background" else "%1"
        for idx, (key, label) in enumerate(FORMATS_FOLDER):
            sub = f"{dbase}\\shell\\{idx:02d}_{key}"
            reg_set(hkcu, sub, {"MUIVerb": label})
            reg_set(hkcu, sub + "\\command", {"": f'"{exe_path}" "{arg}" --batch --format {key}'})
    say("      OK")

    # ── Acceso directo Menu Inicio ────────────────────────────────────
    try:
        start_menu = (Path(os.environ["APPDATA"])
                      / "Microsoft/Windows/Start Menu/Programs"
                      / f"{APP_NAME}.lnk")
        ps = (f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{start_menu}");'
              f'$s.TargetPath="{exe_path}";$s.Description="{APP_NAME}";$s.Save()')
        subprocess.run(["powershell","-WindowStyle","Hidden","-Command",ps], capture_output=True)
    except Exception:
        pass

    # ── Reiniciar Explorer ────────────────────────────────────────────
    subprocess.run(["taskkill","/f","/im","explorer.exe"], capture_output=True)
    time.sleep(1.2)
    subprocess.Popen(["explorer.exe"])

    say("")
    say("============================================")
    say(f"  {APP_NAME}")
    say("  Instalado correctamente!")
    say("============================================")
    say(f"\n  Instalado en: {INSTALL_DIR}")
    say("\n  Archivos : click derecho -> Mostrar mas opciones")
    say(f"             -> '{APP_NAME}'")
    say("\n  Carpetas : click derecho -> Mostrar mas opciones")
    say(f"             -> '{APP_NAME}' -> formato")
    say("\nPresiona Enter para cerrar...")
    input()

if __name__ == "__main__":
    install()
