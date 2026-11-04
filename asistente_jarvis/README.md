# 🤖 Asistente personal estilo JARVIS (Python)

Asistente de voz/texto que se ejecuta en tu ordenador: abre apps y webs, busca en
internet, dice la hora/fecha/estado del sistema y responde preguntas con IA.

## Estructura

```
asistente_jarvis/
├── interfaz.py        # 🖥️ Interfaz gráfica (ventana con chat, botones y micrófono)
├── main.py            # Versión de consola e intérprete de comandos (lo usa también la interfaz)
├── gestor_sistema.py  # Apps, webs, búsquedas, hora, fecha, estado del sistema
├── voz.py             # Texto a voz (pyttsx3) y voz a texto (SpeechRecognition)
├── asistente_ia.py    # IA: Anthropic (nube) u Ollama (local)
├── config.py          # Configuración y variables de entorno
├── requirements.txt
└── .env.example       # Plantilla para tu clave de API
```

## 1. Instalación

Necesitas **Python 3.9+** (recomendado 3.10 o superior).

### Windows (PowerShell)
```powershell
cd asistente_jarvis
python -m venv venv
venv\Scripts\Activate.ps1          # Si falla: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
```

### macOS (Terminal)
```bash
cd asistente_jarvis
brew install portaudio              # Necesario para PyAudio (micrófono)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **¿No quieres usar el micrófono?** Borra las dos últimas líneas de `requirements.txt`
> (SpeechRecognition y PyAudio). El asistente funcionará en modo texto sin problemas.

## 2. Configurar la clave de API de Anthropic

1. Crea una cuenta en <https://console.anthropic.com> y añade un método de pago/créditos
   (la API se factura aparte de cualquier suscripción a Claude.ai).
2. Ve a **API Keys → Create Key** y copia la clave (empieza por `sk-ant-`).
3. Copia la plantilla y edítala:
   - Windows: `copy .env.example .env`
   - macOS: `cp .env.example .env`
4. Abre `.env` y pega tu clave en `ANTHROPIC_API_KEY=`.

El modelo se configura en `ANTHROPIC_MODELO` (por defecto `claude-sonnet-5-5`). Puedes
cambiarlo por otro de la lista oficial: <https://docs.claude.com/en/docs/about-claude/models>

**Alternativa 100% local (sin clave):** instala [Ollama](https://ollama.com), ejecuta
`ollama pull llama3.1` y en `.env` pon `PROVEEDOR_IA=ollama`.

> Sin clave ni Ollama, el asistente sigue funcionando para todos los comandos de
> control del sistema; solo las preguntas generales quedarán desactivadas.

## 3. Ejecutar

### Interfaz gráfica (recomendado)
```bash
python3 interfaz.py
```
Ventana con chat, botones de acciones rápidas (hora, fecha, sistema, Spotify…), botón 🎤
(pulsa y habla una frase), interruptor **Escucha continua** (manos libres) e interruptor **Voz**.

> **macOS:** si al abrirla da un error de `tkinter`/`_tkinter`, instala el soporte con
> `brew install python-tk` (o usa el Python de python.org, que ya lo incluye) y repite
> `pip install customtkinter` dentro del entorno virtual.

### Abrirlo con doble clic (sin Terminal) – solo macOS
Una vez instaladas las dependencias, crea la app con:
```bash
bash crear_app_mac.sh
```
Aparecerá `Jarvis.app` en la carpeta: ábrela con doble clic o arrástrala al Dock. Los errores
quedan registrados en `jarvis.log`. Si mueves la carpeta del proyecto, vuelve a ejecutar el script.

### Versión de consola
```bash
python main.py              # Texto + respuestas habladas
python main.py --voz        # Te escucha por el micrófono
python main.py --silencio   # Solo texto
```

En macOS usa `python3`. Dentro del asistente puedes decir/escribir «modo voz», «modo texto»,
«silencio» y «activa la voz» para cambiar de modo en caliente.

## 4. Ejemplos de comandos

| Dices / escribes | Resultado |
|---|---|
| `abre spotify` / `abre el bloc de notas` / `abre vs code` | Abre la aplicación |
| `abre youtube` / `abre github.com` | Abre el sitio en tu navegador |
| `busca recetas de paella` | Búsqueda en Google (nueva pestaña) |
| `busca gatos en youtube` | Búsqueda en YouTube |
| `qué hora es` · `qué día es hoy` | Hora y fecha |
| `estado del sistema` | CPU, RAM, disco y batería |
| `Jarvis, abre la terminal` | El nombre del asistente al inicio se ignora |
| `¿Por qué el cielo es azul?` | Se envía a la IA |
| `ayuda` · `olvida la conversación` · `salir` | Utilidades |

## 5. Permisos y problemas frecuentes

- **macOS – micrófono:** *Ajustes del Sistema → Privacidad y seguridad → Micrófono* y activa tu Terminal (o VS Code).
- **Windows – micrófono:** *Configuración → Privacidad → Micrófono* → permitir apps de escritorio.
- **`pip install pyaudio` falla:** en macOS falta `brew install portaudio`; en Windows actualiza pip (`python -m pip install -U pip`) o usa `pip install pipwin && pipwin install pyaudio`.
- **macOS – voz:** el asistente usa el comando nativo `say`. Si suena en inglés, instala una voz en español (*Ajustes del Sistema → Accesibilidad → Contenido hablado → Voz del sistema → Gestionar voces*).
- **No suena la voz en español (Windows):** instala una voz en español en tu sistema (Windows: *Configuración → Hora e idioma → Voz*; macOS: *Accesibilidad → Contenido hablado → Voces del sistema*).
- **El reconocimiento de voz no funciona:** usa el servicio gratuito de Google y necesita internet.
- **«No he podido abrir X»:** esa app no está instalada o no está en el PATH (p. ej. `code` en VS Code: *Shell Command: Install 'code' command in PATH*).

## 6. Cómo ampliarlo

- **Nueva app:** añade una entrada al diccionario `APPS` en `gestor_sistema.py`.
- **Nuevo sitio web:** añádelo a `SITIOS`.
- **Nuevo comando:** crea un método `_cmd_xxx` en `main.py` y registra su patrón en `self.comandos`.
- **Seguridad:** el asistente solo ejecuta acciones de un catálogo cerrado; nunca lanza comandos arbitrarios del shell ni de la IA. Mantén ese diseño si lo amplías.
