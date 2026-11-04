"""
probar_voz.py
Comprueba que Jarvis puede HABLAR en tu ordenador y te dice qué sintetizador usa.

    python probar_voz.py        (en macOS/Linux: python3 probar_voz.py)
"""
import time

from voz import Voz

voz = Voz(activa=True)
print(f"Sistema de voz elegido : {voz.backend}")
if voz.detalle:
    print(f"Detalle                : {voz.detalle}")

frase = "Hola, soy Jarvis. Si oyes esta frase, mi voz funciona correctamente."
print("\nHablando...")
inicio = time.time()
voz.hablar(frase)                      # Espera a que termine
duracion = time.time() - inicio

print(f"Terminado en {duracion:.1f} segundos.")
if duracion < 0.5:
    print("\n⚠ Ha terminado demasiado rápido: lo más probable es que NO haya sonado nada.")
print("""
¿No has oído nada? Revisa, por orden:
  1. El volumen del equipo y que no esté en silencio.
  2. Que la salida de audio correcta esté seleccionada (altavoces/auriculares).
  3. Si arriba aparece un mensaje "[voz] ...", ese es el motivo del fallo.
  4. Windows: instala una voz en español en Configuración > Hora e idioma > Voz.
     macOS: Ajustes > Accesibilidad > Contenido hablado > Voz del sistema.
     Linux: instala espeak-ng  (sudo apt install espeak-ng).
""")
