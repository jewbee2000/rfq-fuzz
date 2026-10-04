$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath 'work/consumer-env').Path
$evidenceRoot = (Resolve-Path -LiteralPath 'evidence/M5/consumer-environments').Path
$qemuId = [int](Get-Content -LiteralPath (Join-Path $taskRoot 'linux-vm/qemu.pid'))
$serverId = [int](Get-Content -LiteralPath (Join-Path $taskRoot 'localhost-server.pid'))
$qemuBefore = Get-CimInstance Win32_Process -Filter "ProcessId = $qemuId"
if (-not $qemuBefore -or $qemuBefore.Name -ne 'qemu-system-x86_64.exe' -or
    -not $qemuBefore.CommandLine.Contains($taskRoot) -or
    -not $qemuBefore.CommandLine.Contains('rfqfuzz-local-consumer') -or
    -not $qemuBefore.CommandLine.Contains('consumer-overlay.qcow2') -or
    -not $qemuBefore.CommandLine.Contains('28444')) {
    throw 'QEMU identity did not match this task-owned helper.'
}
$serverBefore = Get-CimInstance Win32_Process -Filter "ProcessId = $serverId"
if (-not $serverBefore -or -not $serverBefore.CommandLine.Contains($taskRoot) -or
    -not $serverBefore.CommandLine.Contains('-m http.server 28080 --bind 127.0.0.1') -or
    -not $serverBefore.CommandLine.Contains('guest-transfer')) {
    throw 'Transfer server launcher did not match this task-owned helper.'
}
$listener = @(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 28080 -State Listen -ErrorAction SilentlyContinue)
if ($listener.Count -ne 1) { throw 'Expected one task transfer-server listener.' }
$listenerId = [int]$listener[0].OwningProcess
$listenerBefore = Get-CimInstance Win32_Process -Filter "ProcessId = $listenerId"
if (-not $listenerBefore -or $listenerBefore.ParentProcessId -ne $serverId -or
    -not $listenerBefore.CommandLine.Contains($taskRoot) -or
    -not $listenerBefore.CommandLine.Contains('-m http.server 28080 --bind 127.0.0.1') -or
    -not $listenerBefore.CommandLine.Contains('guest-transfer')) {
    throw 'Transfer listener did not match the task-owned launcher child.'
}
$started = (Get-Date).ToUniversalTime().ToString('o')
$qmpLog = Join-Path $evidenceRoot 'setup/helper-powerdown-qmp.log'
& (Join-Path $taskRoot 'tooling-venv/Scripts/python.exe') (Join-Path $taskRoot 'qmp_command.py') system_powerdown *> $qmpLog
$qmpExit = $LASTEXITCODE
if ($qmpExit -ne 0) { throw "QMP powerdown returned $qmpExit" }
$qemuProcess = Get-Process -Id $qemuId -ErrorAction SilentlyContinue
$graceful = -not $qemuProcess
if ($qemuProcess) { $graceful = $qemuProcess.WaitForExit(30000) }
Stop-Process -Id $listenerId
Start-Sleep -Milliseconds 500
$serverAfter = Get-CimInstance Win32_Process -Filter "ProcessId = $serverId"
$launcherStoppedExplicitly = $false
if ($serverAfter) {
    if (-not $serverAfter.CommandLine.Contains($taskRoot) -or
        -not $serverAfter.CommandLine.Contains('-m http.server 28080 --bind 127.0.0.1') -or
        -not $serverAfter.CommandLine.Contains('guest-transfer')) {
        throw 'Transfer launcher identity changed before stopping it.'
    }
    Stop-Process -Id $serverId
    $launcherStoppedExplicitly = $true
}
Start-Sleep -Milliseconds 500
$remaining = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 28080,28444,22222 } | Select-Object LocalAddress,LocalPort,OwningProcess)
$result = [ordered]@{
    status = $(if ($graceful -and $remaining.Count -eq 0) { 'task_helpers_stopped' } else { 'cleanup_incomplete' })
    started_utc = $started
    completed_utc = (Get-Date).ToUniversalTime().ToString('o')
    ownership_checks = 'Exact workspace paths, guest name, own disk/control port, server command and launcher-child relation checked immediately before mutation.'
    qemu = [ordered]@{ pid = $qemuId; command = 'QMP system_powerdown'; qmp_exit = $qmpExit; graceful_exit_within_30_seconds = $graceful; process_present_after = [bool](Get-Process -Id $qemuId -ErrorAction SilentlyContinue) }
    transfer_server = [ordered]@{ launcher_pid = $serverId; listener_pid = $listenerId; command = 'Stop-Process on verified task-owned listener child; launcher only if still present'; launcher_stopped_explicitly = $launcherStoppedExplicitly; launcher_present_after = [bool](Get-Process -Id $serverId -ErrorAction SilentlyContinue); listener_present_after = [bool](Get-Process -Id $listenerId -ErrorAction SilentlyContinue) }
    remaining_task_port_listeners = $remaining
    unaffected_scope = 'No unrelated processes, host settings, Docker/WSL services, or other VMs were changed.'
    retention = 'Ignored guest/tool files remain local; no keys, seed content, guest disks, or executable binaries are retained in evidence.'
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'helper-shutdown.json') -Encoding utf8
$result | ConvertTo-Json -Depth 8
