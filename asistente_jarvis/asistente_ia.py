"""
asistente_ia.py
Cerebro conversacional del asistente. Responde preguntas generales cuando el
comando no es una acción directa sobre el sistema.

Proveedores soportados (se elige con PROVEEDOR_IA en el archivo .env):
  - "anthropic": API de Anthropic (Claude), en la nube.
  - "ollama":    modelo local servido por Ollama (https://ollama.com), sin internet.
"""
import json
import urllib.error
import urllib.request

import config


class CerebroIA:
    """Mantiene el historial de conversación y consulta al modelo elegido."""

    def __init__(self):
        self.proveedor = config.PROVEEDOR_IA
        self.historial = []          # Lista de {"role": "user"|"assistant", "content": str}
        self._cliente = None
        self.error_inicio = ""
        self._inicializar()

    # ----------------------------------------------------------- arranque
    def _inicializar(self):
        if self.proveedor == "anthropic":
            if not config.ANTHROPIC_API_KEY:
                self.error_inicio = (
                    "No hay ANTHROPIC_API_KEY configurada. Crea un archivo .env "
                    "(copia .env.example) para activar las respuestas con IA."
                )
                return
            try:
                import anthropic
                self._cliente = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            except ImportError:
                self.error_inicio = "Falta instalar la librería 'anthropic' (pip install anthropic)."
        elif self.proveedor == "ollama":
            pass  # No requiere inicialización; se comprueba al primer uso
        else:
            self.error_inicio = f"PROVEEDOR_IA desconocido: '{self.proveedor}'."

    @property
    def disponible(self) -> bool:
        return not self.error_inicio

    # ---------------------------------------------------------- consultas
    def responder(self, pregunta: str) -> str:
        """Envía la pregunta al modelo y devuelve su respuesta en texto."""
        if not self.disponible:
            return self.error_inicio

        self.historial.append({"role": "user", "content": pregunta})
        self._recortar_historial()

        try:
            if self.proveedor == "anthropic":
                respuesta = self._consultar_anthropic()
            else:
                respuesta = self._consultar_ollama()
        except Exception as e:
            self.historial.pop()               # No guardamos la pregunta fallida
            return self._explicar_error(e)

        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta

    def reiniciar(self):
        """Olvida la conversación anterior."""
        self.historial.clear()

    def _recortar_historial(self):
        """Mantiene solo los últimos mensajes y asegura que empiece por 'user'."""
        exceso = len(self.historial) - config.MAX_MENSAJES_HISTORIAL
        if exceso > 0:
            del self.historial[:exceso]
        while self.historial and self.historial[0]["role"] != "user":
            self.historial.pop(0)

    # ------------------------------------------------------ proveedores
    def _consultar_anthropic(self) -> str:
        resp = self._cliente.messages.create(
            model=config.ANTHROPIC_MODELO,
            max_tokens=config.MAX_TOKENS_RESPUESTA,
            system=config.PROMPT_SISTEMA,
            messages=self.historial,
        )
        texto = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return texto.strip() or "No he obtenido respuesta del modelo."

    def _consultar_ollama(self) -> str:
        cuerpo = json.dumps({
            "model": config.OLLAMA_MODELO,
            "stream": False,
            "messages": [{"role": "system", "content": config.PROMPT_SISTEMA}] + self.historial,
        }).encode("utf-8")
        peticion = urllib.request.Request(
            f"{config.OLLAMA_URL}/api/chat", data=cuerpo,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(peticion, timeout=120) as r:
            datos = json.loads(r.read().decode("utf-8"))
        return datos["message"]["content"].strip()

    # ---------------------------------------------------------- errores
    def _explicar_error(self, e: Exception) -> str:
        """Traduce los errores más comunes a mensajes comprensibles."""
        if self.proveedor == "anthropic":
            import anthropic
            if isinstance(e, anthropic.AuthenticationError):
                return "La clave de API de Anthropic no es válida. Revisa tu archivo .env."
            if isinstance(e, anthropic.RateLimitError):
                return "He alcanzado el límite de peticiones. Inténtalo de nuevo en un momento."
            if isinstance(e, anthropic.APIConnectionError):
                return "No puedo conectar con Anthropic. Revisa tu conexión a internet."
            if isinstance(e, anthropic.NotFoundError):
                return (f"El modelo '{config.ANTHROPIC_MODELO}' no existe o no tienes acceso. "
                        "Cambia ANTHROPIC_MODELO en el .env.")
            if isinstance(e, anthropic.APIStatusError):
                return f"Error de la API de Anthropic ({e.status_code})."
        if isinstance(e, urllib.error.URLError):
            return ("No puedo conectar con Ollama. ¿Está en ejecución? "
                    "(Prueba 'ollama serve' y que el modelo esté descargado.)")
        return f"Error al consultar la IA: {e}"
