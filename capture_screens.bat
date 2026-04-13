@echo off
echo.
echo === SCB Demo Screen Capture ===
echo.
echo Make sure the demo server is running at http://localhost:8888
echo (If not, open a terminal and run: python -m http.server 8888)
echo.
pause
cd /d "%~dp0"
python capture_screens.py
