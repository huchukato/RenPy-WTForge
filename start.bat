@echo off
REM Ren'Py WTForge - Windows Launcher

cd /d "%~dp0"

REM Controlla se uv è installato
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WTForge] uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    REM Aggiorna PATH per questa sessione
    set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
)

REM Verifica di nuovo
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WTForge] ERROR: uv installation failed.
    echo Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo [WTForge] Starting...
for /f "delims=" %%i in ('where python') do set PYTHON_BIN=%%i & goto found_python
:found_python
uv run --python "%PYTHON_BIN%" wt_tool.py
pause
