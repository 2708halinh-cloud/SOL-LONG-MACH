#requires -Version 5.1
<#
Read-only inventory for browser RAM acceleration and existing ububu_daemon.
Never imports/executes unknown daemon scripts, moves profiles, formats disks,
copies credentials, or reveals browser history/cookies/tokens.
#>
[CmdletBinding()]
param(
    [string]$DaemonRoot = 'G:\OS_Workspace\ububu_daemon',
    [string[]]$RamDriveCandidates = @('R:\','S:\','T:\'),
    [int]$MaxDaemonFiles = 1200,
    [int]$MaxDepth = 5
)
$ErrorActionPreference = 'Stop'
function Safe-Item($Path) {
    try { return Get-Item -LiteralPath $Path -ErrorAction Stop } catch { return $null }
}
function Safe-ProcessNames {
    @(Get-Process -ErrorAction SilentlyContinue |
      Where-Object { $_.ProcessName -match 'chrome|firefox|msedge|imdisk|hwinfo|ububu' } |
      Select-Object -ExpandProperty ProcessName -Unique)
}
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$memTotal = [int64]$cs.TotalPhysicalMemory
$memAvailable = [int64]$os.FreePhysicalMemory * 1024
$memory = [ordered]@{
    total_bytes = $memTotal
    available_bytes = $memAvailable
    available_pct = if($memTotal -gt 0){[math]::Round(100*$memAvailable/$memTotal,1)}else{$null}
}
$ramDisks = @(
    foreach ($letter in $RamDriveCandidates) {
        $drive = $letter.TrimEnd('\')
        $item = Safe-Item $drive
        if ($null -eq $item) { continue }
        $volume = Get-CimInstance Win32_LogicalDisk -Filter ("DeviceID='" + $drive.TrimEnd(':') + ":'") -ErrorAction SilentlyContinue
        [pscustomobject]@{
            path = $letter
            exists = $true
            drive_type = if($volume){$volume.DriveType}else{$null}
            filesystem = if($volume){$volume.FileSystem}else{$null}
            volume_label = if($volume){$volume.VolumeName}else{$null}
            free_bytes = if($volume){$volume.FreeSpace}else{$null}
            RAM_backed_verified = $false
            warning = 'A drive letter is not proof of a RAM disk; inspect driver and device mapping'
        }
    }
)
$tools = @(
    foreach($name in @('imdisk.exe','awealloc.exe','chrome.exe','firefox.exe','wsl.exe')) {
        $c = Get-Command $name -ErrorAction SilentlyContinue
        if($c){[pscustomobject]@{name=$name;available=$true;location=$c.Source}}
        else{[pscustomobject]@{name=$name;available=$false;location=$null}}
    }
)
$profileRoots = @(
    Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data'
    Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\User Data'
    Join-Path $env:APPDATA 'Mozilla\Firefox\Profiles'
)
$profiles = @(foreach($p in $profileRoots) {
    $item = Safe-Item $p
    [pscustomobject]@{
        path=$p; exists=($null -ne $item)
        is_reparse_point=if($item){[bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)}else{$null}
        role='PERSISTENT_BROWSER_PROFILE_NEVER_MOVE_TO_VOLATILE_RAM'
    }
})
$roots = @($DaemonRoot)
$queue = [System.Collections.Queue]::new()
$queue.Enqueue([pscustomobject]@{p=$DaemonRoot;depth=0})
$seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$entries = [System.Collections.Generic.List[object]]::new()
$visited = 0
while ($queue.Count -gt 0 -and $visited -lt $MaxDaemonFiles) {
    $node = $queue.Dequeue()
    if (-not $seen.Add($node.p)) { continue }
    $parent = Safe-Item $node.p
    if (-not $parent -or -not $parent.PSIsContainer) { continue }
    if ([bool]($parent.Attributes -band [IO.FileAttributes]::ReparsePoint)) { continue }
    foreach ($item in @(Get-ChildItem -LiteralPath $node.p -Force -ErrorAction SilentlyContinue)) {
        $visited++
        if ($visited -gt $MaxDaemonFiles){ break }
        if([bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)){ continue }
        if($item.PSIsContainer){
            if($node.depth -lt $MaxDepth) {
                $queue.Enqueue([pscustomobject]@{p=$item.FullName;depth=($node.depth+1)})
            }
        } elseif ($item.Extension -in @('.ps1','.py','.sh','.bat','.cmd','.toml','.json','.ini','.yaml','.yml','.md')) {
            $entries.Add([pscustomobject]@{
                path=$item.FullName;bytes=$item.Length;modified_utc=$item.LastWriteTimeUtc.ToString('o')
                classification='FILE_METADATA_ONLY_NOT_EXECUTED'
            })
        }
    }
}
[pscustomobject]@{
    schema = 'SOL_UBUBU_RAM_HOST_AUDIT_V1'
    observed_utc = [DateTime]::UtcNow.ToString('o')
    host = $env:COMPUTERNAME
    memory = $memory
    installed_tools = $tools
    browser_processes = @(Safe-ProcessNames)
    browser_profiles = $profiles
    ramdisk_candidates = $ramDisks
    daemon_root = $DaemonRoot
    daemon_present = [bool](Safe-Item $DaemonRoot)
    daemon_files = @($entries)
    daemon_entries_scanned = $visited
    daemon_scan_truncated = ($visited -ge $MaxDaemonFiles -or $queue.Count -gt 0)
    applied_changes = 0
    changed_or_deleted_source_files = 0
} | ConvertTo-Json -Depth 8
