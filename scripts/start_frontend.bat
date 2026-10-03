@echo off

cd /d "C:\ProgramData\Jenkins\deploy\DevOps\client"

set JENKINS_NODE_COOKIE=dontKillMe

start "Vue Server" /B node node_modules\vite\bin\vite.js --host 0.0.0.0

echo Vue server started.