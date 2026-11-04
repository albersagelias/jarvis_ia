#!/bin/bash
# crear_lanzador_linux.sh
# Crea un icono de "Jarvis" en el menu de aplicaciones (y en el Escritorio).
# Ejecutalo UNA vez:   bash crear_lanzador_linux.sh
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$DIR/venv/bin/python3"

if [ ! -x "$PYTHON" ]; then
  echo "X No encuentro el entorno virtual en $DIR/venv. Ejecuta antes:  bash instalar.sh"
  exit 1
fi

# Script que arranca la interfaz (y guarda los errores en jarvis.log)
cat > "$DIR/jarvis.sh" << LANZ
#!/bin/bash
cd "$DIR"
exec "$PYTHON" interfaz.py >> "$DIR/jarvis.log" 2>&1
LANZ
chmod +x "$DIR/jarvis.sh"

APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
ENTRADA="$APPS/jarvis.desktop"
cat > "$ENTRADA" << DESK
[Desktop Entry]
Type=Application
Name=Jarvis
Comment=Asistente personal de voz y texto
Exec="$DIR/jarvis.sh"
Path=$DIR
Terminal=false
Categories=Utility;
DESK
chmod +x "$ENTRADA"

# Copia en el Escritorio, si existe
ESCRITORIO="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
if [ -d "$ESCRITORIO" ]; then
  cp "$ENTRADA" "$ESCRITORIO/jarvis.desktop"
  chmod +x "$ESCRITORIO/jarvis.desktop"
  gio set "$ESCRITORIO/jarvis.desktop" metadata::trusted true 2>/dev/null || true
fi
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" 2>/dev/null || true

echo "OK Lanzador creado. Busca 'Jarvis' en el menu de aplicaciones"
[ -d "$ESCRITORIO" ] && echo "   y tambien en el Escritorio (en GNOME: clic derecho > 'Permitir lanzar')."
echo "   Si falla, mira el registro: $DIR/jarvis.log"
