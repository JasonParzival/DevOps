@echo off

cd /d "C:\ProgramData\Jenkins\deploy\DevOps"

set JENKINS_NODE_COOKIE=dontKillMe

start "Django Server" /B .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

echo Django server started.