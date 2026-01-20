@echo off
chcp 65001 >nul
echo [GitHub Launcher Installer]
echo ==========================

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile '%TEMP%\python-setup.exe'"
    start /wait "" "%TEMP%\python-setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    echo Please restart the installer after Python installation.
    pause
    exit /b
)

REM Download the launcher
echo Downloading launcher...
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set LAUNCHER_URL=https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/github_launcher.pyw

powershell -Command "Invoke-WebRequest -Uri '%LAUNCHER_URL%' -OutFile '%STARTUP%\github_launcher.pyw'"

REM Create a shortcut to run at startup (alternative method)
echo Creating startup entry...
echo Set WshShell = CreateObject("WScript.Shell") > "%STARTUP%\launch.vbs"
echo strPath = WshShell.ExpandEnvironmentStrings("%STARTUP%") >> "%STARTUP%\launch.vbs"
echo WshShell.Run chr(34) ^& strPath ^& "\github_launcher.pyw" ^& Chr(34), 0 >> "%STARTUP%\launch.vbs"
echo Set WshShell = Nothing >> "%STARTUP%\launch.vbs"

echo.
echo Installation complete!
echo The launcher will:
echo 1. Run on every startup
echo 2. Check GitHub for updates
echo 3. Install required packages automatically
echo 4. Run the latest version of your script
echo.
echo Launcher location: %STARTUP%\github_launcher.pyw
pause