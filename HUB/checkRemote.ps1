# ============================================================
# KIOSK REMOTE CONTROL / MANAGEMENT ANALYZER
# Không kiểm tra UltraViewer
# Chạy PowerShell bằng Administrator
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

$OutDir = Join-Path $env:USERPROFILE "Desktop\Kiosk_Remote_Analysis"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Time = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " KIOSK REMOTE CONTROL / MANAGEMENT ANALYZER" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# 1. MACHINE INFORMATION
# ------------------------------------------------------------

Write-Host "[1] Machine information..." -ForegroundColor Yellow

Get-ComputerInfo |
    Select-Object `
        CsName,
        WindowsProductName,
        WindowsVersion,
        OsBuildNumber,
        OsArchitecture,
        CsDomain,
        CsWorkgroup,
        CsManufacturer,
        CsModel |
    Out-File "$OutDir\01_machine.txt"


# ------------------------------------------------------------
# 2. SERVICES
# ------------------------------------------------------------

Write-Host "[2] Windows services..." -ForegroundColor Yellow

Get-CimInstance Win32_Service |
    Select-Object `
        Name,
        DisplayName,
        State,
        StartMode,
        StartName,
        PathName |
    Sort-Object Name |
    Export-Csv "$OutDir\02_services.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 3. REMOTE / MANAGEMENT RELATED SERVICES
# ------------------------------------------------------------

Write-Host "[3] Searching remote-management services..." -ForegroundColor Yellow

$Keywords = @(
    "remote",
    "remoting",
    "rdp",
    "terminal",
    "ssh",
    "winrm",
    "vnc",
    "anydesk",
    "teamviewer",
    "rustdesk",
    "meshcentral",
    "mesh",
    "screenconnect",
    "connectwise",
    "splashtop",
    "logmein",
    "bomgar",
    "beyondtrust",
    "dameware",
    "realvnc",
    "tightvnc",
    "ultravnc",
    "chrome remote",
    "remote utilities",
    "zoho",
    "manageengine",
    "n-able",
    "datto",
    "atera",
    "syncro",
    "ninja",
    "kaseya",
    "pulseway",
    "action1",
    "atera",
    "tacticalrmm"
)

$Services = Get-CimInstance Win32_Service

$RemoteServices = $Services | Where-Object {

    $Text = "$($_.Name) $($_.DisplayName) $($_.PathName)"

    foreach ($Key in $Keywords) {
        if ($Text -match [regex]::Escape($Key)) {
            return $true
        }
    }

    return $false
}

$RemoteServices |
    Select-Object Name,DisplayName,State,StartMode,StartName,PathName |
    Export-Csv "$OutDir\03_remote_services.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 4. PROCESSES
# ------------------------------------------------------------

Write-Host "[4] Running processes..." -ForegroundColor Yellow

Get-CimInstance Win32_Process |
    Select-Object `
        ProcessId,
        Name,
        ExecutablePath,
        CommandLine,
        ParentProcessId |
    Sort-Object Name |
    Export-Csv "$OutDir\04_processes.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 5. SEARCH PROCESS NAMES
# ------------------------------------------------------------

Write-Host "[5] Searching remote-management processes..." -ForegroundColor Yellow

$RemoteProcesses = Get-CimInstance Win32_Process | Where-Object {

    $Text = "$($_.Name) $($_.ExecutablePath) $($_.CommandLine)"

    foreach ($Key in $Keywords) {
        if ($Text -match [regex]::Escape($Key)) {
            return $true
        }
    }

    return $false
}

$RemoteProcesses |
    Select-Object ProcessId,Name,ExecutablePath,CommandLine,ParentProcessId |
    Export-Csv "$OutDir\05_remote_processes.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 6. LISTENING PORTS
# ------------------------------------------------------------

Write-Host "[6] Listening TCP/UDP ports..." -ForegroundColor Yellow

Get-NetTCPConnection |
    Where-Object State -eq "Listen" |
    Select-Object `
        LocalAddress,
        LocalPort,
        OwningProcess |
    Sort-Object LocalPort |
    Export-Csv "$OutDir\06_tcp_listen.csv" -NoTypeInformation -Encoding UTF8


