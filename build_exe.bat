@echo off
title Build Standalone Executable
echo ==============================================
echo Building Standalone Mouse Pointer Highlighter
echo ==============================================
echo Compiling into single offline .exe file...

.\venv\Scripts\pyinstaller --noconsole --onefile --name "MouseHighlighter" main.py

echo.
echo ==============================================
echo Build Completed!
echo You can find your standalone app inside: dist\MouseHighlighter.exe
echo ==============================================
pause
