@echo off
rem Windows: start the oyster wallet (if needed), wait for sync, then open the menu.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% main.py 11
%PY% main.py
pause
