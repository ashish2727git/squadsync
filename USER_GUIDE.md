# SquadSync User Guide

Welcome to SquadSync! This guide will help you get started with the platform and make the most of its features.

## 📚 Table of Contents
1. [Getting Started](#getting-started)
2. [Creating Your First Squad](#creating-your-first-squad)
3. [Using the Dashboard](#using-the-dashboard)
4. [Summon System](#summon-system)
5. [Player Vault](#player-vault)
6. [Squad Scheduling](#squad-scheduling)
7. [War Room](#war-room)
8. [Profile Settings](#profile-settings)

---

## 🚀 Getting Started

### Registration
1. Navigate to http://localhost:3000
2. Click **Register** (or go to /register)
3. Fill in your details:
   - Username (2-50 characters)
   - Email address
   - Password (8+ chars, must include uppercase, lowercase, number, special character)
4. Click **Register**

### First Login
1. After registration, you'll be redirected to the login page
2. Enter your username/email and password
3. Click **Login**
4. You'll be taken to the onboarding flow

---

## 🎯 Creating Your First Squad

### Onboarding Wizard
The first time you log in, you'll see a 3-step wizard:

#### Step 1: Create an Organization
- **Organization** is the top-level group (e.g., your gaming clan or esports team)
- Enter a name (e.g., "Elite Gamers")
- Add an optional description
- Click **Next**

#### Step 2: Create a Team
- **Team** is a game-specific group within your organization
- Enter team name (e.g., "Valorant Pro Team")
- Enter the game title (e.g., "Valorant")
- Click **Next**

#### Step 3: Create Your Squad
- **Squad** is a small tactical group (typically 5-10 players)
- Enter squad name (e.g., "Alpha Squad")
- Add description (optional)
- Set max members (default: 10)
- Click **Finish**

You can skip this wizard and complete it later by clicking "Skip for now"

---

## 📊 Using the Dashboard

The Dashboard is your main hub. Here you'll see:

### Squad Grid
- All squads you're a member of
- Click any squad card to view details
- Shows member count: 👥 5/10

### Active Summons
- Urgent notifications from squad leaders
- Displayed prominently at the top when active
- Color-coded by urgency (Critical = Red, High = Orange, Medium = Yellow)

### Quick Actions
- **+ Create Squad** - Make a new squad
- **Navigation Bar** - Access Dashboard, Vault, Profile

### Empty State
- If you have no squads, you'll see:
  - "No squads yet" message
  - **Get Started** button to open onboarding

---

## 🚨 Summon System

### What is a Summon?
Summons are urgent notifications to rally your squad for immediate gameplay.

### Receiving a Summon
When a squad leader sends a summon:
1. You'll see a **red alert banner** at the top of your dashboard
2. The banner shows:
   - Who summoned (username)
   - Which squad
   - Urgency level

### Responding to a Summon
1. Click on the summon
2. Choose your response:
   - **ACCEPT** - You're ready to join
   - **DECLINE** - You can't join
3. Optionally add:
   - Message (e.g., "On my way!")
   - ETA in minutes (e.g., "5 minutes")

### Sending a Summon (Squad Leaders Only)
1. Go to your squad detail page
2. Click **Send Summon**
3. Select urgency:
   - LOW - Casual invitation
   - MEDIUM - Normal priority
   - HIGH - Important session
   - CRITICAL - Emergency/tournament
4. Add optional message
5. Click **Send**

---

## 🔒 Player Vault

Your personal storage for gaming content.

### Accessing the Vault
- Click **Vault** in the navigation bar
- Or go to /vault

### Creating Vault Items
1. Click **+ New Item**
2. Fill in the form:
   - **Name** - Item title
   - **Description** - Details (optional)
   - **Type** - Choose from:
     - 🎮 Loadout (weapon configurations)
     - 🎬 Clip (gameplay recordings)
     - 🏆 Achievement (accomplishments)
     - 📝 Note (general notes)
   - **Privacy** - Check to keep private
3. Click **Create**

### Managing Items
- **View** - All items displayed in a grid
- **Delete** - Click Delete button (asks for confirmation)
- **Share** - Click Share to send to squad (coming soon)

### Item Types
- **Loadout** (Blue) - Weapon setups, character builds
- **Clip** (Orange) - Video highlights, funny moments
- **Achievement** (Green) - Milestones, records
- **Note** (Purple) - Strategy notes, tips

---

## 📅 Squad Scheduling

View and manage squad events and goals.

### Viewing Schedule
1. Go to Squad Detail page
2. Click **Schedule** tab
3. See:
   - **Upcoming Events** - Practices, tournaments, casual games
   - **Daily Goals** - Today's objectives

### Creating Events (Squad Leaders Only)
1. Click **+ New Event**
2. Fill in:
   - **Title** - Event name
   - **Description** - Details (optional)
   - **Event Type** - Practice, Tournament, or Casual
   - **Scheduled At** - Date and time
   - **Duration** - In minutes
3. Click **Create**

### Setting Daily Goals (Squad Leaders Only)
1. Click **+ New Goal**
2. Enter:
   - **Description** - What to accomplish
   - **Target Date** - When to complete
   - **Assign To** - Specific member (optional)
3. Click **Create**

### Managing Events/Goals
- **Edit** - Click edit icon to modify
- **Complete** - Check off completed goals
- **Delete** - Remove events/goals

---

## 🎨 War Room

Collaborative space with whiteboard and voice chat.

### Accessing War Room
1. Go to Squad Detail page
2. Click **Enter War Room**
3. Or navigate to `/squads/{squadId}/warroom`

### Whiteboard Features
- **Drawing Tool** - Click and drag to draw
- **Color Picker** - Choose drawing color
- **Clear Canvas** - Reset the board
- **Real-time Sync** - Everyone sees drawings instantly

### Voice Chat (WebRTC)
- **Start Call** - Click microphone icon
- **Mute/Unmute** - Toggle microphone
- **End Call** - Click hangup icon
- **Peer-to-Peer** - Direct connections for low latency

### Best Practices
- Use whiteboard for:
  - Strategy planning
  - Map callouts
  - Formation diagrams
  - Quick sketches
- Use voice chat for:
  - Real-time coordination
  - Quick discussions
  - Practice sessions

---

## 👤 Profile Settings

Manage your account and preferences.

### Accessing Profile
- Click **Profile** in navigation
- Or go to /profile

### Profile Information
- **Avatar** - Shows your username initial
- **Username** - Display name
- **Email** - Account email
- **Role** - Your permission level
  - 🔵 PLAYER - Standard user
  - 🟢 SQUAD_LEADER - Can manage squads
  - 🟠 TEAM_MANAGER - Can manage teams
  - 🔴 ORG_ADMIN - Full admin access

### Account Settings
- View account status (Active/Inactive)
- See role and permissions
- Account creation date

### Preferences
- ✅ **Email Notifications** - Receive emails for events
- ✅ **Summon Alerts** - Get notified of summons
- ✅ **Show Online Status** - Display to others

### Actions
- **Change Password** - Update your password
- **Delete Account** - Permanently remove account (requires confirmation)

---

## 🎮 Tips & Best Practices

### For Squad Leaders
1. **Send summons strategically** - Don't overuse high/critical urgency
2. **Schedule regular practice** - Keep squad engaged
3. **Set daily goals** - Give squad focus and direction
4. **Use War Room for strategy** - Visualize plans on whiteboard
5. **Respond to members** - Keep squad morale high

### For All Users
1. **Keep vault organized** - Use clear names and descriptions
2. **Respond to summons promptly** - Respect your squad's time
3. **Check dashboard regularly** - Stay updated on squad activity
4. **Complete onboarding** - Set up your organization/team/squad
5. **Update preferences** - Customize notifications to your needs

### Squad Management
1. **Communicate** - Use messages in summons and events
2. **Be consistent** - Regular play times build strong squads
3. **Collaborate in War Room** - Better coordination = better results
4. **Track achievements** - Document milestones in vault
5. **Set realistic goals** - Achievable daily objectives

---

## 🆘 Troubleshooting

### Can't Log In
- ✅ Check username/email is correct
- ✅ Verify password (case-sensitive)
- ✅ Ensure account is active
- ✅ Clear browser cache and try again

### Not Receiving Summons
- ✅ Check you're a member of the squad
- ✅ Verify WebSocket connection (look for status indicator)
- ✅ Refresh the page
- ✅ Check browser console for errors

### Can't Create Squad
- ✅ Complete onboarding first (need organization and team)
- ✅ Ensure you have necessary permissions
- ✅ Fill all required fields
- ✅ Check squad name is unique within team

### War Room Not Working
- ✅ Ensure you're a squad member
- ✅ Check browser permissions for microphone (voice chat)
- ✅ Try refreshing the page
- ✅ Verify WebSocket connection

### Vault Items Not Loading
- ✅ Check network connection
- ✅ Verify you're logged in
- ✅ Refresh the page
- ✅ Check browser console for errors

---

## 📞 Need Help?

### Resources
- **API Documentation**: `/docs` endpoint
- **Architecture Guide**: ARCHITECTURE.md
- **Deployment Guide**: DEPLOYMENT_GUIDE.md
- **Feature List**: FEATURES_COMPLETE.md

### Common Questions

**Q: How many squads can I join?**  
A: Unlimited! You can be a member of as many squads as you want.

**Q: Can I be a leader of multiple squads?**  
A: Yes! You can create and lead multiple squads.

**Q: Are vault items visible to others?**  
A: Only if you uncheck "Private" when creating them. By default, items are private.

**Q: How long do summons stay active?**  
A: Summons remain active until the squad leader cancels them or marks them complete.

**Q: Can I delete my account?**  
A: Yes, from your profile page. Note: This is permanent and cannot be undone.

**Q: What happens if I leave a squad?**  
A: You lose access to that squad's content, events, and War Room. You can rejoin if invited.

---

## 🚀 Getting the Most Out of SquadSync

### Daily Routine
1. **Check Dashboard** - Review active summons and squad updates
2. **Review Schedule** - See today's events and goals
3. **Update Vault** - Add new loadouts or achievements
4. **Respond to Summons** - Keep squad informed of availability

### Weekly Routine
1. **Plan Events** - Schedule practices for the week
2. **Set Goals** - Define objectives for the squad
3. **Review Performance** - Check completed goals and achievements
4. **Clean Vault** - Remove outdated items

### Best Times to Use Features
- **Summons** - When you need immediate squad response
- **War Room** - Pre-game strategy planning, post-game review
- **Vault** - After matches (store loadouts/clips), before matches (review strategies)
- **Scheduling** - Beginning of week (plan), end of week (review)

---

## 🎉 Welcome to SquadSync!

You're now ready to coordinate your gaming squads like never before. Start by:
1. Completing the onboarding wizard
2. Inviting your gaming friends
3. Creating your first event
4. Sending your first summon
5. Building your vault

**Happy Gaming! 🎮🚀**
