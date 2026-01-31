import { useEffect, useState } from 'react'

interface UseWebRTCProps {
  socket: WebSocket | null
  userId: string
  username: string
  roomId: string
}

export function useWebRTCSignaling({ socket, userId, username, roomId }: UseWebRTCProps) {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null)
  const [peers, setPeers] = useState<Map<string, RTCPeerConnection>>(new Map())
  const [remoteStreams, setRemoteStreams] = useState<Map<string, MediaStream>>(new Map())
  const [isMuted, setIsMuted] = useState(false)
  const [isCallActive, setIsCallActive] = useState(false)
  const [iceServers, setIceServers] = useState<RTCIceServer[]>([
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ])

  // Fetch TURN servers from backend on mount
  useEffect(() => {
    const fetchIceServers = async () => {
      try {
        const hostname = window.location.hostname
        const apiHost = (hostname === 'localhost' || hostname === '127.0.0.1')
          ? 'localhost'
          : hostname
        
        const response = await fetch(`http://${apiHost}:8000/api/v1/webrtc/ice-servers`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.iceServers && data.iceServers.length > 0) {
            setIceServers(data.iceServers)
            console.log('✅ Using Twilio TURN servers for better quality')
          }
        }
      } catch (err) {
        console.log('Using default STUN servers')
      }
    }
    
    fetchIceServers()
  }, [])

  const configuration: RTCConfiguration = {
    iceServers
  }

  useEffect(() => {
    if (!socket) return

    const handleMessage = async (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'webrtc_offer') {
          await handleOffer(data)
        } else if (data.type === 'webrtc_answer') {
          await handleAnswer(data)
        } else if (data.type === 'webrtc_ice_candidate') {
          await handleIceCandidate(data)
        } else if (data.type === 'user_left_call') {
          handleUserLeft(data.userId)
        }
      } catch (err) {
        console.error('WebRTC signaling error:', err)
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket, localStream, peers])

  const startCall = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true,
        video: false 
      })
      setLocalStream(stream)
      setIsCallActive(true)

      if (socket) {
        socket.send(JSON.stringify({
          type: 'join_voice_call',
          roomId,
          userId,
          username
        }))
      }
    } catch (err) {
      console.error('Failed to get media:', err)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const endCall = () => {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop())
      setLocalStream(null)
    }

    peers.forEach(peer => peer.close())
    setPeers(new Map())
    setRemoteStreams(new Map())
    setIsCallActive(false)

    if (socket) {
      socket.send(JSON.stringify({
        type: 'leave_voice_call',
        roomId,
        userId
      }))
    }
  }

  const toggleMute = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !track.enabled
      })
      setIsMuted(!isMuted)
    }
  }

  const createPeerConnection = (targetUserId: string) => {
    const peer = new RTCPeerConnection(configuration)

    if (localStream) {
      localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream)
      })
    }

    peer.onicecandidate = (event) => {
      if (event.candidate && socket) {
        socket.send(JSON.stringify({
          type: 'webrtc_ice_candidate',
          candidate: event.candidate,
          targetUserId,
          fromUserId: userId
        }))
      }
    }

    peer.ontrack = (event) => {
      setRemoteStreams(prev => {
        const newMap = new Map(prev)
        newMap.set(targetUserId, event.streams[0])
        return newMap
      })
    }

    setPeers(prev => {
      const newMap = new Map(prev)
      newMap.set(targetUserId, peer)
      return newMap
    })

    return peer
  }

  const handleOffer = async (data: any) => {
    const peer = createPeerConnection(data.fromUserId)
    await peer.setRemoteDescription(new RTCSessionDescription(data.offer))
    const answer = await peer.createAnswer()
    await peer.setLocalDescription(answer)

    if (socket) {
      socket.send(JSON.stringify({
        type: 'webrtc_answer',
        answer,
        targetUserId: data.fromUserId,
        fromUserId: userId
      }))
    }
  }

  const handleAnswer = async (data: any) => {
    const peer = peers.get(data.fromUserId)
    if (peer) {
      await peer.setRemoteDescription(new RTCSessionDescription(data.answer))
    }
  }

  const handleIceCandidate = async (data: any) => {
    const peer = peers.get(data.fromUserId)
    if (peer && data.candidate) {
      await peer.addIceCandidate(new RTCIceCandidate(data.candidate))
    }
  }

  const handleUserLeft = (leftUserId: string) => {
    const peer = peers.get(leftUserId)
    if (peer) {
      peer.close()
      setPeers(prev => {
        const newMap = new Map(prev)
        newMap.delete(leftUserId)
        return newMap
      })
    }

    setRemoteStreams(prev => {
      const newMap = new Map(prev)
      newMap.delete(leftUserId)
      return newMap
    })
  }

  return {
    localStream,
    remoteStreams,
    isMuted,
    isCallActive,
    startCall,
    endCall,
    toggleMute
  }
}
