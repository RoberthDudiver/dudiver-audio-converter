<p align="center">
  <img src="icon.png" width="120" alt="Dudiver Music Audio Converter">
</p>

<h1 align="center">Dudiver Music Audio Converter</h1>

<p align="center">
  <strong>Right-click any audio file → convert to any format, silently, in seconds.</strong><br>
  <em>Click derecho en cualquier audio → convierte al formato que quieras, sin abrir nada.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-e94560?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4?style=for-the-badge" alt="Windows">
  <img src="https://img.shields.io/badge/powered%20by-FFmpeg-007808?style=for-the-badge" alt="FFmpeg">
  <img src="https://img.shields.io/badge/license-Free%20%E2%80%A2%20No%20Resale-ffd460?style=for-the-badge" alt="License">
</p>

<p align="center">
  <a href="../../releases"><strong>⬇ Download Installer</strong></a> ·
  <a href="#english"><strong>English</strong></a> ·
  <a href="#español"><strong>Español</strong></a> ·
  <a href="#about--acerca-de"><strong>About</strong></a>
</p>

---

## English

### What is it?

**Dudiver Music Audio Converter** is a free Windows tool that adds a context menu entry to every audio file. Right-click any MP3, WAV, FLAC, OGG, or other audio file — choose the target format from the submenu — and the conversion happens silently in the background. A notification pops up when it's done.

No windows to open. No dragging files. Just right-click → convert.

### Supported Formats

| Format | Quality | Use case |
|--------|---------|----------|
| **FLAC** | Lossless | Archiving, mastering |
| **WAV 24-bit** | Lossless | Studio work, DAW import |
| **WAV 16-bit** | CD quality | CD burning, compatibility |
| **AIFF** | Lossless | Apple / Pro Tools |
| **MP3 320k** | Near-lossless | Streaming, sharing |
| **MP3 VBR V0** | Near-lossless | Optimal size/quality |
| **AAC / M4A 256k** | High quality | Apple devices, YouTube |
| **OGG Vorbis** | High quality | Games, web |
| **OPUS 256k** | High quality | Podcasts, voice calls |
| **WMA 320k** | High quality | Windows Media |

### How to Use

#### Convert a single file

1. **Download** the installer from [Releases](../../releases) and run it.
2. **Right-click** any audio file (MP3, WAV, FLAC, OGG, M4A, AIFF, WMA, OPUS, AAC, APE, MKA).
3. On **Windows 11** → click **"Show more options"** first (or press `Shift + F10`).
4. **Hover** over **"Dudiver Music Audio Converter"**.
5. **Select** the target format from the submenu.
6. A balloon notification appears: **"Converting…"** then **"Done ✅"**.
7. The converted file appears in the **same folder**, auto-numbered if the name already exists (`song.flac`, `song 1.flac`, `song 2.flac`…).

#### Convert an entire folder (batch mode)

1. **Right-click** any folder that contains audio files.
2. On **Windows 11** → click **"Show more options"**.
3. **Hover** over **"Dudiver Music Audio Converter"**.
4. **Select** the target format.
5. A window opens showing all audio files found. Click **Start**.
6. Output is saved to a new sibling folder named **`Folder Name [FORMAT]`** (e.g. `Albums [FLAC]`).
   If that folder already exists, it's auto-numbered: `Albums [FLAC] 1`, `Albums [FLAC] 2`…

### Installation

**Option A — Installer (recommended)**

Download `DudiverMusicAudioConverter_Setup.exe` from [Releases](../../releases) and run it. No admin required. The context menu is registered automatically.

**Option B — PowerShell (no admin needed)**

```powershell
# From the project folder, run:
powershell -ExecutionPolicy Bypass -File install_user.ps1
```

### Uninstall

Use **Control Panel → Programs → Uninstall a program** and select **Dudiver Music Audio Converter**.

Or via PowerShell (manual install only):

