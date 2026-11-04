# 🤖 Jarvis · asistente personal de voz y texto

Asistente que se ejecuta **en tu ordenador** (Windows, macOS o Linux). Tiene ventana gráfica, **habla**,
te puede escuchar por el micrófono y entiende órdenes como:

| Categoría | Ejemplos |
|---|---|
| Abrir apps | «abre spotify» · «abre vs code» · «abre el bloc de notas» · «abre la calculadora» |
| Webs y búsquedas | «abre youtube» · «busca recetas de paella» · «busca gatos en youtube» |
| Sistema | «qué hora es» · «qué día es hoy» · «estado del sistema» |
| Conversación | Cualquier otra pregunta se la pasa a una IA (Anthropic, o un modelo gratuito local con Ollama) |

## Índice

1. [Qué necesitas](#1-qué-necesitas)
2. [Descargar el proyecto](#2-descargar-el-proyecto)
3. [Instalar](#3-instalar) · [Windows](#-windows) · [macOS](#-macos) · [Linux](#-linux)
4. [Configurar la IA](#4-configurar-la-ia)
5. [Abrir Jarvis](#5-abrir-jarvis)
6. [Comprobar que funciona](#6-comprobar-que-funciona)
7. [Usarlo desde VS Code](#7-usarlo-desde-vs-code)
8. [Voz y micrófono](#8-voz-y-micrófono)
9. [Problemas frecuentes](#9-problemas-frecuentes)
10. [Actualizar, desinstalar, ampliar](#10-actualizar-desinstalar-y-ampliar)

---

## 1. Qué necesitas

- Un ordenador con **Windows 10/11, macOS o Linux**.
- **Python 3.9 o superior** (recomendado **3.12**). Si no lo tienes, el paso 3 te explica cómo instalarlo.
- Conexión a internet para la instalación (y para el micrófono y la IA en la nube).
- *Opcional:* una clave de la API de Anthropic (de pago) **o** Ollama (gratis). Sin ninguna de las dos, Jarvis
  funciona igual, pero no responderá preguntas generales.

> 💡 **Qué es "la terminal":** una ventana donde se escriben comandos (en Windows se llama *PowerShell*,
> en macOS *Terminal*). En cada paso te digo exactamente qué escribir: copia y pega cada línea y pulsa Enter.

---

## 2. Descargar el proyecto

Hay dos formas. Si no sabes qué es Git, usa la **A**.

### A) Descargar el ZIP (la más fácil)

1. Abre la página del proyecto en GitHub: `https://github.com/albersagelias/jarvis_ia`
2. Pulsa el botón verde **`<> Code`** y luego **Download ZIP**. Se descargará un archivo llamado
   **`jarvis_ia-main.zip`** (normalmente en tu carpeta *Descargas*).
3. **Descomprime `jarvis_ia-main.zip`** (no lo uses desde dentro del ZIP, no funciona):
   - **Windows:** clic derecho sobre `jarvis_ia-main.zip` → **Extraer todo…** → Extraer.
   - **macOS:** doble clic sobre `jarvis_ia-main.zip`.
   - **Linux:** clic derecho → *Extraer aquí*, o en la terminal: `unzip jarvis_ia-main.zip`.
4. Al abrir el ZIP obtendrás la carpeta **`jarvis_ia`**. Dentro debes ver `interfaz.py`, `README.md` e `instalar…`:
   esa es la **carpeta del proyecto**.
   *(Si tu sistema la llama `jarvis_ia-main`, renómbrala a `jarvis_ia`; y si dentro solo ves otra carpeta,
   entra en ella hasta encontrar `interfaz.py`.)*
   Puedes moverla donde quieras (Documentos, por ejemplo), pero hazlo **antes** de instalar.

### B) Con Git

```bash
git clone https://github.com/albersagelias/jarvis_ia.git
cd jarvis_ia
```

---

## 3. Instalar

Los instaladores hacen todo solos: buscan Python, crean un entorno aislado (`venv`), instalan las librerías,
crean tu archivo de configuración `.env` y te ofrecen crear un **icono** para abrir Jarvis con doble clic.
Tarda un par de minutos.

### 🪟 Windows

**Paso 1 · Comprueba si tienes Python.** Abre PowerShell (menú Inicio → escribe `PowerShell`) y ejecuta:

```powershell
py --version
```

- Si muestra `Python 3.x.x` (3.9 o superior) → **ve al paso 2**.
- Si da error, instálalo (con este comando, o desde <https://www.python.org/downloads/> marcando
  **"Add python.exe to PATH"**):

  ```powershell
  winget install Python.Python.3.12
  ```

  Después **cierra y vuelve a abrir** PowerShell antes de continuar.

> ℹ️ En Windows, si escribes `python` sin tenerlo instalado se abre la Microsoft Store. Es normal: ignórala
> e instala Python como se indica arriba.

**Paso 2 · Ejecuta el instalador.** En el Explorador de archivos, entra en la carpeta del proyecto y haz
**doble clic en `instalar_windows.bat`**.

- Si Windows muestra *"Windows protegió su PC"*: pulsa **Más información → Ejecutar de todas formas**
  (aparece porque el archivo viene de internet; el contenido es texto que puedes abrir y leer).
- Cuando pregunte *"Crear acceso directo de Jarvis…"*, escribe `S` y pulsa Enter.

**Paso 3 ·** Configura la IA (siguiente apartado) y abre **Jarvis** desde el acceso directo del Escritorio.

<details>
<summary>¿Prefieres hacerlo desde la terminal en vez de con doble clic?</summary>

En la carpeta del proyecto: clic en la barra de direcciones del Explorador, escribe `powershell` y pulsa Enter.
Luego ejecuta `.\instalar_windows.bat`.
</details>

### 🍎 macOS

**Paso 1 · Abre Terminal en la carpeta del proyecto.** Abre *Terminal* (Cmd + Espacio → `Terminal`), escribe
`cd ` (con un espacio detrás), **arrastra la carpeta del proyecto** a la ventana y pulsa Enter.

**Paso 2 · Comprueba Python:**

```bash
python3 --version
```

Si da error o es anterior a 3.9, instálalo desde <https://www.python.org/downloads/> (incluye el soporte de ventanas)
o con [Homebrew](https://brew.sh): `brew install python@3.12 python-tk@3.12`.

**Paso 3 · Ejecuta el instalador:**

```bash
bash instalar.sh
```

Si tienes Homebrew, instalará `portaudio` (necesario para el micrófono). Cuando pregunte por el icono, pulsa
`S`: se creará **`Jarvis.app`** en la carpeta (ábrela con doble clic o arrástrala al Dock).
La primera vez, si macOS la bloquea: clic derecho sobre `Jarvis.app` → **Abrir** → confirmar.

### 🐧 Linux

**Paso 1 · Instala las dependencias del sistema** (Debian/Ubuntu; en Fedora: `sudo dnf install python3 python3-tkinter espeak-ng portaudio-devel`):

```bash
sudo apt install python3 python3-venv python3-pip python3-tk espeak-ng portaudio19-dev python3-dev
```

> `espeak-ng` es la **voz** de Jarvis; `portaudio` solo hace falta para el **micrófono**.

**Paso 2 · Abre una terminal en la carpeta del proyecto** (clic derecho en la carpeta → *Abrir en terminal*)
y ejecuta:

```bash
bash instalar.sh
```

Cuando pregunte por el icono, pulsa `S`: aparecerá **Jarvis** en el menú de aplicaciones y en el Escritorio
(en GNOME, clic derecho en el icono del Escritorio → *Permitir lanzar*).

<details>
<summary><b>Instalación manual (solo si el instalador no te funciona)</b></summary>

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt     # núcleo
pip install -r requirements-voz.txt # micrófono y voz de respaldo (opcional)
cp .env.example .env                # Windows: copy .env.example .env
python interfaz.py
```
</details>

---

## 4. Configurar la IA

El instalador creó un archivo llamado **`.env`** en la carpeta del proyecto (si no existe: copia `.env.example`
y renómbralo a `.env`). Ábrelo con cualquier editor de texto:

- **Windows:** `notepad .env` en PowerShell, desde la carpeta del proyecto.
- **macOS:** `open -e .env`
- **Linux:** `nano .env`
- En cualquier sistema también sirve abrirlo con **VS Code**.

> En el Explorador/Finder los archivos que empiezan por punto pueden estar ocultos:
> Windows → *Ver → Mostrar → Elementos ocultos* · macOS → `Cmd + Shift + .`

Elige **una** de las tres opciones:

| Opción | Coste | Qué poner en `.env` |
|---|---|---|
| **Sin IA** | Gratis | Nada. Funcionan todos los comandos menos las preguntas generales. |
| **Ollama (IA local)** | Gratis | 1) Instala [Ollama](https://ollama.com). 2) En la terminal: `ollama pull llama3.2` (unos 2 GB). 3) En `.env`: `PROVEEDOR_IA=ollama` y `OLLAMA_MODELO=llama3.2`. Ollama debe estar abierto al usar Jarvis. |
| **Anthropic (en la nube)** | De pago | 1) Crea una cuenta en <https://console.anthropic.com> y añade crédito. 2) *API Keys → Create Key* y copia la clave (empieza por `sk-ant-`). 3) Pégala en `ANTHROPIC_API_KEY=` (sin comillas ni espacios). |

La API de Anthropic se factura aparte de cualquier suscripción a Claude.ai. El modelo se cambia en
`ANTHROPIC_MODELO` (lista oficial: <https://docs.claude.com/en/docs/about-claude/models>).

Guarda el archivo. Si Jarvis estaba abierto, ciérralo y ábrelo otra vez.

> 🔒 **Nunca subas tu `.env` a GitHub ni lo compartas:** contiene tu clave. El `.gitignore` del proyecto ya lo excluye.

---

## 5. Abrir Jarvis

| Cómo | Resultado |
|---|---|
| **Icono creado por el instalador** (Escritorio / menú Inicio / `Jarvis.app` / menú de aplicaciones) | Abre la ventana, **sin terminal** |
| Terminal: `python interfaz.py` | La ventana |
| Terminal: `python main.py` | Versión de consola (`--voz` para hablarle, `--silencio` sin voz) |
| Terminal: `python probar_voz.py` | Comprueba que Jarvis puede hablar |

En macOS/Linux escribe `python3` en lugar de `python`. Si no has activado el entorno virtual, usa la ruta completa
del Python del entorno (funciona siempre):

- **Windows:** `venv\Scripts\python.exe interfaz.py`
- **macOS / Linux:** `venv/bin/python interfaz.py`

**La ventana** tiene un chat, botones de acciones rápidas (hora, fecha, sistema, Spotify…), un botón 🎤
(pulsa y habla una frase), un interruptor **Escucha continua** (manos libres), un interruptor **Voz** y un
botón 🧹 para limpiar la conversación. Si falla al abrirla con el icono, el motivo queda en `jarvis.log`.

---

## 6. Comprobar que funciona

Haz estas pruebas en orden. Si alguna falla, mira el [apartado de problemas](#9-problemas-frecuentes).

**1 · La voz.** En la terminal, dentro de la carpeta del proyecto:

```bash
venv/bin/python probar_voz.py             # Windows: venv\Scripts\python.exe probar_voz.py
```

Debe mostrar qué sintetizador usa y **decir una frase en voz alta**.

**2 · La ventana.** Abre Jarvis y comprueba:

| Prueba | Resultado esperado |
|---|---|
| Se abre la ventana | Chat con un saludo y una línea gris «Salida de voz: …» |
| Pulsas el botón **Hora** | Responde con la hora y la dice en voz alta |
| Escribes `abre el bloc de notas` | Se abre el editor de texto del sistema |
| Escribes `busca gatos en youtube` | Se abre el navegador con la búsqueda |
| Escribes `estado del sistema` | Informa de CPU, memoria y disco |
| Haces una pregunta general («¿por qué el cielo es azul?») | Responde la IA (o avisa de que no está configurada) |
| Pulsas 🎤 y dices «qué hora es» | Lo reconoce y responde (si el micrófono está instalado) |

---

## 7. Usarlo desde VS Code

Si quieres ejecutarlo, probarlo o modificarlo desde VS Code:

1. **File → Open Folder…** y elige la carpeta del proyecto (la que contiene `interfaz.py`).
2. Abre la terminal integrada: `Ctrl + ñ` (o menú *Terminal → New Terminal*). Ya está dentro de la carpeta.
3. Instala si aún no lo hiciste: `.\instalar_windows.bat` (Windows) o `bash instalar.sh` (macOS/Linux).
4. Ejecuta, usando el Python del entorno (no hace falta activarlo):
   - Windows: `venv\Scripts\python.exe interfaz.py`
   - macOS/Linux: `venv/bin/python interfaz.py`
5. *(Recomendado)* Indica a VS Code qué Python usar: `Ctrl + Shift + P` → **Python: Select Interpreter** → el que
   termina en `venv\Scripts\python.exe` (o `venv/bin/python`).

> **Windows:** si prefieres activar el entorno y da error de «ejecución de scripts deshabilitada», ejecuta una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Sabrás que está activo porque aparece `(venv)` al inicio
> de la línea; entonces `python` y `pip` funcionan normalmente.

---

## 8. Voz y micrófono

### La voz de Jarvis (salida)

Cada sistema usa su sintetizador nativo (sin internet):

| Sistema | Sintetizador | Si no suena en español |
|---|---|---|
| Windows | PowerShell + voces de Windows | *Configuración → Hora e idioma → Voz → Agregar voces* |
| macOS | comando `say` | *Ajustes → Accesibilidad → Contenido hablado → Voz del sistema → Gestionar voces* |
| Linux | `espeak-ng` (o `espeak` / `spd-say`) | `sudo apt install espeak-ng` |

Si el nativo falla, se prueba `pyttsx3` como respaldo. **¿No oyes nada?** Ejecuta `probar_voz.py` (apartado 6):
te dice qué sintetizador usa y el motivo del fallo. Revisa también el volumen, la salida de audio y que el
interruptor **Voz** de la ventana esté activado (o no hayas dicho «silencio»).

### El micrófono (entrada)

Necesita internet (usa el reconocimiento gratuito de Google) y los componentes de `requirements-voz.txt`.
Sin micrófono, Jarvis funciona igual por texto.

- **macOS:** `brew install portaudio`, después `venv/bin/pip install -r requirements-voz.txt`, y concede el permiso en
  *Ajustes → Privacidad y seguridad → Micrófono* (a Terminal, Jarvis o Python, según cómo lo abras).
- **Windows:** *Configuración → Privacidad y seguridad → Micrófono* → permitir apps de escritorio. Si `PyAudio`
  no se instala, usa Python 3.12 (`py -3.12 -m venv venv`) y repite el instalador.
- **Linux:** `sudo apt install portaudio19-dev python3-dev` y `venv/bin/pip install -r requirements-voz.txt`.

---

## 9. Problemas frecuentes

| Problema | Solución |
|---|---|
| *(Windows)* «No se encontró Python… Microsoft Store» | Python no está instalado o falta en el PATH. `winget install Python.Python.3.12`, **cierra y reabre la terminal/VS Code**, y usa `py` en lugar de `python`. |
| *(Windows)* «Windows protegió su PC» al abrir el `.bat` | **Más información → Ejecutar de todas formas.** |
| *(Windows)* «la ejecución de scripts está deshabilitada» | Una vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`; o no actives el entorno y usa `venv\Scripts\python.exe`. |
| El `.bat` / el instalador no encuentran los archivos | Descomprimiste mal el ZIP: usa **Extraer todo** y ejecuta el instalador desde la carpeta extraída. |
| Error con `tkinter` / `_tkinter` | macOS: `brew install python-tk@3.12` · Debian/Ubuntu: `sudo apt install python3-tk` · Fedora: `sudo dnf install python3-tkinter`. Mientras tanto, usa `python main.py`. |
| `pip` / `python` «no se reconoce» | Usa la ruta completa del entorno: `venv\Scripts\python.exe -m pip …` (Windows) o `venv/bin/python -m pip …`. |
| `PyAudio` no se instala | Solo afecta al micrófono. Instala `portaudio` (macOS/Linux) o usa Python 3.12 (Windows). Jarvis funciona igual por texto. |
| «No puedo conectar con Ollama» | Abre Ollama (o ejecuta `ollama serve`) y comprueba el nombre del modelo con `ollama list`. |
| «La clave de API no es válida» | Revisa `ANTHROPIC_API_KEY` en `.env` (sin espacios ni comillas) y que tengas crédito. |
| «No he podido abrir X» | La app no está instalada o no está en el PATH (ej. `code`: en VS Code, *Shell Command: Install 'code' command in PATH*). |
| macOS bloquea `Jarvis.app` | Clic derecho → **Abrir** → confirmar. |
| Linux: el icono del Escritorio no abre | Clic derecho → **Permitir lanzar** (GNOME). |
| Moví la carpeta del proyecto | Los iconos apuntan a la ruta antigua: ejecuta de nuevo `crear_app_mac.sh` / `crear_lanzador_linux.sh` / `crear_acceso_windows.ps1`. |
| El icono no abre nada | Mira `jarvis.log` en la carpeta del proyecto: ahí queda el error. |

---

## 10. Actualizar, desinstalar y ampliar

**Actualizar:** si lo descargaste con Git, ejecuta `git pull` y luego repite `instalar_windows.bat` / `bash instalar.sh`
(conserva tu `.env`). Si descargaste el ZIP, descarga el nuevo, copia tu `.env` dentro y repite el instalador.

**Desinstalar:** borra la carpeta del proyecto y los iconos (`Jarvis.app`, `Jarvis.lnk` del Escritorio/menú Inicio, o
`~/.local/share/applications/jarvis.desktop`). No instala nada fuera de esa carpeta, salvo `portaudio` si usaste Homebrew.

**Ampliarlo:**
- Nueva app → añádela al diccionario `APPS` de `gestor_sistema.py`.
- Nuevo sitio web → añádelo a `SITIOS`.
- Nuevo comando → crea un método `_cmd_xxx` en `main.py` y registra su patrón en `self.comandos`.

**Seguridad:** Jarvis solo ejecuta acciones de un catálogo cerrado: **nunca** lanza comandos arbitrarios de la terminal,
ni los que proponga la IA. Mantén ese diseño si lo amplías.

### 📁 Estructura del proyecto

```
├── interfaz.py                 # Ventana gráfica
├── main.py                     # Versión de consola + intérprete de comandos
├── gestor_sistema.py           # Apps, webs, búsquedas, hora, fecha, estado
├── voz.py                      # Voz de salida (nativa) y micrófono
├── asistente_ia.py             # IA: Anthropic u Ollama
├── config.py                   # Configuración y variables de entorno
├── probar_voz.py               # Diagnóstico de la voz
├── requirements.txt            # Dependencias básicas
├── requirements-voz.txt        # Micrófono y voz de respaldo (opcional)
├── .env.example                # Plantilla de configuración (se copia a .env)
├── instalar.sh                 # Instalador macOS / Linux
├── instalar_windows.bat / .ps1 # Instalador Windows
├── crear_app_mac.sh            # Crea Jarvis.app (macOS)
├── crear_lanzador_linux.sh     # Crea el icono en el menú (Linux)
└── crear_acceso_windows.ps1    # Crea el acceso directo (Windows)
```
