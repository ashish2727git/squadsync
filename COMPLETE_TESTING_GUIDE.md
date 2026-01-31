# 🧪 COMPLETE 2-USER TESTING GUIDE

## 🎯 WHAT WE'RE TESTING:

✅ Registration & Login  
✅ Squad Creation  
✅ Squad Invitation & Joining  
✅ Real-time Member Updates  
✅ War Room Features  
✅ Voice Chat (WebRTC)  
✅ Whiteboard (Real-time Drawing)  
✅ Text Chat (Real-time)  
✅ Summon Notifications  
✅ File Uploads (AWS S3)  

---

## 🚀 STEP-BY-STEP TEST PLAN:

### **Setup: Open 2 Browsers**

**Browser 1 (Chrome):** User 1 - Squad Leader  
**Browser 2 (Chrome Incognito or Firefox):** User 2 - Squad Member

**URL for both:** `http://localhost:3000`

---

## 📝 TEST SCENARIO:

### **STEP 1: Register Both Users**

**Browser 1 (User 1):**
1. Go to `http://localhost:3000/register`
2. Fill in:
   - Username: `alpha`
   - Email: `alpha@test.com`
   - Password: `Test123!@#`
3. Click **Register**
4. ✅ **Expected:** Redirected to dashboard

**Browser 2 (User 2):**
1. Go to `http://localhost:3000/register`
2. Fill in:
   - Username: `bravo`
   - Email: `bravo@test.com`
   - Password: `Test123!@#`
3. Click **Register**
4. ✅ **Expected:** Redirected to dashboard

---

### **STEP 2: Create Squad (User 1)**

**In Browser 1:**
1. Click **"+ Create Squad"** button
2. Fill in:
   - Squad Name: `Alpha Strike Team`
   - Description: `Elite gaming squad for real-time coordination`
3. Click **Create**
4. ✅ **Expected:** Squad created, redirected to squad detail page
5. ✅ **You should see:**
   - Squad name at top
   - Your username as member
   - **"Send Summon"** button
   - **"War Room"** button
   - **"Generate Invite Link"** button

---

### **STEP 3: Generate & Copy Invite Link (User 1)**

**In Browser 1 (Squad Detail Page):**
1. Click **"Generate Invite Link"** button
2. ✅ **Expected:** Popup appears with invite link
3. **COPY THE ENTIRE LINK** (e.g., `http://localhost:3000/invite/abc123...`)
4. Keep this window open

---

### **STEP 4: Join Squad (User 2)**

**In Browser 2:**
1. **Paste the invite link** in address bar
2. Press Enter
3. ✅ **Expected:** Shows "Join Squad?" page with squad name
4. Click **"Join Squad"** button
5. ✅ **Expected:** "Successfully joined!" message
6. Click **"Go to Dashboard"**

---

### **STEP 5: Verify Real-Time Member Update**

**In Browser 1 (Squad Detail Page):**
1. ✅ **Expected:** You should NOW see **2 members** in the squad:
   - `alpha` (you)
   - `bravo` (just joined)
2. If you don't see it, refresh the page

**In Browser 2 (Dashboard):**
1. ✅ **Expected:** You should see "Alpha Strike Team" in your squads list
2. Click on the squad to open squad detail page

---

### **STEP 6: Test Summon Feature**

**In Browser 1 OR Browser 2:**
1. Click **"Send Summon"** button
2. Fill in:
   - Title: `Match Starting Now!`
   - Message: `Everyone get online, match starts in 5 minutes`
3. Click **Send Summon**
4. ✅ **Expected:** "Summon sent!" message

**In OTHER Browser:**
1. ✅ **Expected:** Real-time notification appears on dashboard
2. Shows summon title and message
3. Shows who sent it

---

### **STEP 7: Enter War Room (BOTH USERS)**

**In Browser 1:**
1. Click **"War Room"** button on squad detail page
2. ✅ **Expected:** War Room page loads with:
   - Whiteboard (center)
   - Chat sidebar (right)
   - Voice controls (bottom)

**In Browser 2:**
1. Click **"War Room"** button on squad detail page
2. ✅ **Expected:** Same War Room page loads

---

### **STEP 8: Test Real-Time Chat**

**In Browser 1:**
1. Type in chat: `Hey bravo, can you hear me?`
2. Press Enter

**In Browser 2:**
1. ✅ **Expected:** Message appears INSTANTLY in chat
2. Shows username and message
3. Type back: `Yes alpha, I see your message!`
4. Press Enter

**In Browser 1:**
1. ✅ **Expected:** Bravo's message appears INSTANTLY

---

### **STEP 9: Test Real-Time Whiteboard**

**In Browser 1:**
1. Select a color (e.g., red)
2. Draw something on the whiteboard (e.g., a circle)

**In Browser 2:**
1. ✅ **Expected:** Drawing appears in REAL-TIME as User 1 draws
2. You see the exact strokes appear live
3. Now draw something yourself (different color)

**In Browser 1:**
1. ✅ **Expected:** User 2's drawing appears in REAL-TIME

**Both Browsers:**
1. Try clicking **"Clear"** button
2. ✅ **Expected:** Whiteboard clears for BOTH users

---

### **STEP 10: Test Voice Chat (WebRTC)**

**In Browser 1:**
1. Click **"Start Call"** button
2. ✅ **Expected:** Browser asks for microphone permission
3. Click **Allow**
4. ✅ **Expected:** Button changes to "End Call" and shows "Mute/Unmute"

**In Browser 2:**
1. Click **"Start Call"** button
2. Click **Allow** for microphone
3. ✅ **Expected:** 
   - Button changes to "End Call"
   - You should hear User 1 if they're speaking
   - User 1 should hear you

**Test Audio:**
1. Speak in Browser 1
2. ✅ **Expected:** Browser 2 hears you
3. Speak in Browser 2
4. ✅ **Expected:** Browser 1 hears you

**Test Mute:**
1. Click **"Mute"** in Browser 1
2. Speak
3. ✅ **Expected:** Browser 2 does NOT hear you
4. Click **"Unmute"**
5. Speak
6. ✅ **Expected:** Browser 2 hears you again

---

### **STEP 11: Test File Upload (AWS S3) - OPTIONAL**

**In Browser 1:**
1. Go back to Dashboard
2. Look for avatar upload area (if visible)
3. Click to upload profile picture
4. Select an image (max 5MB)
5. ✅ **Expected:** 
   - Image preview appears
   - Image uploaded to AWS S3
   - Avatar URL saved to database

---

## ✅ SUCCESS CHECKLIST:

After completing all steps, verify:

- [ ] Both users registered successfully
- [ ] Squad created by User 1
- [ ] User 2 joined via invite link
- [ ] Real-time member list updated
- [ ] Summon notification appeared in real-time
- [ ] Both users entered War Room
- [ ] Chat messages appear instantly for both users
- [ ] Whiteboard drawing syncs in real-time
- [ ] Voice call connected (both can hear each other)
- [ ] Mute/unmute works
- [ ] File upload to S3 works (if tested)

---

## 🐛 IF SOMETHING DOESN'T WORK:

**Check Browser Console (F12 → Console tab):**
- Look for red errors
- Share the error message with me

**Check Backend Logs:**
```powershell
docker-compose logs backend --tail 50
```

**Check if services are running:**
```powershell
docker-compose ps
```

---

## 🎮 START TESTING NOW!

**Open 2 browsers and follow the steps above!**

**Tell me which step you're on or if you hit any issues!** 🚀
