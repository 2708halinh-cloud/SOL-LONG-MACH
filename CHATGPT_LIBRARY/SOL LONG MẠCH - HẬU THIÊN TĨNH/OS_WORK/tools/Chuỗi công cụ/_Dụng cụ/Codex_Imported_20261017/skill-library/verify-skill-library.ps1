param(
    [string]$InventoryPath = 'C:\Users\halin\.codex\tools\skill-library\state\source-inventory.json',
    [string]$MaterializationPath = 'C:\Users\halin\.codex\tools\skill-library\state\c-materialization.json',
    [string]$OutputPath = 'C:\Users\halin\.codex\tools\skill-library\state\final-verification.json'
)

$ErrorActionPreference = 'Stop'
$inventory = Get-Content -LiteralPath $InventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$materialization = Get-Content -LiteralPath $MaterializationPath -Raw -Encoding UTF8 | ConvertFrom-Json
$packageById = @{}
foreach ($package in $inventory.packages) {
    $packageById[$package.source_id] = $package
}

$errors = [System.Collections.Generic.List[object]]::new()
$verifiedFiles = 0
$verifiedBytes = [int64]0

foreach ($result in $materialization.results) {
    if (-not $packageById.ContainsKey($result.source_id)) {
        $errors.Add([pscustomobject]@{ source_id = $result.source_id; error = 'PACKAGE_NOT_IN_INVENTORY' })
        continue
    }

    $package = $packageById[$result.source_id]
    foreach ($file in $package.files) {
        $target = Join-Path $result.c_path $file.relative_path

        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
            $errors.Add([pscustomobject]@{ source_id = $result.source_id; path = $target; error = 'FILE_NOT_FOUND' })
            continue
        }

        $item = Get-Item -LiteralPath $target -Force
        $actualHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        if ([int64]$item.Length -ne [int64]$file.bytes -or $actualHash -ne $file.sha256) {
            $errors.Add([pscustomobject]@{
                source_id = $result.source_id
                path = $target
                error = 'CONTENT_MISMATCH'
                expected_bytes = [int64]$file.bytes
                actual_bytes = [int64]$item.Length
                expected_sha256 = $file.sha256
                actual_sha256 = $actualHash
            })
            continue
        }

        $verifiedFiles++
        $verifiedBytes += [int64]$item.Length
    }
}

$receipt = [ordered]@{
    schema_version = 1
    verified_at = (Get-Date).ToString('o')
    inventory_sha256 = (Get-FileHash -LiteralPath $InventoryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    materialization_sha256 = (Get-FileHash -LiteralPath $MaterializationPath -Algorithm SHA256).Hash.ToLowerInvariant()
    package_count = @($inventory.packages).Count
    expected_file_count = [int](($inventory.packages | ForEach-Object { @($_.files).Count } | Measure-Object -Sum).Sum)
    verified_file_count = $verifiedFiles
    verified_bytes = $verifiedBytes
    error_count = $errors.Count
    status = if ($errors.Count -eq 0) { 'PASS' } else { 'FAIL' }
    errors = @($errors)
}

$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$receipt | ConvertTo-Json -Depth 8
if ($errors.Count -ne 0) { exit 1 }