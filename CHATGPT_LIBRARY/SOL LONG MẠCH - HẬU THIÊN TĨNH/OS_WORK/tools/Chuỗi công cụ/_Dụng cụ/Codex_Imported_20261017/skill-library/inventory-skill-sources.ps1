param(
    [string]$OutputPath = 'C:\Users\halin\.codex\tools\skill-library\state\source-inventory.json',
    [switch]$Diagnostic,
    [string[]]$OnlyRoot,
    [string]$DiagnosticLog,
    [string[]]$OnlySkillFile
)

$ErrorActionPreference = 'Stop'

$sourceRoots = @(
    [pscustomobject]@{ Path = 'C:\Users\halin\.codex\skills'; Class = 'RUNTIME_CURRENT'; Action = 'KEEP_AND_MIRROR' },
    [pscustomobject]@{ Path = 'C:\Users\halin\.codex\plugins'; Class = 'PLUGIN_RUNTIME'; Action = 'CENTRALIZE_WITH_JUNCTION' },
    [pscustomobject]@{ Path = 'C:\Users\halin\.agents\skills'; Class = 'AGENTS_RUNTIME'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'C:\Users\halin\skills'; Class = 'USER_SKILLS'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'Y:\.codex_old_RETRIEVED\skills'; Class = 'OLD_CODEX_Y'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'Y:\AGENT\SKILL'; Class = 'AGENT_SKILL_Y'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'Y:\AGENT\ALL_OLD'; Class = 'AGENT_ALL_OLD_Y'; Action = 'RELOCATE_HISTORICAL_CAPABILITY_ONLY' },
    [pscustomobject]@{ Path = 'Y:\OneDrive_Halinh\.codex'; Class = 'ONEDRIVE_OLD_CODEX'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'Z:\CODEX_SHARED_ROOT'; Class = 'CODEX_SHARED_Z'; Action = 'RELOCATE' },
    [pscustomobject]@{ Path = 'Z:\.codex_old_RETRIEVED'; Class = 'OLD_CODEX_Z'; Action = 'RELOCATE' }
)

if ($OnlyRoot) {
    $sourceRoots = @($sourceRoots | Where-Object { $OnlyRoot -contains $_.Path })
}

function Get-StringHash([string]$Value) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Value)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLower()
}

function Get-FileSha([string]$Path) {
    $stream = [IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
    try {
        return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLower()
    }
    finally {
        $stream.Dispose()
    }
}

function Get-PackageRecord($Source, [string]$SkillFile) {
    $skillItem = Get-Item -LiteralPath $SkillFile -Force
    $isAtSourceRoot = $skillItem.Directory.FullName.TrimEnd('\') -ieq $Source.Path.TrimEnd('\')
    $isHistoricalLoose = $Source.Class -eq 'AGENT_ALL_OLD_Y'
    $isEntry = ($skillItem.Name -ieq 'SKILL.md') -and (-not $isAtSourceRoot) -and (-not $isHistoricalLoose)
    $packageRoot = if ($isEntry) { $skillItem.Directory.FullName } else { $skillItem.FullName }
    $files = if ($isEntry) {
        @(Get-ChildItem -LiteralPath $packageRoot -File -Force -Recurse -ErrorAction Stop | Sort-Object FullName)
    }
    else {
        @($skillItem)
    }

    $fileRows = foreach ($file in $files) {
        if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "FILE_START $((Get-Date).ToString('o')) $($file.FullName)`r`n") }
        $relative = if ($isEntry) {
            [IO.Path]::GetRelativePath($packageRoot, $file.FullName)
        }
        else {
            $file.Name
        }
        $row = [pscustomobject]@{
            relative_path = $relative
            bytes = $file.Length
            sha256 = Get-FileSha $file.FullName
        }
        if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "FILE_END $((Get-Date).ToString('o')) $($file.FullName)`r`n") }
        $row
    }

    if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "SIGNATURE_START $((Get-Date).ToString('o')) $packageRoot`r`n") }
    $signature = ($fileRows | ForEach-Object { '{0}|{1}|{2}' -f $_.relative_path, $_.bytes, $_.sha256 }) -join "`n"
    $sourceId = '{0}_{1}' -f $Source.Class, (Get-StringHash $packageRoot).Substring(0, 16)
    $record = [pscustomobject]@{
        source_id = $sourceId
        source_class = $Source.Class
        requested_action = $Source.Action
        source_root = $Source.Path
        package_root = $packageRoot
        package_kind = if ($isEntry) { 'DIRECTORY' } else { 'LOOSE_FILE' }
        entry_file = $skillItem.FullName
        file_count = $fileRows.Count
        total_bytes = ($fileRows | Measure-Object bytes -Sum).Sum
        package_sha256 = Get-StringHash $signature
        files = @($fileRows)
    }
    if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "RECORD_END $((Get-Date).ToString('o')) $packageRoot`r`n") }
    $record
}

