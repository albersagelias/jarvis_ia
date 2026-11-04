"""
config.py
Configuración central del asistente. Lee variables de entorno (y del archivo .env).
"""
import os
import platform
from pathlib import Path

# Carga opcional del archivo .env (si python-dotenv está instalado)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# --- Identidad ---
NOMBRE = os.getenv("ASISTENTE_NOMBRE", "Jarvis")

# --- Sistema operativo: "Windows", "Darwin" (macOS) o "Linux" ---
SISTEMA = platform.system()

# --- Voz ---
IDIOMA_RECONOCIMIENTO = "es-ES"   # Idioma que entiende el micrófono
IDIOMA_VOZ_TTS = "es"             # Se busca una voz instalada que contenga este código

# --- IA ---
PROVEEDOR_IA = os.getenv("PROVEEDOR_IA", "anthropic").lower()   # "anthropic" | "ollama"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODELO = os.getenv("ANTHROPIC_MODELO", "claude-sonnet-5-5")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODELO = os.getenv("OLLAMA_MODELO", "llama3.1")

MAX_TOKENS_RESPUESTA = 500
MAX_MENSAJES_HISTORIAL = 20   # Memoria de la conversación (mensajes recordados)

PROMPT_SISTEMA = (
    f"Eres {NOMBRE}, un asistente personal que se ejecuta en el ordenador del usuario. "
    "Responde siempre en español, de forma clara y concisa (máximo 3-4 frases salvo que "
    "se pida más detalle). Tus respuestas pueden leerse en voz alta, así que evita "
    "Markdown, listas largas, tablas y símbolos especiales. "
    "No tienes acceso directo al sistema del usuario: las acciones sobre el ordenador "
    "(abrir apps, buscar en la web, hora, estado) las gestiona otro módulo."
)
