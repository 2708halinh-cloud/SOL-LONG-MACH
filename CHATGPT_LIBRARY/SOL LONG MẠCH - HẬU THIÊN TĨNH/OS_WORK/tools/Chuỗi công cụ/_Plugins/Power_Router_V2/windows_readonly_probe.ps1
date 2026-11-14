# Exact-host, read-only inspection for SOL_WIN11_HYPERV_GATE.
# No adapter, firewall, DNS, service, partition, or disk mutations.
$ErrorActionPreference = 'Stop'
if ($env:COMPUTERNAME -ine 'DESKTOP-86ITNQ4') { throw 'HOSTNAME_MISMATCH' }
function Read-Link([string]$label) {
  $a = Get-NetAdapter -ErrorAction Stop | Where-Object { $_.InterfaceDescription -eq $label } | Select-Object -First 1
  if ($null -eq $a) { return @{ label=$label; found=$false } }
  $ip = @(Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Select-Object IPAddress,PrefixLength,PrefixOrigin)
  $routes = @(Get-NetRoute -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue |
    Select-Object NextHop,RouteMetric)
  return @{ label=$label; found=$true; adapter_status=[string]$a.Status; ipv4=$ip; default_routes=$routes }
}
$os = Get-CimInstance Win32_OperatingSystem
$svcnames = @('sol-ingest','sol-memory','sol-decision','sol-journal','sol-watchdog')
$services = @($svcnames | ForEach-Object {
  $s = Get-Service -Name $_ -ErrorAction SilentlyContinue
  @{ name=$_; installed=($null -ne $s); status=$(if ($s) { [string]$s.Status } else { 'NOT_INSTALLED' }) }
})
$q = @(Get-Process -Name 'qemu-system-x86_64','qemu-system-aarch64' -ErrorAction SilentlyContinue)
[ordered]@{
  schema='SOL_WINDOWS_TARGET_READBACK/1.0'
  alias='SOL_WIN11_HYPERV_GATE'
  at_utc=(Get-Date).ToUniversalTime().ToString('o')
  host=$env:COMPUTERNAME
  os_caption=$os.Caption
  os_build=$os.BuildNumber
  remote_ndis=(Read-Link 'Remote NDIS Compatible Device')
  hyperv=(Read-Link 'Hyper-V Virtual Ethernet Adapter')
  services=$services
  qemu_process_count=$q.Count
  action='READ_ONLY'
} | ConvertTo-Json -Depth 6 -Compress
