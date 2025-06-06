@echo off
echo Installing SupplyLine MRO Suite...
echo.

REM Get current directory
set CURRENT_DIR=%~dp0
echo Current directory: %CURRENT_DIR%

REM Create installation directory (check both Program Files locations)
if exist "%PROGRAMFILES%" (
    set INSTALL_DIR=%PROGRAMFILES%\SupplyLine MRO Suite
) else (
    set INSTALL_DIR=%PROGRAMFILES(X86)%\SupplyLine MRO Suite
)
echo Creating installation directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying application files...
echo Source: %CURRENT_DIR%SupplyLine-MRO-Suite
echo Target: %INSTALL_DIR%
xcopy "%CURRENT_DIR%SupplyLine-MRO-Suite\*" "%INSTALL_DIR%\" /E /I /Y /H

REM Check if copy was successful
if exist "%INSTALL_DIR%\SupplyLine MRO Suite.exe" (
    echo ✓ Application files copied successfully!
) else (
    echo ✗ Error: Failed to copy application files!
    pause
    exit /b 1
)

REM Create desktop shortcut using PowerShell (more reliable)
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\SupplyLine MRO Suite.lnk
set TARGET_PATH=%INSTALL_DIR%\SupplyLine MRO Suite.exe

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'SupplyLine MRO Suite - Tool and Chemical Management'; $Shortcut.Save()"

REM Check if shortcut was created
if exist "%SHORTCUT_PATH%" (
    echo ✓ Desktop shortcut created successfully!
) else (
    echo ✗ Warning: Could not create desktop shortcut
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Application installed to: %INSTALL_DIR%
echo Desktop shortcut: %SHORTCUT_PATH%
echo.
echo You can now run SupplyLine MRO Suite from:
echo 1. Desktop shortcut
echo 2. Start Menu (search for "SupplyLine")
echo 3. Direct path: %INSTALL_DIR%\SupplyLine MRO Suite.exe
echo.
pause
