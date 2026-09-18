@echo off
setlocal

cd /d "%~dp0"
python -m PyInstaller --clean --noconfirm main.spec

endlocal