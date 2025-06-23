
@echo off
echo Установка Railway CLI...
powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
powershell -Command "iwr https://railway.app/install.ps1 -useb | iex"

echo Проверка Railway CLI версии...
railway version

echo Авторизация...
railway login

echo Инициализация проекта...
railway init

echo Загрузка проекта на Railway...
railway up

pause
