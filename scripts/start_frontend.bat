@echo off

cd /d "%~dp0..\client"

set JENKINS_NODE_COOKIE=dontKillMe

start "Vue Server" /B npm.cmd run dev -- --host 0.0.0.0

echo Vue server started.