"""
gestor_sistema.py
Control del sistema operativo: abrir aplicaciones, abrir sitios web,
buscar en internet y consultar hora, fecha y estado del equipo.

Funciona en Windows, macOS y (básicamente) Linux.
"""
import re
import shutil
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

from config import SISTEMA

try:
    import psutil
except ImportError:  # psutil es opcional: sin él solo falla el "estado del sistema"
    psutil = None


# ---------------------------------------------------------------------------
# CATÁLOGO DE APLICACIONES
# Para cada app: alias que el usuario puede decir + qué ejecutar en cada SO.
# Cada SO tiene una lista de candidatos: se prueba en orden hasta que uno funcione.
#   - Windows: nombre de ejecutable (en el PATH) o URI (termina en ":", ej. "spotify:")
#   - macOS:   nombre de la aplicación tal como aparece en /Applications
#   - Linux:   comando ejecutable
# ¡Añade aquí tus propias aplicaciones!
# ---------------------------------------------------------------------------
APPS = {
    "bloc de notas": {
        "alias": ["bloc de notas", "notepad", "notas", "editor de texto", "textedit"],
        "Windows": ["notepad"],
        "Darwin": ["TextEdit"],
        "Linux": ["gedit", "kate", "mousepad", "nano"],
    },
    "calculadora": {
        "alias": ["calculadora", "calc", "calculator"],
        "Windows": ["calc"],
        "Darwin": ["Calculator"],
        "Linux": ["gnome-calculator", "kcalc", "galculator"],
    },
    "terminal": {
        "alias": ["terminal", "consola", "cmd", "powershell", "linea de comandos", "shell"],
        "Windows": ["wt", "powershell", "cmd"],
        "Darwin": ["Terminal"],
        "Linux": ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"],
    },
    "visual studio code": {
        "alias": ["vs code", "vscode", "visual studio code", "visual studio", "code"],
        "Windows": ["code"],
        "Darwin": ["Visual Studio Code"],
        "Linux": ["code"],
    },
    "spotify": {
        "alias": ["spotify", "musica"],
        "Windows": ["spotify:"],
        "Darwin": ["Spotify"],
        "Linux": ["spotify"],
    },
    "explorador de archivos": {
        "alias": ["explorador", "explorador de archivos", "archivos", "finder", "carpetas"],
        "Windows": ["explorer"],
        "Darwin": ["Finder"],
        "Linux": ["nautilus", "dolphin", "thunar", "xdg-open ."],
    },
    "configuracion": {
        "alias": ["configuracion", "ajustes", "preferencias"],
        "Windows": ["ms-settings:"],
        "Darwin": ["System Settings", "System Preferences"],
        "Linux": ["gnome-control-center", "systemsettings"],
    },
    "discord": {
        "alias": ["discord"],
        "Windows": ["discord"],
        "Darwin": ["Discord"],
        "Linux": ["discord"],
    },
}

# El navegador se trata aparte: usamos el navegador PREDETERMINADO del usuario.
ALIAS_NAVEGADOR = ["navegador", "browser", "chrome", "firefox", "edge", "safari", "internet"]

# Sitios web conocidos que se pueden abrir por nombre ("abre youtube").
SITIOS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "correo": "https://mail.google.com",
    "github": "https://github.com",
    "claude": "https://claude.ai",
    "wikipedia": "https://es.wikipedia.org",
    "maps": "https://maps.google.com",
    "mapas": "https://maps.google.com",
    "netflix": "https://www.netflix.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "twitter": "https://x.com",
    "reddit": "https://www.reddit.com",
    "drive": "https://drive.google.com",
    "calendario": "https://calendar.google.com",
}

# Motores de búsqueda disponibles
MOTORES = {
    "google": "https://www.google.com/search?q={}",
    "youtube": "https://www.youtube.com/results?search_query={}",
    "wikipedia": "https://es.wikipedia.org/w/index.php?search={}",
    "maps": "https://www.google.com/maps/search/{}",
}

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


