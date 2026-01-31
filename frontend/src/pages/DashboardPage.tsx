import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { squadAPI, summonAPI, Squad, Summon } from '../api/services'
import { useWebSocket } from '../hooks/useWebSocket'
import './DashboardPage.css'

export function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [squads, setSquads] = useState<Squad[]>([])
  const [summons, setSummons] = useState<Summon[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // WebSocket for real-time notifications
  useWebSocket((message) => {
    if (message.type === 'summon_created') {
      fetchSummons()
    } else if (message.type === 'user_joined') {
      fetchSquads() // Refresh squad member counts
    }
  })

  const fetchSquads = async () => {
    try {
      const response = await squadAPI.list()
      setSquads(response.data)
    } catch (err: any) {
      console.error('Failed to fetch squads:', err)
      setError(err.response?.data?.detail || 'Failed to load squads')
    }
  }

  const fetchSummons = async () => {
    try {
      // Get active summons for current user's squads
      const squadIds = squads.map(s => s.id)
      if (squadIds.length === 0) return
      
      // For now, just fetch from API - backend should filter by user's squads
      const response = await summonAPI.listActive()
      setSummons(response.data)
    } catch (err) {
      console.error('Failed to fetch summons:', err)
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await fetchSquads()
      setLoading(false)
    }
    loadData()
  }, [])

  // Fetch summons when squads are loaded
  useEffect(() => {
    if (squads.length > 0) {
      fetchSummons()
    }
  }, [squads.length])

  const handleLogout = () => {
    useAuthStore.getState().clearAuth()
    navigate('/login')
  }

  return (
    <div className="dashboard-page">
      {/* MODERN HEADER WITH CLEAR NAVIGATION */}
      <header className="modern-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo" onClick={() => navigate('/dashboard')}>
              <span className="logo-icon">🎮</span>
              <span className="logo-text">SquadSync</span>
            </div>
            <nav className="main-nav">
              <Link to="/dashboard" className="nav-link active">
                <span className="nav-icon">🏠</span>
                <span>Dashboard</span>
              </Link>
              <Link to="/vault" className="nav-link">
                <span className="nav-icon">🔒</span>
                <span>Vault</span>
              </Link>
              <Link to="/profile" className="nav-link">
                <span className="nav-icon">👤</span>
                <span>Profile</span>
              </Link>
            </nav>
          </div>
          <div className="header-right">
            <div className="user-menu">
              <div className="user-avatar" title={user?.username}>
                {user?.username?.charAt(0).toUpperCase()}
              </div>
              <span className="user-name">{user?.username}</span>
              <button onClick={handleLogout} className="btn-logout" title="Logout">
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="dashboard-main">
        <div className="dashboard-container">
          {/* ERROR MESSAGE */}
          {error && (
            <div className="error-banner">
              <span>⚠️</span>
              <span>{error}</span>
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* ACTIVE SUMMONS ALERT */}
          {summons.length > 0 && (
            <div className="alert-card summon-alert">
              <div className="alert-header">
                <h3>🚨 Active Summons ({summons.length})</h3>
                <button onClick={() => setSummons([])}>Dismiss All</button>
              </div>
              <div className="summons-list">
                {summons.map((summon) => (
                  <div key={summon.id} className="summon-card">
                    <div className="summon-info">
                      <div className="summon-title">
                        <strong>{summon.summoner_username}</strong> summoned the squad!
                      </div>
                      {summon.message && <p className="summon-message">{summon.message}</p>}
                      <span className="summon-time">
                        {new Date(summon.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="summon-actions">
                      <button 
                        className="btn-summon-respond"
                        onClick={() => navigate(`/squads/${summon.squad_id}`)}
                      >
                        View Squad
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* WELCOME SECTION */}
          <div className="welcome-section">
            <h1>Welcome back, {user?.username}! 👋</h1>
            <p className="welcome-subtitle">Manage your squads and coordinate with your team</p>
          </div>

          {/* QUICK ACTIONS */}
          <div className="quick-actions">
            <button 
              className="action-card action-create"
              onClick={() => navigate('/onboarding')}
            >
              <span className="action-icon">➕</span>
              <div className="action-content">
                <h3>Create Squad</h3>
                <p>Start a new gaming squad</p>
              </div>
              <span className="action-arrow">→</span>
            </button>
            
            <button 
              className="action-card action-vault"
              onClick={() => navigate('/vault')}
            >
              <span className="action-icon">🔒</span>
              <div className="action-content">
                <h3>Open Vault</h3>
                <p>Access your saved items</p>
              </div>
              <span className="action-arrow">→</span>
            </button>
            
            <button 
              className="action-card action-profile"
              onClick={() => navigate('/profile')}
            >
              <span className="action-icon">👤</span>
              <div className="action-content">
                <h3>Edit Profile</h3>
                <p>Update your settings</p>
              </div>
              <span className="action-arrow">→</span>
            </button>
          </div>

          {/* SQUADS SECTION */}
          <div className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Your Squads</h2>
                <p className="section-subtitle">
                  {squads.length === 0 
                    ? 'You haven\'t joined any squads yet' 
                    : `Managing ${squads.length} squad${squads.length > 1 ? 's' : ''}`
                  }
                </p>
              </div>
              <button 
                className="btn btn-primary"
                onClick={() => navigate('/onboarding')}
              >
                <span>➕</span>
                <span>Create New Squad</span>
              </button>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading your squads...</p>
              </div>
            ) : squads.length === 0 ? (
              <div className="empty-state card">
                <div className="empty-icon">🎯</div>
                <h3>No Squads Yet</h3>
                <p>Create your first squad to start coordinating with your team!</p>
                <div className="empty-actions">
                  <button 
                    className="btn btn-primary btn-lg"
                    onClick={() => navigate('/onboarding')}
                  >
                    <span>➕</span>
                    <span>Create Your First Squad</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="squads-grid">
                {squads.map((squad) => (
                  <div key={squad.id} className="squad-card card">
                    <div className="squad-header">
                      <div className="squad-icon">👥</div>
                      <div className="squad-title">
                        <h3>{squad.name}</h3>
                        <span className={`status-badge ${squad.is_active ? 'active' : 'inactive'}`}>
                          {squad.is_active ? '✓ Active' : '✗ Inactive'}
                        </span>
                      </div>
                    </div>
                    
                    {squad.description && (
                      <p className="squad-description">{squad.description}</p>
                    )}
                    
                    <div className="squad-stats">
                      <div className="stat-item">
                        <span className="stat-icon">👥</span>
                        <span className="stat-value">{squad.member_count}/{squad.max_members}</span>
                        <span className="stat-label">Members</span>
                      </div>
                    </div>

                    <div className="squad-actions">
                      <button 
                        className="btn btn-primary btn-sm"
                        onClick={() => navigate(`/squads/${squad.id}`)}
                      >
                        <span>👁️</span>
                        <span>View Details</span>
                      </button>
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => navigate(`/squads/${squad.id}/warroom`)}
                      >
                        <span>🎨</span>
                        <span>War Room</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default DashboardPage
