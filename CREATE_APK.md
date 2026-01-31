# 📦 **Create Android APK for SquadSync**

## 🎯 **3 Methods to Create APK**

---

## ⚡ **METHOD 1: Capacitor (Recommended - Full Native)**

### **What You'll Get:**
- ✅ True native Android app
- ✅ APK file you can share
- ✅ Install on any Android device
- ✅ Works offline completely
- ✅ Access to native Android features

### **Prerequisites:**
```powershell
# Check if Node.js is installed
node --version

# Check if npm is installed
npm --version
```

### **Step 1: Install Capacitor**

Open PowerShell in the project folder and run:

```powershell
cd frontend
npm install @capacitor/core @capacitor/cli @capacitor/android
```

### **Step 2: Initialize Capacitor**

```powershell
npx cap init "SquadSync" "com.squadsync.app" --web-dir=dist
```

### **Step 3: Build Frontend**

```powershell
npm run build
```

### **Step 4: Add Android Platform**

```powershell
npx cap add android
```

### **Step 5: Copy Web Assets**

```powershell
npx cap copy android
npx cap sync android
```

### **Step 6: Update Config**

The file `frontend/capacitor.config.ts` should look like:

```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.squadsync.app',
  appName: 'SquadSync',
  webDir: 'dist',
  server: {
    // For development: point to your backend
    url: 'http://192.168.1.5:3000',
    cleartext: true
  }
};

export default config;
```

### **Step 7: Build APK**

**Option A: Using Android Studio (Recommended)**

1. Install Android Studio from: https://developer.android.com/studio
2. Open Android Studio
3. Select "Open an existing project"
4. Navigate to: `C:\Users\19255\Desktop\squadsync\frontend\android`
5. Wait for Gradle sync to complete
6. Go to: **Build → Build Bundle(s) / APK(s) → Build APK(s)**
7. Wait for build to complete
8. Find APK at: `frontend\android\app\build\outputs\apk\debug\app-debug.apk`

**Option B: Using Command Line**

```powershell
cd android
.\gradlew assembleDebug
```

APK will be at: `app\build\outputs\apk\debug\app-debug.apk`

### **Step 8: Transfer APK to Phone**

**Option 1: USB Cable**
1. Connect phone to computer
2. Copy `app-debug.apk` to phone's Download folder
3. On phone, open Files app
4. Tap the APK file
5. Allow installation from unknown sources if prompted
6. Tap "Install"

**Option 2: Share via Cloud**
1. Upload APK to Google Drive / Dropbox
2. Download on phone
3. Install

**Option 3: Direct URL**
1. Put APK in a folder
2. Use Python to serve: `python -m http.server 8080`
3. On phone, download from: `http://192.168.1.5:8080/app-debug.apk`

---

## 🌐 **METHOD 2: PWABuilder (Easiest - No Coding)**

### **What You'll Get:**
- ✅ Trusted Web Activity (TWA) APK
- ✅ Google Play ready
- ✅ Works like native app
- ✅ Automatic updates from web

### **Requirements:**
Your app must be accessible via HTTPS URL (not localhost)

### **Step 1: Expose Your App to Internet**

**Install ngrok:**
1. Download from: https://ngrok.com/download
2. Extract and run:

```powershell
.\ngrok.exe http 3000
```

You'll get a URL like: `https://abc123.ngrok-free.app`

### **Step 2: Use PWABuilder**

1. Go to: **https://www.pwabuilder.com/**
2. Enter your ngrok URL
3. Click "Start"
4. Click "Package for Stores"
5. Select "Android"
6. Configure:
   - App name: **SquadSync**
   - Package ID: **com.squadsync.app**
   - Host: Your ngrok URL
   - Version: **1.0.0**
7. Click "Generate Package"
8. Download the APK

### **Step 3: Install on Phone**
- Transfer APK to phone
- Install like normal app

---

## 🔨 **METHOD 3: Bubblewrap (Google's Official TWA Tool)**

### **What You'll Get:**
- ✅ Official TWA wrapper
- ✅ Signed APK
- ✅ Play Store ready

### **Step 1: Install Bubblewrap**

```powershell
npm install -g @bubblewrap/cli
```

### **Step 2: Install JDK**

Download and install: https://adoptium.net/

### **Step 3: Initialize Project**

```powershell
bubblewrap init --manifest http://192.168.1.5:3000/manifest.json
```

Follow the prompts:
- Package name: `com.squadsync.app`
- App name: `SquadSync`

### **Step 4: Build APK**

```powershell
bubblewrap build
```

APK will be in the output folder.

---

## 🎯 **Quick & Easy: Use the Automated Script**

### **I've created a script for you!**

Just run:

```batch
build-android-app.bat
```

This will:
1. Install Capacitor
2. Build the frontend
3. Create Android project
4. Set up everything
5. Guide you to build APK

---

## 📱 **Installing the APK**

### **On Your Phone:**

1. **Enable Unknown Sources:**
   - Settings → Security
   - Enable "Unknown sources" or "Install unknown apps"
   - Allow installation from Files/Chrome

2. **Transfer APK:**
   - Copy to phone via USB, or
   - Share via email/cloud, or
   - Download from local server

3. **Install:**
   - Tap the APK file
   - Tap "Install"
   - Open app!

---

## 🔐 **Creating a Signed APK (For Distribution)**

### **Generate Signing Key:**

```powershell
cd frontend\android
keytool -genkey -v -keystore squadsync-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias squadsync
```

### **Sign APK:**

In `android/app/build.gradle`, add:

```gradle
android {
    signingConfigs {
        release {
            storeFile file('squadsync-release-key.jks')
            storePassword 'your-password'
            keyAlias 'squadsync'
            keyPassword 'your-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

### **Build Signed APK:**

```powershell
cd android
.\gradlew assembleRelease
```

Signed APK: `app\build\outputs\apk\release\app-release.apk`

---

## 🎉 **SUCCESS!**

**You now have multiple ways to create an Android APK!**

### **For Quick Testing:**
- Use PWA install method (no build needed)
- URL: `http://192.168.1.5:3000`

### **For Real APK:**
- Run `build-android-app.bat`
- Or follow Capacitor method above

### **For Sharing with Friends:**
- Build signed release APK
- Share the file
- They can install on any Android device

---

## 🔧 **Troubleshooting**

### **Build Fails?**

**Check Java:**
```powershell
java -version
```
Should be Java 11 or higher

**Check Android SDK:**
- Install Android Studio
- Install SDK via SDK Manager
- Set ANDROID_HOME environment variable

### **APK Won't Install?**

- Enable "Unknown sources" in phone settings
- Make sure APK is not corrupted
- Try transferring again

### **App Crashes?**

- Check logs: `npx cap open android` then View → Tool Windows → Logcat
- Make sure backend is accessible
- Update server URL in capacitor.config.ts

---

## 📚 **Next Steps**

1. **Build your first APK** using `build-android-app.bat`
2. **Install on your phone**
3. **Test all features**
4. **Share with your squad!**

**Enjoy your native Android app!** 📱🎮✨
