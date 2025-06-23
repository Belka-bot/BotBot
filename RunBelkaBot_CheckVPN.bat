@BELKA Арсений🐿️, [22.06.2025 15:37]
BelkaBot_CheckVPN_Ready.zip

BELKA Арсений🐿️, [22.06.2025 15:42]
@echo off
chcp 65001 >nul
echo 🚀 Запуск Bebra VPN...
start "" "%USERPROFILE%\Desktop\Bebra VPN.lnk"
timeout /t 10 >nul

echo 🔍 Проверка подключения к Railway API...
curl -s https://backboard.railway.app/graphql/v2 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Нет доступа к Railway. Попробуйте другой VPN или сервер США.
    pause
    exit /b
)

echo ✅ Доступ к Railway получен. Запуск railway.exe...
cd /d "%~dp0"
.\railway.exe up
pause
