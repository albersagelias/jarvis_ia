# instalar_windows.ps1 - Instalador de Jarvis para Windows
# Se ejecuta con doble clic en instalar_windows.bat
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
Write-Host "=== Instalando Jarvis en: $PSScriptRoot ==="

# --- 1. Buscar Python 3.9 o superior (sin fiarnos del acceso directo de la Microsoft Store) ---
$candidatos = @(
  @{ exe = "py"; args = @("-3.12") },
  @{ exe = "py"; args = @("-3.11") },
  @{ exe = "py"; args = @("-3.10") },
  @{ exe = "py"; args = @("-3.13") },
  @{ exe = "py"; args = @("-3") },
  @{ exe = "python"; args = @() }
)
$py = $null
foreach ($c in $candidatos) {
  if (-not (Get-Command $c.exe -ErrorAction SilentlyContinue)) { continue }
  try {
    $salida = & $c.exe @($c.args) --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -and $salida -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 9) {
      $py = $c
      Write-Host "OK  $($salida.Trim())"
      break
    }
  } catch { }
}
if (-not $py) {
  Write-Host "X  No encuentro Python 3.9 o superior."
  Write-Host "   Instalalo con este comando y vuelve a ejecutar este instalador:"
  Write-Host "       winget install Python.Python.3.12"
  Write-Host "   (o desde https://www.python.org/downloads/ marcando 'Add python.exe to PATH')"
  exit 1
}

# --- 2. Entorno virtual ---
$vpy = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $vpy)) {
  Write-Host "-> Creando entorno virtual..."
  & $py.exe @($py.args) -m venv venv
  if (-not (Test-Path $vpy)) { Write-Host "X  No se pudo crear el entorno virtual."; exit 1 }
}

# --- 3. Dependencias ---
Write-Host "-> Instalando dependencias (puede tardar un par de minutos)..."
& $vpy -m pip install --upgrade pip 2>&1 | Out-Null
& $vpy -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "X  Fallo al instalar las dependencias basicas. Revisa tu conexion a internet."; exit 1 }

Write-Host "-> Instalando componentes de voz (opcional)..."
& $vpy -m pip install -r requirements-voz.txt
if ($LASTEXITCODE -ne 0) {
  Write-Host "!  Algun componente de voz no se pudo instalar (normalmente PyAudio)."
  Write-Host "   Jarvis funcionara igualmente por texto y HABLARA con la voz de Windows."
  Write-Host "   Para usar el microfono mira el README, seccion 'Problemas'."
}

# --- 4. Archivo de configuracion ---
if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "OK  Creado .env (editalo con el Bloc de notas para poner tu clave de API o elegir Ollama)"
}

# --- 5. Acceso directo ---
$r = Read-Host "Crear acceso directo de Jarvis en el Escritorio y el menu Inicio? [S/n]"
if ($r -notmatch "^[nN]") { & (Join-Path $PSScriptRoot "crear_acceso_windows.ps1") }

Write-Host ""
Write-Host "=== Instalacion terminada ==="
Write-Host "Probar la voz:      venv\Scripts\python.exe probar_voz.py"
Write-Host "Abrir la ventana:   venv\Scripts\python.exe interfaz.py   (o el acceso directo 'Jarvis')"
Write-Host "Configurar la IA:   edita el archivo .env (ver README)"
