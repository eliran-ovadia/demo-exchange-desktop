@echo off
echo Building DemoExchange...
.venv\Scripts\pyinstaller DemoExchange.spec --clean

echo.
echo Clearing Windows icon cache...
taskkill /F /IM explorer.exe >nul 2>&1
del /A /Q /F "%LocalAppData%\Microsoft\Windows\Explorer\iconcache_*.db" >nul 2>&1
start explorer.exe

echo.
echo Done. dist\DemoExchange.exe is ready.
