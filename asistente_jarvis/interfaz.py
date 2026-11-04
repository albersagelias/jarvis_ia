"""
interfaz.py
Interfaz gráfica del asistente (CustomTkinter). Reutiliza toda la lógica de main.py.

Ejecutar:   python3 interfaz.py

Cómo está organizado (para que la ventana nunca se congele):
  - El hilo principal SOLO dibuja la ventana.
  - Un hilo "trabajador" procesa los comandos uno a uno (y habla la respuesta).
  - Los hilos del micrófono dejan el texto reconocido en una cola.
  - Los hilos comunican cambios a la ventana mediante `cola_ui`, que la ventana
    revisa cada 100 ms (tkinter no es seguro si se toca desde otros hilos).
"""
import queue
import sys
import threading
import time

try:
    import customtkinter as ctk
except ImportError:
    sys.exit("Falta customtkinter. Instálalo con:  pip install customtkinter\n"
             "(En macOS con Python de Homebrew quizá también:  brew install python-tk)")

import config
from main import Asistente

# Botones de acción rápida: (texto del botón, comando que se envía al asistente)
ACCIONES_RAPIDAS = [
    ("🕐 Hora", "qué hora es"),
    ("📅 Fecha", "qué día es hoy"),
    ("💻 Sistema", "estado del sistema"),
    ("🌐 Web", "abre el navegador"),
    ("🎵 Spotify", "abre spotify"),
    ("📝 Notas", "abre el bloc de notas"),
    ("⌨️ Code", "abre vs code"),
    ("❓ Ayuda", "ayuda"),
]

COLOR_USUARIO = "#3b82f6"
COLOR_ASISTENTE = "#10b981"
COLOR_SISTEMA = "#9ca3af"
COLORES_ESTADO = {"Listo": "#22c55e", "Pensando...": "#f59e0b",
                  "Hablando...": "#3b82f6", "Escuchando...": "#ef4444"}


