Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

function Find-Python {
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command) {
        try {
            & $command.Source --version *> $null
            if ($LASTEXITCODE -eq 0) { return $command.Source }
        } catch { }
    }

    $installRoot = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path $installRoot) {
        $candidate = Get-ChildItem -Path $installRoot -Directory |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'python.exe' } |
            Where-Object { Test-Path $_ } |
            Select-Object -First 1
        if ($candidate) { return $candidate }
    }

    throw 'Python 3.8+ is not installed. Run: winget install --id Python.Python.3.14 --exact'
}

$pythonExe = Find-Python
Write-Host "Using Python: $pythonExe"

function Invoke-Checked {
    param(
        [string]$Executable,
        [string[]]$Arguments,
        [string]$Description
    )
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE."
    }
}

$venvDir = Join-Path $root 'venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'

$rebuildVenv = -not (Test-Path $venvPython)
if (-not $rebuildVenv) {
    try {
        & $venvPython --version *> $null
        $rebuildVenv = $LASTEXITCODE -ne 0
    } catch {
        $rebuildVenv = $true
    }
}

if ($rebuildVenv) {
    if (Test-Path $venvDir) {
        Write-Host 'Removing stale virtual environment...'
        Remove-Item -LiteralPath $venvDir -Recurse -Force
    }
    Write-Host 'Creating virtual environment...'
    Invoke-Checked -Executable $pythonExe -Arguments @('-m', 'venv', $venvDir) -Description 'Virtual environment creation'
}

Write-Host 'Checking dependencies...'
& $venvPython -c "import flask, joblib, numpy, pytest, sklearn, xgboost"
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Installing missing dependencies...'
    Invoke-Checked -Executable $venvPython -Arguments @('-m', 'pip', '--disable-pip-version-check', 'install', '-r', 'requirements.txt') -Description 'Dependency installation'
}

function Test-Server {
    try {
        Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/models' -Method Get -TimeoutSec 2 -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-Server)) {
    $logDir = Join-Path $root 'logs'
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    $stdoutLog = Join-Path $logDir 'flask.stdout.log'
    $stderrLog = Join-Path $logDir 'flask.stderr.log'
    Write-Host 'Starting Flask server...'
    Start-Process -WindowStyle Hidden -FilePath $venvPython -ArgumentList '-m', 'app.app' -WorkingDirectory $root -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog

    $attempt = 0
    while (-not (Test-Server) -and $attempt -lt 20) {
        Start-Sleep -Seconds 1
        $attempt++
    }
    if (-not (Test-Server)) {
        throw "Flask did not start. See $stderrLog"
    }
}

Write-Host 'Running tests...'
Invoke-Checked -Executable $venvPython -Arguments @('-m', 'pytest', '-q') -Description 'Test suite'

$body = @{ sample = 'Test sample 12345' } | ConvertTo-Json
$response = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/scan' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 10
$response | ConvertTo-Json -Depth 5
Write-Host 'The project is running at http://127.0.0.1:5000'
