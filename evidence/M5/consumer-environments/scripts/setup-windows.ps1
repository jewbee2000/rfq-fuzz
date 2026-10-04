$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$consumerRoot = $PSScriptRoot
$pythonPath = Join-Path $consumerRoot 'windows-venv/Scripts/python.exe'
$logPath = Join-Path $consumerRoot 'windows-setup.log'
Start-Transcript -LiteralPath $logPath -Force
try {
    Write-Output ('UTC start: ' + (Get-Date).ToUniversalTime().ToString('o'))
    Write-Output ('Repository: ' + $repoRoot)
    Write-Output ('Source revision: ' + (& git -C $repoRoot rev-parse HEAD))
    Write-Output ('Lock SHA256: ' + (Get-FileHash -LiteralPath (Join-Path $repoRoot 'requirements-m0.lock') -Algorithm SHA256).Hash)
    Write-Output 'COMMAND: py -3.12 -m venv work/consumer-env/windows-venv'
    & py -3.12 -m venv (Join-Path $consumerRoot 'windows-venv')
    if ($LASTEXITCODE -ne 0) { throw 'Fresh virtual environment creation failed' }
    Write-Output 'COMMAND: windows-venv/Scripts/python.exe -m pip install pip==26.2.1'
    & $pythonPath -m pip install pip==26.2.1 --log (Join-Path $consumerRoot 'windows-pip-bootstrap.log')
    if ($LASTEXITCODE -ne 0) { throw 'Pip bootstrap failed' }
    Write-Output 'COMMAND: windows-venv/Scripts/python.exe -m pip install -r requirements-m0.lock --report windows-install-report.json'
    & $pythonPath -m pip install -r (Join-Path $repoRoot 'requirements-m0.lock') --report (Join-Path $consumerRoot 'windows-install-report.json') --log (Join-Path $consumerRoot 'windows-pip-install.log')
    if ($LASTEXITCODE -ne 0) { throw 'Pinned dependency installation failed' }
    Write-Output 'COMMAND: windows-venv/Scripts/python.exe -m pip check'
    & $pythonPath -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Pip check failed' }
    Write-Output 'COMMAND: windows-venv/Scripts/python.exe inspect_environment.py windows-environment.json'
    & $pythonPath (Join-Path $consumerRoot 'inspect_environment.py') (Join-Path $consumerRoot 'windows-environment.json')
    if ($LASTEXITCODE -ne 0) { throw 'Import/version inspection failed' }
    $smokeRoot = Join-Path $consumerRoot 'windows-smoke'
    New-Item -ItemType Directory -Path $smokeRoot -Force | Out-Null
    Push-Location $smokeRoot
    try {
        Write-Output ('COMMAND cwd=' + $smokeRoot + ': windows-venv/Scripts/python.exe ' + (Join-Path $repoRoot 'tools/smoke.py'))
        & $pythonPath (Join-Path $repoRoot 'tools/smoke.py')
        if ($LASTEXITCODE -ne 0) { throw 'Smoke failed' }
    } finally { Pop-Location }
    Write-Output ('UTC finish: ' + (Get-Date).ToUniversalTime().ToString('o'))
} finally { Stop-Transcript }
