@echo off
cd /d "%~dp0"
echo ============================
echo   嘶好冷 EXE 打包工具
echo ============================
echo.
pip install pyinstaller
pyinstaller --onefile --windowed --name "嘶好冷" --add-data "sihaolen.py;." sihaolen.py
echo.
echo 打包完成！EXE 在 dist\ 目录下
pause
