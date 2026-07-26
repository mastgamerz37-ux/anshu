@echo off
setlocal EnableDelayedExpansion

echo [ANSH] Checking Python installation...
:: Check for py launcher first (most reliable on Windows)
set "PYTHON_CMD=py"
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set "PYTHON_CMD=python"
    !PYTHON_CMD! --version >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo [ANSH] Python is not installed!
        echo [ANSH] Automatically downloading and installing Python for you...
        winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        echo.
        echo [ANSH] Python has been installed successfully!
        echo [ANSH] PLEASE CLOSE THIS WINDOW AND RUN start.bat AGAIN.
        pause
        exit /b
    )
)

if not exist venv (
    echo [ANSH] Creating Virtual Environment (First time setup)...
    %PYTHON_CMD% -m venv venv
)

echo [ANSH] Activating Environment...
call venv\Scripts\activate.bat

:: Upgrade pip and install requirements
echo [ANSH] Installing/Verifying dependencies (This may take a while on first run)...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo [ANSH] Starting ANSH...
python main.py
pause
