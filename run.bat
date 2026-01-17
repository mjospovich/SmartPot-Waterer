@echo off
REM SmartPot Waterer API Startup Script (Windows)

setlocal EnableDelayedExpansion

echo.
echo ==============================
echo   SmartPot Waterer API
echo ==============================
echo.

cd /d "%~dp0"

REM ============================================================================
REM Check Python installation
REM ============================================================================
set PYTHON_CMD=

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ERROR: Python not found. Please install Python 3.8+
        echo Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Check Python version
for /f "tokens=*" %%i in ('%PYTHON_CMD% -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
echo Using Python %PYTHON_VERSION%

REM ============================================================================
REM Setup virtual environment
REM ============================================================================
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment
        echo Try: %PYTHON_CMD% -m pip install --user virtualenv
        pause
        exit /b 1
    )
)

REM Activate virtual environment (Windows)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment activation script not found
    echo Try deleting the venv folder and running this script again
    pause
    exit /b 1
)

REM ============================================================================
REM Upgrade pip and install dependencies
REM ============================================================================
echo Checking pip...

REM Upgrade pip
python -m pip install --upgrade pip --quiet 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not upgrade pip, continuing...
)

REM Install setuptools and wheel
python -m pip install --upgrade setuptools wheel --quiet 2>nul

REM Install requirements
echo Installing dependencies...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --quiet
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies
        echo.
        echo Common fixes:
        echo   1. Check your internet connection
        echo   2. Try: python -m pip install -r requirements.txt --verbose
        echo   3. If SSL errors: python -m pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM ============================================================================
REM Load environment variables from .env
REM ============================================================================
if exist ".env" (
    echo Loading .env file...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        REM Skip comments
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Default values
if not defined API_HOST set API_HOST=0.0.0.0
if not defined API_PORT set API_PORT=8001
if not defined API_ENV set API_ENV=dev

REM ============================================================================
REM Start server
REM ============================================================================
echo Starting server on http://%API_HOST%:%API_PORT%
echo Environment: %API_ENV%
echo Press Ctrl+C to stop
echo.

if "%API_ENV%"=="dev" (
    python -m uvicorn api.src.main:app --host %API_HOST% --port %API_PORT% --reload
) else (
    python -m uvicorn api.src.main:app --host %API_HOST% --port %API_PORT%
)

pause
