/**
 * WebRTC Signaling Hook
 * Handles WebRTC signaling via WebSocket for multi-participant war rooms
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { UseWebRTCSignalingOptions, WebRTCSignalingState, PeerConnection } from './types';
import { createRTCConfig, validateRTCConfig } from './utils/rtcConfig';
import {
  createJoinRoomMessage,
  createLeaveRoomMessage,
  createOfferMessage,
  createAnswerMessage,
  createIceCandidateMessage,
  parseSignalingMessageSync,
  validateSignalingMessage,
} from './utils/signalingMessages';
import {
  createPeerConnection,
  setupLocalMedia,
  handleRemoteStream,
  monitorConnectionState,
  collectIceCandidates,
  closePeerConnection,
  closeAllPeerConnections,
} from './utils/peerManager';

/**
 * Hook for WebRTC signaling in war rooms
 */
export function useWebRTCSignaling(options: UseWebRTCSignalingOptions) {
  const {
    socket,
    userId,
    username,
    roomId,
    config: configOptions = {},
    onRemoteStream,
    onPeerJoined,
    onPeerLeft,
    onConnectionStateChange,
    onError,
  } = options;

  // State
  const [state, setState] = useState<WebRTCSignalingState>({
    isJoined: false,
    peers: new Map(),
    localStream: null,
    connectionState: 'idle',
  });

  // Refs for stable references
  const peersRef = useRef<Map<string, PeerConnection>>(new Map());
  const localStreamRef = useRef<MediaStream | null>(null);
  const rtcConfigRef = useRef<RTCConfiguration | null>(null);
  const isJoiningRef = useRef(false);
  const joinedPeersRef = useRef<Set<string>>(new Set());

  // Initialize RTC configuration
  useEffect(() => {
    const rtcConfig = createRTCConfig([], configOptions);
    if (!validateRTCConfig(rtcConfig)) {
      const error = new Error('Invalid RTC configuration');
      onError?.(error);
      return;
    }
    rtcConfigRef.current = rtcConfig;
  }, [configOptions, onError]);

  /**
   * Join the war room
   */
  const joinRoom = useCallback(async (mediaConstraints: MediaStreamConstraints = { audio: true, video: true }) => {
    if (isJoiningRef.current || state.connectionState === 'joined') {
      console.warn('Already joined or joining');
      return;
    }

    if (!rtcConfigRef.current) {
      const error = new Error('RTC configuration not initialized');
      onError?.(error);
      return;
    }

    if (socket.readyState !== WebSocket.OPEN) {
      const error = new Error('WebSocket is not open');
      onError?.(error);
      return;
    }

    try {
      isJoiningRef.current = true;
      setState((prev) => ({ ...prev, connectionState: 'joining' }));

      // Get local media stream
      const stream = await setupLocalMedia(
        createPeerConnection(rtcConfigRef.current),
        mediaConstraints
      );
      localStreamRef.current = stream;

      // Send join room message
      const joinMessage = createJoinRoomMessage(userId, roomId, userId, username);
      socket.send(JSON.stringify(joinMessage));

      setState((prev) => ({
        ...prev,
        isJoined: true,
        localStream: stream,
        connectionState: 'joined',
      }));

      isJoiningRef.current = false;
    } catch (error) {
      isJoiningRef.current = false;
      setState((prev) => ({ ...prev, connectionState: 'error' }));
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }, [socket, userId, username, roomId, state.connectionState, onError]);

  /**
   * Leave the war room
   */
  const leaveRoom = useCallback(() => {
    if (state.connectionState !== 'joined') {
      return;
    }

    setState((prev) => ({ ...prev, connectionState: 'leaving' }));

    // Stop local stream
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    // Close all peer connections
    closeAllPeerConnections(peersRef.current);

    // Send leave room message
    if (socket.readyState === WebSocket.OPEN) {
      const leaveMessage = createLeaveRoomMessage(userId, roomId, userId);
      socket.send(JSON.stringify(leaveMessage));
    }

    setState((prev) => ({
      ...prev,
      isJoined: false,
      peers: new Map(),
      localStream: null,
      connectionState: 'idle',
    }));

    joinedPeersRef.current.clear();
  }, [socket, userId, roomId, state.connectionState]);

  /**
   * Create offer and send to peer
   */
  const createOfferForPeer = useCallback(async (peerId: string) => {
    if (!rtcConfigRef.current) {
      onError?.(new Error('RTC configuration not initialized'));
      return;
    }

    if (!localStreamRef.current) {
      onError?.(new Error('Local stream not available'));
      return;
    }

    try {
      // Create new peer connection
      const connection = createPeerConnection(rtcConfigRef.current);

      // Add local tracks
      localStreamRef.current.getTracks().forEach((track) => {
        connection.addTrack(track, localStreamRef.current!);
      });

      // Set up remote stream handling
      const cleanupTrack = handleRemoteStream(connection, (stream) => {
        const peer = peersRef.current.get(peerId);
        if (peer) {
          peer.remoteStream = stream;
          onRemoteStream?.(peerId, stream);
        }
      });

      // Monitor connection state
      const cleanupConnectionState = monitorConnectionState(connection, (connectionState) => {
        onConnectionStateChange?.(peerId, connectionState);
        
        const peer = peersRef.current.get(peerId);
        if (peer) {
          peer.isConnected = connectionState === 'connected';
        }
      });

      // Collect ICE candidates
      const cleanupIce = collectIceCandidates(connection, (candidate) => {
        if (socket.readyState === WebSocket.OPEN) {
          const iceMessage = createIceCandidateMessage(userId, peerId, roomId, candidate.toJSON());
          socket.send(JSON.stringify(iceMessage));
        }
      });

      // Create and set local description
      const offer = await connection.createOffer();
      await connection.setLocalDescription(offer);

      // Store peer connection
      const peer: PeerConnection = {
        peerId,
        connection,
        isInitiator: true,
        isConnected: false,
      };
      peersRef.current.set(peerId, peer);

      // Store cleanup functions (in a real implementation, you might want to track these)
      (peer as any)._cleanup = () => {
        cleanupTrack();
        cleanupConnectionState();
        cleanupIce();
      };

      // Send offer
      if (socket.readyState === WebSocket.OPEN) {
        const offerMessage = createOfferMessage(userId, peerId, roomId, offer);
        socket.send(JSON.stringify(offerMessage));
      }

      setState((prev) => ({
        ...prev,
        peers: new Map(peersRef.current),
      }));
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }, [socket, userId, roomId, onRemoteStream, onConnectionStateChange, onError]);

  /**
   * Handle incoming offer
   */
  const handleOffer = useCallback(async (from: string, offer: RTCSessionDescriptionInit) => {
    if (!rtcConfigRef.current) {
      onError?.(new Error('RTC configuration not initialized'));
      return;
    }

    if (!localStreamRef.current) {
      onError?.(new Error('Local stream not available'));
      return;
    }

    try {
      // Create peer connection
      const connection = createPeerConnection(rtcConfigRef.current);

      // Add local tracks
      localStreamRef.current.getTracks().forEach((track) => {
        connection.addTrack(track, localStreamRef.current!);
      });

      // Set up remote stream handling
      const cleanupTrack = handleRemoteStream(connection, (stream) => {
        const peer = peersRef.current.get(from);
        if (peer) {
          peer.remoteStream = stream;
          onRemoteStream?.(from, stream);
        }
      });

      // Monitor connection state
      const cleanupConnectionState = monitorConnectionState(connection, (connectionState) => {
        onConnectionStateChange?.(from, connectionState);
        
        const peer = peersRef.current.get(from);
        if (peer) {
          peer.isConnected = connectionState === 'connected';
        }
      });

      // Collect ICE candidates
      const cleanupIce = collectIceCandidates(connection, (candidate) => {
        if (socket.readyState === WebSocket.OPEN) {
          const iceMessage = createIceCandidateMessage(userId, from, roomId, candidate.toJSON());
          socket.send(JSON.stringify(iceMessage));
        }
      });

      // Set remote description and create answer
      await connection.setRemoteDescription(offer);
      const answer = await connection.createAnswer();
      await connection.setLocalDescription(answer);

      // Store peer connection
      const peer: PeerConnection = {
        peerId: from,
        connection,
        isInitiator: false,
        isConnected: false,
      };
      peersRef.current.set(from, peer);

      // Store cleanup functions
      (peer as any)._cleanup = () => {
        cleanupTrack();
        cleanupConnectionState();
        cleanupIce();
      };

      // Send answer
      if (socket.readyState === WebSocket.OPEN) {
        const answerMessage = createAnswerMessage(userId, from, roomId, answer);
        socket.send(JSON.stringify(answerMessage));
      }

      setState((prev) => ({
        ...prev,
        peers: new Map(peersRef.current),
      }));
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }, [socket, userId, roomId, onRemoteStream, onConnectionStateChange, onError]);

  /**
   * Handle incoming answer
   */
  const handleAnswer = useCallback(async (from: string, answer: RTCSessionDescriptionInit) => {
    const peer = peersRef.current.get(from);
    if (!peer) {
      console.warn(`No peer connection found for ${from}`);
      return;
    }

    try {
      await peer.connection.setRemoteDescription(answer);
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }, [onError]);

  /**
   * Handle incoming ICE candidate
   */
  const handleIceCandidate = useCallback(async (from: string, candidate: RTCIceCandidateInit) => {
    const peer = peersRef.current.get(from);
    if (!peer) {
      console.warn(`No peer connection found for ${from}`);
      return;
    }

    try {
      await peer.connection.addIceCandidate(candidate);
    } catch (error) {
      console.error('Failed to add ICE candidate:', error);
      // Non-fatal error, don't call onError
    }
  }, []);

  /**
   * Remove peer connection
   */
  const removePeer = useCallback((peerId: string) => {
    const peer = peersRef.current.get(peerId);
    if (peer) {
      // Clean up event listeners
      if ((peer as any)._cleanup) {
        (peer as any)._cleanup();
      }
      closePeerConnection(peer);
      peersRef.current.delete(peerId);
      
      setState((prev) => ({
        ...prev,
        peers: new Map(peersRef.current),
      }));

      onPeerLeft?.(peerId);
    }
  }, [onPeerLeft]);

  // WebSocket message handler
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // WebSocket text messages are always strings
      const message = parseSignalingMessageSync(event.data as string);
      if (!message || !validateSignalingMessage(message)) {
        return;
      }

      // Ignore messages from self
      if (message.from === userId) {
        return;
      }

      // Ignore messages for different rooms
      if (message.roomId !== roomId) {
        return;
      }

      // Handle targeted messages
      if (message.to && message.to !== userId) {
        return;
      }

      switch (message.type) {
        case 'peer_joined':
          if (message.payload.userId && !joinedPeersRef.current.has(message.payload.userId)) {
            joinedPeersRef.current.add(message.payload.userId);
            onPeerJoined?.(message.payload.userId);
            
            // Create offer if we're already in the room
            if (state.isJoined && localStreamRef.current) {
              createOfferForPeer(message.payload.userId);
            }
          }
          break;

        case 'peer_left':
          if (message.payload.userId) {
            joinedPeersRef.current.delete(message.payload.userId);
            removePeer(message.payload.userId);
          }
          break;

        case 'offer':
          if (message.payload.sdp) {
            handleOffer(message.from, message.payload.sdp);
          }
          break;

        case 'answer':
          if (message.payload.sdp) {
            handleAnswer(message.from, message.payload.sdp);
          }
          break;

        case 'ice_candidate':
          if (message.payload.candidate) {
            handleIceCandidate(message.from, message.payload.candidate);
          }
          break;

        case 'room_error':
          if (message.payload.error) {
            onError?.(new Error(message.payload.error));
          }
          break;
      }
    };

    socket.addEventListener('message', handleMessage);

    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, userId, roomId, state.isJoined, createOfferForPeer, handleOffer, handleAnswer, handleIceCandidate, removePeer, onPeerJoined, onError]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      leaveRoom();
    };
  }, [leaveRoom]);

  return {
    state,
    joinRoom,
    leaveRoom,
    removePeer,
  };
}
