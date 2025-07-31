@echo off
echo Starting Cargo Backend Server...
echo.

REM Kích hoạt virtual environment
call .venv\Scripts\activate.bat

REM Chạy server
python run_server.py

pause 