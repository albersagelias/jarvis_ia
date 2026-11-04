"""
main.py
Punto de entrada del asistente personal (estilo JARVIS).

Uso:
    python main.py              # modo texto, con salida de voz
    python main.py --voz        # arranca escuchando por el micrófono
    python main.py --silencio   # sin salida de voz (solo texto)

Flujo: entrada (texto o voz) -> intérprete de comandos -> acción del sistema
       o, si no es un comando directo, consulta a la IA.
"""
import argparse
import re
import sys
import unicodedata

import config
from asistente_ia import CerebroIA
from gestor_sistema import GestorSistema
from voz import Oido, Voz

# Palabras que se ignoran al principio del objetivo: "abre la aplicación de spotify" -> "spotify"
PALABRAS_RELLENO = {"la", "el", "las", "los", "una", "un", "aplicacion", "app", "programa",
                    "pagina", "web", "sitio", "pestana", "de", "del", "en", "me"}

AYUDA = (
    "Puedo hacer esto:\n"
    "  • Abrir apps:        «abre spotify», «abre el bloc de notas», «abre vs code»\n"
    "  • Abrir webs:        «abre youtube», «abre github.com»\n"
    "  • Buscar:            «busca recetas de paella», «busca gatos en youtube»\n"
    "  • Hora y fecha:      «qué hora es», «qué día es hoy»\n"
    "  • Estado del equipo: «estado del sistema», «cómo está la batería»\n"
    "  • Voz:               «modo voz», «modo texto», «silencio», «activa la voz»\n"
    "  • Conversación:      cualquier otra pregunta se la paso a la IA\n"
    "  • «olvida la conversación» reinicia la memoria · «salir» termina"
)


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y sin signos en los extremos, para comparar comandos."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.strip(" \t\n¿?¡!.,;:")


