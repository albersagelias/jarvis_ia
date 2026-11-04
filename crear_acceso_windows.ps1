# crear_acceso_windows.ps1
# Crea el acceso directo "Jarvis" (abre la ventana SIN consola) en el Escritorio,
# el menu Inicio y esta carpeta. Ejecutalo una vez: clic derecho > Ejecutar con PowerShell,
# o desde una terminal:  powershell -ExecutionPolicy Bypass -File crear_acceso_windows.ps1
$dir = $PSScriptRoot
$pyw = Join-Path $dir "venv\Scripts\pythonw.exe"
if (-not (Test-Path $pyw)) {
  Write-Host "X  No encuentro el entorno virtual (venv). Ejecuta antes instalar_windows.bat"
  exit 1
}
$ws = New-Object -ComObject WScript.Shell
$destinos = @([Environment]::GetFolderPath("Desktop"), [Environment]::GetFolderPath("Programs"), $dir)
foreach ($d in $destinos) {
  try {
    $acceso = $ws.CreateShortcut((Join-Path $d "Jarvis.lnk"))
    $acceso.TargetPath = $pyw
    $acceso.Arguments = '"' + (Join-Path $dir "interfaz.py") + '"'
    $acceso.WorkingDirectory = $dir
    $acceso.Description = "Jarvis - asistente personal de voz y texto"
    $acceso.Save()
    Write-Host "OK  Acceso directo creado en: $d"
  } catch {
    Write-Host "!   No se pudo crear en: $d"
  }
}
Write-Host "Si algo falla al abrirlo, mira el registro: $dir\jarvis.log"
