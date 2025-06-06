@echo off
echo ========================================
echo SupplyLine MRO Suite - Icon Fix
echo ========================================
echo.

cd /d "%~dp0"

echo Checking current icon files...
if exist "assets\icon.png" (
    echo ✓ PNG icon found
) else (
    echo ✗ PNG icon missing - cannot convert
    pause
    exit /b 1
)

echo.
echo Backing up current icon.ico...
if exist "assets\icon.ico" (
    copy "assets\icon.ico" "assets\icon.ico.backup"
    echo ✓ Backup created
)

echo.
echo Option 1: Remove icon configuration temporarily...
echo This will build without any icons to test if that's the issue.
echo.
set /p choice1="Remove icons and test build? (y/n): "
if /i "%choice1%"=="y" goto remove_icons

echo.
echo Option 2: Try using PNG instead of ICO...
echo This changes the config to use the PNG file directly.
echo.
set /p choice2="Use PNG instead of ICO? (y/n): "
if /i "%choice2%"=="y" goto use_png

echo.
echo Option 3: Download a proper ICO converter...
echo This will help you convert the PNG to a proper ICO file.
echo.
set /p choice3="Get ICO converter info? (y/n): "
if /i "%choice3%"=="y" goto ico_info

goto end

:remove_icons
echo.
echo Temporarily removing icon configuration...

REM Backup package.json
copy package.json package.json.icon-backup

REM Create PowerShell script to remove icon lines
echo $content = Get-Content 'package.json' > temp_fix_icons.ps1
echo $content = $content -replace '.*"icon".*,?', '' >> temp_fix_icons.ps1
echo $content = $content -replace '.*Icon".*,?', '' >> temp_fix_icons.ps1
echo $content ^| Where-Object { $_.Trim() -ne '' } ^| Set-Content 'package.json' >> temp_fix_icons.ps1

powershell -ExecutionPolicy Bypass -File temp_fix_icons.ps1

echo ✓ Icon configuration removed
echo.
echo Testing build without icons...
call npm run dist:win

if %errorlevel% equ 0 (
    echo.
    echo ✓ SUCCESS! Build worked without icons.
    echo The icon file was definitely the problem.
    echo.
    echo You can now:
    echo 1. Use this version (no icon)
    echo 2. Create a proper ICO file later
    echo 3. Use PNG format instead
) else (
    echo.
    echo ✗ Build still failed - there's another issue beyond the icon.
)

REM Restore original package.json
copy package.json.icon-backup package.json
del package.json.icon-backup
del temp_fix_icons.ps1

goto end

:use_png
echo.
echo Changing configuration to use PNG instead of ICO...

REM Backup package.json
copy package.json package.json.png-backup

REM Replace .ico with .png in package.json
powershell -Command "(Get-Content package.json) -replace 'icon\.ico', 'icon.png' | Set-Content package.json"

echo ✓ Configuration changed to use PNG
echo.
echo Testing build with PNG icons...
call npm run dist:win

if %errorlevel% equ 0 (
    echo.
    echo ✓ SUCCESS! Build worked with PNG icons.
    echo The ICO file was corrupted.
) else (
    echo.
    echo ✗ Build still failed with PNG icons.
    REM Restore original
    copy package.json.png-backup package.json
    del package.json.png-backup
)

goto end

:ico_info
echo.
echo ========================================
echo ICO File Conversion Options
echo ========================================
echo.
echo The current icon.ico file appears to be corrupted.
echo Here are ways to create a proper ICO file:
echo.
echo 1. Online Converter:
echo    - Go to: https://convertio.co/png-ico/
echo    - Upload your assets\icon.png
echo    - Download the converted .ico file
echo    - Replace assets\icon.ico with the new file
echo.
echo 2. Windows Built-in:
echo    - Right-click assets\icon.png
echo    - Open with Paint
echo    - Save As ^> Other formats ^> ICO
echo.
echo 3. Use PNG instead:
echo    - Run this script again and choose option 2
echo.
echo After fixing the icon, run quick-build.bat again.

:end
echo.
pause
