import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Whiteboard } from '../components/Whiteboard'
import { Chat } from '../components/Chat'
import { useWebRTCSignaling } from '../hooks/useWebRTCSignaling'
import './WarRoomPage.css'

export function WarRoomPage() {
  const { squadId } = useParams<{ squadId: string }>()
  const { user } = useAuthStore()
  const userId = user?.id || "";
  const username = user?.username || "";
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    if (!user || !squadId) return

    const token = useAuthStore.getState().accessToken
    if (!token) return

    // Determine WebSocket URL based on current location
    const hostname = window.location.hostname;
    const wsHost = (hostname === 'localhost' || hostname === '127.0.0.1') 
      ? 'localhost' 
      : hostname;
    const ws = new WebSocket(`ws://${wsHost}:8000/ws?token=${token}`)
    
    ws.onopen = () => {
      ws.send(JSON.stringify({ token }))
      setConnected(true)
      
      ws.send(JSON.stringify({
        type: 'subscribe_whiteboard',
        squad_id: squadId,
      }))
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      setConnected(false)
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [user, squadId])

  const { 
    remoteStreams, 
    isMuted, 
    isCallActive, 
    startCall, 
    endCall, 
    toggleMute 
  } = useWebRTCSignaling({
    socket: socket!,
    userId,
    username,
    roomId: squadId || "",
  })

  useEffect(() => {
    const audioElements = document.querySelectorAll<HTMLAudioElement>('.remote-audio')
    audioElements.forEach(audio => {
      const stream = remoteStreams.get(audio.dataset.userId || '')
      if (stream) {
        audio.srcObject = stream
      }
    })
  }, [remoteStreams])

  return (
    <div className="war-room-page">
      <header className="war-room-header">
        <Link to={`/squads/${squadId}`}>← Back to Squad</Link>
        <h1>🎨 War Room</h1>
        <div className="connection-status">
          {connected ? (
            <span className="status-connected">● Connected</span>
          ) : (
            <span className="status-disconnected">● Disconnected</span>
          )}
        </div>
      </header>
      
      <main className="war-room-main">
        <div className="war-room-grid">
          <div className="whiteboard-section">
            <h2>Tactical Whiteboard</h2>
            {socket && user ? (
              <Whiteboard
                socket={socket}
                userId={user.id}
                username={user.username}
                width={1000}
                height={600}
              />
            ) : (
              <div className="loading">Connecting...</div>
            )}
          </div>

          <div className="sidebar">
            <div className="voice-section">
              <h2>🎙️ Voice Chat</h2>
              <div className="voice-controls">
                {!isCallActive ? (
                  <button className="btn-start-call" onClick={startCall}>
                    🎤 Start Voice Call
                  </button>
                ) : (
                  <>
                    <button 
                      className={`btn-mute ${isMuted ? 'muted' : ''}`} 
                      onClick={toggleMute}
                    >
                      {isMuted ? '🔇 Unmute' : '🔊 Mute'}
                    </button>
                    <button className="btn-end-call" onClick={endCall}>
                      ❌ End Call
                    </button>
                  </>
                )}
              </div>
              <div className="participants">
                <h3>Participants ({1 + remoteStreams.size})</h3>
                <div className="participant-item">
                  <span className="participant-name">{username} (You)</span>
                  {isCallActive && (
                    <span className="status-indicator">
                      {isMuted ? '🔇' : '🎤'}
                    </span>
                  )}
                </div>
                {Array.from(remoteStreams.keys()).map(remoteUserId => (
                  <div key={remoteUserId} className="participant-item">
                    <span className="participant-name">User {remoteUserId.slice(0, 8)}</span>
                    <span className="status-indicator">🎤</span>
                    <audio 
                      className="remote-audio" 
                      data-user-id={remoteUserId}
                      autoPlay 
                      playsInline
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="chat-section">
              {socket ? (
                <Chat
                  socket={socket}
                  userId={userId}
                  username={username}
                  roomId={squadId || ''}
                />
              ) : (
                <div className="chat-offline">
                  <h2>💬 Squad Chat</h2>
                  <div className="offline-message">
                    <p>⚠️ Chat is offline</p>
                    <p>WebSocket connection failed</p>
                    <small>Check browser console (F12) for errors</small>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
