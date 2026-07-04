@echo off
chcp 65001 >nul
title JARBISEO — 자비서
cd /d "%~dp0"

rem --- 1. Check Node.js ---------------------------------------------------
where node >nul 2>nul
if errorlevel 1 goto noNode
goto hasNode

:noNode
echo.
echo  [!] Node.js가 설치되어 있지 않습니다.
echo      지금 열리는 페이지에서 LTS 버전을 설치한 뒤,
echo      이 파일(자비서시작.bat)을 다시 더블클릭해 주세요.
start https://nodejs.org/ko/download
pause
exit /b 1

:hasNode
rem --- 2. First-run install ------------------------------------------------
if exist node_modules goto installed
echo.
echo  처음 실행 준비 중입니다... 1~2분 정도 걸릴 수 있습니다.
call npm install --no-audit --no-fund
if errorlevel 1 goto installFail
goto installed

:installFail
echo.
echo  [!] 설치에 실패했습니다. 인터넷 연결을 확인하고 다시 실행해 주세요.
pause
exit /b 1

:installed
rem --- 3. First-run API key setup -------------------------------------------
if exist .env goto hasKey
echo.
echo  Anthropic API 키가 필요합니다. (https://console.anthropic.com 에서 발급)
echo  키는 이 컴퓨터의 .env 파일에만 저장되며 외부로 나가지 않습니다.
echo.
set /p APIKEY="  API 키를 붙여넣고 Enter: "
>.env echo ANTHROPIC_API_KEY=%APIKEY%
echo.
echo  저장 완료. (.env 파일은 절대 다른 사람과 공유하지 마세요)

:hasKey
rem --- 4. Launch: open browser after the server has a moment to boot --------
start "" /min cmd /c "timeout /t 2 >nul & start http://localhost:3800"
echo.
echo  ============================================
echo   자비서를 시작합니다.
echo   브라우저가 자동으로 열립니다: http://localhost:3800
echo   이 검은 창은 닫지 마세요. (닫으면 자비서가 종료됩니다)
echo  ============================================
echo.
node server.js
pause
