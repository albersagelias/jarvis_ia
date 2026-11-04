"""
voz.py
Entrada y salida de voz:
  - Voz:  texto a voz. Funciona en un hilo propio para no bloquear la interfaz.
          · macOS: usa el comando nativo "say" (muy fiable, voces en español del sistema).
          · Windows/Linux: usa pyttsx3 (offline).
  - Oido: voz a texto con SpeechRecognition (usa el servicio gratuito de Google,
          por lo que necesita conexión a internet).

Ambas clases degradan con elegancia: si falta una librería o el micrófono,
el asistente sigue funcionando en modo texto.
"""
import queue
import re
import subprocess
import threading

from config import IDIOMA_RECONOCIMIENTO, IDIOMA_VOZ_TTS, SISTEMA


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
        self._proceso = None                 # Proceso "say" en curso (solo macOS)
        self._candado = threading.Lock()
        self._hilo = threading.Thread(target=self._trabajador, name="voz-tts", daemon=True)
        self._hilo.start()

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
        with self._candado:                           # Cortar el "say" en curso (macOS)
            if self._proceso is not None and self._proceso.poll() is None:
                self._proceso.terminate()

    # ------------------------------------------------------------ hilo de voz
    def _trabajador(self):
        motor, voz_mac = None, None
        if SISTEMA == "Darwin":
            voz_mac = self._buscar_voz_mac()
        else:
            motor = self._crear_motor()   # pyttsx3 debe crearse en el mismo hilo que lo usa

        while True:
            texto, terminado = self._cola.get()
            try:
                if SISTEMA == "Darwin":
                    self._decir_mac(texto, voz_mac)
                elif motor is not None:
                    motor.say(texto)
                    motor.runAndWait()
            except Exception as e:
                print(f"[voz] Error al hablar: {e}")
            finally:
                terminado.set()               # Siempre liberamos a quien esté esperando

    # -------------------------------------------------------- Windows / Linux
    @staticmethod
    def _crear_motor():
        try:
            import pyttsx3
            motor = pyttsx3.init()
            motor.setProperty("rate", 175)    # Velocidad (palabras/min)
            for voz in motor.getProperty("voices"):
                ident = f"{voz.id} {voz.name} {getattr(voz, 'languages', '')}".lower()
                if IDIOMA_VOZ_TTS in ident or "spanish" in ident or "español" in ident:
                    motor.setProperty("voice", voz.id)
                    break
            return motor
        except Exception as e:
            print(f"[voz] pyttsx3 no disponible ({e}). Continuaré sin salida de voz.")
            return None

    # ------------------------------------------------------------------ macOS
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

    def _decir_mac(self, texto: str, voz_mac):
        orden = ["say"] + (["-v", voz_mac] if voz_mac else [])
        proceso = subprocess.Popen(orden, stdin=subprocess.PIPE)
        with self._candado:
            self._proceso = proceso
        proceso.communicate(texto.encode("utf-8"))   # Por stdin: evita problemas con "-" o comillas


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
            self.motivo_no_disponible = "Falta instalar SpeechRecognition."
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
                print("🎤 Escuchando...")
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
