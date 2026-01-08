# WebRTC Signaling Hook

Production-ready WebRTC signaling hook for SquadSync War Rooms. Handles offer/answer/ICE candidate exchange via WebSocket for multi-participant video/audio calls.

## Features

- ✅ **WebRTC Signaling**: Complete offer/answer/ICE candidate handling
- ✅ **WebSocket-based**: Uses existing WebSocket connection for signaling
- ✅ **Multi-participant**: Supports multiple peers in a war room
- ✅ **Automatic Peer Management**: Creates offers/answers automatically
- ✅ **Connection State Tracking**: Monitors peer connection states
- ✅ **Clean Architecture**: Separated utilities and types
- ✅ **TypeScript**: Fully typed with comprehensive type definitions

## Architecture

The hook is structured with clear separation of concerns:

- **`useWebRTCSignaling.ts`**: Main hook logic
- **`types.ts`**: TypeScript type definitions
- **`utils/rtcConfig.ts`**: RTC configuration utilities
- **`utils/signalingMessages.ts`**: Message creation and parsing
- **`utils/peerManager.ts`**: Peer connection management utilities

## Usage

```tsx
import { useWebRTCSignaling } from '@/hooks/useWebRTCSignaling';

function WarRoom() {
  const socket = useWebSocket(); // Your WebSocket connection
  const userId = 'user-123';
  const username = 'PlayerOne';
  const roomId = 'war-room-456';

  const { state, joinRoom, leaveRoom } = useWebRTCSignaling({
    socket,
    userId,
    username,
    roomId,
    config: {
      // Optional: Add TURN servers
      iceServers: [
        {
          urls: 'turn:turn.example.com:3478',
          username: 'turn-user',
          credential: 'turn-password',
        },
      ],
      iceTransportPolicy: 'all',
    },
    onRemoteStream: (peerId, stream) => {
      // Handle remote video/audio stream
      const videoElement = document.getElementById(`video-${peerId}`);
      if (videoElement && videoElement instanceof HTMLVideoElement) {
        videoElement.srcObject = stream;
      }
    },
    onPeerJoined: (peerId) => {
      console.log(`Peer ${peerId} joined the room`);
    },
    onPeerLeft: (peerId) => {
      console.log(`Peer ${peerId} left the room`);
      // Clean up UI elements for this peer
    },
    onConnectionStateChange: (peerId, state) => {
      console.log(`Peer ${peerId} connection state: ${state}`);
      // Update UI to reflect connection state
    },
    onError: (error) => {
      console.error('WebRTC error:', error);
      // Handle errors
    },
  });

  // Join room when component mounts
  useEffect(() => {
    joinRoom({
      audio: true,
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    });

    return () => {
      leaveRoom();
    };
  }, []);

  // Use local stream
  useEffect(() => {
    if (state.localStream) {
      const localVideo = document.getElementById('local-video');
      if (localVideo && localVideo instanceof HTMLVideoElement) {
        localVideo.srcObject = state.localStream;
      }
    }
  }, [state.localStream]);

  return (
    <div>
      <video id="local-video" autoPlay muted />
      {Array.from(state.peers.keys()).map((peerId) => (
        <video key={peerId} id={`video-${peerId}`} autoPlay />
      ))}
      <button onClick={leaveRoom}>Leave Room</button>
    </div>
  );
}
```

## API

### Hook Options

```typescript
interface UseWebRTCSignalingOptions {
  socket: WebSocket;                    // WebSocket connection (must be authenticated)
  userId: string;                       // Current user's unique ID
  username: string;                     // Current user's display name
  roomId: string;                       // War room ID
  config?: Partial<WebRTCConfig>;       // Optional RTC configuration
  onRemoteStream?: (peerId: string, stream: MediaStream) => void;
  onPeerJoined?: (peerId: string) => void;
  onPeerLeft?: (peerId: string) => void;
  onConnectionStateChange?: (peerId: string, state: RTCPeerConnectionState) => void;
  onError?: (error: Error) => void;
}
```

### Return Value

```typescript
{
  state: WebRTCSignalingState;  // Current hook state
  joinRoom: (constraints?: MediaStreamConstraints) => Promise<void>;
  leaveRoom: () => void;
  removePeer: (peerId: string) => void;
}
```

### State

```typescript
interface WebRTCSignalingState {
  isJoined: boolean;                           // Whether user has joined the room
  peers: Map<string, PeerConnection>;         // Map of peer connections
  localStream: MediaStream | null;            // Local media stream
  connectionState: 'idle' | 'joining' | 'joined' | 'leaving' | 'error';
}
```

## Signaling Protocol

The hook sends and receives the following WebSocket messages:

### Outgoing Messages

```typescript
// Join room
{
  type: 'join_room',
  from: string,
  roomId: string,
  payload: { userId: string, username: string }
}

// Leave room
{
  type: 'leave_room',
  from: string,
  roomId: string,
  payload: { userId: string }
}

// Offer
{
  type: 'offer',
  from: string,
  to: string,
  roomId: string,
  payload: { sdp: RTCSessionDescriptionInit }
}

// Answer
{
  type: 'answer',
  from: string,
  to: string,
  roomId: string,
  payload: { sdp: RTCSessionDescriptionInit }
}

// ICE Candidate
{
  type: 'ice_candidate',
  from: string,
  to: string,
  roomId: string,
  payload: { candidate: RTCIceCandidateInit }
}
```

### Incoming Messages

The hook handles the same message types from other peers, plus:

```typescript
// Peer joined (broadcast by server)
{
  type: 'peer_joined',
  from: string,
  roomId: string,
  payload: { userId: string, username: string }
}

// Peer left (broadcast by server)
{
  type: 'peer_left',
  from: string,
  roomId: string,
  payload: { userId: string }
}

// Room error
{
  type: 'room_error',
  from: string,
  roomId: string,
  payload: { error: string }
}
```

## Server-Side Requirements

The WebSocket server should:

1. **Handle room joining**: When receiving `join_room`, broadcast `peer_joined` to all other participants
2. **Route signaling messages**: Forward `offer`, `answer`, and `ice_candidate` messages to the specified `to` user
3. **Handle leaving**: When receiving `leave_room`, broadcast `peer_left` to remaining participants
4. **Validate permissions**: Ensure users can only join/leave rooms they have access to

## RTC Configuration

The hook uses Google's public STUN servers by default. For production, provide TURN servers:

```typescript
config: {
  iceServers: [
    {
      urls: 'turn:your-turn-server.com:3478',
      username: 'turn-username',
      credential: 'turn-password',
    },
  ],
}
```

## Error Handling

The hook handles various error scenarios:

- **Invalid RTC configuration**: Calls `onError` if configuration is invalid
- **Media access denied**: Calls `onError` if user denies camera/microphone access
- **WebSocket closed**: Logs warning and maintains state
- **ICE candidate errors**: Logs but doesn't break connection (non-fatal)

## Performance Considerations

- **Automatic cleanup**: All event listeners and peer connections are cleaned up
- **Efficient state updates**: Uses refs to minimize re-renders
- **Connection pooling**: Reuses peer connections where possible
- **ICE candidate batching**: Sends ICE candidates as they're generated

## Browser Support

- Chrome/Edge (latest) ✅
- Firefox (latest) ✅
- Safari (latest) ✅
- Mobile browsers (iOS Safari, Chrome Mobile) ✅

## Notes

- The hook assumes the WebSocket connection is already authenticated
- Media stream constraints can be customized in `joinRoom()`
- The hook automatically creates offers when new peers join
- All peer connections are cleaned up when leaving the room
- The hook is stateless regarding room membership - the server should track who's in which room