class Asistente:
    def __init__(self, modo_voz: bool, con_sonido: bool):
        self.sistema = GestorSistema()
        self.voz = Voz(activa=con_sonido)
        self.oido = Oido()
        self.ia = CerebroIA()
        self.modo_voz = modo_voz and self.oido.disponible
        self.en_marcha = True

        if modo_voz and not self.oido.disponible:
            print(f"[aviso] No se puede usar la voz: {self.oido.motivo_no_disponible}")

        # Tabla de comandos: (expresión regular sobre el texto normalizado, método).
        # El ORDEN importa: los patrones más específicos van primero.
        self.comandos = [
            (r"^(salir|adios|hasta luego|apagate|termina|cierra el asistente)\b", self._cmd_salir),
            (r"^(ayuda|help|comandos|que puedes hacer)\b", self._cmd_ayuda),
            (r"^(olvida|reinicia|borra) (la |nuestra )?(conversacion|memoria|chat)", self._cmd_olvidar),
            (r"^(modo voz|activa(r)? (el )?(modo voz|microfono))", self._cmd_modo_voz),
            (r"^(modo texto|desactiva(r)? (el )?(modo voz|microfono))", self._cmd_modo_texto),
            (r"^(silencio|silencia|callate|mute|desactiva(r)? (la )?voz)", self._cmd_silenciar),
            (r"^(habla|activa(r)? (la )?voz|activa(r)? (el )?sonido)", self._cmd_activar_voz),
            (r"\bque hora\b|^(dime )?la hora$|^hora$", self._cmd_hora),
            (r"\bque (dia|fecha)\b|\bfecha de hoy\b|^(dime )?la fecha$", self._cmd_fecha),
            (r"estado (del )?(sistema|equipo|pc|ordenador)|\bbateria\b|uso de (cpu|memoria|ram)",
             self._cmd_estado),
            (r"^(?:busca|buscar|googlea)\s+en\s+(youtube|google|wikipedia|maps)\s+(.+)$",
             self._cmd_buscar_motor_primero),
            (r"^(?:busca|buscar|reproduce|pon)\s+(.+?)\s+en\s+(youtube|google|wikipedia|maps)$",
             self._cmd_buscar_motor_ultimo),
            (r"^(?:busca|buscar|googlea|investiga)\s+(.+)$", self._cmd_buscar),
            (r"^(?:abre|abrir|abreme|ejecuta|lanza|inicia|arranca|ve a|ir a)\s+(.+)$",
             self._cmd_abrir),
        ]

    # ================================================================ SALIDA
    def decir(self, texto: str):
        """Muestra la respuesta en pantalla y la dice en voz alta (si está activa)."""
        print(f"\n{config.NOMBRE}: {texto}\n")
        self.voz.hablar(texto)

    # ============================================================== COMANDOS
    def _cmd_salir(self, m):
        self.en_marcha = False
        return "Hasta luego. Apagando sistemas."

    def _cmd_ayuda(self, m):
        return AYUDA

    def _cmd_olvidar(self, m):
        self.ia.reiniciar()
        return "Conversación reiniciada. He olvidado lo anterior."

    def _cmd_modo_voz(self, m):
        if not self.oido.disponible:
            return f"No puedo usar el micrófono. {self.oido.motivo_no_disponible}"
        self.modo_voz = True
        return "Modo voz activado. Te escucho."

    def _cmd_modo_texto(self, m):
        self.modo_voz = False
        return "Modo texto activado."

    def _cmd_silenciar(self, m):
        self.voz.activa = False
        return "De acuerdo, me quedo en silencio. Responderé solo por texto."

    def _cmd_activar_voz(self, m):
        self.voz.activa = True
        return "Voz activada."

    def _cmd_hora(self, m):
        return self.sistema.hora()

    def _cmd_fecha(self, m):
        return self.sistema.fecha()

    def _cmd_estado(self, m):
        return self.sistema.estado_sistema()

    def _cmd_buscar_motor_primero(self, m):
        return self.sistema.buscar_web(m.group(2), motor=m.group(1))

    def _cmd_buscar_motor_ultimo(self, m):
        return self.sistema.buscar_web(m.group(1), motor=m.group(2))

    def _cmd_buscar(self, m):
        return self.sistema.buscar_web(m.group(1))

    def _cmd_abrir(self, m):
        objetivo = m.group(1)
        # Quitamos palabras de relleno al principio ("la aplicación de ...")
        palabras = objetivo.split()
        while len(palabras) > 1 and palabras[0] in PALABRAS_RELLENO:
            palabras.pop(0)
        objetivo = " ".join(palabras)

        # 1º intentamos como aplicación; 2º como sitio web; 3º error amistoso.
        encontrada, mensaje = self.sistema.abrir_aplicacion(objetivo)
        if encontrada:
            return mensaje
        encontrado, mensaje = self.sistema.abrir_sitio(objetivo)
        if encontrado:
            return mensaje
        return (f"No conozco «{objetivo}». Puedes añadirla al catálogo APPS "
                "en gestor_sistema.py o decirme una dirección web.")

    # ========================================================== PROCESAMIENTO
    def procesar(self, entrada: str) -> str:
        """Interpreta una entrada y devuelve la respuesta a mostrar."""
        texto = normalizar(entrada)

        # Si el usuario dice el nombre del asistente al principio ("Jarvis, abre..."), lo quitamos
        nombre = normalizar(config.NOMBRE)
        texto = re.sub(rf"^{re.escape(nombre)}\b[\s,:]*", "", texto)
        if not texto:
            return "Dime."

        for patron, manejador in self.comandos:
            m = re.search(patron, texto)
            if m:
                try:
                    return manejador(m)
                except Exception as e:      # Un fallo en un comando nunca debe tumbar el asistente
                    return f"Ha ocurrido un error al ejecutar ese comando: {e}"

        # No es un comando de control: se lo pasamos a la IA (con el texto original)
        if not self.ia.disponible:
            return ("No reconozco ese comando y la IA no está disponible. "
                    f"{self.ia.error_inicio} Escribe «ayuda» para ver lo que sé hacer.")
        print("(pensando...)")
        return self.ia.responder(entrada.strip())

    # ============================================================ BUCLE PRINCIPAL
    def _leer_entrada(self):
        """Devuelve el siguiente texto del usuario (por voz o teclado), o None si no hubo nada."""
        if self.modo_voz:
            texto = self.oido.escuchar()
            if texto:
                print(f"Tú (voz): {texto}")
            return texto
        return input("Tú: ").strip()

    def ejecutar(self):
        print("=" * 60)
        print(f"  {config.NOMBRE} · asistente personal   (escribe 'ayuda' para ver comandos)")
        print(f"  Sistema: {config.SISTEMA} · IA: {config.PROVEEDOR_IA}"
              f" · Voz de entrada: {'sí' if self.modo_voz else 'no'}")
        print("=" * 60)
        if not self.ia.disponible:
            print(f"[aviso] IA desactivada: {self.ia.error_inicio}")
        self.decir(f"Hola, soy {config.NOMBRE}. ¿En qué puedo ayudarte?")

        while self.en_marcha:
            try:
                entrada = self._leer_entrada()
                if not entrada:
                    continue
                self.decir(self.procesar(entrada))
            except (KeyboardInterrupt, EOFError):
                print("\nInterrumpido. Hasta luego.")
                break
            except Exception as e:
                print(f"[error] {e}")


def main():
    parser = argparse.ArgumentParser(description="Asistente personal de voz/texto.")
    parser.add_argument("--voz", action="store_true", help="Escuchar por el micrófono al iniciar")
    parser.add_argument("--silencio", action="store_true", help="Desactivar la salida de voz")
    args = parser.parse_args()

    if sys.version_info < (3, 9):
        sys.exit("Se requiere Python 3.9 o superior.")

    Asistente(modo_voz=args.voz, con_sonido=not args.silencio).ejecutar()


if __name__ == "__main__":
    main()
