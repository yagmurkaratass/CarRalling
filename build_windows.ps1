$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "Car Ralling Windows paketi hazırlanıyor..." -ForegroundColor Cyan
$buildPython = Join-Path $PSScriptRoot ".build-venv312\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $buildPython)) {
    py -3.12 -m venv ".build-venv312"
    if ($LASTEXITCODE -ne 0) { throw "Python 3.12 sanal ortamı oluşturulamadı." }
}

& $buildPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip güncellenemedi." }
& $buildPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Gerekli paketler kurulamadı." }

$buildArgs = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "CarRalling",
    "--version-file", "version_info.txt",
    "--add-data", "assets;assets",
    "--collect-all", "pygame"
)

if (Test-Path -LiteralPath "game.ico") {
    $buildArgs += @("--icon", "game.ico")
}

& $buildPython -m PyInstaller @buildArgs "car_ralling.py"
if ($LASTEXITCODE -ne 0) { throw "Windows paketi oluşturulamadı." }

Write-Host ""
Write-Host "Hazır: dist\CarRalling.exe" -ForegroundColor Green
Write-Host "Kayıtlar: %LOCALAPPDATA%\CarRalling\savegame.json"
