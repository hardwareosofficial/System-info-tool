$src = Join-Path $PSScriptRoot '..\dist\SystemInfoTool.exe'
if (Test-Path $src) {
    $dst = "$env:USERPROFILE\Downloads\SystemInfoTool-FromLocal.exe"
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "Copied to $dst"
    Start-Process -FilePath $dst -WorkingDirectory (Split-Path $dst)
    Write-Host "Started"
} else {
    Write-Host "Local build not found at $src"
}
