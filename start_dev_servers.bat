@echo off
echo ===================================================
echo    SupplyLine MRO Suite - Development Environment
echo ===================================================
echo.
echo Starting development servers...
echo.

REM Store the project root directory
set PROJECT_ROOT=%~dp0

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8+ and try again.
    goto :error
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Node.js is not installed or not in PATH. Please install Node.js v14+ and try again.
    goto :error
)

REM Create database directory if it doesn't exist
if not exist "%PROJECT_ROOT%database" (
    echo Creating database directory...
    mkdir "%PROJECT_ROOT%database"
)

echo Starting backend server...
start cmd /k "cd /d %PROJECT_ROOT%backend && echo Activating virtual environment if it exists... && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (echo No virtual environment found, continuing without it...)) && echo Installing backend dependencies... && pip install -r requirements.txt && echo Starting Flask server... && python run.py"

echo Starting frontend server...
start cmd /k "cd /d %PROJECT_ROOT%frontend && echo Installing frontend dependencies... && npm install && echo Starting Vite development server... && npm run dev"

echo.
echo ===================================================
echo Development servers are starting in separate windows.
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend API will be available at: http://localhost:5000
echo.
echo Default admin credentials:
echo - Employee Number: ADMIN001
echo - Password: admin123
echo ===================================================
echo.
echo Press any key to close this window...
pause > nul
exit /b 0

:error
echo.
echo Error occurred. Please check the requirements and try again.
echo.
echo Press any key to close this window...
pause > nul
exit /b 1
