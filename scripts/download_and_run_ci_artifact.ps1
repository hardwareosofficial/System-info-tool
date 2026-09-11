$artifactUrl = 'https://api.github.com/repos/hardwareosofficial/System-info-tool/actions/artifacts/9951481002/zip'
$out = "$env:USERPROFILE\Downloads\systeminfotool-windows-latest.zip"
Write-Host "Downloading to $out"
Invoke-WebRequest -Uri $artifactUrl -OutFile $out -Headers @{Accept='application/octet-stream'}
$dest = "$env:USERPROFILE\Downloads\systeminfotool-ci"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Expand-Archive -LiteralPath $out -DestinationPath $dest -Force
Write-Host "Contents:"
Get-ChildItem -Recurse $dest | Select-Object FullName,Length | Format-Table -AutoSize
$exe = Get-ChildItem -Path $dest -Filter "*.exe" -Recurse | Select-Object -First 1
if ($null -ne $exe) {
    Write-Host "Found exe: $($exe.FullName)"
    Start-Process -FilePath $exe.FullName -WorkingDirectory $exe.Directory.FullName
    Write-Host "Started process"
} else {
    Write-Host "No exe found in artifact"
}
