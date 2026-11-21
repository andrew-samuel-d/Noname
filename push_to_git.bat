@echo off
title Push CashFlowScore to GitHub
cd /d "%~dp0"
echo ========================================================
echo  Pushing CashFlowScore to https://github.com/andrew-samuel-d/Noname
echo ========================================================
echo.
git push -u origin main --force
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo  SUCCESS! Successfully pushed to GitHub main branch!
    echo ========================================================
) else (
    echo.
    echo If requested, please sign in via the browser window that popped up.
)
pause
