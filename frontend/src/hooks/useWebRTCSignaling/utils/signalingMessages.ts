/**
 * Signaling message utilities
 */

import { SignalingMessage, SignalingMessageType, SignalingPayload } from '../types';

/**
 * Create a signaling message
 */
export function createSignalingMessage(
  type: SignalingMessageType,
  from: string,
  roomId: string,
  payload: SignalingPayload,
  to?: string
): SignalingMessage {
  return {
    type,
    from,
    to,
    roomId,
    payload,
    timestamp: Date.now(),
  };
}

/**
 * Create join room message
 */
export function createJoinRoomMessage(
  from: string,
  roomId: string,
  userId: string,
  username: string
): SignalingMessage {
  return createSignalingMessage('join_room', from, roomId, {
    userId,
    username,
  });
}

/**
 * Create leave room message
 */
export function createLeaveRoomMessage(
  from: string,
  roomId: string,
  userId: string
): SignalingMessage {
  return createSignalingMessage('leave_room', from, roomId, {
    userId,
  });
}

/**
 * Create offer message
 */
export function createOfferMessage(
  from: string,
  to: string,
  roomId: string,
  offer: RTCSessionDescriptionInit
): SignalingMessage {
  return createSignalingMessage('offer', from, roomId, {
    sdp: offer,
  }, to);
}

/**
 * Create answer message
 */
export function createAnswerMessage(
  from: string,
  to: string,
  roomId: string,
  answer: RTCSessionDescriptionInit
): SignalingMessage {
  return createSignalingMessage('answer', from, roomId, {
    sdp: answer,
  }, to);
}

/**
 * Create ICE candidate message
 */
export function createIceCandidateMessage(
  from: string,
  to: string,
  roomId: string,
  candidate: RTCIceCandidateInit
): SignalingMessage {
  return createSignalingMessage('ice_candidate', from, roomId, {
    candidate,
  }, to);
}

/**
 * Parse signaling message from WebSocket
 * Note: WebSocket messages are typically strings, but this handles both
 */
export async function parseSignalingMessage(data: string | Blob): Promise<SignalingMessage | null> {
  try {
    let text: string;
    
    if (typeof data === 'string') {
      text = data;
    } else if (data instanceof Blob) {
      // Convert Blob to text (shouldn't happen with text WebSocket, but handle it)
      text = await data.text();
    } else {
      return null;
    }

    const message: SignalingMessage = JSON.parse(text);
    
    // Validate message structure
    if (!message.type || !message.from || !message.roomId || !message.payload) {
      return null;
    }
    
    return message;
  } catch (error) {
    console.error('Failed to parse signaling message:', error);
    return null;
  }
}

/**
 * Synchronous version for use in event handlers where data is always string
 */
export function parseSignalingMessageSync(data: string): SignalingMessage | null {
  try {
    const message: SignalingMessage = JSON.parse(data);
    
    // Validate message structure
    if (!message.type || !message.from || !message.roomId || !message.payload) {
      return null;
    }
    
    return message;
  } catch (error) {
    console.error('Failed to parse signaling message:', error);
    return null;
  }
}

/**
 * Validate signaling message
 */
export function validateSignalingMessage(message: any): message is SignalingMessage {
  if (!message || typeof message !== 'object') return false;
  if (!message.type || typeof message.type !== 'string') return false;
  if (!message.from || typeof message.from !== 'string') return false;
  if (!message.roomId || typeof message.roomId !== 'string') return false;
  if (!message.payload || typeof message.payload !== 'object') return false;
  if (typeof message.timestamp !== 'number') return false;
  
  // Validate payload based on message type
  switch (message.type) {
    case 'offer':
    case 'answer':
      return !!message.payload.sdp;
    case 'ice_candidate':
      return !!message.payload.candidate;
    case 'join_room':
    case 'leave_room':
      return !!message.payload.userId;
    default:
      return true;
  }
}
