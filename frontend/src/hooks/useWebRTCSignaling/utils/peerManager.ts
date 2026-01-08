/**
 * Peer connection management utilities
 */

import { PeerConnection } from '../types';

/**
 * Create a new RTCPeerConnection with configuration
 */
export function createPeerConnection(
  config: RTCConfiguration
): RTCPeerConnection {
  return new RTCPeerConnection(config);
}

/**
 * Set up local media stream and add tracks to peer connection
 */
export async function setupLocalMedia(
  connection: RTCPeerConnection,
  constraints: MediaStreamConstraints = { audio: true, video: true }
): Promise<MediaStream> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    
    // Add all tracks to the connection
    stream.getTracks().forEach((track) => {
      connection.addTrack(track, stream);
    });
    
    return stream;
  } catch (error) {
    console.error('Failed to get user media:', error);
    throw error;
  }
}

/**
 * Handle remote stream from peer connection
 */
export function handleRemoteStream(
  connection: RTCPeerConnection,
  onStream: (stream: MediaStream) => void
): () => void {
  const handleTrack = (event: RTCTrackEvent) => {
    if (event.streams && event.streams.length > 0) {
      onStream(event.streams[0]);
    }
  };

  connection.addEventListener('track', handleTrack);

  // Return cleanup function
  return () => {
    connection.removeEventListener('track', handleTrack);
  };
}

/**
 * Monitor connection state changes
 */
export function monitorConnectionState(
  connection: RTCPeerConnection,
  onStateChange: (state: RTCPeerConnectionState) => void
): () => void {
  const handleStateChange = () => {
    onStateChange(connection.connectionState);
  };

  connection.addEventListener('connectionstatechange', handleStateChange);

  // Return cleanup function
  return () => {
    connection.removeEventListener('connectionstatechange', handleStateChange);
  };
}

/**
 * Monitor ICE connection state changes
 */
export function monitorIceConnectionState(
  connection: RTCPeerConnection,
  onStateChange: (state: RTCIceConnectionState) => void
): () => void {
  const handleStateChange = () => {
    onStateChange(connection.iceConnectionState);
  };

  connection.addEventListener('iceconnectionstatechange', handleStateChange);

  // Return cleanup function
  return () => {
    connection.removeEventListener('iceconnectionstatechange', handleStateChange);
  };
}

/**
 * Collect ICE candidates from peer connection
 */
export function collectIceCandidates(
  connection: RTCPeerConnection,
  onCandidate: (candidate: RTCIceCandidate) => void
): () => void {
  const handleCandidate = (event: RTCPeerConnectionIceEvent) => {
    if (event.candidate) {
      onCandidate(event.candidate);
    }
  };

  connection.addEventListener('icecandidate', handleCandidate);

  // Return cleanup function
  return () => {
    connection.removeEventListener('icecandidate', handleCandidate);
  };
}

/**
 * Close peer connection and clean up
 */
export function closePeerConnection(peer: PeerConnection): void {
  if (peer.remoteStream) {
    peer.remoteStream.getTracks().forEach((track) => track.stop());
  }

  peer.connection.getSenders().forEach((sender) => {
    if (sender.track) {
      sender.track.stop();
    }
  });

  peer.connection.close();
}

/**
 * Close all peer connections
 */
export function closeAllPeerConnections(peers: Map<string, PeerConnection>): void {
  peers.forEach((peer) => {
    closePeerConnection(peer);
  });
  peers.clear();
}
