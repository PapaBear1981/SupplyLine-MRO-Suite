@echo off
echo ========================================
echo SupplyLine MRO Suite - Build Without Icons
echo ========================================
echo.

cd /d "%~dp0"

echo This will temporarily remove icon configuration to test the build...
echo.

REM Backup the current package.json
copy package.json package.json.backup

echo Creating temporary package.json without icon references...

REM Create a simple PowerShell script to remove icon lines
echo $content = Get-Content 'package.json' ^| Where-Object { $_ -notmatch '"icon"' -and $_ -notmatch 'Icon' } > temp_remove_icons.ps1
echo $content ^| Set-Content 'package_temp.json' >> temp_remove_icons.ps1

powershell -ExecutionPolicy Bypass -File temp_remove_icons.ps1

REM Replace the original with the temp version
move package_temp.json package.json

echo Building without icons...
call npm run dist:win

if %errorlevel% equ 0 (
    echo ✓ Build successful without icons!
    echo.
    echo This confirms the icon was the issue.
    echo We can add a proper icon back later.
) else (
    echo ✗ Build still failed - there's another issue.
)

REM Restore the original package.json
copy package.json.backup package.json

REM Cleanup
del temp_remove_icons.ps1 2>nul
del package.json.backup 2>nul

pause
