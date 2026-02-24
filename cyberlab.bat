@echo off
REM CyberLab Assistant Windows Launcher
REM Usage: cyberlab.bat [arguments]

REM Check if Python is available (try multiple versions)
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        REM Try Python313 directly
        C:\Python313\python.exe --version >nul 2>&1
        if errorlevel 1 (
            echo Error: Python is not installed or not in PATH
            echo Please install Python 3.9 or later from https://python.org
            pause
            exit /b 1
        ) else (
            set PYTHON=C:\Python313\python.exe
        )
    ) else (
        set PYTHON=py
    )
) else (
    set PYTHON=python
)

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Run the CLI with any arguments passed
%PYTHON% -m slm.cli %*

REM Exit with the same code as the Python script
exit /b %errorlevel%
