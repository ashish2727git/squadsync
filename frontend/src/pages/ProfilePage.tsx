import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { UserStatusSelector } from '../components/UserStatusBadge';
import './ProfilePage.css';

type PresenceStatus = 'ONLINE' | 'IDLE' | 'DND' | 'OFFLINE';

interface UserProfile {
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  avatar_url?: string;
  bio?: string;
  presence?: PresenceStatus;
  status_text?: string;
  current_activity?: string;
}

export function ProfilePage() {
  const { user, setAuth, accessToken, refreshToken } = useAuthStore();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    username: '',
    email: '',
    bio: '',
  });
  const [currentStatus, setCurrentStatus] = useState<PresenceStatus>('ONLINE');
  const [statusText, setStatusText] = useState('');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (user) {
      setProfile({
        username: user.username || '',
        email: user.email || '',
        role: user.role || 'PLAYER',
        is_active: user.is_active ?? true,
        avatar_url: user.avatar_url,
        bio: user.bio || '',
        presence: 'ONLINE',
        status_text: '',
      });
      setEditForm({
        username: user.username || '',
        email: user.email || '',
        bio: user.bio || '',
      });
    }
  }, [user]);

  useEffect(() => {
    // Update presence on mount
    updatePresence('ONLINE');
    
    // Set offline on unmount
    return () => {
      updatePresence('OFFLINE');
    };
  }, []);

  const updatePresence = async (presence: PresenceStatus, text?: string) => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch('http://localhost:8000/api/v1/messages/status', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          presence,
          status_text: text || statusText,
        }),
      });
      setCurrentStatus(presence);
      if (text !== undefined) setStatusText(text);
    } catch (err) {
      console.error('Failed to update presence:', err);
    }
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadAvatar = async () => {
    if (!avatarFile) return null;

    const formData = new FormData();
    formData.append('file', avatarFile);

    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/api/v1/upload/avatar', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      return data.url;
    }
    return null;
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      let avatarUrl = profile?.avatar_url;
      
      if (avatarFile) {
        avatarUrl = await uploadAvatar();
      }

      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/api/v1/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: editForm.username,
          bio: editForm.bio,
          avatar_url: avatarUrl,
        }),
      });

      if (res.ok) {
        const updatedUser = await res.json();
        setAuth(accessToken!, refreshToken!, updatedUser);
        setProfile(prev => prev ? { ...prev, ...updatedUser } : prev);
        setIsEditing(false);
        setAvatarFile(null);
        setAvatarPreview(null);
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save profile. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleStatusChange = (status: PresenceStatus, text?: string) => {
    updatePresence(status, text);
  };

  const getStatusColor = (status: PresenceStatus) => {
    switch (status) {
      case 'ONLINE': return '#43b581';
      case 'IDLE': return '#faa61a';
      case 'DND': return '#f04747';
      default: return '#747f8d';
    }
  };

  if (!profile) {
    return (
      <div className="profile-page loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <header className="page-header">
        <div className="header-content">
          <Link to="/dashboard" className="back-link">← Back</Link>
          <h1>My Profile</h1>
        </div>
      </header>

      <main className="profile-main">
        {message && (
          <div className={`message-banner ${message.type}`}>
            {message.text}
            <button onClick={() => setMessage(null)}>×</button>
          </div>
        )}

        {/* Profile Banner & Avatar */}
        <div className="profile-banner">
          <div className="banner-gradient"></div>
          <div className="profile-avatar-section">
            <div 
              className="profile-avatar-large"
              onClick={isEditing ? handleAvatarClick : undefined}
              style={{ cursor: isEditing ? 'pointer' : 'default' }}
            >
              {avatarPreview || profile.avatar_url ? (
                <img src={avatarPreview || profile.avatar_url} alt={profile.username} />
              ) : (
                <span className="avatar-initial">{profile.username.charAt(0).toUpperCase()}</span>
              )}
              <span 
                className="status-dot-large"
                style={{ backgroundColor: getStatusColor(currentStatus) }}
              />
              {isEditing && (
                <div className="avatar-edit-overlay">
                  <span>📷</span>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        {/* Profile Card */}
        <div className="profile-card">
          <div className="card-header">
            <div className="user-info-header">
              {isEditing ? (
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                  className="edit-username"
                  placeholder="Username"
                />
              ) : (
                <h2>{profile.username}</h2>
              )}
              <span className={`role-badge role-${profile.role.toLowerCase()}`}>
                {profile.role}
              </span>
            </div>
            
            {!isEditing ? (
              <button className="edit-profile-btn" onClick={() => setIsEditing(true)}>
                Edit Profile
              </button>
            ) : (
              <div className="edit-actions">
                <button className="cancel-btn" onClick={() => {
                  setIsEditing(false);
                  setAvatarFile(null);
                  setAvatarPreview(null);
                  setEditForm({
                    username: profile.username,
                    email: profile.email,
                    bio: profile.bio || '',
                  });
                }}>
                  Cancel
                </button>
                <button 
                  className="save-btn" 
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            )}
          </div>

          {/* Status Section */}
          <div className="profile-section status-section">
            <h3>Status</h3>
            <UserStatusSelector 
              currentStatus={currentStatus} 
              onStatusChange={handleStatusChange}
            />
          </div>

          {/* About Section */}
          <div className="profile-section">
            <h3>About Me</h3>
            {isEditing ? (
              <textarea
                value={editForm.bio}
                onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                placeholder="Tell us about yourself..."
                maxLength={200}
                rows={3}
              />
            ) : (
              <p className="bio-text">
                {profile.bio || 'No bio yet. Click Edit Profile to add one!'}
              </p>
            )}
          </div>

          {/* Account Info */}
          <div className="profile-section">
            <h3>Account</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Email</label>
                <span>{profile.email}</span>
              </div>
              <div className="info-item">
                <label>Account Status</label>
                <span className={profile.is_active ? 'active' : 'inactive'}>
                  {profile.is_active ? '✓ Active' : '✗ Inactive'}
                </span>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="profile-section">
            <h3>Preferences</h3>
            <div className="preference-list">
              <label className="preference-item">
                <input type="checkbox" defaultChecked />
                <span className="checkbox-custom"></span>
                <span>Enable notifications</span>
              </label>
              <label className="preference-item">
                <input type="checkbox" defaultChecked />
                <span className="checkbox-custom"></span>
                <span>Summon sound alerts</span>
              </label>
              <label className="preference-item">
                <input type="checkbox" defaultChecked />
                <span className="checkbox-custom"></span>
                <span>Show online status to others</span>
              </label>
              <label className="preference-item">
                <input type="checkbox" />
                <span className="checkbox-custom"></span>
                <span>Enable desktop notifications</span>
              </label>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="profile-section danger-zone">
            <h3>Danger Zone</h3>
            <div className="danger-actions">
              <button className="btn-secondary">Change Password</button>
              <button className="btn-danger">Delete Account</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default ProfilePage;
