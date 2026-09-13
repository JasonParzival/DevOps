@echo off

cd /d "%~dp0.."

start "Django Server" /B .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

echo Django server started.