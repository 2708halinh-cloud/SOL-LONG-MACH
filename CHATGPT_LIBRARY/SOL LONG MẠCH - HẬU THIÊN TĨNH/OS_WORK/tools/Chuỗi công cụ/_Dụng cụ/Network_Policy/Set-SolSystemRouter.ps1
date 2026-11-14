# User-owned Windows 11 Pro only; intended to run on the PC, not in ChatGPT cloud.
# Status and Warn never modify networking. Block -Apply adds reversible exact-host
# overrides; IP firewall requires separately identified dedicated destination IPs.
[CmdletBinding()]
param(
  [ValidateSet('Status','Warn','Block','Rollback')][string]$Mode = 'Status',
  [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$hostsPath = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$start = '# SOL_SYSTEM_ROUTER_BEGIN'
$end = '# SOL_SYSTEM_ROUTER_END'
$exactHosts = @('openai.com','api.openai.com','auth.openai.com','platform.openai.com','chatgpt.com','chat.openai.com','oaistatic.com','oaiusercontent.com','oaistatsig.com','openaimerge.com')
$original = [IO.File]::ReadAllText($hostsPath)
$hasBlock = $original.Contains($start)
if ($Mode -eq 'Status') {
  [pscustomobject]@{Computer=$env:COMPUTERNAME; Mode='Status'; ExactHostsBlocked=$hasBlock; HostsPath=$hostsPath; WildcardsOrDynamicIPBlocked=$false}
  exit 0
}
if ($Mode -eq 'Warn') {
  Write-Warning 'SOL System_Router WARN. No firewall, hosts, DNS, or route changes performed.'
  exit 0
}
if (-not $Apply) { throw 'Explicit -Apply required for Block/Rollback. No changes made.' }
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Run as Windows Administrator. No changes made.'
}
if ($Mode -eq 'Block') {
  if ($hasBlock) { Write-Output 'ALREADY_APPLIED'; exit 0 }
  $backup = Join-Path $env:TEMP ('SOL_HOSTS_BACKUP_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.bak')
  [IO.File]::Copy($hostsPath, $backup, $false)
  $addition = "`r`n$start`r`n" + (($exactHosts | ForEach-Object { '0.0.0.0 ' + $_ }) -join "`r`n") + "`r`n$end`r`n"
  [IO.File]::AppendAllText($hostsPath, $addition, [Text.Encoding]::ASCII)
  Clear-DnsClientCache
  if (-not [IO.File]::ReadAllText($hostsPath).Contains($start)) { throw 'HOSTS_READBACK_FAILED' }
  Write-Output ('APPLIED_EXACT_NAMES_ONLY; BACKUP=' + $backup)
  Write-Warning 'Does NOT cover all subdomains, direct IP, DoH, VPN or dynamic CDN addresses; requires separately configured egress gateway for total blocking.'
  exit 0
}
if ($Mode -eq 'Rollback') {
  if (-not $hasBlock) { Write-Output 'NOTHING_TO_ROLLBACK'; exit 0 }
  $escapedStart = [regex]::Escape($start)
  $escapedEnd = [regex]::Escape($end)
  $replacement = [regex]::Replace($original, '(?s)\r?\n?' + $escapedStart + '.*?' + $escapedEnd + '\r?\n?', "`r`n", 1)
  $backup = Join-Path $env:TEMP ('SOL_HOSTS_ROLLBACK_BACKUP_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.bak')
  [IO.File]::Copy($hostsPath, $backup, $false)
  [IO.File]::WriteAllText($hostsPath, $replacement, [Text.Encoding]::UTF8)
  Clear-DnsClientCache
  if ([IO.File]::ReadAllText($hostsPath).Contains($start)) { throw 'ROLLBACK_READBACK_FAILED' }
  Write-Output 'EXACT_HOSTS_OVERRIDES_REMOVED'
}