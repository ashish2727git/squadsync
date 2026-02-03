import { useState, useEffect } from 'react'
import { UserStatusBadge } from './UserStatusBadge'
import './SummonPanel.css'

interface SummonPanelProps {
  squadId: string
  userId: string
  isLeader: boolean
  socket: WebSocket | null
}

interface Summon {
  id: string
  title: string
  description?: string
  status: string
  expires_at?: string
  created_by_username: string
  total_members: number
  response_summary: {
    PENDING: number
    ACCEPT: number
    DECLINE: number
    MAYBE: number
  }
  responses: SummonResponse[]
}

interface SummonResponse {
  id: string
  user_id: string
  username: string
  response_type: string
  message?: string
  created_at: string
}

export function SummonPanel({ squadId, userId, isLeader, socket }: SummonPanelProps) {
  const [summons, setSummons] = useState<Summon[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newSummon, setNewSummon] = useState({ title: '', description: '', expiresIn: 60 })
  const [selectedSummon, setSelectedSummon] = useState<Summon | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [responseMessage, setResponseMessage] = useState('')

  useEffect(() => {
    fetchSummons()
  }, [squadId])

  useEffect(() => {
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'summon_created' || data.type === 'summon_update') {
          fetchSummons()
        }
        if (data.type === 'summon_response') {
          fetchSummons()
        }
      } catch (err) {
        console.error('Summon socket error:', err)
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket])

  const fetchSummons = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`http://localhost:8000/api/v1/summons/squad/${squadId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setSummons(data.summons || [])
      }
    } catch (err) {
      console.error('Failed to fetch summons:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const createSummon = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const expiresAt = new Date(Date.now() + newSummon.expiresIn * 60000).toISOString()
      
      const res = await fetch('http://localhost:8000/api/v1/summons/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          squad_id: squadId,
          title: newSummon.title,
          description: newSummon.description,
          expires_at: expiresAt,
        }),
      })

      if (res.ok) {
        setShowCreateModal(false)
        setNewSummon({ title: '', description: '', expiresIn: 60 })
        fetchSummons()
        
        // Play notification sound
        const audio = new Audio('/summon-sound.mp3')
        audio.play().catch(() => {})
      }
    } catch (err) {
      console.error('Failed to create summon:', err)
    }
  }

  const respondToSummon = async (summonId: string, responseType: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`http://localhost:8000/api/v1/summons/${summonId}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          response_type: responseType,
          message: responseMessage,
        }),
      })

      if (res.ok) {
        fetchSummons()
        setResponseMessage('')
        setSelectedSummon(null)
      }
    } catch (err) {
      console.error('Failed to respond to summon:', err)
    }
  }

  const getTimeRemaining = (expiresAt?: string) => {
    if (!expiresAt) return null
    const remaining = new Date(expiresAt).getTime() - Date.now()
    if (remaining <= 0) return 'Expired'
    
    const minutes = Math.floor(remaining / 60000)
    const hours = Math.floor(minutes / 60)
    
    if (hours > 0) return `${hours}h ${minutes % 60}m remaining`
    return `${minutes}m remaining`
  }

  const getUserResponse = (summon: Summon) => {
    return summon.responses.find(r => r.user_id === userId)
  }

  const activeSummons = summons.filter(s => s.status === 'ACTIVE' || s.status === 'PENDING')

  return (
    <div className="summon-panel">
      <div className="summon-header">
        <h3>⚡ Squad Summons</h3>
        {isLeader && (
          <button 
            className="create-summon-btn"
            onClick={() => setShowCreateModal(true)}
          >
            + New Summon
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="summon-loading">Loading summons...</div>
      ) : activeSummons.length === 0 ? (
        <div className="no-summons">
          <span className="no-summons-icon">⚡</span>
          <p>No active summons</p>
          {isLeader && <span>Create one to rally your squad!</span>}
        </div>
      ) : (
        <div className="summon-list">
          {activeSummons.map(summon => {
            const userResponse = getUserResponse(summon)
            return (
              <div 
                key={summon.id} 
                className={`summon-card ${userResponse ? `responded-${userResponse.response_type.toLowerCase()}` : ''}`}
                onClick={() => setSelectedSummon(summon)}
              >
                <div className="summon-card-header">
                  <h4>{summon.title}</h4>
                  <span className="summon-time">{getTimeRemaining(summon.expires_at)}</span>
                </div>
                
                {summon.description && (
                  <p className="summon-description">{summon.description}</p>
                )}

                <div className="summon-stats">
                  <span className="stat accept">✓ {summon.response_summary.ACCEPT}</span>
                  <span className="stat decline">✗ {summon.response_summary.DECLINE}</span>
                  <span className="stat maybe">? {summon.response_summary.MAYBE}</span>
                  <span className="stat pending">⏳ {summon.response_summary.PENDING}</span>
                </div>

                <div className="summon-progress">
                  <div 
                    className="progress-bar accept" 
                    style={{ width: `${(summon.response_summary.ACCEPT / summon.total_members) * 100}%` }}
                  />
                  <div 
                    className="progress-bar decline" 
                    style={{ width: `${(summon.response_summary.DECLINE / summon.total_members) * 100}%` }}
                  />
                  <div 
                    className="progress-bar maybe" 
                    style={{ width: `${(summon.response_summary.MAYBE / summon.total_members) * 100}%` }}
                  />
                </div>

                {!userResponse && (
                  <div className="quick-respond">
                    <button 
                      className="respond-btn accept"
                      onClick={(e) => { e.stopPropagation(); respondToSummon(summon.id, 'ACCEPT'); }}
                    >
                      ✓ Accept
                    </button>
                    <button 
                      className="respond-btn decline"
                      onClick={(e) => { e.stopPropagation(); respondToSummon(summon.id, 'DECLINE'); }}
                    >
                      ✗ Decline
                    </button>
                    <button 
                      className="respond-btn maybe"
                      onClick={(e) => { e.stopPropagation(); respondToSummon(summon.id, 'MAYBE'); }}
                    >
                      ? Maybe
                    </button>
                  </div>
                )}

                {userResponse && (
                  <div className="your-response">
                    Your response: <strong>{userResponse.response_type}</strong>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Create Summon Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>⚡ Create New Summon</h3>
            
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={newSummon.title}
                onChange={(e) => setNewSummon({ ...newSummon, title: e.target.value })}
                placeholder="e.g., Raid Tonight!"
                maxLength={100}
              />
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={newSummon.description}
                onChange={(e) => setNewSummon({ ...newSummon, description: e.target.value })}
                placeholder="Add details about the summon..."
                maxLength={500}
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Expires in</label>
              <select
                value={newSummon.expiresIn}
                onChange={(e) => setNewSummon({ ...newSummon, expiresIn: parseInt(e.target.value) })}
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={120}>2 hours</option>
                <option value={240}>4 hours</option>
                <option value={1440}>24 hours</option>
              </select>
            </div>

            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button 
                className="create-btn"
                onClick={createSummon}
                disabled={!newSummon.title.trim()}
              >
                ⚡ Send Summon
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Summon Detail Modal */}
      {selectedSummon && (
        <div className="modal-overlay" onClick={() => setSelectedSummon(null)}>
          <div className="modal-content large" onClick={e => e.stopPropagation()}>
            <h3>{selectedSummon.title}</h3>
            <p className="summon-detail-desc">{selectedSummon.description}</p>
            
            <div className="response-summary">
              <div className="summary-item accept">
                <span className="count">{selectedSummon.response_summary.ACCEPT}</span>
                <span className="label">Accepted</span>
              </div>
              <div className="summary-item decline">
                <span className="count">{selectedSummon.response_summary.DECLINE}</span>
                <span className="label">Declined</span>
              </div>
              <div className="summary-item maybe">
                <span className="count">{selectedSummon.response_summary.MAYBE}</span>
                <span className="label">Maybe</span>
              </div>
              <div className="summary-item pending">
                <span className="count">{selectedSummon.response_summary.PENDING}</span>
                <span className="label">Pending</span>
              </div>
            </div>

            <div className="responses-list">
              <h4>Responses</h4>
              {selectedSummon.responses.map(r => (
                <div key={r.id} className={`response-item ${r.response_type.toLowerCase()}`}>
                  <UserStatusBadge
                    userId={r.user_id}
                    username={r.username}
                    size="small"
                    showStatus={false}
                  />
                  <span className="response-type">{r.response_type}</span>
                  {r.message && <span className="response-message">"{r.message}"</span>}
                </div>
              ))}
            </div>

            {!getUserResponse(selectedSummon) && (
              <div className="respond-form">
                <input
                  type="text"
                  value={responseMessage}
                  onChange={(e) => setResponseMessage(e.target.value)}
                  placeholder="Add a message (optional)..."
                />
                <div className="respond-buttons">
                  <button onClick={() => respondToSummon(selectedSummon.id, 'ACCEPT')}>✓ Accept</button>
                  <button onClick={() => respondToSummon(selectedSummon.id, 'DECLINE')}>✗ Decline</button>
                  <button onClick={() => respondToSummon(selectedSummon.id, 'MAYBE')}>? Maybe</button>
                </div>
              </div>
            )}

            <button className="close-modal-btn" onClick={() => setSelectedSummon(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
