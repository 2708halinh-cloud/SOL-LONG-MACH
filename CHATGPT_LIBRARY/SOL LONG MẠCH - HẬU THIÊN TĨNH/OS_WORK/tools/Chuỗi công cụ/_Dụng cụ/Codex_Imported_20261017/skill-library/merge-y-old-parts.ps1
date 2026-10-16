$ErrorActionPreference = 'Stop'
$state = 'C:\Users\halin\.codex\tools\skill-library\state'
$parts = 1..9 | ForEach-Object {
    $path = Join-Path $state ("root-y-old-part-$_.json")
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing $path" }
    Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
}
$packages = @($parts.packages | Sort-Object package_root -Unique)
$manifest = [ordered]@{
    schema_version = '1.0'
    generated_at = (Get-Date).ToString('o')
    host = $env:COMPUTERNAME
    home_source_protocol = 'HOME_SOURCE -> ASSTANGT -> T007_SKILL'
    asstangt_document_id = '1ATodMSDxYaA_sc3SEq8viWkiw6to76bb-Y3n51Pa9eU'
    asstangt_revision_id = 'AIroW34RV70IBwiEVQbUHF67hrh0dF9wvixcC_W8Oh-OIw0Aj4Cj-W5UdP47vkbJIVqIPjxrsBWCHA-kPrcj-MFKXF4o9mYdHJUDxJcLa9c'
    t007_sha256 = '079bf64b906e0b3fb2f1444eeaf990c86ca6c1365dd51a4703dec6471f1ae47e'
    provenance = [ordered]@{ original_authors = 'PRESERVED_PER_SOURCE; NOT INFERRED FROM LOCATION'; executing_actor = 'Codex'; requested_by = 'Hà Linh' }
    roots = @([pscustomobject]@{ path = 'Y:\.codex_old_RETRIEVED\skills'; exists = $true; skill_file_count = $packages.Count })
    package_count = $packages.Count
    byte_unique_count = @($packages.package_sha256 | Sort-Object -Unique).Count
    packages = $packages
}
$out = Join-Path $state 'root-y-old.json'
$tmp = "$out.$([Guid]::NewGuid().ToString('N')).tmp"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $tmp -Encoding UTF8
Move-Item -LiteralPath $tmp -Destination $out -Force
$readback = Get-Content -Raw -LiteralPath $out | ConvertFrom-Json
if ($readback.package_count -ne 9) { throw 'Y old package count mismatch.' }
[pscustomobject]@{ output = $out; package_count = $readback.package_count; byte_unique_count = $readback.byte_unique_count; sha256 = (Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLower() } | ConvertTo-Json