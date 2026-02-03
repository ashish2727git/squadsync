import { useState, useEffect } from 'react'
import './UserStatusBadge.css'

interface UserStatusBadgeProps {
  userId: string
  username: string
  avatarUrl?: string
  size?: 'small' | 'medium' | 'large'
  showStatus?: boolean
  showName?: boolean
  onClick?: () => void
}

type PresenceStatus = 'ONLINE' | 'IDLE' | 'DND' | 'OFFLINE'

interface UserPresence {
  presence: PresenceStatus
  status_text?: string
  current_activity?: string
}

export function UserStatusBadge({ 
  userId, 
  username, 
  avatarUrl,
  size = 'medium',
  showStatus = true,
  showName = true,
  onClick
}: UserStatusBadgeProps) {
  const [presence, setPresence] = useState<UserPresence>({ presence: 'OFFLINE' })

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`http://localhost:8000/api/v1/messages/status/${userId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setPresence(data)
        }
      } catch (err) {
        console.log('Could not fetch user status')
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [userId])

  const getStatusColor = () => {
    switch (presence.presence) {
      case 'ONLINE': return '#43b581'
      case 'IDLE': return '#faa61a'
      case 'DND': return '#f04747'
      default: return '#747f8d'
    }
  }

  const getStatusLabel = () => {
    switch (presence.presence) {
      case 'ONLINE': return 'Online'
      case 'IDLE': return 'Idle'
      case 'DND': return 'Do Not Disturb'
      default: return 'Offline'
    }
  }

  const sizeMap = { small: 24, medium: 40, large: 80 }
  const avatarSize = sizeMap[size]

  return (
    <div 
      className={`user-status-badge size-${size} ${onClick ? 'clickable' : ''}`}
      onClick={onClick}
      title={`${username} - ${getStatusLabel()}${presence.status_text ? `: ${presence.status_text}` : ''}`}
    >
      <div className="badge-avatar" style={{ width: avatarSize, height: avatarSize }}>
        {avatarUrl ? (
          <img src={avatarUrl} alt={username} />
        ) : (
          <span className="avatar-initial">{username.charAt(0).toUpperCase()}</span>
        )}
        {showStatus && (
          <span 
            className="status-indicator"
            style={{ backgroundColor: getStatusColor() }}
          />
        )}
      </div>
      
      {showName && (
        <div className="badge-info">
          <span className="badge-username">{username}</span>
          {presence.current_activity && (
            <span className="badge-activity">🎮 {presence.current_activity}</span>
          )}
          {presence.status_text && !presence.current_activity && (
            <span className="badge-status-text">{presence.status_text}</span>
          )}
        </div>
      )}
    </div>
  )
}

export function UserStatusSelector({ 
  currentStatus, 
  onStatusChange 
}: { 
  currentStatus: PresenceStatus
  onStatusChange: (status: PresenceStatus, statusText?: string) => void 
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [customStatus, setCustomStatus] = useState('')

  const statuses: { value: PresenceStatus; label: string; color: string; icon: string }[] = [
    { value: 'ONLINE', label: 'Online', color: '#43b581', icon: '🟢' },
    { value: 'IDLE', label: 'Idle', color: '#faa61a', icon: '🌙' },
    { value: 'DND', label: 'Do Not Disturb', color: '#f04747', icon: '⛔' },
    { value: 'OFFLINE', label: 'Invisible', color: '#747f8d', icon: '⚫' },
  ]

  const handleSelect = (status: PresenceStatus) => {
    onStatusChange(status, customStatus || undefined)
    setIsOpen(false)
  }

  return (
    <div className="status-selector">
      <button 
        className="status-selector-trigger"
        onClick={() => setIsOpen(!isOpen)}
      >
        {statuses.find(s => s.value === currentStatus)?.icon} Set Status
      </button>
      
      {isOpen && (
        <div className="status-dropdown">
          <div className="status-custom-input">
            <input
              type="text"
              placeholder="Set a custom status..."
              value={customStatus}
              onChange={(e) => setCustomStatus(e.target.value)}
              maxLength={128}
            />
          </div>
          
          <div className="status-options">
            {statuses.map(status => (
              <button
                key={status.value}
                className={`status-option ${currentStatus === status.value ? 'active' : ''}`}
                onClick={() => handleSelect(status.value)}
              >
                <span className="status-dot" style={{ backgroundColor: status.color }} />
                <span>{status.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
