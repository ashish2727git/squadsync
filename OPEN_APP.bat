@echo off
echo ================================================
echo   SquadSync - Opening Application
echo ================================================
echo.
echo Opening SquadSync in your default browser...
echo.
echo URL: http://localhost:3000
echo.

start http://localhost:3000

echo.
echo ================================================
echo   Application opened!
echo ================================================
echo.
echo What you can do now:
echo   1. Register a new account
echo   2. Complete the 3-step onboarding
echo   3. Create and join squads
echo   4. Install on your mobile phone
echo.
echo Documentation:
echo   - USER_GUIDE.md - How to use features
echo   - MOBILE_INSTALL_GUIDE.md - Install on phone
echo   - UI_REDESIGN_COMPLETE.md - Design details
echo.
echo To manage services:
echo   - View logs:    docker-compose logs -f
echo   - Stop app:     docker-compose down
echo   - Restart app:  docker-compose up -d
echo.
pause
