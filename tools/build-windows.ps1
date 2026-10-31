$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$py312 = & py -3.12 -c "import sys; print(sys.executable)"
if (-not $py312) {
    throw "Python 3.12 is required. PyQt5 does not load on Python 3.13 on this machine. Install 3.12.6 and retry."
}

$venvPython = Join-Path (Get-Location) "packenv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating packenv with Python 3.12..."
    & py -3.12 -m venv packenv
}

Write-Host "Using $venvPython"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
& $venvPython -m PyInstaller --clean --noconfirm ImageKeysort.spec

$exe = Join-Path (Get-Location) "dist\ImageKeysort\ImageKeysort.exe"
if (-not (Test-Path $exe)) {
    throw "Build finished but $exe was not created."
}

Write-Host "Built $exe"
Write-Host "Run it from that folder so _internal stays next to the exe."
