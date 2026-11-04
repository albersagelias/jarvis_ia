#!/bin/bash
# crear_app_mac.sh
# Crea "Jarvis.app" en esta carpeta: una app de macOS que abre la interfaz con doble clic,
# sin ventana de Terminal. Ejecútalo UNA vez:   bash crear_app_mac.sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/Jarvis.app"
PYTHON="$DIR/venv/bin/python3"

if [ ! -x "$PYTHON" ]; then
  echo "❌ No encuentro el entorno virtual en: $DIR/venv"
  echo "   Primero crea el entorno e instala dependencias (ver README, paso 1)."
  exit 1
fi
if ! "$PYTHON" -c "import customtkinter" 2>/dev/null; then
  echo "❌ Falta customtkinter en el entorno virtual."
  echo "   Ejecuta:  source venv/bin/activate && pip install customtkinter"
  exit 1
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"

# --- Lanzador: arranca la interfaz con el Python del entorno virtual ---
cat > "$APP/Contents/MacOS/Jarvis" << LANZADOR
#!/bin/bash
cd "$DIR"
exec "$PYTHON" interfaz.py >> "$DIR/jarvis.log" 2>&1
LANZADOR
chmod +x "$APP/Contents/MacOS/Jarvis"

# --- Info.plist: identidad de la app y texto del permiso de micrófono ---
cat > "$APP/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Jarvis</string>
  <key>CFBundleDisplayName</key><string>Jarvis</string>
  <key>CFBundleIdentifier</key><string>local.asistente.jarvis</string>
  <key>CFBundleExecutable</key><string>Jarvis</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>NSMicrophoneUsageDescription</key>
  <string>Jarvis necesita el micrófono para entender tus comandos de voz.</string>
</dict>
</plist>
PLIST

command -v xattr >/dev/null 2>&1 && xattr -cr "$APP" || true

echo "✅ Creada: $APP"
echo "   Haz doble clic en Jarvis.app, o arrástrala al Dock / a la carpeta Aplicaciones."
echo "   Si algo falla, mira el registro en: $DIR/jarvis.log"
