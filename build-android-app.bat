@echo off
echo ================================================
echo   SquadSync - Android App Builder
echo ================================================
echo.
echo This will create a native Android app package
echo.
pause

cd frontend

echo.
echo [1/5] Installing Capacitor...
call npm install @capacitor/core @capacitor/cli @capacitor/android

echo.
echo [2/5] Initializing Capacitor...
call npx cap init SquadSync com.squadsync.app --web-dir=dist

echo.
echo [3/5] Adding Android platform...
call npx cap add android

echo.
echo [4/5] Building frontend...
call npm run build

echo.
echo [5/5] Copying web assets to Android...
call npx cap copy android

echo.
echo ================================================
echo   Android project created!
echo ================================================
echo.
echo Next steps:
echo   1. Open Android Studio
echo   2. Open folder: frontend\android
echo   3. Build APK: Build -^> Build Bundle(s) / APK(s) -^> Build APK(s)
echo   4. Find APK in: frontend\android\app\build\outputs\apk\debug\
echo.
echo To run on device:
echo   cd frontend
echo   npx cap run android
echo.
pause