```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

### Build from Source

Requirements: Python 3.10+, FFmpeg in PATH.

```bash
pip install customtkinter pyinstaller
build.bat
```

Output: `dist\DudiverConverter.exe` + `dist\ffmpeg.exe`

---

## Español

### ¿Qué es?

**Dudiver Music Audio Converter** es una herramienta gratuita para Windows que agrega una opción al menú contextual de cualquier archivo de audio. Haz click derecho en un MP3, WAV, FLAC u otro formato — elige el formato destino en el submenú — y la conversión se realiza en segundo plano sin abrir ninguna ventana. Cuando termina, aparece una notificación.

Sin abrir programas. Sin arrastrar archivos. Solo click derecho → convertir.

### Formatos Soportados

| Formato | Calidad | Uso |
|---------|---------|-----|
| **FLAC** | Sin pérdida | Archivo, masterización |
| **WAV 24-bit** | Sin pérdida | Estudio, DAW |
| **WAV 16-bit** | Calidad CD | Grabación, compatibilidad |
| **AIFF** | Sin pérdida | Apple / Pro Tools |
| **MP3 320k** | Casi sin pérdida | Streaming, compartir |
| **MP3 VBR V0** | Casi sin pérdida | Tamaño/calidad óptimo |
| **AAC / M4A 256k** | Alta calidad | Apple, YouTube |
| **OGG Vorbis** | Alta calidad | Juegos, web |
| **OPUS 256k** | Alta calidad | Podcasts, llamadas |
| **WMA 320k** | Alta calidad | Windows Media |

### Cómo Usar

#### Convertir un archivo

1. **Descarga** el instalador desde [Releases](../../releases) y ejecútalo.
2. **Click derecho** en cualquier archivo de audio (MP3, WAV, FLAC, OGG, M4A, AIFF, WMA, OPUS, AAC, APE, MKA).
3. En **Windows 11** → haz click en **"Mostrar más opciones"** (o presiona `Shift + F10`).
4. **Pasa el cursor** sobre **"Dudiver Music Audio Converter"**.
5. **Elige** el formato de destino en el submenú.
6. Aparece una notificación: **"Convirtiendo…"** y luego **"Listo ✅"**.
7. El archivo convertido aparece en la **misma carpeta**, con numeración automática si el nombre ya existe (`cancion.flac`, `cancion 1.flac`, `cancion 2.flac`…).

#### Convertir una carpeta entera (modo lote)

1. **Click derecho** en una carpeta que contenga archivos de audio.
2. En **Windows 11** → haz click en **"Mostrar más opciones"**.
3. **Pasa el cursor** sobre **"Dudiver Music Audio Converter"**.
4. **Elige** el formato de destino.
5. Se abre una ventana con todos los archivos encontrados. Haz click en **Iniciar**.
6. El resultado se guarda en una carpeta nueva junto a la original llamada **`Nombre [FORMATO]`** (ej: `Álbumes [FLAC]`).
   Si esa carpeta ya existe, se numera automáticamente: `Álbumes [FLAC] 1`, `Álbumes [FLAC] 2`…

### Instalación

**Opción A — Instalador (recomendado)**

Descarga `DudiverMusicAudioConverter_Setup.exe` desde [Releases](../../releases) y ejecútalo. No requiere administrador. El menú contextual se registra automáticamente.

**Opción B — PowerShell (sin admin)**

```powershell
powershell -ExecutionPolicy Bypass -File install_user.ps1
```

### Desinstalar

Usa **Panel de Control → Programas → Desinstalar un programa** y selecciona **Dudiver Music Audio Converter**.

O vía PowerShell (solo instalación manual):

```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

---

## License / Licencia

**Free for personal and professional use. Cannot be sold or redistributed for profit.**

**Gratis para uso personal y profesional. No puede ser vendido ni redistribuido con fines de lucro.**

> You are free to:
> - Use this software for any personal or professional purpose
> - Modify it for your own use
> - Share it with others at no charge
>
> You may not:
> - Sell this software or include it in a paid product
> - Charge others for access to it
> - Remove the author's credits

> Puedes:
> - Usar este software para cualquier propósito personal o profesional
> - Modificarlo para tu propio uso
> - Compartirlo con otros de forma gratuita
>
> No puedes:
> - Vender este software ni incluirlo en un producto de pago
> - Cobrar a otros por acceso a él
> - Eliminar los créditos del autor

---

## About / Acerca de

<p align="center">
  <img src="icon.png" width="80" alt="Dudiver">
</p>

<p align="center">
  Made with code and beats by <strong><a href="https://github.com/RoberthDudiver">Roberth Dudiver</a></strong> from Venezuela 🇻🇪
</p>

<p align="center">
  <a href="https://instagram.com/dudivermusic"><img src="https://img.shields.io/badge/Instagram-@dudivermusic-E4405F?style=flat-square&logo=instagram&logoColor=white" alt="Instagram"></a>
  <a href="https://tiktok.com/@dudivermusic"><img src="https://img.shields.io/badge/TikTok-@dudivermusic-000000?style=flat-square&logo=tiktok&logoColor=white" alt="TikTok"></a>
  <a href="https://youtube.com/@Dudiver"><img src="https://img.shields.io/badge/YouTube-@Dudiver-FF0000?style=flat-square&logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://open.spotify.com/artist/dudiver"><img src="https://img.shields.io/badge/Spotify-Dudiver-1DB954?style=flat-square&logo=spotify&logoColor=white" alt="Spotify"></a>
</p>

<p align="center">
  <em>If this saved you time, drop a ⭐ — it helps others find it.</em><br>
  <em>Si te ahorró tiempo, deja una ⭐ — ayuda a que otros lo encuentren.</em>
</p>
