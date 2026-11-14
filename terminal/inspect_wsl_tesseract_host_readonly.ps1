# Đọc dấu nguồn Windows trước khi đổi .wslconfig. Không sửa VHDX, WSL, Docker hay file nào.
$ErrorActionPreference = 'Stop'
$userHome = [Environment]::GetFolderPath('UserProfile')
$possible = @('.wslconfig', '.WslConfig', '.WslDocker') |
    ForEach-Object { Join-Path $userHome $_ } | Select-Object -Unique
$items = @(
    foreach ($p in $possible) {
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            $f = Get-Item -LiteralPath $p
            [pscustomobject]@{
                path = $f.FullName
                length = $f.Length
                modified = $f.LastWriteTimeUtc.ToString('o')
                sha256 = (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
                content = [IO.File]::ReadAllText($p)
            }
        }
    }
)
$vhdPath = 'G:\OS_Workspace\TESSERACT_OS\TESSERACT Hard Disk.vhdx'
$vhd = $null
if (Test-Path -LiteralPath $vhdPath -PathType Leaf) {
    $i = Get-Item -LiteralPath $vhdPath
    $vhd = [pscustomobject]@{path=$i.FullName; length=$i.Length; modified=$i.LastWriteTimeUtc.ToString('o')}
}
$version = @()
try { $version = @(& wsl.exe --version 2>&1 | ForEach-Object { [string]$_ }) } catch { $version = @('WSL_VERSION_UNAVAILABLE') }
$versions = @()
try { $versions = @(& wsl.exe --list --verbose 2>&1 | ForEach-Object { [string]$_ }) } catch { $versions = @('WSL_LIST_UNAVAILABLE') }
[pscustomobject]@{
    schema='SOL_WSL_HOST_AUDIT_READONLY_V1'
    host=$env:COMPUTERNAME
    config_sources=$items
    tesseract_vhdx_metadata=$vhd
    wsl_version=$version
    wsl_distributions=$versions
    modified_files=0
    touched_vhdx=$false
} | ConvertTo-Json -Depth 7
