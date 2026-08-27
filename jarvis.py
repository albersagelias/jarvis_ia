import os
import sys
import io
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import pyttsx3
from google import genai

# 1. Configuración del motor de voz para Windows
def hablar(texto):
    print(f"\n🤖 Jarvis: {texto}")
    try:
        # Re-inicializar el motor en cada llamada evita bloqueos del sintetizador SAPI5 en Windows
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 160)
        
        # Seleccionar la primera voz en español disponible
        voices = engine.getProperty('voices')
        for voice in voices:
            if "spanish" in voice.name.lower() or "es" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break

        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"❌ Error al reproducir audio: {e}")

# 2. Comprobar API Key de Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: No se ha detectado la variable GEMINI_API_KEY.")
    sys.exit()

client = genai.Client(api_key=api_key)

chat = client.chats.create(
    model='gemini-3.6-flash',
    config={
        'system_instruction': 'Eres Jarvis, un asistente virtual muy eficiente, conciso y educado. Responde en una o dos frases cortas.'
    }
)

# 3. Capturar voz
def escuchar():
    fs = 44100
    segundos = 5

    print("\n🎙️ Escuchando (habla ahora)...")
    grabacion = sd.rec(int(segundos * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    buffer_wav = io.BytesIO()
    write(buffer_wav, fs, grabacion)
    buffer_wav.seek(0)

    recognizer = sr.Recognizer()
    with sr.AudioFile(buffer_wav) as source:
        audio = recognizer.record(source)
        try:
            print("🧠 Procesando voz...")
            texto = recognizer.recognize_google(audio, language="es-ES")
            print(f"👤 Tú: {texto}")
            return texto
        except sr.UnknownValueError:
            print("⏳ No he entendido lo que has dicho.")
            return None
        except Exception as e:
            print(f"❌ Error al reconocer: {e}")
            return None

# 4. Bucle principal
if __name__ == "__main__":
    hablar("Sistemas iniciados. Hola Alberto, te escucho.")
    
    while True:
        comando = escuchar()
        if comando:
            if "salir" in comando.lower() or "apagar" in comando.lower():
                hablar("Hasta luego, Alberto.")
                break
            
            try:
                response = chat.send_message(comando)
                hablar(response.text)
            except Exception as e:
                print(f"❌ Error en Gemini: {e}")