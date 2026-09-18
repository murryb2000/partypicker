@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto run
py -3 --version >nul 2>&1
if errorlevel 1 goto missing
py -3 -m venv .venv
if errorlevel 1 goto error
:run
if exist ".venv\ready-v2" goto launch
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo ready > .venv\ready-v2
:launch
.venv\Scripts\python.exe party_picker.py
if errorlevel 1 goto error
exit /b 0
:missing
echo Bitte Python 3.12 oder neuer von python.org installieren, inklusive Python Launcher.
pause
exit /b 1
:error
echo Start fehlgeschlagen. Bitte die Fehlermeldung oben kopieren.
pause
exit /b 1