class VentanaAsistente(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")        # "dark" / "light" / "system"
        ctk.set_default_color_theme("blue")
        self.title(f"{config.NOMBRE} · Asistente personal")
        self.geometry("840x700")
        self.minsize(680, 540)

        # --- Lógica (la misma que usa la versión de consola) ---
        self.asistente = Asistente(modo_voz=False, con_sonido=True)

        # --- Comunicación entre hilos ---
        self.cola_ui = queue.Queue()        # hilos -> ventana
        self.cola_entrada = queue.Queue()   # textos pendientes de procesar
        self.ocupado = threading.Event()    # activo mientras procesa o habla
        self.continuo = threading.Event()   # activo mientras la escucha continua está encendida
        self._candado_mic = threading.Lock()  # solo una escucha de micrófono a la vez
        self.cerrando = False

        self._construir_interfaz()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        threading.Thread(target=self._trabajador, name="trabajador", daemon=True).start()
        self.after(100, self._revisar_cola_ui)
        self._mensaje_inicial()

    # ====================================================== CONSTRUCCIÓN
    def _construir_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---- Cabecera: título, estado y ajustes ----
        cab = ctk.CTkFrame(self, corner_radius=0)
        cab.grid(row=0, column=0, sticky="ew")
        cab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cab, text=f"🤖 {config.NOMBRE}",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, padx=16, pady=12)

        self.lbl_estado = ctk.CTkLabel(cab, text="● Listo", text_color=COLORES_ESTADO["Listo"])
        self.lbl_estado.grid(row=0, column=1, sticky="w")

        self.sw_voz = ctk.CTkSwitch(cab, text="Voz", command=self._cambiar_voz)
        self.sw_voz.grid(row=0, column=2, padx=8)
        self.sw_voz.select()

        self.sw_mic = ctk.CTkSwitch(cab, text="Escucha continua", command=self._cambiar_continuo)
        self.sw_mic.grid(row=0, column=3, padx=8)

        ctk.CTkButton(cab, text="🧹", width=36, command=self._limpiar,
                      fg_color="transparent", border_width=1,
                      text_color=("gray10", "gray90")).grid(row=0, column=4, padx=(8, 16))

        # ---- Zona de chat ----
        self.chat = ctk.CTkTextbox(self, wrap="word", state="disabled",
                                   font=ctk.CTkFont(size=15))
        self.chat.grid(row=1, column=0, sticky="nsew", padx=12, pady=(10, 4))
        self.chat.tag_config("n_usuario", foreground=COLOR_USUARIO)
        self.chat.tag_config("n_asistente", foreground=COLOR_ASISTENTE)
        self.chat.tag_config("t_sistema", foreground=COLOR_SISTEMA)

        # ---- Acciones rápidas ----
        rapidas = ctk.CTkFrame(self, fg_color="transparent")
        rapidas.grid(row=2, column=0, sticky="ew", padx=12, pady=4)
        for i, (etiqueta, comando) in enumerate(ACCIONES_RAPIDAS):
            rapidas.grid_columnconfigure(i, weight=1, uniform="rapidas")
            ctk.CTkButton(rapidas, text=etiqueta, height=30, font=ctk.CTkFont(size=12),
                          command=lambda c=comando: self._encolar(c)).grid(
                row=0, column=i, padx=2, sticky="ew")

        # ---- Entrada de texto + micrófono ----
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 12))
        barra.grid_columnconfigure(0, weight=1)

        self.entrada = ctk.CTkEntry(barra, height=42, font=ctk.CTkFont(size=15),
                                    placeholder_text="Escribe un comando o una pregunta…")
        self.entrada.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entrada.bind("<Return>", self._enviar_texto)
        self.entrada.focus()

        self.btn_mic = ctk.CTkButton(barra, text="🎤", width=48, height=42,
                                     command=self._escuchar_una_vez)
        self.btn_mic.grid(row=0, column=1, padx=3)

        ctk.CTkButton(barra, text="Enviar", width=80, height=42,
                      command=self._enviar_texto).grid(row=0, column=2, padx=(3, 0))

        # Si no hay micrófono, desactivamos los controles de voz de entrada
        if not self.asistente.oido.disponible:
            self.btn_mic.configure(state="disabled")
            self.sw_mic.configure(state="disabled")

    def _mensaje_inicial(self):
        saludo = f"Hola, soy {config.NOMBRE}. ¿En qué puedo ayudarte? Escribe «ayuda» para ver mis comandos."
        self._escribir("asistente", saludo)
        self.asistente.voz.hablar(saludo, esperar=False)
        if not self.asistente.ia.disponible:
            self._escribir("sistema", f"IA desactivada: {self.asistente.ia.error_inicio}")
        if not self.asistente.oido.disponible:
            self._escribir("sistema",
                           f"Micrófono desactivado: {self.asistente.oido.motivo_no_disponible}")

    # ============================================================ CHAT
    def _escribir(self, quien: str, texto: str):
        self.chat.configure(state="normal")
        if quien == "usuario":
            self.chat.insert("end", "Tú\n", "n_usuario")
            self.chat.insert("end", texto + "\n\n")
        elif quien == "asistente":
            self.chat.insert("end", f"{config.NOMBRE}\n", "n_asistente")
            self.chat.insert("end", texto + "\n\n")
        else:
            self.chat.insert("end", texto + "\n\n", "t_sistema")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _poner_estado(self, texto):
        texto = texto or "Listo"
        self.lbl_estado.configure(text=f"● {texto}",
                                  text_color=COLORES_ESTADO.get(texto, COLORES_ESTADO["Listo"]))

    def _limpiar(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.asistente.ia.reiniciar()
        self._escribir("sistema", "Conversación reiniciada.")

    # ===================================================== ENTRADA DE TEXTO
    def _enviar_texto(self, evento=None):
        texto = self.entrada.get().strip()
        if texto:
            self.entrada.delete(0, "end")
            self._encolar(texto)

    def _encolar(self, texto: str):
        """Muestra el mensaje del usuario y lo manda al hilo trabajador."""
        self._escribir("usuario", texto)
        self.cola_entrada.put(texto)

    # ======================================================= HILO TRABAJADOR
    def _trabajador(self):
        """Procesa los comandos de uno en uno y dice la respuesta en voz alta."""
        while True:
            texto = self.cola_entrada.get()
            if texto is None:                      # Señal de cierre
                break
            self.ocupado.set()
            try:
                self.cola_ui.put(("estado", "Pensando..."))
                respuesta = self.asistente.procesar(texto)
                self.cola_ui.put(("asistente", respuesta))
                self.cola_ui.put(("sincronizar", None))
                if self.asistente.voz.activa:
                    self.cola_ui.put(("estado", "Hablando..."))
                    self.asistente.voz.hablar(respuesta, esperar=True)
            except Exception as e:
                self.cola_ui.put(("sistema", f"Error inesperado: {e}"))
            finally:
                self.ocupado.clear()
                self.cola_ui.put(("estado", None))
                if not self.asistente.en_marcha:   # El usuario dijo "salir"
                    self.cola_ui.put(("salir", None))

    # =============================================================== MICRÓFONO
    def _escuchar_una_vez(self):
        """Botón 🎤: escucha una sola frase (pulsar para hablar)."""
        threading.Thread(target=self._tarea_escuchar, args=(True,), daemon=True).start()

    def _tarea_escuchar(self, avisar: bool):
        if not self._candado_mic.acquire(blocking=False):
            return                                  # Ya se está escuchando
        try:
            self.cola_ui.put(("estado", "Escuchando..."))
            texto = self.asistente.oido.escuchar()
            if texto:
                self.cola_ui.put(("usuario", texto))
                self.cola_entrada.put(texto)
            else:
                if avisar:
                    self.cola_ui.put(("sistema", "No te he entendido. Inténtalo de nuevo."))
                if not self.ocupado.is_set():
                    self.cola_ui.put(("estado", None))
        finally:
            self._candado_mic.release()

    def _bucle_continuo(self):
        """Escucha una frase tras otra, esperando a que el asistente termine de hablar."""
        while self.continuo.is_set() and not self.cerrando:
            if self.ocupado.is_set() or not self.cola_entrada.empty():
                time.sleep(0.3)
                continue
            self._tarea_escuchar(avisar=False)

    def _activar_continuo(self):
        if self.continuo.is_set():
            return
        self.continuo.set()
        self.asistente.modo_voz = True
        threading.Thread(target=self._bucle_continuo, daemon=True).start()

    def _desactivar_continuo(self):
        self.continuo.clear()
        self.asistente.modo_voz = False

    # ============================================================== AJUSTES
    def _cambiar_voz(self):
        self.asistente.voz.activa = bool(self.sw_voz.get())
        if not self.asistente.voz.activa:
            self.asistente.voz.detener()

    def _cambiar_continuo(self):
        if self.sw_mic.get():
            self._activar_continuo()
        else:
            self._desactivar_continuo()

    def _sincronizar_controles(self):
        """Ajusta los interruptores si un comando de voz/texto cambió el modo ('modo voz', 'silencio'...)."""
        if self.asistente.voz.activa:
            self.sw_voz.select()
        else:
            self.sw_voz.deselect()
        if self.asistente.modo_voz and not self.continuo.is_set():
            self.sw_mic.select()
            self._activar_continuo()
        elif not self.asistente.modo_voz and self.continuo.is_set():
            self.sw_mic.deselect()
            self._desactivar_continuo()

    # ===================================================== COLA HILOS -> VENTANA
    def _revisar_cola_ui(self):
        try:
            while True:
                tipo, dato = self.cola_ui.get_nowait()
                if tipo in ("usuario", "asistente", "sistema"):
                    self._escribir(tipo, dato)
                elif tipo == "estado":
                    self._poner_estado(dato)
                elif tipo == "sincronizar":
                    self._sincronizar_controles()
                elif tipo == "salir":
                    self._cerrar()
                    return
        except queue.Empty:
            pass
        if not self.cerrando:
            self.after(100, self._revisar_cola_ui)

    def _cerrar(self):
        self.cerrando = True
        self.continuo.clear()
        self.asistente.voz.detener()
        self.cola_entrada.put(None)
        self.destroy()


def main():
    VentanaAsistente().mainloop()


if __name__ == "__main__":
    main()
