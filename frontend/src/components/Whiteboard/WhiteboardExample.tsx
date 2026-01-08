/**
 * Example usage of Whiteboard component
 * This is a reference implementation showing how to integrate the whiteboard
 */

import React, { useState, useEffect, useRef } from 'react';
import { Whiteboard } from './Whiteboard';

interface WhiteboardExampleProps {
  wsUrl: string;
  token: string;
  userId: string;
  username: string;
  backgroundImageUrl?: string;
}

export const WhiteboardExample: React.FC<WhiteboardExampleProps> = ({
  wsUrl,
  token,
  userId,
  username,
  backgroundImageUrl,
}) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    let isMounted = true;

    const connect = () => {
      try {
        const ws = new WebSocket(`${wsUrl}?token=${token}`);

        ws.onopen = () => {
          if (isMounted) {
            console.log('WebSocket connected');
            setConnectionStatus('connected');
            setSocket(ws);
            reconnectAttemptsRef.current = 0;
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          if (isMounted) {
            setConnectionStatus('error');
          }
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          if (isMounted) {
            setConnectionStatus('disconnected');
            setSocket(null);

            // Attempt reconnection with exponential backoff
            if (reconnectAttemptsRef.current < maxReconnectAttempts) {
              const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
              reconnectAttemptsRef.current++;

              reconnectTimeoutRef.current = setTimeout(() => {
                if (isMounted) {
                  setConnectionStatus('connecting');
                  connect();
                }
              }, delay);
            } else {
              console.error('Max reconnection attempts reached');
            }
          }
        };

        return ws;
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        if (isMounted) {
          setConnectionStatus('error');
        }
        return null;
      }
    };

    const ws = connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [wsUrl, token]);

  const handleBackgroundImageLoad = (img: HTMLImageElement) => {
    console.log('Background image loaded:', {
      width: img.width,
      height: img.height,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
    });
  };

  if (connectionStatus === 'connecting') {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        Connecting to server...
      </div>
    );
  }

  if (connectionStatus === 'error' || !socket || socket.readyState !== WebSocket.OPEN) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#e74c3c' }}>
        Failed to connect to server. Please check your connection and try again.
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ 
        padding: '8px 16px', 
        backgroundColor: '#2c3e50', 
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <strong>SquadSync Whiteboard</strong> - {username}
        </div>
        <div style={{ fontSize: '12px', opacity: 0.8 }}>
          Status: {connectionStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>
      <div style={{ flex: 1, position: 'relative' }}>
        <Whiteboard
          socket={socket}
          userId={userId}
          username={username}
          width={1200}
          height={800}
          strokeColor="#000000"
          strokeWidth={3}
          backgroundImageUrl={backgroundImageUrl}
          onBackgroundImageLoad={handleBackgroundImageLoad}
        />
      </div>
    </div>
  );
};

export default WhiteboardExample;
