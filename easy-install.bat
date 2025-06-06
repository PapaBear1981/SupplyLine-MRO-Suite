@echo off
echo ========================================
echo SupplyLine MRO Suite - Easy Installer
echo ========================================
echo.

REM Get current directory
set CURRENT_DIR=%~dp0
echo Current directory: %CURRENT_DIR%

REM Install to user's AppData folder (no admin rights needed)
set INSTALL_DIR=%LOCALAPPDATA%\SupplyLine MRO Suite
echo Installing to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Check if source files exist
if not exist "%CURRENT_DIR%installer\SupplyLine-MRO-Suite\SupplyLine MRO Suite.exe" (
    echo ✗ Error: Source files not found!
    echo Expected: %CURRENT_DIR%installer\SupplyLine-MRO-Suite\
    echo.
    echo Please make sure you're running this from the correct folder.
    pause
    exit /b 1
)

REM Copy files
echo Copying application files...
echo Source: %CURRENT_DIR%installer\SupplyLine-MRO-Suite
echo Target: %INSTALL_DIR%
xcopy "%CURRENT_DIR%installer\SupplyLine-MRO-Suite\*" "%INSTALL_DIR%\" /E /I /Y /H

REM Check if copy was successful
if exist "%INSTALL_DIR%\SupplyLine MRO Suite.exe" (
    echo ✓ Application files copied successfully!
) else (
    echo ✗ Error: Failed to copy application files!
    pause
    exit /b 1
)

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\SupplyLine MRO Suite.lnk
set TARGET_PATH=%INSTALL_DIR%\SupplyLine MRO Suite.exe

echo Desktop: %DESKTOP%
echo Shortcut: %SHORTCUT_PATH%
echo Target: %TARGET_PATH%

REM Create shortcut using VBScript (more compatible)
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\shortcut.vbs"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%TEMP%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\shortcut.vbs"
echo oLink.TargetPath = "%TARGET_PATH%" >> "%TEMP%\shortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\shortcut.vbs"
echo oLink.Description = "SupplyLine MRO Suite - Tool and Chemical Management" >> "%TEMP%\shortcut.vbs"
echo oLink.Save >> "%TEMP%\shortcut.vbs"

cscript //nologo "%TEMP%\shortcut.vbs"
del "%TEMP%\shortcut.vbs"

REM Check if shortcut was created
if exist "%SHORTCUT_PATH%" (
    echo ✓ Desktop shortcut created successfully!
) else (
    echo ✗ Warning: Could not create desktop shortcut automatically
    echo You can create it manually by right-clicking the desktop
)

REM Create Start Menu shortcut
echo.
echo Creating Start Menu shortcut...
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
set STARTMENU_SHORTCUT=%STARTMENU%\SupplyLine MRO Suite.lnk

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\startmenu.vbs"
echo sLinkFile = "%STARTMENU_SHORTCUT%" >> "%TEMP%\startmenu.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\startmenu.vbs"
echo oLink.TargetPath = "%TARGET_PATH%" >> "%TEMP%\startmenu.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\startmenu.vbs"
echo oLink.Description = "SupplyLine MRO Suite - Tool and Chemical Management" >> "%TEMP%\startmenu.vbs"
echo oLink.Save >> "%TEMP%\startmenu.vbs"

cscript //nologo "%TEMP%\startmenu.vbs"
del "%TEMP%\startmenu.vbs"

if exist "%STARTMENU_SHORTCUT%" (
    echo ✓ Start Menu shortcut created successfully!
) else (
    echo ✗ Warning: Could not create Start Menu shortcut
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo ✓ Application installed to: %INSTALL_DIR%
echo ✓ Desktop shortcut: %SHORTCUT_PATH%
echo ✓ Start Menu shortcut: %STARTMENU_SHORTCUT%
echo.
echo You can now run SupplyLine MRO Suite from:
echo 1. Desktop shortcut (double-click the icon)
echo 2. Start Menu (search for "SupplyLine")
echo 3. Direct path: %INSTALL_DIR%\SupplyLine MRO Suite.exe
echo.
echo To uninstall: Delete the folder %INSTALL_DIR% and the shortcuts
echo.
pause
