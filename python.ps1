#!/usr/bin/env pwsh
<# PowerShell shim to call the project's virtualenv Python interpreter.
   Usage (PowerShell): .\python.ps1 script.py args
#>

$PSScriptRootAbs = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvExe = Join-Path $PSScriptRootAbs '.venv\Scripts\python.exe'

if (Test-Path $venvExe) {
    & $venvExe @args
    exit $LASTEXITCODE
}

# Fallback to system python
try {
    $py = Get-Command python -ErrorAction Stop
    & $py.Path @args
    exit $LASTEXITCODE
} catch {
    Write-Error "No python interpreter found in .venv or PATH"
    exit 1
}