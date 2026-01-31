# 🎮 HOW TO USE ALL FEATURES - COMPLETE USER GUIDE

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Squad Management](#squad-management)
3. [Inviting People to Your Squad](#inviting-people)
4. [Vault Features](#vault-features)
5. [Profile Management](#profile-management)
6. [War Room](#war-room)
7. [Mobile App](#mobile-app)
8. [All Available Features List](#all-features)

---

## 🚀 GETTING STARTED

### **Step 1: Create an Account**

1. Open **http://localhost:3000**
2. Click **"Register"**
3. Fill in:
   - Username (min 3 characters)
   - Email
   - Password (min 8 chars, needs: uppercase, lowercase, number, special char, max 72 chars)
4. Click **"Register"**
5. You'll be auto-logged in!

### **Step 2: Create Your First Squad**

1. After registration, you'll see **"Create Your First Squad"**
2. Fill in:
   - **Squad Name** (required) - e.g., "Alpha Team"
   - **Game** (optional) - e.g., "BGMI", "Valorant", "Fortnite"
   - **Description** (optional) - Describe your squad
   - **Max Members** (default: 10) - Set 2-50
3. Click **"Create Squad"**
4. ✅ Done! You're now the squad leader

---

## 👥 SQUAD MANAGEMENT

### **View All Your Squads**

**Location:** Dashboard (http://localhost:3000/dashboard)

**What You See:**
- ✅ Squad name and icon
- ✅ Member count (e.g., 1/10)
- ✅ Squad status (Active/Inactive)
- ✅ Description

**Actions:**
- Click on any squad card to **view details**

### **Squad Detail Page**

**Location:** Click any squad from dashboard

**What You See:**
- 📊 **Statistics**: Members, Events, Active Goals
- 👥 **Member List**: All current members with leader badge
- 📅 **Schedule**: Upcoming events and daily goals
- 🎨 **War Room** button
- 📢 **Send Summon** button
- 🔗 **Invite Link** button

**Tabs Available:**
1. **Overview** - Squad info and upcoming events
2. **Members** - Full member list with leader indicators
3. **Schedule** - All scheduled events with timeline view

---

## 🔗 INVITING PEOPLE TO YOUR SQUAD

### **Method 1: Share Invite Link (EASIEST)**

1. **Go to your squad detail page:**
   - Dashboard → Click your squad

2. **Click the "Invite Link" button** (🔗 icon)
   - You'll see a popup with the invite link

3. **Copy the link:**
   - Click **"Copy Link"** button
   - OR click the link text to select it and press Ctrl+C

4. **Share the link:**
   - Send via WhatsApp, Discord, Telegram, etc.
   - Post in group chat
   - Email to friends
   - Share on social media

5. **What your friends see:**
   - They open the link
   - See squad name, description, current members
   - Click **"Join Squad"** button
   - ✅ They're in!

**Example Invite Link:**
```
http://localhost:3000/join/abc123-def456-ghi789
```

**For Mobile Access:**
```
http://YOUR_IP:3000/join/abc123-def456-ghi789
Example: http://192.168.1.5:3000/join/abc123-def456-ghi789
```

### **Method 2: Manual Join (Advanced)**

1. Tell your friend the squad ID (visible in URL)
2. They navigate to: `/join/{squadId}`
3. Click "Join Squad"

### **Invite Link Features:**
- ✅ Works for anyone on your WiFi (local network)
- ✅ Shows squad info before joining
- ✅ Displays current member count
- ✅ Shows member list preview
- ✅ Prevents joining if squad is full
- ✅ Prevents duplicate memberships

---

## 📦 VAULT FEATURES

### **What is the Vault?**
Secure storage for your gaming data:
- Game strategies
- Build configurations
- Team compositions
- Tournament notes
- Training schedules

### **How to Access Vault**

**Location:** http://localhost:3000/vault

1. From Dashboard, click **"Vault"** in the top navigation
2. You'll see your personal vault page

### **Create Vault Item**

1. Click **"Add New Item"** or **"+"** button
2. Fill in:
   - **Name** - e.g., "Valorant Setups"
   - **Type** - strategy, build, notes, etc.
   - **Description** - Details about the item
   - **Privacy** - Private (only you) or Shared (squad)
   - **Data** - JSON or structured data
3. Click **"Save"**

### **View Vault Items**

- **All Items** - See everything in your vault
- **Private Items** - Only you can see
- **Shared Items** - Your squad can see
- **Filter by Type** - Strategy, Build, Notes, etc.

### **Share Vault to Squad**

1. Open a vault item
2. Click **"Share"** button
3. Select target squad/chat
4. Add optional message
5. Click **"Share"**
6. ✅ Squad members get notification with shared data

---

## 👤 PROFILE MANAGEMENT

### **Access Your Profile**

**Location:** http://localhost:3000/profile

1. Click **"Profile"** in top navigation
2. Or click your avatar → Profile

### **Edit Profile**

**Available Fields:**
- Username
- Email
- Bio/Description
- Avatar (coming soon)
- Notification preferences
- Privacy settings

### **Change Password**

1. Go to Profile page
2. Click **"Change Password"**
3. Enter current password
4. Enter new password (must meet requirements)
5. Confirm new password
6. Click **"Update"**

### **View Your Stats**

- **Squads Joined**: Total squads you're in
- **Events Attended**: Participation history
- **Leadership**: Squads you lead
- **Vault Items**: Total items in vault

---

## 🎨 WAR ROOM

### **What is War Room?**
Real-time collaboration space with:
- 🖊️ **Whiteboard** - Draw strategies together
- 💬 **Live Chat** - Text communication
- 🎤 **Voice Chat** (WebRTC) - Voice communication
- 📹 **Screen Share** - Share your screen

### **How to Access War Room**

1. Go to Squad Detail Page
2. Click **"Enter War Room"** button (🎨 icon)
3. You'll join the live session

### **War Room Features**

#### **Whiteboard:**
- Draw strategies
- Mark positions
- Plan tactics
- Share game maps
- Collaborate in real-time

#### **Chat:**
- Send text messages
- Share links
- Coordinate timing
- Quick communication

#### **Voice/Video:**
- Click microphone icon to speak
- Click camera icon for video
- Mute/unmute instantly
- See who's talking

#### **Screen Share:**
- Click "Share Screen" button
- Select window/screen to share
- Others see your screen in real-time
- Perfect for reviewing gameplay

---

## 📱 MOBILE APP

### **Install on Android (PWA)**

#### **Quick Install (2 minutes):**

1. **On your computer:**
   ```powershell
   # Find your IP
   ipconfig
   # Look for IPv4 Address, e.g., 192.168.1.5
   ```

2. **On your Android phone:**
   - Open **Chrome** browser
   - Go to: `http://192.168.1.5:3000`
   - Menu (⋮) → **"Add to Home screen"**
   - Name it: `SquadSync`
   - Tap **"Add"**

3. **Use it:**
   - Tap the icon from home screen
   - Works like native app!
   - Full-screen experience
   - No browser UI

### **Install on iPhone (PWA)**

1. **Open Safari** (must use Safari, not Chrome)
2. Go to: `http://YOUR_IP:3000`
3. Tap **Share** button
4. Tap **"Add to Home Screen"**
5. Name it and tap **"Add"**

### **Mobile Features:**
- ✅ All features work on mobile
- ✅ Responsive design
- ✅ Touch-optimized UI
- ✅ Works offline (once cached)
- ✅ Same invite links work

---

## 📋 ALL AVAILABLE FEATURES

### **✅ Authentication**
- [x] User Registration
- [x] User Login
- [x] Auto-login after registration
- [x] Password strength validation
- [x] JWT token authentication
- [x] Token refresh
- [x] Secure logout

### **✅ Squad Management**
- [x] Create Squad (one-step process)
- [x] View All Squads
- [x] Squad Detail Page
- [x] Join Squad via Invite Link
- [x] Leave Squad
- [x] View Squad Members
- [x] Leader Indicators
- [x] Member Count Display
- [x] Squad Status (Active/Inactive)

### **✅ Invite System**
- [x] Generate Invite Link
- [x] Copy Link to Clipboard
- [x] Share via any platform
- [x] Join Page with Squad Preview
- [x] Member List Preview
- [x] Full Squad Prevention
- [x] Duplicate Join Prevention

### **✅ Vault Features**
- [x] Personal Vault
- [x] Create Vault Items
- [x] View All Items
- [x] Edit Items
- [x] Delete Items
- [x] Private/Shared Privacy
- [x] Filter by Type
- [x] Share to Squad
- [x] JSON Data Storage

### **✅ Profile**
- [x] View Profile
- [x] Edit Profile
- [x] Change Password
- [x] View Stats
- [x] Avatar Display
- [x] Bio/Description

### **✅ War Room**
- [x] Whiteboard Collaboration
- [x] Drawing Tools
- [x] Real-time Sync
- [x] Live Chat
- [x] Voice Chat (WebRTC)
- [x] Screen Sharing
- [x] Multi-user Support

### **✅ Schedule & Events**
- [x] Create Events
- [x] View Schedule
- [x] Event Timeline
- [x] Daily Goals
- [x] Event Types (Meeting, Practice, Tournament)
- [x] Event Notifications

### **✅ Dashboard**
- [x] Squad Grid View
- [x] Active Summons Alert
- [x] Member Count Display
- [x] Quick Actions
- [x] Loading States
- [x] Empty States

### **✅ Mobile**
- [x] PWA Support
- [x] Responsive Design
- [x] Touch Optimized
- [x] Offline Support
- [x] Home Screen Install
- [x] Full-Screen Mode

### **✅ UI/UX**
- [x] Modern Gradient Design
- [x] Smooth Animations
- [x] Loading Spinners
- [x] Error Messages
- [x] Success Notifications
- [x] Error Boundaries
- [x] Toast Notifications

---

## 🎯 QUICK REFERENCE

### **Common URLs**

| Feature | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000/dashboard |
| **Create Squad** | http://localhost:3000/onboarding |
| **Vault** | http://localhost:3000/vault |
| **Profile** | http://localhost:3000/profile |
| **Squad Detail** | http://localhost:3000/squads/{id} |
| **Join Squad** | http://localhost:3000/join/{id} |
| **War Room** | http://localhost:3000/squads/{id}/warroom |

### **Quick Actions**

| Action | Steps |
|--------|-------|
| **Create Squad** | Dashboard → Create Squad button → Fill form → Create |
| **Invite Someone** | Squad Detail → Invite Link → Copy → Share |
| **Join Squad** | Click invite link → Join Squad button |
| **Enter War Room** | Squad Detail → Enter War Room button |
| **Add Vault Item** | Vault → Add New Item → Fill form → Save |
| **Edit Profile** | Profile → Edit button → Update → Save |

---

## 🐛 TROUBLESHOOTING

### **"Can't access invite link from my phone"**

**Solution:**
1. Make sure phone and computer are on SAME WiFi
2. Run `enable-firewall-access.bat` as Administrator
3. Use your computer's IP address (not localhost)
4. Verify Docker is running: `docker-compose ps`

### **"Join Squad button doesn't work"**

**Possible Reasons:**
- Squad is full (check member count)
- Already a member
- Need to be logged in

**Solution:**
1. Refresh the page
2. Check if you're logged in
3. Try copying the link and opening in new tab

### **"Invite link not copying"**

**Solution:**
- Click directly on the "Copy Link" button
- OR click the text field and press Ctrl+C / Cmd+C
- Browser will show "Link copied!" notification

---

## 🎉 SUCCESS STORIES

### **Example Workflow:**

1. **Create your squad:** "Elite BGMI Squad" ✅
2. **Get invite link:** `http://localhost:3000/join/abc123...` ✅
3. **Share in WhatsApp group:** Send to 9 friends ✅
4. **They join:** Squad grows to 10/10 ✅
5. **Enter War Room:** Plan strategy together ✅
6. **Add vault items:** Save winning strategies ✅
7. **Schedule events:** Set practice times ✅
8. **Mobile app:** Everyone installs on phones ✅

---

## 📞 NEED MORE HELP?

### **Check These Guides:**

- **`TESTED_WITH_REAL_DATA.md`** - See actual testing results
- **`COMPLETE_ANDROID_GUIDE.md`** - Mobile installation details
- **`INSTALL_ON_ANDROID_NOW.md`** - Quick mobile setup

### **Common Questions:**

**Q: How many people can join my squad?**
A: You set the max members (2-50) when creating the squad.

**Q: Can I be in multiple squads?**
A: Yes! Join as many squads as you want.

**Q: Do invite links expire?**
A: No, they work until the squad is full or deleted.

**Q: Can I remove someone from my squad?**
A: Squad leaders can manage members (feature being added).

**Q: Does War Room work on mobile?**
A: Yes! All features including whiteboard work on mobile.

---

## ✅ CHECKLIST FOR NEW USERS

- [ ] Create account
- [ ] Create first squad
- [ ] Generate invite link
- [ ] Share with friend
- [ ] Friend joins successfully
- [ ] Visit squad detail page
- [ ] Try War Room
- [ ] Add vault item
- [ ] Update profile
- [ ] Install mobile app

**Once you complete this checklist, you're a SquadSync pro!** 🎉

---

**All features are working and tested. Start using them NOW!**

**Quick Start:** http://localhost:3000
