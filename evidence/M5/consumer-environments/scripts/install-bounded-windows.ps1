$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$frozenRoot = Join-Path $taskRoot 'windows-frozen-bounded'
$pythonPath = Join-Path $taskRoot 'windows-venv/Scripts/python.exe'
Start-Transcript -LiteralPath (Join-Path $taskRoot 'windows-bounded-install.log') -Force
try {
    Write-Output 'Frozen source commit: 55b288a8df0d1b3ced607c8d97d23847b2f122ba'
    Get-FileHash -LiteralPath (Join-Path $taskRoot 'frozen-consumer-bounded.tar.gz') -Algorithm SHA256
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Push-Location $frozenRoot
    try {
        & $pythonPath -m pip install --no-index -r requirements-v1.lock -r requirements-build.lock --report (Join-Path $taskRoot 'windows-bounded-dependencies-report.json') --log (Join-Path $taskRoot 'windows-bounded-dependencies-pip.log')
        if ($LASTEXITCODE -ne 0) { throw 'Frozen dependency check failed' }
        & $pythonPath -m pip install --no-index --no-deps --no-build-isolation -e . --report (Join-Path $taskRoot 'windows-bounded-project-report.json') --log (Join-Path $taskRoot 'windows-bounded-project-pip.log')
        if ($LASTEXITCODE -ne 0) { throw 'Frozen project installation failed' }
        & $pythonPath -m pip check
        if ($LASTEXITCODE -ne 0) { throw 'Frozen pip check failed' }
        & $pythonPath -m rfqfuzz.v1 demo examples/v1-demo work/windows-bounded-demo *> (Join-Path $taskRoot 'windows-bounded-demo.log')
        Write-Output ('Default-bound canonical demo exit=' + $LASTEXITCODE)
        if ($LASTEXITCODE -ne 0) { throw 'Final Windows canonical demo failed' }
    } finally { Pop-Location }
    & $pythonPath (Join-Path $taskRoot 'inspect_environment.py') (Join-Path $taskRoot 'windows-bounded-environment.json')
    if ($LASTEXITCODE -ne 0) { throw 'Final Windows environment inspection failed' }
} finally { Stop-Transcript }
