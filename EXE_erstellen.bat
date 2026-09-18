@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Bitte zuerst Starten.bat ausfuehren und die App wieder schliessen.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install pyinstaller==6.22.3
if errorlevel 1 goto error
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onefile --name PartyPicker --icon PartyPicker.ico --add-data "PartyPicker.ico;." --add-data "PartyPicker-icon.png;." --collect-all soundfile party_picker.py
if errorlevel 1 goto error
echo Fertig: dist\PartyPicker.exe
echo Diese einzelne EXE kann weitergegeben und direkt gestartet werden.
echo Auf anderen PCs kann Windows SmartScreen zunaechst eine Warnung anzeigen.
pause
exit /b 0
:error
echo Erstellung fehlgeschlagen. Siehe Fehlermeldung oben.
pause
