@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo  SecureSH Build Script
echo ============================================================
echo.

:: ── Locate Python / pip ──────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found on PATH. Install Python 3.10+ and retry.
    pause & exit /b 1
)

:: ── Install / verify dependencies ───────────────────────────
echo [1/4] Installing Python dependencies...
python -m pip install --quiet paramiko pyinstaller
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause & exit /b 1
)
echo       Done.

:: ── Kill any running instance before overwriting the exe ─────
echo       Stopping any running SecureSH instance...
taskkill /f /im SecureSH.exe >nul 2>&1
if exist "dist\SecureSH.exe" del /f /q "dist\SecureSH.exe" >nul 2>&1

:: ── Build executable with PyInstaller ───────────────────────
echo [2/4] Building standalone executable (PyInstaller)...
python -m PyInstaller --clean --noconfirm securesh.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause & exit /b 1
)
echo       Done.  Executable: dist\SecureSH.exe

:: ── Locate Inno Setup (unquoted paths stored in ISCC) ────────
set "ISCC="
for /f "delims=" %%P in ('dir /b /s "%ProgramFiles(x86)%\Inno Setup*\ISCC.exe" 2^>nul') do set "ISCC=%%P"
if "!ISCC!"=="" (
    for /f "delims=" %%P in ('dir /b /s "%ProgramFiles%\Inno Setup*\ISCC.exe" 2^>nul') do set "ISCC=%%P"
)

if "!ISCC!"=="" (
    echo [3/4] Inno Setup not found. Downloading installer...
    set "INNO_SETUP_EXE=%TEMP%\innosetup_installer.exe"
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://jrsoftware.org/download.php/is.exe' -OutFile '!INNO_SETUP_EXE!'"
    if errorlevel 1 (
        echo [WARN] Could not download Inno Setup automatically.
        echo        Download from https://jrsoftware.org/isdl.php and re-run this script.
        goto :skip_installer
    )
    echo       Installing Inno Setup silently...
    "!INNO_SETUP_EXE!" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
    timeout /t 3 /nobreak >nul
    :: Re-scan after install
    for /f "delims=" %%P in ('dir /b /s "%ProgramFiles(x86)%\Inno Setup*\ISCC.exe" 2^>nul') do set "ISCC=%%P"
    if "!ISCC!"=="" (
        for /f "delims=" %%P in ('dir /b /s "%ProgramFiles%\Inno Setup*\ISCC.exe" 2^>nul') do set "ISCC=%%P"
    )
)

if "!ISCC!"=="" (
    echo [WARN] Inno Setup still not found. Skipping installer creation.
    goto :skip_installer
)

:: ── Create Windows installer ─────────────────────────────────
echo [3/4] Creating Windows installer with Inno Setup...
echo       Using: !ISCC!
if not exist installer_output mkdir installer_output
"!ISCC!" installer.iss
if errorlevel 1 (
    echo [ERROR] Inno Setup compilation failed.
    pause & exit /b 1
)
echo       Done.  Installer: installer_output\SecureSH-1.0.0-Setup.exe
goto :done

:skip_installer
echo       Skipping installer step.

:done
echo.
echo [4/4] Build complete!
echo.
echo   Standalone exe : dist\SecureSH.exe
if exist "installer_output\SecureSH-1.0.0-Setup.exe" (
    echo   Windows installer: installer_output\SecureSH-1.0.0-Setup.exe
)
echo.
pause
