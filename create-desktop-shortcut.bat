@echo off
echo Creating SupplyLine MRO Suite Desktop Shortcut...
echo.

REM Check if app is installed in Program Files
set INSTALL_DIR=%PROGRAMFILES%\SupplyLine MRO Suite
if exist "%INSTALL_DIR%\SupplyLine MRO Suite.exe" (
    echo ✓ Found installed app at: %INSTALL_DIR%
    set TARGET_PATH=%INSTALL_DIR%\SupplyLine MRO Suite.exe
    set WORKING_DIR=%INSTALL_DIR%
) else (
    echo App not found in Program Files, checking portable location...
    REM Check portable location
    set CURRENT_DIR=%~dp0
    set PORTABLE_PATH=%CURRENT_DIR%installer\SupplyLine-MRO-Suite\SupplyLine MRO Suite.exe
    if exist "%PORTABLE_PATH%" (
        echo ✓ Found portable app at: %PORTABLE_PATH%
        set TARGET_PATH=%PORTABLE_PATH%
        set WORKING_DIR=%CURRENT_DIR%installer\SupplyLine-MRO-Suite
    ) else (
        echo ✗ Error: Cannot find SupplyLine MRO Suite executable!
        echo.
        echo Please check:
        echo 1. App is installed in: %INSTALL_DIR%
        echo 2. Or portable version is in: %PORTABLE_PATH%
        pause
        exit /b 1
    )
)

echo.
echo Creating desktop shortcut...
echo Target: %TARGET_PATH%
echo Working Directory: %WORKING_DIR%

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\SupplyLine MRO Suite.lnk

echo Desktop path: %DESKTOP%
echo Shortcut path: %SHORTCUT_PATH%

REM Use PowerShell to create shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%WORKING_DIR%'; $Shortcut.Description = 'SupplyLine MRO Suite - Tool and Chemical Management System'; $Shortcut.Save(); Write-Host 'Shortcut created successfully'}"

REM Verify shortcut was created
if exist "%SHORTCUT_PATH%" (
    echo.
    echo ✓ Desktop shortcut created successfully!
    echo Location: %SHORTCUT_PATH%
    echo.
    echo You should now see "SupplyLine MRO Suite" icon on your desktop.
) else (
    echo.
    echo ✗ Failed to create desktop shortcut automatically.
    echo.
    echo Manual shortcut creation:
    echo 1. Right-click on your desktop
    echo 2. Select "New" → "Shortcut"
    echo 3. Browse to: %TARGET_PATH%
    echo 4. Name it: SupplyLine MRO Suite
    echo 5. Click Finish
)

echo.
pause
