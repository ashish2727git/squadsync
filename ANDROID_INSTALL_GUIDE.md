# 📱 SquadSync - Android Installation Guide

## 🎯 **3 Ways to Install on Android**

---

## ⚡ **METHOD 1: Quick PWA Install (Recommended - Works Now!)**

### **Step 1: Find Your Computer's IP Address**

**On Windows (PowerShell):**
```powershell
ipconfig
```
Look for "IPv4 Address" under your network adapter (e.g., `192.168.1.100`)

### **Step 2: Access from Your Android Phone**

1. **Make sure your phone is on the SAME WiFi network as your computer**
2. Open Chrome on your Android phone
3. Go to: `http://YOUR_COMPUTER_IP:3000`
   - Example: `http://192.168.1.100:3000`

### **Step 3: Install the PWA**

1. You'll see the beautiful SquadSync login page
2. Tap the **three dots menu** (⋮) in Chrome
3. Select **"Add to Home screen"** or **"Install app"**
4. Name it: **SquadSync**
5. Tap **"Add"** or **"Install"**
6. **App icon appears on your home screen!** 🎉

### **Step 4: Use Like a Regular App**

- Launch from home screen
- Full-screen experience (no browser UI)
- Works offline (cached)
- Fast and smooth
- Receives push notifications (if enabled)

---

## 🎁 **METHOD 2: Generate Android APK (For Sharing)**

### **Using PWABuilder (Online Tool - Easiest)**

#### **Step 1: Make Your App Accessible**

First, we need to expose your local app to the internet temporarily:

**Install ngrok (tunneling tool):**
```powershell
# Download ngrok from https://ngrok.com/download
# Or use chocolatey:
choco install ngrok

# Run ngrok to expose your app:
ngrok http 3000
```

You'll get a URL like: `https://abc123.ngrok.io`

#### **Step 2: Generate APK Online**

1. Go to: **https://www.pwabuilder.com/**
2. Enter your ngrok URL: `https://abc123.ngrok.io`
3. Click **"Start"**
4. Click **"Package for Stores"**
5. Select **"Android"**
6. Configure settings:
   - App name: `SquadSync`
   - Package ID: `com.squadsync.app`
   - Version: `1.0.0`
7. Click **"Generate"**
8. Download the APK file
9. Transfer to your phone
10. Install the APK

---

## 🔧 **METHOD 3: Build Native Android App with Capacitor**

### **For a Full Native Experience**

I'll create a native Android build setup for you!

#### **Prerequisites:**
- Android Studio installed
- Java JDK installed
- Node.js installed

Let me set this up for you...