$packages = [Collections.Generic.List[object]]::new()
$rootStatus = [Collections.Generic.List[object]]::new()
foreach ($source in $sourceRoots) {
    if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "ROOT_START $((Get-Date).ToString('o')) $($source.Path)`r`n") }
    if (-not (Test-Path -LiteralPath $source.Path)) {
        $rootStatus.Add([pscustomobject]@{ path = $source.Path; exists = $false; skill_file_count = 0 })
        continue
    }

    $skillFiles = @(& rg --files -uu -g 'SKILL.md' -g '*SKILL*.md' -- $source.Path 2>$null)
    if ($OnlySkillFile) { $skillFiles = @($skillFiles | Where-Object { $OnlySkillFile -contains $_ }) }
    if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "FILES_FOUND $((Get-Date).ToString('o')) $($skillFiles.Count)`r`n") }
    $rootStatus.Add([pscustomobject]@{ path = $source.Path; exists = $true; skill_file_count = $skillFiles.Count })
    foreach ($skillFile in $skillFiles) {
        if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "PACKAGE_START $((Get-Date).ToString('o')) $skillFile`r`n") }
        if ($Diagnostic) { Write-Output ('SCAN_PACKAGE ' + $skillFile) }
        $packages.Add((Get-PackageRecord $source $skillFile))
        if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "PACKAGE_END $((Get-Date).ToString('o')) $skillFile`r`n") }
    }
}

$uniquePackages = @($packages | Sort-Object package_root -Unique)
if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "SERIALIZE_START $((Get-Date).ToString('o')) $($uniquePackages.Count)`r`n") }
$manifest = [ordered]@{
    schema_version = '1.0'
    generated_at = (Get-Date).ToString('o')
    host = $env:COMPUTERNAME
    home_source_protocol = 'HOME_SOURCE -> ASSTANGT -> T007_SKILL'
    asstangt_document_id = '1ATodMSDxYaA_sc3SEq8viWkiw6to76bb-Y3n51Pa9eU'
    asstangt_revision_id = 'AIroW34RV70IBwiEVQbUHF67hrh0dF9wvixcC_W8Oh-OIw0Aj4Cj-W5UdP47vkbJIVqIPjxrsBWCHA-kPrcj-MFKXF4o9mYdHJUDxJcLa9c'
    t007_sha256 = '079bf64b906e0b3fb2f1444eeaf990c86ca6c1365dd51a4703dec6471f1ae47e'
    provenance = [ordered]@{
        original_authors = 'PRESERVED_PER_SOURCE; NOT INFERRED FROM LOCATION'
        executing_actor = 'Codex'
        requested_by = 'Hà Linh'
    }
    roots = @($rootStatus)
    package_count = $uniquePackages.Count
    byte_unique_count = @($uniquePackages.package_sha256 | Sort-Object -Unique).Count
    packages = $uniquePackages
}

$parent = Split-Path -Parent $OutputPath
[IO.Directory]::CreateDirectory($parent) | Out-Null
$temp = "$OutputPath.$([Guid]::NewGuid().ToString('N')).tmp"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temp -Encoding UTF8
Move-Item -LiteralPath $temp -Destination $OutputPath -Force
if ($DiagnosticLog) { [IO.File]::AppendAllText($DiagnosticLog, "SERIALIZE_END $((Get-Date).ToString('o'))`r`n") }

$readback = Get-Content -Raw -LiteralPath $OutputPath | ConvertFrom-Json
if ($readback.package_count -ne $uniquePackages.Count) {
    throw 'Inventory readback count mismatch.'
}

[pscustomobject]@{
    output = $OutputPath
    package_count = $readback.package_count
    byte_unique_count = $readback.byte_unique_count
    sha256 = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLower()
} | ConvertTo-Json