param(
  [ValidateRange(1,65535)][int]$Port = 8776
)
$ErrorActionPreference = 'Stop'
$runtime = Split-Path -Parent $PSScriptRoot
$nodeCommand = Get-Command node -ErrorAction Stop
$npmCommand = Get-Command npm -ErrorAction Stop
$logFolder = Join-Path $env:LOCALAPPDATA 'SOL\Puppeteer'
New-Item -Path $logFolder -ItemType Directory -Force | Out-Null
$baseUrl = 'http://127.0.0.1:' + $Port
Push-Location $runtime
try {
  & $npmCommand.Source ci --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw 'npm ci failed' }
  try {
    $prior = Invoke-RestMethod -Uri ($baseUrl + '/health') -TimeoutSec 2
    if ($prior.service -eq 'SOL_PUPPETEER_RUNTIME' -and $prior.browser_connected) {
      Write-Output 'SOL_PUPPETEER_ALREADY_RUNNING'
      return
    }
  } catch { }
  $env:SOL_PUPPETEER_PORT = [string]$Port
  $child = Start-Process -FilePath $nodeCommand.Source -ArgumentList @('src/server.mjs') -WorkingDirectory $runtime -RedirectStandardOutput (Join-Path $logFolder 'stdout.log') -RedirectStandardError (Join-Path $logFolder 'stderr.log') -WindowStyle Hidden -PassThru
  $healthy = $false
  for ($i = 0; $i -lt 60; $i++) {
    if ($child.HasExited) { break }
    try {
      $health = Invoke-RestMethod -Uri ($baseUrl + '/health') -TimeoutSec 2
      if ($health.service -eq 'SOL_PUPPETEER_RUNTIME' -and $health.browser_connected) {
        $healthy = $true
        break
      }
    } catch { }
    Start-Sleep -Milliseconds 500
  }
  if (-not $healthy) {
    if (-not $child.HasExited) { Stop-Process -Id $child.Id -ErrorAction SilentlyContinue }
    throw 'Puppeteer did not reach health ready'
  }
  @{pid=$child.Id;port=$Port;state='ready';utc=(Get-Date).ToUniversalTime().ToString('o')} |
    ConvertTo-Json | Set-Content -Path (Join-Path $logFolder 'runtime-state.json') -Encoding UTF8
  Write-Output ('SOL_PUPPETEER_READY '+$baseUrl+'/health PID='+$child.Id)
} finally {
  Pop-Location
}
