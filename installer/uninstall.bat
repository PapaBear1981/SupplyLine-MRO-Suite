@echo off 
echo Uninstalling SupplyLine MRO Suite... 
 
set INSTALL_DIR=%PROGRAMFILES%\SupplyLine MRO Suite 
set DESKTOP=%USERPROFILE%\Desktop 
 
REM Remove desktop shortcut 
if exist "%DESKTOP%\SupplyLine MRO Suite.lnk" del "%DESKTOP%\SupplyLine MRO Suite.lnk" 
 
REM Remove installation directory 
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%" 
 
echo Uninstallation completed! 
pause 
