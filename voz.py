"""
voz.py
Entrada y salida de voz.

SALIDA (clase Voz) - cada sistema usa su sintetizador nativo, que es lo más fiable:
  - Windows: PowerShell + System.Speech (voces SAPI de Windows, sin dependencias).
  - macOS:   comando "say".
  - Linux:   espeak-ng / espeak / spd-say (el que haya instalado).
  - Respaldo: pyttsx3, si el sintetizador nativo falla o no existe.
  Todo se ejecuta en un hilo propio, así la interfaz nunca se bloquea.

ENTRADA (clase Oido) - SpeechRecognition + micrófono (usa el servicio gratuito
de Google, por lo que necesita conexión a internet).

Ambas clases degradan con elegancia: si falta algo, el asistente sigue en modo texto.
"""
import base64
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading

from config import IDIOMA_RECONOCIMIENTO, IDIOMA_VOZ_TTS, SISTEMA

# Script de PowerShell que lee el texto de un archivo UTF-8 y lo dice en voz alta,
# eligiendo una voz en español si existe. Se pasa codificado (-EncodedCommand)
# para evitar cualquier problema de comillas o tildes.
_SCRIPT_WINDOWS = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$v = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -like 'es*' } | Select-Object -First 1
if ($v) { $s.SelectVoice($v.VoiceInfo.Name) }
$s.Volume = 100
$t = Get-Content -Raw -Encoding UTF8 -LiteralPath $env:JARVIS_TXT
$s.Speak($t)
"""
_SCRIPT_WINDOWS_B64 = base64.b64encode(_SCRIPT_WINDOWS.encode("utf-16-le")).decode("ascii")


def limpiar_para_voz(texto: str) -> str:
    """Quita símbolos de Markdown y viñetas que sonarían raro al leerlos en voz alta."""
    texto = re.sub(r"```.*?```", " (bloque de código omitido) ", texto, flags=re.S)
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)   # [texto](url) -> texto
    texto = re.sub(r"[*_`#>•«»]+", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


class Voz:
    """Síntesis de voz (texto a voz) con cola y hilo propio."""

    def __init__(self, activa: bool = True):
        self.activa = activa
        self._cola = queue.Queue()
        self._proceso = None                 # Proceso de voz en curso (para poder cortarlo)
        self._cortado = False
        self._candado = threading.Lock()
        self._avisos_mostrados = set()
        self._ruta = None                    # Ejecutable nativo elegido
        self._voz_mac = None
        self._motor = None                   # Motor pyttsx3 (solo respaldo)
        self._motor_intentado = False
        self._modo, self.backend, self.detalle = self._elegir_backend()
        threading.Thread(target=self._trabajador, name="voz-tts", daemon=True).start()

    # ------------------------------------------------------------ API pública
    def hablar(self, texto: str, esperar: bool = True):
        """
        Dice el texto en voz alta.
        esperar=True  -> no vuelve hasta terminar de hablar (modo consola).
        esperar=False -> vuelve al instante (modo interfaz gráfica).
        """
        if not self.activa:
            return
        texto = limpiar_para_voz(texto)
        if not texto:
            return
        terminado = threading.Event()
        self._cola.put((texto, terminado))
        if esperar:
            terminado.wait()

    def detener(self):
        """Corta lo que se esté diciendo y descarta lo pendiente."""
        while True:                                   # Vaciar la cola
            try:
                _, terminado = self._cola.get_nowait()
                terminado.set()
            except queue.Empty:
                break
        with self._candado:                           # Cortar el proceso en curso
            self._cortado = True
            if self._proceso is not None and self._proceso.poll() is None:
                self._proceso.terminate()

    # ------------------------------------------------------ elección de motor
    def _elegir_backend(self):
        """Devuelve (modo, nombre legible, detalle)."""
        if SISTEMA == "Darwin" and shutil.which("say"):
            self._voz_mac = self._buscar_voz_mac()
            return "mac", "say (macOS)", self._voz_mac or "voz predeterminada del sistema"
        if SISTEMA == "Windows":
            ps = shutil.which("powershell") or shutil.which("pwsh")
            if ps:
                self._ruta = ps
                return "windows", "PowerShell / System.Speech (Windows)", "voz en español si está instalada"
        if SISTEMA == "Linux":
            for exe in ("espeak-ng", "espeak", "spd-say"):
                ruta = shutil.which(exe)
                if ruta:
                    self._ruta = ruta
                    return "linux", f"{exe} (Linux)", "idioma: es"
        return "pyttsx3", "pyttsx3 (respaldo)", ""

    # -------------------------------------------------------------- hilo de voz
    def _trabajador(self):
        while True:
            texto, terminado = self._cola.get()
            try:
                hecho = False
                if self._modo != "pyttsx3":
                    ok, error = self._decir_nativo(texto)
                    if ok:
                        hecho = True
                    else:
                        self._avisar(f"El sintetizador nativo falló: {error or 'error desconocido'}. "
                                     "Probando pyttsx3 como respaldo.")
                if not hecho:
                    self._decir_pyttsx3(texto)
            except Exception as e:
                self._avisar(f"Error al hablar: {e}")
            finally:
                terminado.set()               # Siempre liberamos a quien esté esperando

    def _avisar(self, mensaje: str):
        """Muestra cada aviso de voz una sola vez (para no llenar la pantalla)."""
        if mensaje not in self._avisos_mostrados:
            self._avisos_mostrados.add(mensaje)
            print(f"[voz] {mensaje}")

    def _ejecutar(self, orden, entrada=None, env=None):
        """Lanza un proceso de voz y espera a que termine. Devuelve (ok, texto_de_error)."""
        opciones = {}
        if SISTEMA == "Windows":
            opciones["creationflags"] = 0x08000000        # CREATE_NO_WINDOW: sin ventana negra
        with self._candado:
            self._cortado = False
        proceso = subprocess.Popen(
            orden,
            stdin=subprocess.PIPE if entrada is not None else subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env, **opciones)
        with self._candado:
            self._proceso = proceso
        _, error = proceso.communicate(entrada)
        with self._candado:
            cortado = self._cortado
        return (proceso.returncode == 0 or cortado), (error or b"").decode("utf-8", "replace").strip()

    # ---------------------------------------------------------- motores nativos
    def _decir_nativo(self, texto: str):
        if self._modo == "windows":
            return self._decir_windows(texto)
        if self._modo == "mac":
            orden = ["say"] + (["-v", self._voz_mac] if self._voz_mac else [])
            return self._ejecutar(orden, entrada=texto.encode("utf-8"))   # Por stdin: evita problemas con "-"
        if self._modo == "linux":
            if os.path.basename(self._ruta).startswith("spd-say"):
                return self._ejecutar([self._ruta, "-w", "-l", "es", " " + texto])
            return self._ejecutar([self._ruta, "-v", "es", "--stdin"], entrada=texto.encode("utf-8"))
        return False, "modo desconocido"

    def _decir_windows(self, texto: str):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(texto)
            ruta_txt = f.name
        try:
            orden = [self._ruta, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                     "-EncodedCommand", _SCRIPT_WINDOWS_B64]
            return self._ejecutar(orden, env=dict(os.environ, JARVIS_TXT=ruta_txt))
        finally:
            try:
                os.remove(ruta_txt)
            except OSError:
                pass

    @staticmethod
    def _buscar_voz_mac():
        """Busca una voz en español instalada en macOS (prefiere es_ES)."""
        try:
            salida = subprocess.run(["say", "-v", "?"], capture_output=True,
                                    text=True, timeout=10).stdout
        except Exception:
            return None
        candidatas = []
        for linea in salida.splitlines():
            m = re.match(r"^(.+?)\s+([A-Za-z]{2}_[A-Za-z]{2})\s+#", linea)
            if m and m.group(2).lower().startswith("es_"):
                candidatas.append((m.group(1).strip(), m.group(2)))
        for nombre, loc in candidatas:
            if loc == "es_ES":
                return nombre
        return candidatas[0][0] if candidatas else None

    # ------------------------------------------------------------------ respaldo
    def _decir_pyttsx3(self, texto: str):
        if not self._motor_intentado:
            self._motor_intentado = True
            try:
                import pyttsx3
                self._motor = pyttsx3.init()       # Debe crearse en el mismo hilo que lo usa
                self._motor.setProperty("rate", 175)
                for voz in self._motor.getProperty("voices"):
                    ident = f"{voz.id} {voz.name} {getattr(voz, 'languages', '')}".lower()
                    if IDIOMA_VOZ_TTS in ident or "spanish" in ident or "español" in ident:
                        self._motor.setProperty("voice", voz.id)
                        break
            except Exception as e:
                self._avisar(f"No hay salida de voz disponible (pyttsx3: {e}). "
                             "Ejecuta 'python probar_voz.py' para diagnosticarlo.")
        if self._motor is not None:
            self._motor.say(texto)
            self._motor.runAndWait()


class Oido:
    """Reconocimiento de voz (voz a texto)."""

    def __init__(self):
        self.disponible = False
        self._sr = None
        self._reconocedor = None
        self.motivo_no_disponible = ""
        self._inicializar()

    def _inicializar(self):
        try:
            import speech_recognition as sr
        except ImportError:
            self.motivo_no_disponible = ("Falta instalar SpeechRecognition "
                                         "(pip install -r requirements-voz.txt).")
            return
        try:
            sr.Microphone()   # Lanza error si no hay PyAudio o no hay micrófono
        except Exception as e:
            self.motivo_no_disponible = (
                f"No puedo acceder al micrófono ({e}). "
                "¿Está instalado PyAudio y concedidos los permisos?"
            )
            return
        self._sr = sr
        self._reconocedor = sr.Recognizer()
        self._reconocedor.dynamic_energy_threshold = True
        self.disponible = True

    def escuchar(self):
        """
        Escucha una frase por el micrófono y la devuelve como texto.
        Devuelve None si no se oyó nada o no se entendió.
        """
        if not self.disponible:
            return None
        sr = self._sr
        try:
            with sr.Microphone() as fuente:
                self._reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
                print("Escuchando...")
                audio = self._reconocedor.listen(fuente, timeout=8, phrase_time_limit=15)
            return self._reconocedor.recognize_google(audio, language=IDIOMA_RECONOCIMIENTO)
        except sr.WaitTimeoutError:
            return None                      # Nadie habló
        except sr.UnknownValueError:
            return None                      # Se oyó algo ininteligible
        except sr.RequestError as e:
            print(f"[oído] Error del servicio de reconocimiento (¿sin internet?): {e}")
            return None
        except Exception as e:
            print(f"[oído] Error inesperado con el micrófono: {e}")
            return None
