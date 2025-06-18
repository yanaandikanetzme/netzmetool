@echo off
cd /d "%~dp0"

pip install pyinstaller
pip install -r requirements.txt

start /B python main.py
exit