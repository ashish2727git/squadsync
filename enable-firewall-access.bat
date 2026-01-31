@echo off
echo ================================================
echo   SquadSync - Enable Firewall Access
echo ================================================
echo.
echo This will allow mobile devices to access SquadSync
echo Requires Administrator privileges
echo.
pause

echo.
echo Opening port 3000 in Windows Firewall...
netsh advfirewall firewall add rule name="SquadSync Port 3000" dir=in action=allow protocol=TCP localport=3000

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Port 3000 is now accessible from your network
    echo.
    echo Your phone can now access SquadSync at:
    echo http://192.168.1.5:3000
) else (
    echo FAILED! Please run this file as Administrator:
    echo   Right-click -^> "Run as administrator"
)

echo.
pause
