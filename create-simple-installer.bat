@echo off
REM Simple Installer Creator for SupplyLine MRO Suite
REM This script creates a basic installer using the built application

echo ========================================
echo SupplyLine MRO Suite - Simple Installer
echo ========================================
echo.

REM Check if the built application exists
if not exist "dist-new\win-unpacked\SupplyLine MRO Suite.exe" (
    echo ERROR: Built application not found!
    echo Please run the build process first.
    pause
    exit /b 1
)

echo Creating simple installer package...
echo.

REM Create installer directory
if not exist "installer" mkdir installer

REM Copy the application
echo Copying application files...
xcopy "dist-new\win-unpacked\*" "installer\SupplyLine-MRO-Suite\" /E /I /Y >nul

REM Create a simple installer script
echo Creating installer script...
echo @echo off > installer\install.bat
echo echo Installing SupplyLine MRO Suite... >> installer\install.bat
echo. >> installer\install.bat
echo REM Create installation directory >> installer\install.bat
echo set INSTALL_DIR=%%PROGRAMFILES%%\SupplyLine MRO Suite >> installer\install.bat
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%" >> installer\install.bat
echo. >> installer\install.bat
echo REM Copy files >> installer\install.bat
echo xcopy "SupplyLine-MRO-Suite\*" "%%INSTALL_DIR%%\" /E /I /Y >> installer\install.bat
echo. >> installer\install.bat
echo REM Create desktop shortcut >> installer\install.bat
echo echo Creating desktop shortcut... >> installer\install.bat
echo set DESKTOP=%%USERPROFILE%%\Desktop >> installer\install.bat
echo echo [InternetShortcut] ^> "%%DESKTOP%%\SupplyLine MRO Suite.lnk" >> installer\install.bat
echo echo URL=file:///%%INSTALL_DIR:\=/%%/SupplyLine MRO Suite.exe ^>^> "%%DESKTOP%%\SupplyLine MRO Suite.lnk" >> installer\install.bat
echo. >> installer\install.bat
echo echo Installation completed! >> installer\install.bat
echo echo You can now run SupplyLine MRO Suite from the desktop shortcut. >> installer\install.bat
echo pause >> installer\install.bat

REM Create uninstaller
echo Creating uninstaller...
echo @echo off > installer\uninstall.bat
echo echo Uninstalling SupplyLine MRO Suite... >> installer\uninstall.bat
echo. >> installer\uninstall.bat
echo set INSTALL_DIR=%%PROGRAMFILES%%\SupplyLine MRO Suite >> installer\uninstall.bat
echo set DESKTOP=%%USERPROFILE%%\Desktop >> installer\uninstall.bat
echo. >> installer\uninstall.bat
echo REM Remove desktop shortcut >> installer\uninstall.bat
echo if exist "%%DESKTOP%%\SupplyLine MRO Suite.lnk" del "%%DESKTOP%%\SupplyLine MRO Suite.lnk" >> installer\uninstall.bat
echo. >> installer\uninstall.bat
echo REM Remove installation directory >> installer\uninstall.bat
echo if exist "%%INSTALL_DIR%%" rmdir /s /q "%%INSTALL_DIR%%" >> installer\uninstall.bat
echo. >> installer\uninstall.bat
echo echo Uninstallation completed! >> installer\uninstall.bat
echo pause >> installer\uninstall.bat

REM Create README
echo Creating installation instructions...
echo SupplyLine MRO Suite - Installation Package > installer\README.txt
echo ============================================= >> installer\README.txt
echo. >> installer\README.txt
echo This package contains the SupplyLine MRO Suite application. >> installer\README.txt
echo. >> installer\README.txt
echo INSTALLATION OPTIONS: >> installer\README.txt
echo. >> installer\README.txt
echo Option 1 - Portable Use: >> installer\README.txt
echo   - Navigate to the SupplyLine-MRO-Suite folder >> installer\README.txt
echo   - Double-click "SupplyLine MRO Suite.exe" to run >> installer\README.txt
echo   - No installation required! >> installer\README.txt
echo. >> installer\README.txt
echo Option 2 - Full Installation: >> installer\README.txt
echo   - Right-click "install.bat" and select "Run as administrator" >> installer\README.txt
echo   - Follow the prompts to install to Program Files >> installer\README.txt
echo   - A desktop shortcut will be created >> installer\README.txt
echo. >> installer\README.txt
echo UNINSTALLATION: >> installer\README.txt
echo   - Run "uninstall.bat" as administrator to remove the application >> installer\README.txt
echo. >> installer\README.txt
echo SYSTEM REQUIREMENTS: >> installer\README.txt
echo   - Windows 10 or later >> installer\README.txt
echo   - 4GB RAM minimum >> installer\README.txt
echo   - 500MB free disk space >> installer\README.txt
echo. >> installer\README.txt
echo For support, please contact the SupplyLine MRO Suite team. >> installer\README.txt

echo.
echo ========================================
echo INSTALLER PACKAGE CREATED SUCCESSFULLY!
echo ========================================
echo.
echo Location: installer\ folder
echo.
echo Contents:
echo - SupplyLine-MRO-Suite\ (Application files)
echo - install.bat (Installation script)
echo - uninstall.bat (Uninstallation script)  
echo - README.txt (Installation instructions)
echo.
echo You can now:
echo 1. Zip the entire 'installer' folder for distribution
echo 2. Share the folder directly on a network drive
echo 3. Copy to USB drives for offline installation
echo.
echo The application can be used portably or installed system-wide.
echo.
pause
