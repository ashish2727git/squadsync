import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Whiteboard } from '../components/Whiteboard'
import { Chat } from '../components/Chat'
import { VoiceCallPanel } from '../components/VoiceCallPanel'
import { SummonPanel } from '../components/SummonPanel'
import { UserStatusBadge } from '../components/UserStatusBadge'
import './WarRoomPage.css'

interface SquadMember {
  id: string
  username: string
  role: string
}

export function WarRoomPage() {
  const { squadId } = useParams<{ squadId: string }>()
  const { user } = useAuthStore()
  const userId = user?.id || ""
  const username = user?.username || ""
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [members, setMembers] = useState<SquadMember[]>([])
  const [squadName, setSquadName] = useState('')
  const [isLeader, setIsLeader] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'summons'>('chat')

  // Fetch squad details
  useEffect(() => {
    const fetchSquad = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`http://localhost:8000/api/v1/squads/${squadId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setSquadName(data.name)
          setMembers(data.members || [])
          // Check if current user is a leader
          const userMember = data.members?.find((m: any) => m.id === userId)
          setIsLeader(userMember?.role === 'SQUAD_LEADER' || userMember?.role === 'TEAM_MANAGER' || userMember?.role === 'ORG_ADMIN')
        }
      } catch (err) {
        console.error('Failed to fetch squad:', err)
      }
    }
    if (squadId && userId) fetchSquad()
  }, [squadId, userId])

  // WebSocket connection
  useEffect(() => {
    if (!user || !squadId) return

    const token = useAuthStore.getState().accessToken
    if (!token) return

    const hostname = window.location.hostname
    const wsHost = (hostname === 'localhost' || hostname === '127.0.0.1') 
      ? 'localhost' 
      : hostname
    const ws = new WebSocket(`ws://${wsHost}:8000/ws?token=${token}`)
    
    ws.onopen = () => {
      console.log('✅ War Room WebSocket connected!')
      setConnected(true)
      setSocket(ws)
      
      // Subscribe to all channels
      ws.send(JSON.stringify({ type: 'subscribe_whiteboard', squad_id: squadId }))
      setTimeout(() => {
        ws.send(JSON.stringify({ type: 'subscribe_chat', squad_id: squadId }))
      }, 100)
      setTimeout(() => {
        ws.send(JSON.stringify({ type: 'subscribe_voice', squad_id: squadId }))
      }, 200)
      setTimeout(() => {
        ws.send(JSON.stringify({ type: 'subscribe_squad', squad_id: squadId }))
      }, 300)

      // Update presence to online
      ws.send(JSON.stringify({ type: 'presence_update', presence: 'ONLINE' }))
    }

    ws.onerror = (error) => console.error('WebSocket error:', error)

    ws.onclose = () => {
      console.log('❌ War Room WebSocket disconnected')
      setConnected(false)
      setSocket(null)
    }

    return () => {
      ws.close()
      setSocket(null)
    }
  }, [user, squadId])

  return (
    <div className="war-room-page">
      <header className="war-room-header">
        <div className="header-left">
          <Link to={`/squads/${squadId}`} className="back-link">← Back</Link>
          <div className="header-info">
            <h1>{squadName || 'War Room'}</h1>
            <div className="connection-badge">
              <span className={connected ? 'connected' : 'disconnected'}>
                {connected ? '● Connected' : '○ Connecting...'}
              </span>
            </div>
          </div>
        </div>
        <div className="header-right">
          <div className="online-members">
            {members.slice(0, 5).map(m => (
              <UserStatusBadge 
                key={m.id}
                userId={m.id}
                username={m.username}
                size="small"
                showName={false}
              />
            ))}
            {members.length > 5 && (
              <span className="more-members">+{members.length - 5}</span>
            )}
          </div>
        </div>
      </header>
      
      <main className="war-room-main">
        <div className="war-room-grid">
          {/* Main Content Area */}
          <div className="main-content">
            <div className="whiteboard-section">
              <div className="section-header">
                <h2>🎨 Tactical Whiteboard</h2>
                <span className="section-hint">Draw strategies with your squad</span>
              </div>
              {socket && user ? (
                <Whiteboard
                  socket={socket}
                  userId={user.id}
                  username={user.username}
                  width={1000}
                  height={500}
                />
              ) : (
                <div className="loading-placeholder">
                  <div className="spinner"></div>
                  <p>Connecting to whiteboard...</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="sidebar">
            {/* Voice Panel */}
            <VoiceCallPanel
              socket={socket}
              userId={userId}
              username={username}
              roomId={squadId || ''}
              members={members}
            />

            {/* Squad Members */}
            <div className="members-section">
              <h3>Squad Members ({members.length})</h3>
              <div className="members-list">
                {members.map(m => (
                  <UserStatusBadge 
                    key={m.id}
                    userId={m.id}
                    username={m.username}
                    size="small"
                    showStatus={true}
                    showName={true}
                  />
                ))}
              </div>
            </div>

            {/* Tabs for Chat/Summons */}
            <div className="sidebar-tabs">
              <button 
                className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
              >
                💬 Chat
              </button>
              <button 
                className={`tab ${activeTab === 'summons' ? 'active' : ''}`}
                onClick={() => setActiveTab('summons')}
              >
                ⚡ Summons
              </button>
            </div>

            {/* Chat Section */}
            {activeTab === 'chat' && (
              <div className="chat-section">
                {socket ? (
                  <Chat
                    socket={socket}
                    userId={userId}
                    username={username}
                    roomId={squadId || ''}
                  />
                ) : (
                  <div className="offline-message">
                    <p>Chat is connecting...</p>
                  </div>
                )}
              </div>
            )}

            {/* Summons Section */}
            {activeTab === 'summons' && (
              <SummonPanel
                squadId={squadId || ''}
                userId={userId}
                isLeader={isLeader}
                socket={socket}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
