@echo off
echo Проверка пинга railway.app
ping railway.app

echo.
echo Проверка пинга backboard.railway.app
ping backboard.railway.app

echo.
echo Проверка curl https://railway.app
curl -I https://railway.app

echo.
echo Проверка curl https://backboard.railway.app
curl -I https://backboard.railway.app

pause
