param([switch]$Offline, [ValidateRange(1,4)][int]$Vcpu = 1)
$ErrorActionPreference = 'Stop'
$consumerRoot = $PSScriptRoot
$vmRoot = Join-Path $consumerRoot 'linux-vm'
$qemuRoot = Join-Path $consumerRoot 'qemu'
$imagePath = Join-Path $vmRoot 'ubuntu-24.04-minimal-cloudimg-amd64.img'
$overlayPath = Join-Path $vmRoot 'consumer-overlay.qcow2'
$varsPath = Join-Path $vmRoot 'consumer-uefi-vars.fd'
if (-not (Test-Path -LiteralPath $overlayPath)) {
    & (Join-Path $qemuRoot 'qemu-img.exe') create -f qcow2 -F qcow2 -b $imagePath $overlayPath 16G *>&1 | Tee-Object -FilePath (Join-Path $consumerRoot 'qemu-overlay-create.log')
    if ($LASTEXITCODE -ne 0) { throw 'Own guest overlay creation failed' }
}
if (-not (Test-Path -LiteralPath $varsPath)) {
    Copy-Item -LiteralPath (Join-Path $qemuRoot 'share/edk2-i386-vars.fd') -Destination $varsPath
}
$network = 'user,id=guestnet,hostfwd=tcp:127.0.0.1:22222-:22'
if ($Offline) { $network += ',restrict=on' }
$tcgThread = if ($Vcpu -eq 1) { 'single' } else { 'multi' }
$qemuArgs = @(
    '-name','rfqfuzz-local-consumer',
    '-L',(Join-Path $qemuRoot 'share'),
    '-machine','pc',
    '-accel',('tcg,thread=' + $tcgThread),
    '-cpu','max',
    '-smp',[string]$Vcpu,
    '-m','4096',
    '-kernel',(Join-Path $vmRoot 'kernel-extract/vmlinuz-6.8.0-146-generic'),
    '-initrd',(Join-Path $vmRoot 'kernel-extract/microcode.cpio'),
    '-append','root=PARTUUID=bd907978-e121-479a-9598-288628fcfd21 ro console=ttyS0 noapic ds=nocloud',
    '-drive',('file=' + $overlayPath + ',if=virtio,format=qcow2'),
    '-drive',('file=' + (Join-Path $vmRoot 'seed.iso') + ',if=virtio,readonly=on,format=raw'),
    '-netdev',$network,
    '-device','virtio-net-pci,netdev=guestnet',
    '-display','none',
    '-serial',('file:' + (Join-Path $vmRoot 'serial.log')),
    '-qmp','tcp:127.0.0.1:28444,server=on,wait=off',
    '-no-reboot',
    '-pidfile',(Join-Path $vmRoot 'qemu.pid')
)
$record = @{utc=(Get-Date).ToUniversalTime().ToString('o'); executable=(Join-Path $qemuRoot 'qemu-system-x86_64.exe'); arguments=$qemuArgs; mode= $(if($Offline){'offline_restricted_user_network_localhost_ssh_only'}else{'dependency_setup_network'}); accelerator='TCG software emulation'; boot_method='direct kernel from verified Ubuntu image; noapic avoids emulated IO-APIC timer failure'; guest_original_sha256='a8eb6570f87a941f3de2e000c046b9367f8ab1423756a94830d454fae8ad80ff'; kernel_sha256=(Get-FileHash -LiteralPath (Join-Path $vmRoot 'kernel-extract/vmlinuz-6.8.0-146-generic') -Algorithm SHA256).Hash}
$record | ConvertTo-Json -Depth 6 | Out-File -LiteralPath (Join-Path $vmRoot ('launch-' + $record.mode + '.json')) -Encoding utf8
$quotedArgs = $qemuArgs | ForEach-Object { '"' + $_.Replace('"','\"') + '"' }
$process = Start-Process -FilePath $record.executable -ArgumentList $quotedArgs -WorkingDirectory $qemuRoot -WindowStyle Hidden -PassThru -RedirectStandardError (Join-Path $vmRoot 'qemu-stderr.log') -RedirectStandardOutput (Join-Path $vmRoot 'qemu-stdout.log')
Write-Output ('Started own headless QEMU guest PID ' + $process.Id + '; mode ' + $record.mode)
