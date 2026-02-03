import { useState, useEffect, useRef, useCallback } from 'react'
import './VoiceCallPanel.css'

interface VoiceCallPanelProps {
  socket: WebSocket | null
  userId: string
  username: string
  roomId: string
  members: { id: string; username: string }[]
}

interface Participant {
  id: string
  username: string
  isMuted: boolean
  isDeafened: boolean
  isSpeaking: boolean
  stream?: MediaStream
}

export function VoiceCallPanel({ socket, userId, username, roomId, members }: VoiceCallPanelProps) {
  const [isInCall, setIsInCall] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isDeafened, setIsDeafened] = useState(false)
  const [isVideoOn, setIsVideoOn] = useState(false)
  const [isScreenSharing, setIsScreenSharing] = useState(false)
  const [participants, setParticipants] = useState<Participant[]>([])
  const [callDuration, setCallDuration] = useState(0)
  
  const localStreamRef = useRef<MediaStream | null>(null)
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map())
  const callTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'join_voice_call') {
          if (data.userId !== userId) {
            setParticipants(prev => {
              if (prev.find(p => p.id === data.userId)) return prev
              return [...prev, {
                id: data.userId,
                username: data.username,
                isMuted: false,
                isDeafened: false,
                isSpeaking: false
              }]
            })
            if (isInCall) {
              initiateCall(data.userId)
            }
          }
        }
        
        if (data.type === 'leave_voice_call') {
          setParticipants(prev => prev.filter(p => p.id !== data.userId))
          const pc = peerConnectionsRef.current.get(data.userId)
          if (pc) {
            pc.close()
            peerConnectionsRef.current.delete(data.userId)
          }
        }

        if (data.type === 'webrtc_offer' && data.fromUserId !== userId) {
          handleOffer(data)
        }

        if (data.type === 'webrtc_answer' && data.fromUserId !== userId) {
          handleAnswer(data)
        }

        if (data.type === 'webrtc_ice_candidate' && data.fromUserId !== userId) {
          handleIceCandidate(data)
        }

        if (data.type === 'user_muted') {
          setParticipants(prev => prev.map(p => 
            p.id === data.userId ? { ...p, isMuted: data.isMuted } : p
          ))
        }
      } catch (err) {
        console.error('Voice call message error:', err)
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket, userId, isInCall])

  useEffect(() => {
    if (isInCall) {
      callTimerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1)
      }, 1000)
    } else {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current)
      }
      setCallDuration(0)
    }

    return () => {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current)
      }
    }
  }, [isInCall])

  const createPeerConnection = useCallback((targetUserId: string) => {
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
      ]
    })

    pc.onicecandidate = (event) => {
      if (event.candidate && socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'webrtc_ice_candidate',
          targetUserId,
          candidate: event.candidate
        }))
      }
    }

    pc.ontrack = (event) => {
      setParticipants(prev => prev.map(p =>
        p.id === targetUserId ? { ...p, stream: event.streams[0] } : p
      ))
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current!)
      })
    }

    peerConnectionsRef.current.set(targetUserId, pc)
    return pc
  }, [socket])

  const initiateCall = useCallback(async (targetUserId: string) => {
    const pc = createPeerConnection(targetUserId)
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'webrtc_offer',
        targetUserId,
        offer
      }))
    }
  }, [socket, createPeerConnection])

  const handleOffer = async (data: any) => {
    const pc = createPeerConnection(data.fromUserId)
    await pc.setRemoteDescription(new RTCSessionDescription(data.offer))
    const answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'webrtc_answer',
        targetUserId: data.fromUserId,
        answer
      }))
    }
  }

  const handleAnswer = async (data: any) => {
    const pc = peerConnectionsRef.current.get(data.fromUserId)
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(data.answer))
    }
  }

  const handleIceCandidate = async (data: any) => {
    const pc = peerConnectionsRef.current.get(data.fromUserId)
    if (pc && data.candidate) {
      await pc.addIceCandidate(new RTCIceCandidate(data.candidate))
    }
  }

  const joinCall = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      localStreamRef.current = stream
      setIsInCall(true)

      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'join_voice_call',
          roomId,
          userId,
          username
        }))
      }

      // Add self to participants
      setParticipants([{ id: userId, username, isMuted: false, isDeafened: false, isSpeaking: false }])
    } catch (err) {
      console.error('Failed to get microphone access:', err)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const leaveCall = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop())
      localStreamRef.current = null
    }

    peerConnectionsRef.current.forEach(pc => pc.close())
    peerConnectionsRef.current.clear()

    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'leave_voice_call',
        roomId,
        userId,
        username
      }))
    }

    setIsInCall(false)
    setParticipants([])
    setIsMuted(false)
    setIsDeafened(false)
    setIsVideoOn(false)
    setIsScreenSharing(false)
  }

  const toggleMute = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach(track => {
        track.enabled = isMuted
      })
    }
    setIsMuted(!isMuted)
    
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'user_muted',
        roomId,
        userId,
        isMuted: !isMuted
      }))
    }
  }

  const toggleDeafen = () => {
    setIsDeafened(!isDeafened)
    // Mute all remote audio when deafened
  }

  const toggleVideo = async () => {
    if (!isVideoOn) {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (localStreamRef.current) {
          videoStream.getVideoTracks().forEach(track => {
            localStreamRef.current!.addTrack(track)
          })
        }
        setIsVideoOn(true)
      } catch (err) {
        console.error('Failed to get camera access:', err)
      }
    } else {
      if (localStreamRef.current) {
        localStreamRef.current.getVideoTracks().forEach(track => {
          track.stop()
          localStreamRef.current!.removeTrack(track)
        })
      }
      setIsVideoOn(false)
    }
  }

  const toggleScreenShare = async () => {
    if (!isScreenSharing) {
      try {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true })
        // Replace video track with screen share
        setIsScreenSharing(true)
        screenStream.getVideoTracks()[0].onended = () => {
          setIsScreenSharing(false)
        }
      } catch (err) {
        console.error('Failed to share screen:', err)
      }
    } else {
      setIsScreenSharing(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!isInCall) {
    return (
      <div className="voice-panel-inactive">
        <div className="voice-channel-info">
          <span className="voice-icon">🔊</span>
          <span>Voice Channel</span>
        </div>
        <button className="join-voice-btn" onClick={joinCall}>
          Join Voice
        </button>
        {members.length > 0 && (
          <div className="voice-members-preview">
            <span>{members.length} member{members.length !== 1 ? 's' : ''} in channel</span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="voice-call-panel">
      <div className="call-header">
        <div className="call-info">
          <span className="call-status">🔊 Voice Connected</span>
          <span className="call-duration">{formatDuration(callDuration)}</span>
        </div>
      </div>

      <div className="call-participants">
        {participants.map(p => (
          <div key={p.id} className={`participant ${p.isSpeaking ? 'speaking' : ''}`}>
            <div className="participant-avatar">
              {p.username.charAt(0).toUpperCase()}
              {p.isMuted && <span className="muted-icon">🔇</span>}
            </div>
            <span className="participant-name">{p.username}</span>
          </div>
        ))}
      </div>

      <div className="call-controls">
        <button 
          className={`control-btn ${isMuted ? 'active' : ''}`}
          onClick={toggleMute}
          title={isMuted ? 'Unmute' : 'Mute'}
        >
          {isMuted ? '🔇' : '🎤'}
        </button>
        
        <button 
          className={`control-btn ${isDeafened ? 'active' : ''}`}
          onClick={toggleDeafen}
          title={isDeafened ? 'Undeafen' : 'Deafen'}
        >
          {isDeafened ? '🔇' : '🔊'}
        </button>

        <button 
          className={`control-btn ${isVideoOn ? 'active' : ''}`}
          onClick={toggleVideo}
          title={isVideoOn ? 'Turn off camera' : 'Turn on camera'}
        >
          {isVideoOn ? '📹' : '📷'}
        </button>

        <button 
          className={`control-btn ${isScreenSharing ? 'active' : ''}`}
          onClick={toggleScreenShare}
          title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
        >
          🖥️
        </button>

        <button 
          className="control-btn leave-btn"
          onClick={leaveCall}
          title="Leave call"
        >
          📞
        </button>
      </div>
    </div>
  )
}
