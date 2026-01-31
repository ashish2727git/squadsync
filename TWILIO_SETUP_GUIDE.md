# 🎯 TWILIO INTEGRATION - GET YOUR CREDENTIALS

## 📋 STEP-BY-STEP SETUP:

### **1. Create Twilio Account:**
Go to: https://www.twilio.com/try-twilio

**Benefits:**
- Free $15 credit to start
- Professional TURN servers (better voice quality)
- Reliable connection even through firewalls/NAT
- Optional: SMS notifications

---

### **2. Get Account Credentials:**

After signing up:

1. Go to **Console Dashboard**: https://console.twilio.com/
2. Copy these from the dashboard:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
   ```

---

### **3. Create API Key:**

1. Go to: https://console.twilio.com/us1/account/keys-credentials/api-keys
2. Click **"Create API Key"**
3. Give it a name: `SquadSync`
4. **IMPORTANT:** Copy these immediately (shown only once):
   ```
   TWILIO_API_KEY_SID=SKxxxxxxxxxxxxx
   TWILIO_API_KEY_SECRET=xxxxxxxxxxxxx
   ```

---

### **4. (Optional) SMS Setup:**

If you want SMS notifications for summons:

1. Go to **Phone Numbers**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Get a free trial number
3. Copy:
   ```
   TWILIO_PHONE_NUMBER=+1234567890
   ```

---

## 📝 PASTE YOUR CREDENTIALS HERE:

```env
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_API_KEY_SID=
TWILIO_API_KEY_SECRET=
TWILIO_PHONE_NUMBER=    # Optional for SMS
```

---

## ✅ WHAT I'VE PREPARED:

**Backend:**
- ✅ Twilio service integration
- ✅ TURN server endpoint `/api/v1/webrtc/ice-servers`
- ✅ WebRTC configuration with fallback to free STUN

**Frontend:**
- ✅ Auto-fetch TURN servers from backend
- ✅ Fallback to free STUN if Twilio not configured
- ✅ Better voice quality & reliability

**Will work WITHOUT Twilio** (using free STUN servers), but **voice quality will be MUCH better with Twilio TURN servers**!

---

## 🚀 READY WHEN YOU ARE:

**Option A:** Create Twilio account now (15 mins) → Better voice quality
**Option B:** Skip for now → Works with free STUN (good enough for testing)
**Option C:** Give me credentials if you already have Twilio

**What do you want to do?**
