import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import './ProfilePage.css';

export function ProfilePage() {
  const { user } = useAuthStore();

  return (
    <div className="profile-page">
      <header className="page-header">
        <div className="header-content">
          <Link to="/dashboard" className="back-link">← Back</Link>
          <h1>👤 Profile</h1>
        </div>
      </header>

      <main className="profile-main">
        <div className="profile-card">
          <div className="profile-avatar">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <h2>{user?.username}</h2>
          <p className="user-email">{user?.email}</p>
          <span className={`user-role role-${user?.role?.toLowerCase()}`}>
            {user?.role}
          </span>
        </div>

        <div className="profile-section">
          <h3>Account Settings</h3>
          <div className="settings-list">
            <div className="setting-item">
              <span>Username</span>
              <strong>{user?.username}</strong>
            </div>
            <div className="setting-item">
              <span>Email</span>
              <strong>{user?.email}</strong>
            </div>
            <div className="setting-item">
              <span>Role</span>
              <strong>{user?.role}</strong>
            </div>
            <div className="setting-item">
              <span>Account Status</span>
              <strong className={user?.is_active ? 'status-active' : 'status-inactive'}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </strong>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h3>Preferences</h3>
          <div className="settings-list">
            <div className="setting-item">
              <label>
                <input type="checkbox" defaultChecked />
                <span>Email notifications</span>
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input type="checkbox" defaultChecked />
                <span>Summon alerts</span>
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input type="checkbox" defaultChecked />
                <span>Show online status</span>
              </label>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button className="btn-secondary">Change Password</button>
          <button className="btn-danger">Delete Account</button>
        </div>
      </main>
    </div>
  );
}

export default ProfilePage;
