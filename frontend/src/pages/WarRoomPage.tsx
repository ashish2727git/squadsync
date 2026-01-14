import { useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Whiteboard } from '../components/Whiteboard'
import { useWebRTCSignaling } from '../hooks/useWebRTCSignaling'
import './WarRoomPage.css'

export function WarRoomPage() {
  const { squadId } = useParams<{ squadId: string }>()
  const { user } = useAuthStore()
  const userId = user?.id || "";
  const username = user?.username || "";
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (!user || !squadId) return

    const token = useAuthStore.getState().accessToken
    if (!token) return

    // Connect WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`)
    
    ws.onopen = () => {
      // Send auth message
      ws.send(JSON.stringify({ token }))
      setConnected(true)
      
      // Subscribe to whiteboard
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

  // WebRTC signaling
  useWebRTCSignaling({
  socket: socket!,
  userId,
  username,
  roomId: squadId || "",
});



  // useEffect(() => {
  //   if (localStream && videoRef.current) {
  //     videoRef.current.srcObject = localStream
  //   }
  // }, [localStream])

  return (
    <div className="war-room-page">
      <header className="war-room-header">
        <Link to={`/squads/${squadId}`}>← Back to Squad</Link>
        <h1>War Room</h1>
        <div className="connection-status">
          {connected ? (
            <span className="status-connected">● Connected</span>
          ) : (
            <span className="status-disconnected">● Disconnected</span>
          )}
        </div>
      </header>
      <main className="war-room-main">
        <div className="war-room-content">
          <div className="whiteboard-section">
            <h2>Tactical Whiteboard</h2>
            {socket && user ? (
              <Whiteboard
                socket={socket}
                userId={user.id}
                username={user.username}
                width={1200}
                height={800}
              />
            ) : (
              <div>Connecting...</div>
            )}
          </div>
          <div className="video-section">
            <h2>Voice Chat</h2>
            <div className="video-container">
              <video ref={videoRef} autoPlay muted playsInline />
              {/* <div className="video-controls">
                <button onClick={startCall}>Start Call</button>
                <button onClick={endCall}>End Call</button>
              </div> */}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
