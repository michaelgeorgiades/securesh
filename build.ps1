#Requires -Version 5.1
<#
.SYNOPSIS
    Builds SecureSH.exe via PyInstaller and packages it with Inno Setup.
    Run from the project root as your normal (non-admin) user.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '=== SecureSH Build ===' -ForegroundColor Cyan

# Verify not running as admin (PyInstaller 6.x has issues when run elevated)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host 'ERROR: Do not run this script as Administrator.' -ForegroundColor Red
    Write-Host 'Open a normal PowerShell window and run: .\build.ps1'
    Read-Host 'Press Enter to exit'
    exit 1
}

$root = Split-Path $MyInvocation.MyCommand.Path

# Clean previous artefacts
Write-Host 'Cleaning previous build...'
foreach ($dir in 'build', 'dist', 'installer_output') {
    $path = Join-Path $root $dir
    if (Test-Path $path) { Remove-Item $path -Recurse -Force }
}

# Build EXE with PyInstaller
Write-Host 'Running PyInstaller...' -ForegroundColor Cyan
Push-Location $root
try {
    python -m PyInstaller securesh.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
} finally {
    Pop-Location
}

$exe = Join-Path $root 'dist\SecureSH.exe'
if (-not (Test-Path $exe)) { throw "Expected EXE not found: $exe" }
Write-Host "EXE built: $exe" -ForegroundColor Green

# Build installer with Inno Setup
$iscc = 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
if (Test-Path $iscc) {
    Write-Host 'Running Inno Setup...' -ForegroundColor Cyan
    & $iscc (Join-Path $root 'installer.iss')
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed.' }

    $installer = Join-Path $root 'installer_output\SecureSH-1.0.0-Setup.exe'
    if (Test-Path $installer) {
        Write-Host "Installer ready: $installer" -ForegroundColor Green
    }
} else {
    Write-Host 'Inno Setup not found at expected path — skipping installer step.' -ForegroundColor Yellow
    Write-Host "Distribute the standalone EXE at: $exe"
}

Write-Host ''
Write-Host '=== Build complete ===' -ForegroundColor Cyan
Read-Host 'Press Enter to exit'