Get-NetUDPEndpoint |
    Select-Object `
        LocalAddress,
        LocalPort,
        OwningProcess |
    Sort-Object LocalPort |
    Export-Csv "$OutDir\07_udp_listen.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 7. ESTABLISHED CONNECTIONS
# ------------------------------------------------------------

Write-Host "[7] Active network connections..." -ForegroundColor Yellow

$Connections = Get-NetTCPConnection |
    Where-Object State -eq "Established" |
    ForEach-Object {

        $Process = Get-Process -Id $_.OwningProcess

        [PSCustomObject]@{
            ProcessId      = $_.OwningProcess
            ProcessName    = $Process.ProcessName
            LocalAddress   = $_.LocalAddress
            LocalPort      = $_.LocalPort
            RemoteAddress  = $_.RemoteAddress
            RemotePort     = $_.RemotePort
            State          = $_.State
        }
    }

$Connections |
    Sort-Object ProcessName,RemoteAddress |
    Export-Csv "$OutDir\08_established_connections.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 8. ALL NETWORK CONNECTIONS INCLUDING PID
# ------------------------------------------------------------

Write-Host "[8] Detailed network/process mapping..." -ForegroundColor Yellow

$Connections |
    Format-Table -AutoSize |
    Out-File "$OutDir\09_network_process_mapping.txt"


# ------------------------------------------------------------
# 9. COMMON REMOTE PORTS
# ------------------------------------------------------------

Write-Host "[9] Checking common remote-control ports..." -ForegroundColor Yellow

$CommonPorts = @(
    22,     # SSH
    23,     # Telnet
    3389,   # RDP
    5900,   # VNC
    5901,
    5902,
    5938,   # TeamViewer
    6568,   # AnyDesk commonly seen
    7070,
    21115,  # RustDesk
    21116,
    21117,
    21118,
    21119,
    80,
    443
)

$PortResults = foreach ($Port in $CommonPorts) {

    $TCP = Get-NetTCPConnection -LocalPort $Port

    foreach ($Entry in $TCP) {

        [PSCustomObject]@{
            Port          = $Port
            State         = $Entry.State
            LocalAddress  = $Entry.LocalAddress
            RemoteAddress = $Entry.RemoteAddress
            RemotePort    = $Entry.RemotePort
            PID           = $Entry.OwningProcess
        }
    }
}

$PortResults |
    Export-Csv "$OutDir\10_common_ports.csv" -NoTypeInformation -Encoding UTF8


# ------------------------------------------------------------
# 10. RDP CONFIGURATION
# ------------------------------------------------------------

Write-Host "[10] RDP configuration..." -ForegroundColor Yellow

$RDP = [PSCustomObject]@{
    fDenyTSConnections =
        (Get-ItemProperty `
            "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" `
            -Name fDenyTSConnections).fDenyTSConnections

    RDP_Port =
        (Get-ItemProperty `
            "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" `
            -Name PortNumber).PortNumber

    TermService =
        (Get-Service TermService).Status
}

$RDP | Format-List |
    Out-File "$OutDir\11_rdp.txt"


# ------------------------------------------------------------
# 11. WINRM
# ------------------------------------------------------------

Write-Host "[11] WinRM..." -ForegroundColor Yellow

Get-Service WinRM |
    Select-Object Name,Status,StartType |
    Out-File "$OutDir\12_winrm.txt"

winrm get winrm/config |
    Out-File "$OutDir\13_winrm_config.txt"


# ------------------------------------------------------------
# 12. SSH
# ------------------------------------------------------------

Write-Host "[12] SSH..." -ForegroundColor Yellow

Get-Service sshd |
    Select-Object Name,Status,StartType |
    Out-File "$OutDir\14_ssh.txt"


# ------------------------------------------------------------
# 13. SCHEDULED TASKS
# ------------------------------------------------------------

Write-Host "[13] Scheduled tasks..." -ForegroundColor Yellow

Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State,Author,Description |
    Export-Csv "$OutDir\15_scheduled_tasks.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 14. SEARCH SCHEDULED TASKS FOR REMOTE AGENTS
# ------------------------------------------------------------

Write-Host "[14] Searching suspicious scheduled tasks..." -ForegroundColor Yellow

$Tasks = Get-ScheduledTask

$RemoteTasks = $Tasks | Where-Object {

    $Text = "$($_.TaskName) $($_.TaskPath) $($_.Author) $($_.Description)"

    foreach ($Key in $Keywords) {
        if ($Text -match [regex]::Escape($Key)) {
            return $true
        }
    }

    return $false
}

$RemoteTasks |
    Export-Csv "$OutDir\16_remote_tasks.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 15. STARTUP PROGRAMS
# ------------------------------------------------------------

Write-Host "[15] Startup programs..." -ForegroundColor Yellow

Get-CimInstance Win32_StartupCommand |
    Select-Object `
        Name,
        Command,
        Location,
        User |
    Export-Csv "$OutDir\17_startup.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 16. INSTALLED SOFTWARE
