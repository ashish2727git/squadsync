# 📱 **QUICK GUIDE: Install SquadSync on Android**

## ⚡ **Fastest Method (5 Minutes)**

---

## **Step 1: Get Your Computer's IP Address**

**Press `Windows Key + R`, type `cmd`, press Enter**

Type this command:
```
ipconfig
```

Look for: **IPv4 Address** (e.g., `192.168.1.100`)

---

## **Step 2: On Your Android Phone**

### ✅ **Make sure:**
- Phone is on the **SAME WiFi** as your computer
- SquadSync services are running (check with `docker-compose ps`)

### 📱 **Open Chrome and go to:**
```
http://YOUR_IP:3000
```

**Replace YOUR_IP with the number from Step 1**

**Example:** `http://192.168.1.100:3000`

---

## **Step 3: Install the App**

1. You'll see the SquadSync login page
2. Tap the **menu button** (⋮) in Chrome
3. Tap **"Add to Home screen"** or **"Install app"**
4. Name: **SquadSync**
5. Tap **"Add"**

**🎉 Done! App installed!**

---

## **Step 4: Use It**

- Find the **SquadSync icon** on your home screen
- Tap to open
- Enjoy full-screen app experience!
- Works exactly like the web version

---

## ✨ **Features You Get:**

✅ Full-screen (no browser UI)  
✅ App icon on home screen  
✅ Fast loading (cached)  
✅ Works offline  
✅ Push notifications ready  
✅ Looks like a native app  

---

## 🔧 **Troubleshooting**

### **Can't Connect?**

**1. Check services are running:**
```
docker-compose ps
```
All should show "Up"

**2. Check your firewall:**
- Allow port 3000 in Windows Firewall
- Or temporarily disable firewall to test

**3. Use correct IP:**
- Use IPv4 address (e.g., 192.168.x.x)
- NOT localhost or 127.0.0.1

**4. Same WiFi network:**
- Phone and computer must be on same network

### **Installation Option Not Showing?**

**Option A: Chrome Menu**
- Menu (⋮) → "Add to Home screen"

**Option B: Address Bar**
- Look for install icon (+) in address bar
- Tap to install

**Option C: Chrome Settings**
- Settings → Add to Home screen

---

## 📦 **Want a Standalone APK File?**

See: `ANDROID_APK_BUILDER.md` for instructions to:
- Build native Android APK
- Share APK with friends
- Install without browser

---

## 🎮 **That's It!**

**You now have SquadSync installed on your Android phone!**

**Open it and:**
1. Register your account
2. Complete onboarding
3. Create squads
4. Start coordinating!

**Works beautifully on mobile!** 📱✨

