@echo off
echo ========================================
echo SupplyLine MRO Suite - Portable Package Creator
echo ========================================
echo.

REM Check if build exists
if not exist "app-build\win-unpacked\SupplyLine MRO Suite.exe" (
    echo ERROR: Build not found!
    echo Please run the build process first.
    echo Expected location: app-build\win-unpacked\
    pause
    exit /b 1
)

echo Creating portable package...
echo.

REM Create package directory
set PACKAGE_DIR=SupplyLine-MRO-Suite-Portable
if exist "%PACKAGE_DIR%" (
    echo Removing existing package directory...
    rmdir /s /q "%PACKAGE_DIR%"
)

mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\App"

echo Copying application files...
xcopy "app-build\win-unpacked\*" "%PACKAGE_DIR%\App\" /E /I /H /Y

echo Creating launch script...
echo @echo off > "%PACKAGE_DIR%\Launch-SupplyLine.bat"
echo echo Starting SupplyLine MRO Suite... >> "%PACKAGE_DIR%\Launch-SupplyLine.bat"
echo cd /d "%%~dp0App" >> "%PACKAGE_DIR%\Launch-SupplyLine.bat"
echo start "" "SupplyLine MRO Suite.exe" >> "%PACKAGE_DIR%\Launch-SupplyLine.bat"

echo Creating README file...
echo SupplyLine MRO Suite - Portable Version > "%PACKAGE_DIR%\README.txt"
echo. >> "%PACKAGE_DIR%\README.txt"
echo REQUIREMENTS: >> "%PACKAGE_DIR%\README.txt"
echo - Windows 10/11 (64-bit) >> "%PACKAGE_DIR%\README.txt"
echo - Python 3.8+ (for backend server) >> "%PACKAGE_DIR%\README.txt"
echo - 4GB RAM minimum >> "%PACKAGE_DIR%\README.txt"
echo. >> "%PACKAGE_DIR%\README.txt"
echo TO RUN: >> "%PACKAGE_DIR%\README.txt"
echo 1. Double-click "Launch-SupplyLine.bat" >> "%PACKAGE_DIR%\README.txt"
echo 2. Wait for application to start >> "%PACKAGE_DIR%\README.txt"
echo 3. Login with admin credentials >> "%PACKAGE_DIR%\README.txt"
echo. >> "%PACKAGE_DIR%\README.txt"
echo DEFAULT LOGIN: >> "%PACKAGE_DIR%\README.txt"
echo Username: ADMIN001 >> "%PACKAGE_DIR%\README.txt"
echo Password: admin123 >> "%PACKAGE_DIR%\README.txt"

echo Copying documentation...
copy "PORTABLE_DEPLOYMENT_GUIDE.md" "%PACKAGE_DIR%\" >nul 2>&1

echo.
echo ========================================
echo Package Created Successfully!
echo ========================================
echo.
echo Location: %CD%\%PACKAGE_DIR%\
echo.
echo Contents:
echo - App\                    (Application files)
echo - Launch-SupplyLine.bat   (Quick launcher)
echo - README.txt              (User instructions)
echo - PORTABLE_DEPLOYMENT_GUIDE.md (Detailed guide)
echo.
echo To deploy to thumb drive:
echo 1. Copy entire "%PACKAGE_DIR%" folder to thumb drive
echo 2. Users can run "Launch-SupplyLine.bat" to start
echo.
echo Package size: 
for /f %%A in ('dir "%PACKAGE_DIR%" /s /-c ^| find "bytes"') do echo %%A

echo.
echo Ready for deployment!
pause
