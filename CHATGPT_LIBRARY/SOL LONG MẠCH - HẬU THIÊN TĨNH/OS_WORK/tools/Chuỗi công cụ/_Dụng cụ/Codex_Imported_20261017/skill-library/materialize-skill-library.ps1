param(
    [string]$InventoryPath = 'C:\Users\halin\.codex\tools\skill-library\state\source-inventory.json',
    [string]$CollectedRoot = 'C:\Users\halin\.codex\skills\_COLLECTED',
    [string]$OutputPath = 'C:\Users\halin\.codex\tools\skill-library\state\c-materialization.json'
)

$ErrorActionPreference = 'Stop'
$inventory = Get-Content -Raw -LiteralPath $InventoryPath | ConvertFrom-Json
[IO.Directory]::CreateDirectory($CollectedRoot) | Out-Null
$stagingRoot = Join-Path $CollectedRoot '.staging'
[IO.Directory]::CreateDirectory($stagingRoot) | Out-Null

function Get-FileSha([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLower()
}

function Test-Package([object]$Package, [string]$Root) {
    foreach ($file in $Package.files) {
        $path = Join-Path $Root $file.relative_path
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
        $item = Get-Item -LiteralPath $path -Force
        if ($item.Length -ne $file.bytes) { return $false }
        if ((Get-FileSha $path) -ne $file.sha256) { return $false }
    }
    return $true
}

$results = [Collections.Generic.List[object]]::new()
$index = 0
foreach ($package in $inventory.packages) {
    $index += 1
    if ($package.source_class -eq 'RUNTIME_CURRENT') {
        $results.Add([pscustomobject]@{
            source_id = $package.source_id
            source_class = $package.source_class
            package_sha256 = $package.package_sha256
            source_path = $package.package_root
            c_path = $package.package_root
            action = 'KEPT_IN_PLACE'
            verified = (Test-Package $package $package.package_root)
        })
        continue
    }

    $classRoot = Join-Path $CollectedRoot $package.source_class
    $destination = Join-Path $classRoot $package.source_id
    [IO.Directory]::CreateDirectory($classRoot) | Out-Null

    if (Test-Path -LiteralPath $destination) {
        if (-not (Test-Package $package $destination)) {
            throw "Existing destination does not match manifest: $destination"
        }
        $action = 'REUSED_VERIFIED_DESTINATION'
    }
    else {
        $staging = Join-Path $stagingRoot $package.source_id
        if (Test-Path -LiteralPath $staging) { [IO.Directory]::Delete($staging, $true) }
        [IO.Directory]::CreateDirectory($staging) | Out-Null

        if ($package.package_kind -eq 'DIRECTORY') {
            & robocopy.exe $package.package_root $staging /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
            if ($LASTEXITCODE -gt 7) {
                foreach ($file in $package.files) {
                    $sourceFile = Join-Path $package.package_root $file.relative_path
                    $targetFile = Join-Path $staging $file.relative_path
                    [IO.Directory]::CreateDirectory((Split-Path -Parent $targetFile)) | Out-Null
                    Copy-Item -LiteralPath $sourceFile -Destination $targetFile -Force
                }
            }
        }
        else {
            Copy-Item -LiteralPath $package.package_root -Destination (Join-Path $staging ([IO.Path]::GetFileName($package.package_root))) -Force
        }

        if (-not (Test-Package $package $staging)) {
            throw "Staging verification failed: $($package.package_root)"
        }
        [IO.Directory]::Move($staging, $destination)
        $action = 'COPIED_AND_VERIFIED'
    }

    $results.Add([pscustomobject]@{
        source_id = $package.source_id
        source_class = $package.source_class
        requested_action = $package.requested_action
        package_sha256 = $package.package_sha256
        source_path = $package.package_root
        c_path = $destination
        action = $action
        verified = (Test-Package $package $destination)
    })

    if (($index % 25) -eq 0) { Write-Output "MATERIALIZED $index / $($inventory.package_count)" }
}

if (@($results | Where-Object { -not $_.verified }).Count -ne 0) { throw 'One or more C packages failed verification.' }
if (Test-Path -LiteralPath $stagingRoot) {
    $children = @(Get-ChildItem -LiteralPath $stagingRoot -Force -ErrorAction SilentlyContinue)
    if ($children.Count -eq 0) { [IO.Directory]::Delete($stagingRoot, $false) }
}

$manifest = [ordered]@{
    schema_version = '1.0'
    generated_at = (Get-Date).ToString('o')
    inventory_sha256 = (Get-FileHash -LiteralPath $InventoryPath -Algorithm SHA256).Hash.ToLower()
    home_source_protocol = $inventory.home_source_protocol
    asstangt_document_id = $inventory.asstangt_document_id
    asstangt_revision_id = $inventory.asstangt_revision_id
    t007_sha256 = $inventory.t007_sha256
    provenance = $inventory.provenance
    package_count = $results.Count
    verified_count = @($results | Where-Object verified).Count
    results = @($results)
}
$temp = "$OutputPath.$([Guid]::NewGuid().ToString('N')).tmp"
$manifest | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $temp -Encoding UTF8
Move-Item -LiteralPath $temp -Destination $OutputPath -Force
$readback = Get-Content -Raw -LiteralPath $OutputPath | ConvertFrom-Json
if ($readback.package_count -ne $inventory.package_count -or $readback.verified_count -ne $inventory.package_count) { throw 'C materialization readback mismatch.' }

[pscustomobject]@{
    output = $OutputPath
    package_count = $readback.package_count
    verified_count = $readback.verified_count
    sha256 = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLower()
} | ConvertTo-Json