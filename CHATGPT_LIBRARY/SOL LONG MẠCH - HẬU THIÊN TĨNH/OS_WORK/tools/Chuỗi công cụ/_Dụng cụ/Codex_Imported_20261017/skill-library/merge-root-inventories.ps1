param(
    [string]$StateRoot = 'C:\Users\halin\.codex\tools\skill-library\state',
    [string]$OutputPath = 'C:\Users\halin\.codex\tools\skill-library\state\source-inventory.json'
)

$ErrorActionPreference = 'Stop'
$expected = @(
    'root-c-runtime.json',
    'root-c-plugins.json',
    'root-c-agents.json',
    'root-c-user-skills.json',
    'root-y-old.json',
    'root-y-agent-skill.json',
    'root-y-all-old.json',
    'root-y-onedrive-old.json',
    'root-z-shared.json',
    'root-z-old.json'
)

$documents = foreach ($name in $expected) {
    $path = Join-Path $StateRoot $name
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing root manifest: $path" }
    Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
}

$packages = @($documents.packages | Sort-Object package_root -Unique)
$manifest = [ordered]@{
    schema_version = '1.0'
    generated_at = (Get-Date).ToString('o')
    host = $env:COMPUTERNAME
    home_source_protocol = 'HOME_SOURCE -> ASSTANGT -> T007_SKILL'
    asstangt_document_id = '1ATodMSDxYaA_sc3SEq8viWkiw6to76bb-Y3n51Pa9eU'
    asstangt_revision_id = 'AIroW34RV70IBwiEVQbUHF67hrh0dF9wvixcC_W8Oh-OIw0Aj4Cj-W5UdP47vkbJIVqIPjxrsBWCHA-kPrcj-MFKXF4o9mYdHJUDxJcLa9c'
    t007_path = 'Y:\AGENT\SKILL\SKILL_TXXX\T007_SKILL.md'
    t007_sha256 = '079bf64b906e0b3fb2f1444eeaf990c86ca6c1365dd51a4703dec6471f1ae47e'
    provenance = [ordered]@{
        original_authors = 'PRESERVED_PER_SOURCE; NOT INFERRED FROM LOCATION'
        executing_actor = 'Codex'
        requested_by = 'Hà Linh'
    }
    roots = @($documents.roots)
    package_count = $packages.Count
    byte_unique_count = @($packages.package_sha256 | Sort-Object -Unique).Count
    packages = $packages
}

$temp = "$OutputPath.$([Guid]::NewGuid().ToString('N')).tmp"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temp -Encoding UTF8
Move-Item -LiteralPath $temp -Destination $OutputPath -Force

$readback = Get-Content -Raw -LiteralPath $OutputPath | ConvertFrom-Json
if ($readback.package_count -ne $packages.Count) { throw 'Merged package count mismatch.' }
if (@($readback.roots).Count -ne $expected.Count) { throw 'Merged root count mismatch.' }

[pscustomobject]@{
    output = $OutputPath
    root_count = @($readback.roots).Count
    package_count = $readback.package_count
    byte_unique_count = $readback.byte_unique_count
    sha256 = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLower()
} | ConvertTo-Json