#!/bin/bash
# instalar.sh - Instalador de Jarvis para macOS y Linux.
# Uso (desde la carpeta del proyecto):   bash instalar.sh
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
SO="$(uname -s)"
echo "=== Instalando Jarvis en: $DIR  ($SO) ==="

# --- 1. Buscar Python 3.9 o superior ---
PY=""
for c in python3.12 python3.11 python3.10 python3.13 python3.9 python3; do
  if command -v "$c" >/dev/null 2>&1 && \
     "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "X No encuentro Python 3.9 o superior."
  if [ "$SO" = "Darwin" ]; then
    echo "  Instalalo con:  brew install python@3.12   (o desde https://www.python.org/downloads/)"
  else
    echo "  Debian/Ubuntu:  sudo apt install python3 python3-venv python3-pip python3-tk"
    echo "  Fedora:         sudo dnf install python3 python3-tkinter"
    echo "  Arch:           sudo pacman -S python tk"
  fi
  exit 1
fi
VERSION="$($PY -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
echo "OK Python $VERSION  ($PY)"

# --- 2. Soporte de ventana (tkinter) ---
if ! "$PY" -c "import tkinter" 2>/dev/null; then
  echo "!  Tu Python no incluye tkinter (necesario para la ventana)."
  if [ "$SO" = "Darwin" ]; then
    echo "   Instalalo con:  brew install python-tk@$VERSION"
  else
    echo "   Debian/Ubuntu:  sudo apt install python3-tk     Fedora: sudo dnf install python3-tkinter"
  fi
  echo "   (Puedes seguir: el asistente tambien funciona por consola con 'python main.py')"
fi

# --- 3. Dependencias del sistema para voz ---
if [ "$SO" = "Darwin" ]; then
  if command -v brew >/dev/null 2>&1; then
    brew list portaudio >/dev/null 2>&1 || { echo "-> Instalando portaudio (microfono)..."; brew install portaudio; }
  else
    echo "!  Homebrew no esta instalado (https://brew.sh). Sin el, el microfono puede no instalarse."
  fi
else
  if ! command -v espeak-ng >/dev/null 2>&1 && ! command -v espeak >/dev/null 2>&1 && ! command -v spd-say >/dev/null 2>&1; then
    echo "!  Para que Jarvis HABLE necesitas un sintetizador:  sudo apt install espeak-ng"
  fi
  echo "   (Para el microfono en Linux:  sudo apt install portaudio19-dev python3-dev)"
fi

# --- 4. Entorno virtual ---
if [ ! -x "venv/bin/python" ]; then
  echo "-> Creando entorno virtual..."
  rm -rf venv
  if ! "$PY" -m venv venv; then
    echo "X No se pudo crear el entorno virtual."
    echo "  Debian/Ubuntu:  sudo apt install python3-venv"
    exit 1
  fi
fi

# --- 5. Dependencias de Python ---
echo "-> Instalando dependencias (puede tardar un par de minutos)..."
venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1
if ! venv/bin/python -m pip install -r requirements.txt; then
  echo "X Fallo al instalar las dependencias basicas. Revisa tu conexion a internet."
  exit 1
fi
echo "-> Instalando componentes de voz (opcional)..."
if ! venv/bin/python -m pip install -r requirements-voz.txt; then
  echo "!  Algun componente de voz no se pudo instalar (normalmente PyAudio)."
  echo "   Jarvis funcionara igualmente por texto. Mira el README, seccion 'Problemas'."
fi

# --- 6. Archivo de configuracion ---
if [ ! -f .env ]; then
  cp .env.example .env
  echo "OK Creado .env  (editalo para poner tu clave de API o elegir Ollama)"
fi

# --- 7. Lanzador de escritorio ---
LANZADOR=""
[ "$SO" = "Darwin" ] && LANZADOR="crear_app_mac.sh"
[ "$SO" = "Linux" ]  && LANZADOR="crear_lanzador_linux.sh"
if [ -n "$LANZADOR" ]; then
  read -r -p "¿Crear un icono para abrir Jarvis con doble clic? [S/n] " R || R="S"
  case "$R" in n|N) ;; *) bash "$LANZADOR" ;; esac
fi

echo
echo "=== Instalacion terminada ==="
echo "Probar la voz:     venv/bin/python probar_voz.py"
echo "Abrir la ventana:  venv/bin/python interfaz.py"
echo "Configurar la IA:  edita el archivo .env (ver README)"
