/**
 * Type definitions for WebRTC signaling
 */

export interface SignalingMessage {
  type: SignalingMessageType;
  from: string; // User ID of sender
  to?: string; // User ID of recipient (optional for broadcast)
  roomId: string; // War room ID
  payload: SignalingPayload;
  timestamp: number;
}

export type SignalingMessageType =
  | 'join_room'
  | 'leave_room'
  | 'offer'
  | 'answer'
  | 'ice_candidate'
  | 'peer_joined'
  | 'peer_left'
  | 'room_error';

export interface SignalingPayload {
  // Join/Leave room
  userId?: string;
  username?: string;
  
  // Offer/Answer
  sdp?: RTCSessionDescriptionInit;
  
  // ICE Candidate
  candidate?: RTCIceCandidateInit;
  
  // Error
  error?: string;
}

export interface PeerConnection {
  peerId: string;
  connection: RTCPeerConnection;
  isInitiator: boolean;
  isConnected: boolean;
  remoteStream?: MediaStream;
}

export interface WebRTCConfig {
  iceServers: RTCIceServer[];
  iceTransportPolicy?: RTCIceTransportPolicy;
  bundlePolicy?: RTCBundlePolicy;
  rtcpMuxPolicy?: RTCRtcpMuxPolicy;
}

export interface UseWebRTCSignalingOptions {
  socket: WebSocket;
  userId: string;
  username: string;
  roomId: string;
  config?: Partial<WebRTCConfig>;
  onRemoteStream?: (peerId: string, stream: MediaStream) => void;
  onPeerJoined?: (peerId: string) => void;
  onPeerLeft?: (peerId: string) => void;
  onConnectionStateChange?: (peerId: string, state: RTCPeerConnectionState) => void;
  onError?: (error: Error) => void;
}

export interface WebRTCSignalingState {
  isJoined: boolean;
  peers: Map<string, PeerConnection>;
  localStream: MediaStream | null;
  connectionState: 'idle' | 'joining' | 'joined' | 'leaving' | 'error';
}
