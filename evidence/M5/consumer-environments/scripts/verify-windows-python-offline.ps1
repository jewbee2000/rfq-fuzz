$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$pythonPath = Join-Path $taskRoot 'windows-venv/Scripts/python.exe'
$siteRoot = Join-Path $taskRoot 'windows-venv/Lib/site-packages'
$guardModule = Join-Path $siteRoot 'rfqfuzz_consumer_socket_guard.py'
$guardLoader = Join-Path $siteRoot 'rfqfuzz_consumer_socket_guard.pth'
if ((Test-Path -LiteralPath $guardModule) -or (Test-Path -LiteralPath $guardLoader)) { throw 'Own temporary guard names already exist; refusing to overwrite' }
$guardSource = @'
import datetime
import json
import os
import sys
def record(event):
    with open(os.environ['RFQFUZZ_CONSUMER_GUARD_LOG'], 'a', encoding='utf-8') as handle:
        handle.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'pid': os.getpid(), 'executable': sys.executable, 'event': event}) + '\n')
def guard(event, arguments):
    if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto', 'socket.bind'}:
        record('denied:' + event)
        raise RuntimeError('Independent offline consumer verification denies Python socket networking')
sys.addaudithook(guard)
record('guard_loaded')
'@
Start-Transcript -LiteralPath (Join-Path $taskRoot 'windows-all-python-offline.log') -Force
try {
    $env:RFQFUZZ_CONSUMER_GUARD_LOG = Join-Path $taskRoot 'windows-all-python-guard-events.jsonl'
    [System.IO.File]::WriteAllText($guardModule, $guardSource)
    [System.IO.File]::WriteAllText($guardLoader, "import rfqfuzz_consumer_socket_guard`n")
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Write-Output 'Scope: temporary startup hook in this own venv blocks Python socket networking in CLI and native Python subprocesses. Host interfaces/firewall and direct native-library networking are not controlled.'
    Push-Location (Join-Path $taskRoot 'windows-frozen-bounded')
    try {
        Write-Output 'COMMAND: python -m rfqfuzz.v1 demo examples/v1-demo work/windows-all-python-offline-demo'
        & $pythonPath -m rfqfuzz.v1 demo examples/v1-demo work/windows-all-python-offline-demo *> (Join-Path $taskRoot 'windows-all-python-offline-demo.log')
        Write-Output ('Canonical CLI exit=' + $LASTEXITCODE)
        if ($LASTEXITCODE -ne 0) { throw 'All-Python offline replay failed' }
    } finally { Pop-Location }
} finally {
    Remove-Item -LiteralPath $guardLoader -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $guardModule -ErrorAction SilentlyContinue
    Remove-Item Env:RFQFUZZ_CONSUMER_GUARD_LOG -ErrorAction SilentlyContinue
    Write-Output 'Temporary own-venv guard loader/module removed.'
    Stop-Transcript
}