class GestorSistema:
    """Agrupa todas las acciones de control del ordenador."""

    # ------------------------------------------------------------------ APPS
    def abrir_aplicacion(self, nombre: str):
        """
        Intenta abrir una aplicación por su nombre/alias.
        Devuelve (encontrada: bool, mensaje: str).
        'encontrada' = False significa que el nombre no es una app conocida
        (para que el llamador pueda probar con un sitio web).
        """
        nombre = nombre.strip().lower()

        # 1) Navegador predeterminado
        if nombre in ALIAS_NAVEGADOR:
            webbrowser.open_new_tab("https://www.google.com")
            return True, "Abriendo el navegador."

        # 2) Aplicaciones del catálogo
        for titulo, datos in APPS.items():
            if nombre in datos["alias"] or nombre == titulo:
                for candidato in datos.get(SISTEMA, []):
                    if self._lanzar(candidato):
                        return True, f"Abriendo {titulo}."
                return True, f"No he podido abrir {titulo}. ¿Está instalada?"

        return False, ""

    def _lanzar(self, candidato: str) -> bool:
        """Lanza un candidato según el sistema operativo. Devuelve True si funcionó."""
        try:
            if SISTEMA == "Windows":
                if candidato.endswith(":"):                      # URI (spotify:, ms-settings:)
                    import os
                    os.startfile(candidato)                      # type: ignore[attr-defined]
                    return True
                ruta = shutil.which(candidato)
                if not ruta:
                    return False
                # "start" abre apps de consola en una ventana nueva
                subprocess.Popen(["cmd", "/c", "start", "", ruta])
                return True

            if SISTEMA == "Darwin":
                res = subprocess.run(["open", "-a", candidato],
                                     capture_output=True, text=True)
                return res.returncode == 0

            # Linux / otros
            partes = candidato.split()
            if not shutil.which(partes[0]):
                return False
            subprocess.Popen(partes, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------- WEB
    def abrir_sitio(self, texto: str):
        """
        Abre un sitio por nombre conocido ('youtube') o dominio ('wikipedia.org').
        Devuelve (encontrado: bool, mensaje: str).
        """
        texto = texto.strip().lower()
        if texto in SITIOS:
            webbrowser.open_new_tab(SITIOS[texto])
            return True, f"Abriendo {texto}."

        # ¿Parece un dominio o una URL?  ej: "openai.com", "https://x.com/foo"
        if re.match(r"^(https?://)?[\w-]+(\.[\w-]+)+(/\S*)?$", texto):
            url = texto if texto.startswith("http") else f"https://{texto}"
            webbrowser.open_new_tab(url)
            return True, f"Abriendo {texto}."

        return False, ""

    def buscar_web(self, consulta: str, motor: str = "google") -> str:
        """Abre una búsqueda en una nueva pestaña del navegador predeterminado."""
        plantilla = MOTORES.get(motor, MOTORES["google"])
        webbrowser.open_new_tab(plantilla.format(quote_plus(consulta)))
        return f"Buscando «{consulta}» en {motor}."

    # ------------------------------------------------------- HORA Y FECHA
    @staticmethod
    def hora() -> str:
        ahora = datetime.now()
        return f"Son las {ahora.hour:02d}:{ahora.minute:02d}."

    @staticmethod
    def fecha() -> str:
        hoy = datetime.now()
        return (f"Hoy es {DIAS[hoy.weekday()]}, {hoy.day} de "
                f"{MESES[hoy.month - 1]} de {hoy.year}.")

    # ------------------------------------------------------ ESTADO SISTEMA
    @staticmethod
    def estado_sistema() -> str:
        if psutil is None:
            return "Necesito la librería psutil para informar del estado del sistema."
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage("/" if SISTEMA != "Windows" else "C:\\")
            partes = [
                f"CPU al {cpu:.0f}%",
                f"memoria al {ram.percent:.0f}% ({ram.used / 1e9:.1f} de {ram.total / 1e9:.1f} GB)",
                f"disco al {disco.percent:.0f}% ({disco.free / 1e9:.0f} GB libres)",
            ]
            bateria = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
            if bateria is not None:
                enchufado = "cargando" if bateria.power_plugged else "con batería"
                partes.append(f"batería al {bateria.percent:.0f}% ({enchufado})")
            return "Estado del sistema: " + ", ".join(partes) + "."
        except Exception as e:
            return f"No he podido leer el estado del sistema: {e}"
