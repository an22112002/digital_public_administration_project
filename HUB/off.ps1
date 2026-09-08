taskkill /F /IM python.exe

Get-CimInstance Win32_Process | Where-Object {$_.Name -match "python"} | Select-Object ProcessId, Name, CommandLine

Get-ChildItem "D:\deploy\dist\HUB" -Recurse -File | Unblock-File