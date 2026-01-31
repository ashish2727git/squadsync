import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { squadAPI, scheduleAPI, summonAPI, SquadDetail, ScheduleEvent, DailyGoal } from '../api/services'
import './SquadDetailPage.css'

export function SquadDetailPage() {
  const { squadId } = useParams<{ squadId: string }>()
  const navigate = useNavigate()
  const [squad, setSquad] = useState<SquadDetail | null>(null)
  const [events, setEvents] = useState<ScheduleEvent[]>([])
  const [goals, setGoals] = useState<DailyGoal[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [showInvite, setShowInvite] = useState(false)
  const [showSummon, setShowSummon] = useState(false)
  const [summonForm, setSummonForm] = useState({ title: '', description: '' })
  const [summonLoading, setSummonLoading] = useState(false)

  useEffect(() => {
    if (squadId) {
      loadSquadData()
    }
  }, [squadId])

  const loadSquadData = async () => {
    setLoading(true)
    try {
      const [squadRes, eventsRes, goalsRes] = await Promise.all([
        squadAPI.get(squadId!),
        scheduleAPI.getEvents(squadId!).catch(() => ({ data: [] })),
        scheduleAPI.getGoals(squadId!).catch(() => ({ data: [] })),
      ])
      setSquad(squadRes.data)
      setEvents(eventsRes.data)
      setGoals(goalsRes.data)
    } catch (error) {
      console.error('Failed to load squad:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSendSummon = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!summonForm.title.trim()) {
      alert('Please enter a title for the summon')
      return
    }

    setSummonLoading(true)
    try {
      await summonAPI.create({
        squad_id: squadId!,
        title: summonForm.title,
        description: summonForm.description,
        urgency: 'NORMAL',
      })
      alert('✅ Summon sent to all squad members!')
      setShowSummon(false)
      setSummonForm({ title: '', description: '' })
    } catch (error: any) {
      console.error('Failed to send summon:', error)
      alert(error.response?.data?.detail || 'Failed to send summon')
    } finally {
      setSummonLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="squad-detail-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading squad...</p>
        </div>
      </div>
    )
  }

  if (!squad) {
    return (
      <div className="squad-detail-page">
        <div className="empty-state">
          <h3>Squad not found</h3>
          <Link to="/dashboard" className="btn btn-primary">Return to Dashboard</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="squad-detail-page">
      <header className="modern-header">
        <div className="header-content">
          <Link to="/dashboard" className="back-link">
            <span>←</span>
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </header>

      <div className="squad-hero">
        <div className="hero-content">
          <div className="squad-badge">👥</div>
          <h1>{squad.name}</h1>
          {squad.description && <p className="hero-description">{squad.description}</p>}
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-value">{squad.member_count}</span>
              <span className="stat-label">Members</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{events.length}</span>
              <span className="stat-label">Events</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{goals.filter(g => !g.is_completed).length}</span>
              <span className="stat-label">Active Goals</span>
            </div>
          </div>
          
          {/* PRIMARY ACTION BUTTONS */}
          <div className="hero-actions">
            <button 
              className="btn btn-primary btn-lg" 
              onClick={() => navigate(`/squads/${squadId}/warroom`)}
            >
              <span>🎨</span>
              <span>Enter War Room</span>
            </button>
            <button 
              className="btn btn-success btn-lg" 
              onClick={() => setShowSummon(!showSummon)}
            >
              <span>📢</span>
              <span>Send Summon</span>
            </button>
            <button 
              className="btn btn-secondary btn-lg" 
              onClick={() => setShowInvite(!showInvite)}
            >
              <span>🔗</span>
              <span>Invite People</span>
            </button>
            <button 
              className="btn btn-danger btn-lg" 
              onClick={async () => {
                if (confirm('Are you sure you want to leave this squad?')) {
                  try {
                    await squadAPI.leave(squadId!)
                    alert('✅ Left squad successfully')
                    navigate('/dashboard')
                  } catch (error: any) {
                    alert(error.response?.data?.detail || 'Failed to leave squad')
                  }
                }
              }}
            >
              <span>🚪</span>
              <span>Leave Squad</span>
            </button>
          </div>

          {/* INVITE POPUP */}
          {showInvite && (
            <div className="feature-box invite-box">
              <div className="box-header">
                <h3>🔗 Invite People to Squad</h3>
                <button onClick={() => setShowInvite(false)}>✕</button>
              </div>
              <p>Share this link with your friends:</p>
              <div className="invite-link-container">
                <input 
                  type="text" 
                  value={`${window.location.origin}/join/${squadId}`}
                  readOnly
                  onClick={(e) => (e.target as HTMLInputElement).select()}
                />
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/join/${squadId}`)
                    alert('✅ Link copied to clipboard!')
                  }}
                >
                  Copy Link
                </button>
              </div>
              <p className="box-instructions">
                Anyone with this link can join your squad (up to {squad.max_members} members)
              </p>
            </div>
          )}

          {/* SUMMON POPUP */}
          {showSummon && (
            <div className="feature-box summon-box">
              <div className="box-header">
                <h3>📢 Send Summon to All Members</h3>
                <button onClick={() => setShowSummon(false)}>✕</button>
              </div>
              <form onSubmit={handleSendSummon}>
                <div className="form-group">
                  <label>Title *</label>
                  <input
                    type="text"
                    value={summonForm.title}
                    onChange={(e) => setSummonForm({ ...summonForm, title: e.target.value })}
                    placeholder="e.g., Squad meeting in 10 minutes!"
                    required
                    disabled={summonLoading}
                  />
                </div>
                <div className="form-group">
                  <label>Message (optional)</label>
                  <textarea
                    value={summonForm.description}
                    onChange={(e) => setSummonForm({ ...summonForm, description: e.target.value })}
                    placeholder="Additional details..."
                    rows={3}
                    disabled={summonLoading}
                  />
                </div>
                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={summonLoading}
                  >
                    {summonLoading ? 'Sending...' : '📢 Send Summon'}
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowSummon(false)}
                    disabled={summonLoading}
                  >
                    Cancel
                  </button>
                </div>
              </form>
              <p className="box-instructions">
                All {squad.member_count} squad members will be notified immediately
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="squad-content">
        <div className="tabs">
          <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
            📊 Overview
          </button>
          <button className={`tab ${activeTab === 'members' ? 'active' : ''}`} onClick={() => setActiveTab('members')}>
            👥 Members ({squad.member_count})
          </button>
          <button className={`tab ${activeTab === 'schedule' ? 'active' : ''}`} onClick={() => setActiveTab('schedule')}>
            📅 Schedule ({events.length})
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-grid">
              <div className="info-card">
                <h3>Squad Information</h3>
                <div className="info-item">
                  <span className="info-label">Squad Name</span>
                  <span className="info-value">{squad.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Max Members</span>
                  <span className="info-value">{squad.max_members}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Status</span>
                  <span className={`status-badge ${squad.is_active ? 'active' : 'inactive'}`}>
                    {squad.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="info-card">
                <h3>📅 Upcoming Events</h3>
                {events.length === 0 ? (
                  <p className="empty-text">No upcoming events scheduled</p>
                ) : (
                  <div className="events-list">
                    {events.slice(0, 3).map(event => (
                      <div key={event.id} className="event-item">
                        <span className="event-title">{event.title}</span>
                        <span className="event-time">{new Date(event.scheduled_at).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="info-card">
                <h3>🎯 Active Goals</h3>
                {goals.filter(g => !g.is_completed).length === 0 ? (
                  <p className="empty-text">No active goals</p>
                ) : (
                  <div className="goals-list">
                    {goals.filter(g => !g.is_completed).slice(0, 3).map(goal => (
                      <div key={goal.id} className="goal-item">
                        <span>{goal.description}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'members' && (
            <div className="members-grid">
              {squad.members.map(member => (
                <div key={member.id} className="member-card">
                  <div className="member-avatar">{member.username.charAt(0).toUpperCase()}</div>
                  <div className="member-info">
                    <strong>{member.username}</strong>
                    {member.is_leader && <span className="leader-badge">👑 Leader</span>}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'schedule' && (
            <div className="schedule-content">
              <h3>Scheduled Events</h3>
              {events.length === 0 ? (
                <div className="empty-state">
                  <p>No events scheduled</p>
                  <p className="empty-hint">Create events to coordinate with your squad</p>
                </div>
              ) : (
                <div className="events-timeline">
                  {events.map(event => (
                    <div key={event.id} className="timeline-event">
                      <div className="event-marker"></div>
                      <div className="event-content">
                        <h4>{event.title}</h4>
                        {event.description && <p>{event.description}</p>}
                        <div className="event-meta">
                          <span>{new Date(event.scheduled_at).toLocaleString()}</span>
                          <span className={`event-type-badge ${event.event_type}`}>{event.event_type}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SquadDetailPage
