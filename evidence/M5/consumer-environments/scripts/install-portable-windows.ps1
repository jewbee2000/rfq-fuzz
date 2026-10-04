$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$sourceRoot = Join-Path $taskRoot 'windows-portable-348c5f1'
$pythonPath = Join-Path $taskRoot 'windows-venv/Scripts/python.exe'
$entryPoint = Join-Path $taskRoot 'windows-venv/Scripts/rfqfuzz.exe'
$isolatedCwd = Join-Path $taskRoot 'windows-consumer-cwd'
New-Item -ItemType Directory -Force -Path $isolatedCwd | Out-Null
Start-Transcript -LiteralPath (Join-Path $taskRoot 'windows-portable-install-and-demo.log') -Force
try {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Write-Output 'Portable Git source commit: 348c5f1ea5a6e99bc0acdb4f0d0af52f3a8146e0'
    Get-FileHash -LiteralPath (Join-Path $taskRoot 'portable-consumer-348c5f1.tar.gz') -Algorithm SHA256
    Push-Location $isolatedCwd
    try {
        & $pythonPath -m pip install --no-index --no-deps --no-build-isolation -e $sourceRoot --report (Join-Path $taskRoot 'windows-portable-project-report.json') --log (Join-Path $taskRoot 'windows-portable-project-pip.log')
        if ($LASTEXITCODE -ne 0) { throw 'Portable source installation failed' }
        & $pythonPath -m pip check
        if ($LASTEXITCODE -ne 0) { throw 'Portable source pip check failed' }
        Write-Output ('COMMAND from isolated cwd: installed rfqfuzz.exe demo ' + (Join-Path $sourceRoot 'examples/v1-demo') + ' ' + (Join-Path $taskRoot 'windows-portable-demo'))
        & $entryPoint demo (Join-Path $sourceRoot 'examples/v1-demo') (Join-Path $taskRoot 'windows-portable-demo') *> (Join-Path $taskRoot 'windows-portable-demo.log')
        Write-Output ('Portable installed entry point demo exit=' + $LASTEXITCODE)
        if ($LASTEXITCODE -ne 0) { throw 'Portable Git consumer demo failed' }
    } finally { Pop-Location }
    & $pythonPath (Join-Path $taskRoot 'inspect_environment.py') (Join-Path $taskRoot 'windows-portable-environment.json')
    if ($LASTEXITCODE -ne 0) { throw 'Portable environment recording failed' }
} finally { Stop-Transcript }