# ------------------------------------------------------------

Write-Host "[16] Installed software..." -ForegroundColor Yellow

$UninstallPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$Software = foreach ($Path in $UninstallPaths) {

    Get-ItemProperty $Path |
        Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation,UninstallString
}

$Software |
    Where-Object DisplayName |
    Sort-Object DisplayName |
    Export-Csv "$OutDir\18_installed_software.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 17. FIREWALL RULES
# ------------------------------------------------------------

Write-Host "[17] Firewall rules..." -ForegroundColor Yellow

Get-NetFirewallRule |
    Select-Object `
        Name,
        DisplayName,
        Enabled,
        Direction,
        Action,
        Profile |
    Export-Csv "$OutDir\19_firewall_rules.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 18. REMOTE-RELATED FIREWALL RULES
# ------------------------------------------------------------

Write-Host "[18] Remote-related firewall rules..." -ForegroundColor Yellow

Get-NetFirewallRule |
    Where-Object {
        "$($_.DisplayName) $($_.Name)" -match `
        "Remote|RDP|SSH|VNC|AnyDesk|TeamViewer|RustDesk|WinRM|Terminal"
    } |
    Select-Object `
        Name,
        DisplayName,
        Enabled,
        Direction,
        Action,
        Profile |
    Export-Csv "$OutDir\20_remote_firewall.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 19. DNS CACHE
# ------------------------------------------------------------

Write-Host "[19] DNS cache..." -ForegroundColor Yellow

Get-DnsClientCache |
    Where-Object Entry -ne $null |
    Select-Object Entry,RecordName,RecordType,Data |
    Sort-Object Entry |
    Export-Csv "$OutDir\21_dns_cache.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 20. NETWORK ADAPTER / DNS
# ------------------------------------------------------------

Write-Host "[20] Network configuration..." -ForegroundColor Yellow

Get-NetIPConfiguration |
    Format-List |
    Out-File "$OutDir\22_network_config.txt"


# ------------------------------------------------------------
# 21. HOSTS FILE
# ------------------------------------------------------------

Write-Host "[21] Hosts file..." -ForegroundColor Yellow

Get-Content "$env:SystemRoot\System32\drivers\etc\hosts" |
    Out-File "$OutDir\23_hosts.txt"


# ------------------------------------------------------------
# 22. WINDOWS SERVICES RUNNING AS SYSTEM
# ------------------------------------------------------------

Write-Host "[22] SYSTEM services..." -ForegroundColor Yellow

$Services |
    Where-Object {
        $_.State -eq "Running" -and
        $_.StartName -match "LocalSystem|SYSTEM"
    } |
    Select-Object `
        Name,
        DisplayName,
        State,
        StartMode,
        StartName,
        PathName |
    Export-Csv "$OutDir\24_system_services.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 23. PROCESS -> NETWORK CONNECTION CORRELATION
# ------------------------------------------------------------

Write-Host "[23] Process/network correlation..." -ForegroundColor Yellow

