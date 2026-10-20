#requires -Version 5.1
<#
Start Chrome/Edge using ephemeral cache on an already verified ImDisk RAM volume.
DOES NOT move profile, browser history, cookies, logins, extensions or HWiNFO data.
NO diskpart. NO formatting. NO driver installation. NO process termination.
If browser is already running, refuse rather than silently opening old-profile session.
#>
[CmdletBinding()]
param(
    [ValidateSet('Chrome','Edge')][string]$Browser = 'Chrome',
    [ValidatePattern('^[A-Za-z]:\\$')][string]$RamRoot = 'R:\',
    [ValidateRange(64,2048)][int]$CacheMB = 512
)
$ErrorActionPreference = 'Stop'
$letter = $RamRoot.Substring(0,2)
if (-not (Test-Path -LiteralPath $RamRoot -PathType Container)) {
    throw "RAM_DRIVE_MISSING: $RamRoot"
}
$imdisk = Get-Command 'imdisk.exe' -ErrorAction SilentlyContinue
if (-not $imdisk) {
    throw 'IMDISK_NOT_FOUND: do not mistake a normal disk for a RAM disk'
}
$mapping = & $imdisk.Source -l -m $letter 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "IMDISK_DRIVE_NOT_VERIFIED: $letter"
}
$ramEvidence = ($mapping | Out-String)
if (-not $ramEvidence.Trim()) {
    throw "IMDISK_MOUNT_PROOF_EMPTY: $letter"
}
# An ImDisk-mounted letter can still be FILE-BACKED. Treat RAM backing
# as unknown unless the tool positively reports an empty image-file field.
$backingLine = @($ramEvidence -split "\r?\n" |
    Where-Object { $_ -match '(?i)^\s*Image file\s*:' })
if ($backingLine.Count -ne 1) {
    throw "IMDISK_RAM_BACKING_UNVERIFIED: $letter"
}
$backingValue = ($backingLine[0] -replace '(?i)^\s*Image file\s*:\s*','').Trim()
if ($backingValue -and $backingValue -notmatch '^(?i:(none|no image file|\(none\)|\(null\)))$os = Get-CimInstance Win32_OperatingSystem
$freeMB = [math]::Floor(([double]$os.FreePhysicalMemory) / 1024)
if ($freeMB -lt ($CacheMB + 1024)) {
    throw "INSUFFICIENT_FREE_RAM free=$freeMB requestedCacheMB=$CacheMB reservedMB=1024"
}
$pf = [Environment]::GetEnvironmentVariable('ProgramFiles')
$pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
$local = [Environment]::GetEnvironmentVariable('LOCALAPPDATA')
if ($Browser -eq 'Chrome') {
    $image = 'chrome'
    $possible = @(
        (Join-Path $pf 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $pf86 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $local 'Google\Chrome\Application\chrome.exe')
    )
} else {
    $image = 'msedge'
    $possible = @(
        (Join-Path $pf86 'Microsoft\Edge\Application\msedge.exe'),
        (Join-Path $pf 'Microsoft\Edge\Application\msedge.exe')
    )
}
if (@(Get-Process -Name $image -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'BROWSER_ALREADY_RUNNING: close normally before starting a RAM-cache session'
}
$exe = $possible | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -First 1
if (-not $exe) { throw "BROWSER_EXECUTABLE_NOT_FOUND: $Browser" }
$cache = Join-Path $RamRoot ("SOL_EPHEMERAL_CACHE\" + $Browser)
if (-not (Test-Path -LiteralPath $cache -PathType Container)) {
    $null = New-Item -ItemType Directory -Path $cache -Force
}
$bytes = [int64]$CacheMB * 1MB
$arguments = @("--disk-cache-dir=$cache", "--disk-cache-size=$bytes")
$proc = Start-Process -FilePath $exe -ArgumentList $arguments -PassThru
[pscustomobject]@{
    browser=$Browser
    browser_pid=$proc.Id
    cache_path=$cache
    requested_cache_bytes=$bytes
    ram_disk_mapping_checked=$true
    persistent_profile_moved=$false
    existing_profile_deleted=$false
    daemon_touched=$false
} | ConvertTo-Json -Depth 3
) {
    throw "FILE_BACKED_IMDISK_IS_NOT_RAM: $letter"
}
$os = Get-CimInstance Win32_OperatingSystem
$freeMB = [math]::Floor(([double]$os.FreePhysicalMemory) / 1024)
if ($freeMB -lt ($CacheMB + 1024)) {
    throw "INSUFFICIENT_FREE_RAM free=$freeMB requestedCacheMB=$CacheMB reservedMB=1024"
}
$pf = [Environment]::GetEnvironmentVariable('ProgramFiles')
$pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
$local = [Environment]::GetEnvironmentVariable('LOCALAPPDATA')
if ($Browser -eq 'Chrome') {
    $image = 'chrome'
    $possible = @(
        (Join-Path $pf 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $pf86 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $local 'Google\Chrome\Application\chrome.exe')
    )
} else {
    $image = 'msedge'
    $possible = @(
        (Join-Path $pf86 'Microsoft\Edge\Application\msedge.exe'),
        (Join-Path $pf 'Microsoft\Edge\Application\msedge.exe')
    )
}
if (@(Get-Process -Name $image -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'BROWSER_ALREADY_RUNNING: close normally before starting a RAM-cache session'
}
$exe = $possible | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -First 1
if (-not $exe) { throw "BROWSER_EXECUTABLE_NOT_FOUND: $Browser" }
$cache = Join-Path $RamRoot ("SOL_EPHEMERAL_CACHE\" + $Browser)
if (-not (Test-Path -LiteralPath $cache -PathType Container)) {
    $null = New-Item -ItemType Directory -Path $cache -Force
}
$bytes = [int64]$CacheMB * 1MB
$arguments = @("--disk-cache-dir=$cache", "--disk-cache-size=$bytes")
$proc = Start-Process -FilePath $exe -ArgumentList $arguments -PassThru
[pscustomobject]@{
    browser=$Browser
    browser_pid=$proc.Id
    cache_path=$cache
    requested_cache_bytes=$bytes
    ram_disk_mapping_checked=$true
    persistent_profile_moved=$false
    existing_profile_deleted=$false
    daemon_touched=$false
} | ConvertTo-Json -Depth 3
