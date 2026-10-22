# Windows survival preflight, strictly READ-ONLY.
# No deletes, update resets, DISM, CHKDSK /f, reboot, VHDX mount or new C: backups.
[CmdletBinding()]
param([string]$Drive = 'C')
$ErrorActionPreference = 'Stop'
if ($Drive -notmatch '^[A-Za-z]$') { throw 'Drive must be a single letter' }
$target = $Drive.ToUpperInvariant() + ':\\'
$disk = [System.IO.DriveInfo]::new($target)
if (-not $disk.IsReady) { throw 'DRIVE_NOT_READY' }
[long]$capacity = $disk.TotalSize
[long]$free = $disk.AvailableFreeSpace
if ($capacity -le 0) { throw 'DRIVE_CAPACITY_INVALID' }
$freePercent = [math]::Round(100.0 * $free / $capacity, 2)
$usedPercent = [math]::Round(100.0 - $freePercent, 2)
$grade = if ($freePercent -le 5) { 'CRITICAL_PROTECT_DATA' }
         elseif ($freePercent -le 15) { 'HIGH_RISK' }
         elseif ($freePercent -le 20) { 'WARNING' }
         else { 'CAPACITY_OK' }
$updateNames = @('TiWorker','TrustedInstaller','MoUsoCoreWorker','SetupHost')
$updateActive = @(Get-Process -Name $updateNames -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty ProcessName -Unique)
$data = [ordered]@{
    schema = 'WINDOWS_C_SURVIVAL_READ_ONLY_V1'
    observed_utc = [datetime]::UtcNow.ToString('o')
    device_name = $env:COMPUTERNAME
    drive = $target
    total_bytes = $capacity
    free_bytes = $free
    free_percent = $freePercent
    used_percent = $usedPercent
    safety_grade = $grade
    updates_processes_observed = $updateActive
    safe_mode = 'OBSERVE_ONLY_NO_DISK_MUTATION'
    destructive_actions_executed = 0
    guidance = if ($grade -eq 'CRITICAL_PROTECT_DATA') {
        'Keep Windows stable; protect files; no automatic cleanup or workload restart. Require scoped review of expendable items.'
    } else {
        'Recheck before restarting heavy VMs, Docker, WSL, indexing or backups.'
    }
}
$data | ConvertTo-Json -Depth 4
if ($grade -eq 'CRITICAL_PROTECT_DATA') { exit 2 }