$NetworkDetail = foreach ($Conn in Get-NetTCPConnection) {

    $Proc = Get-CimInstance Win32_Process `
        -Filter "ProcessId = $($Conn.OwningProcess)"

    if ($Proc) {

        [PSCustomObject]@{
            PID            = $Conn.OwningProcess
            Process        = $Proc.Name
            Executable     = $Proc.ExecutablePath
            CommandLine    = $Proc.CommandLine
            State          = $Conn.State
            LocalAddress   = $Conn.LocalAddress
            LocalPort      = $Conn.LocalPort
            RemoteAddress  = $Conn.RemoteAddress
            RemotePort     = $Conn.RemotePort
        }
    }
}

$NetworkDetail |
    Export-Csv "$OutDir\25_process_network_full.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 24. POSSIBLE REMOTE AGENT FILES
# ------------------------------------------------------------

Write-Host "[24] Searching common agent directories..." -ForegroundColor Yellow

$SearchRoots = @(
    "$env:ProgramFiles",
    "${env:ProgramFiles(x86)}",
    "$env:ProgramData",
    "$env:LOCALAPPDATA",
    "$env:APPDATA"
)

$AgentFiles = foreach ($Root in $SearchRoots) {

    if (Test-Path $Root) {

        Get-ChildItem $Root `
            -Recurse `
            -File `
            -ErrorAction SilentlyContinue |
        Where-Object {

            $Text = $_.FullName

            foreach ($Key in $Keywords) {
                if ($Text -match [regex]::Escape($Key)) {
                    return $true
                }
            }

            return $false
        }
    }
}

$AgentFiles |
    Select-Object FullName,Length,LastWriteTime |
    Export-Csv "$OutDir\26_possible_agent_files.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 25. WINDOWS EVENT LOG - REMOTE DESKTOP
# ------------------------------------------------------------

Write-Host "[25] RDP event logs..." -ForegroundColor Yellow

Get-WinEvent `
    -LogName "Microsoft-Windows-TerminalServices-LocalSessionManager/Operational" `
    -MaxEvents 500 |
    Select-Object TimeCreated,Id,LevelDisplayName,Message |
    Out-File "$OutDir\27_rdp_events.txt"


# ------------------------------------------------------------
# 26. REMOTE MANAGEMENT EVENT LOGS
# ------------------------------------------------------------

Write-Host "[26] WinRM event logs..." -ForegroundColor Yellow

Get-WinEvent `
    -LogName "Microsoft-Windows-WinRM/Operational" `
    -MaxEvents 500 |
    Select-Object TimeCreated,Id,LevelDisplayName,Message |
    Out-File "$OutDir\28_winrm_events.txt"


# ------------------------------------------------------------
# 27. ARP
# ------------------------------------------------------------

Write-Host "[27] ARP table..." -ForegroundColor Yellow

Get-NetNeighbor |
    Select-Object `
        ifIndex,
        IPAddress,
        LinkLayerAddress,
        State |
    Export-Csv "$OutDir\29_arp.csv" `
        -NoTypeInformation `
        -Encoding UTF8


# ------------------------------------------------------------
# 28. FINAL SUMMARY
# ------------------------------------------------------------

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host " ANALYSIS SUMMARY" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Remote-related services:" -ForegroundColor Cyan

$RemoteServices |
    Select-Object Name,DisplayName,State,StartMode |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Remote-related processes:" -ForegroundColor Cyan

$RemoteProcesses |
    Select-Object ProcessId,Name,ExecutablePath |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Listening ports:" -ForegroundColor Cyan

Get-NetTCPConnection |
    Where-Object State -eq "Listen" |
    Select-Object LocalAddress,LocalPort,OwningProcess |
    Sort-Object LocalPort |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Active external connections:" -ForegroundColor Cyan

$Connections |
    Where-Object {
        $_.RemoteAddress -notmatch `
        "^(127\.|0\.0\.0\.0|::1|::)$"
    } |
    Sort-Object ProcessName,RemoteAddress |
    Format-Table -AutoSize

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "DONE"
Write-Host ""
Write-Host "Results:" -ForegroundColor Yellow
Write-Host $OutDir
Write-Host "==============================================" -ForegroundColor Green