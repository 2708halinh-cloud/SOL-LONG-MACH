@echo off
tasklist /FI "IMAGENAME eq AdGuardHome.exe" | find /I "AdGuardHome.exe" >nul
if errorlevel 1 start "" /min "C:\Users\halin\AppData\Local\Microsoft\WinGet\Packages\AdGuard.AdGuardHome_Microsoft.Winget.Source_8wekyb3d8bbwe\AdGuardHome\AdGuardHome.exe" -w D:\AGH -c D:\AGH\AdGuardHome.yaml --no-check-update

tasklist /FI "IMAGENAME eq nginx.exe" | find /I "nginx.exe" >nul
if errorlevel 1 start "" /min "C:\Users\halin\AppData\Local\Microsoft\WinGet\Packages\nginxinc.nginx_Microsoft.Winget.Source_8wekyb3d8bbwe\nginx-1.31.6\nginx.exe" -p D:\OpenAI_TCP_GATE\ -c conf\nginx.conf

start "" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZERO_DAY_GUARD\dns_resident_watch.ps1
