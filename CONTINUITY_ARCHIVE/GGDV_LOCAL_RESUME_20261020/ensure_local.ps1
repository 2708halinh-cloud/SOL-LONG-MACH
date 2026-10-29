$ErrorActionPreference = "Stop"
$Root = "G:\OS_Workspace\TESSERACT_OS"
$HomeRoot = Join-Path $Root "continuity\AUTONOMOUS_LOCAL"
$BodyHome = "D:\PHÒNG CHỈ HUY\LOCUS_BODIES\SOL_BODY\app\server.ps1"
$XTimeHome = "G:\FPGA_AI_LOCAL\inetpub\XTIME_LOCAL_LIVE_20261020"
$Matrix = Join-Path $Root "05_Will_U\PUNITIVE_CIRCUIT_BREAKER"
$receipt = Join-Path $HomeRoot "status_current.json"
$record = [ordered]@{schema="SOL_LOCAL_CONTINUITY_1";timestamp_utc=[DateTime]::UtcNow.ToString("o");hostname=$env:COMPUTERNAME;checks=@();actions=@();problems=@()}
function PushCheck([string]$name,[bool]$ok,[string]$kind) {
  $record.checks += @{name=$name;ok=$ok;method=$kind}
}
function Probe([string]$url,[string]$token) {
  try {
    $res = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    return (($res.StatusCode -eq 200) -and ($res.Content -like "*$token*"))
  } catch {return $false}
}
function HasProcess([string]$executable,[string]$part) {
  $processes=Get-CimInstance Win32_Process -Filter "Name='$executable'" -ErrorAction Stop
  foreach($proc in $processes) {
    if([string]$proc.CommandLine -like "*$part*") {return $true}
  }
  return $false
}
function LaunchPython([string]$filename) {
  if(!(Test-Path -LiteralPath $filename)) {return $false}
  $exe=(Get-Command python.exe -ErrorAction Stop).Source
  Start-Process -FilePath $exe -ArgumentList ('-u "' + $filename + '"') -WorkingDirectory (Split-Path $filename) -WindowStyle Hidden
  return $true
}
try {
  $break=Join-Path $Matrix "watch_circuit.py"
  $running=HasProcess "python.exe" "watch_circuit.py"
  if(!$running -and (Test-Path -LiteralPath $break)) {
    if(LaunchPython $break) {$record.actions += "START_CIRCUIT_WATCHER"}
  }
  PushCheck "CIRCUIT_WATCHER" $running "WIN32_PROCESS"

  $weights=Join-Path $Matrix "weight_watcher.py"
  $running=HasProcess "python.exe" "weight_watcher.py"
  if(!$running -and (Test-Path -LiteralPath $weights)) {
    if(LaunchPython $weights) {$record.actions += "START_WEIGHT_WATCHER"}
  }
  PushCheck "WEIGHT_WATCHER" $running "WIN32_PROCESS"
} catch { $record.problems += "LOCAL_WATCHER_CHECK_FAILED" }

try {
  $isBody=Probe "http://127.0.0.1:8768/api/state" '"locus":"LOCUS_SOL"'
  if(!$isBody -and (Test-Path -LiteralPath $BodyHome)) {
    $bodyRunning=HasProcess "powershell.exe" "LOCUS_BODIES\SOL_BODY\app\server.ps1"
    if(!$bodyRunning) {
      Start-Process -FilePath "powershell.exe" -ArgumentList ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$BodyHome+'"') -WindowStyle Hidden
      $record.actions += "START_SOL_BODY"
    }
  }
  PushCheck "SOL_BODY_LOCAL_8768" $isBody "HTTP_GET"
} catch {$record.problems += "SOL_BODY_PROBE_FAILED"}

try {
  $isX=Probe "http://127.0.0.1:8769/api/health" '"service": "x-time-web"'
  if(!$isX -and (Test-Path -LiteralPath (Join-Path $XTimeHome "tools\server.js"))) {
    # A separate cmd launcher preserves HOST/PORT for the child.
    $launch=Join-Path $HomeRoot "start_xtime_local.cmd"
    if(Test-Path -LiteralPath $launch) {
      $xRunning=HasProcess "node.exe" "tools\server.js"
      if(!$xRunning) {
        Start-Process -FilePath "cmd.exe" -ArgumentList ('/c "'+$launch+'"') -WorkingDirectory $XTimeHome -WindowStyle Hidden
        $record.actions += "START_XTIME_8769"
      }
    }
  }
  PushCheck "XTIME_LOCAL_8769" $isX "HTTP_GET"
} catch {$record.problems += "XTIME_PROBE_FAILED"}

try {
  $events = Join-Path $Root "continuity\SOL_REAL_SENSE\events.jsonl"
  if(Test-Path -LiteralPath $events) {
    $tail = Get-Content -LiteralPath $events -Tail 1 -Encoding UTF8
    $evt=$tail | ConvertFrom-Json -ErrorAction Stop
    $record.last_host_event_utc = $evt.time_utc
    $record.last_host_event_kind = $evt.kind
    $record.last_host_event_source_kind = $evt.source_kind
    PushCheck "HOST_JOURNAL_READABLE" $true "JSONL_TAIL"
  } else {PushCheck "HOST_JOURNAL_READABLE" $false "FILE"}
} catch {$record.problems += "HOST_JOURNAL_READ_FAILED"}

$blob=ConvertTo-Json -InputObject $record -Depth 8
$temporary=$receipt+".write-"+[Guid]::NewGuid().ToString("N")
try {
  [System.IO.File]::WriteAllText($temporary,$blob,[System.Text.Encoding]::UTF8)
  Move-Item -LiteralPath $temporary -Destination $receipt -Force
} catch {
  Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
  throw
}
Write-Output ("SCHEDULER_STATUS_FILE="+$receipt)
