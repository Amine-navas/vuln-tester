Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$connections = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if (-not $connections) {
    Write-Host 'No server is listening on port 5000.'
    exit 0
}

$processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($processId in $processIds) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if (-not $process) { continue }

    if ($process.ProcessName -notlike 'python*') {
        Write-Warning "Port 5000 is used by $($process.ProcessName) (PID $processId); it was not stopped."
        continue
    }

    Stop-Process -Id $processId -Force
    Write-Host "Flask server stopped (PID $processId)."
}
