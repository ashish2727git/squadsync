import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';

export interface WebSocketMessage {
  type: string;
  data: any;
}

export function useWebSocket(onMessage?: (message: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;  // Increased from 3 to 10
  const { accessToken } = useAuthStore();

  const connect = useCallback(() => {
    if (!accessToken || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }
    
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.log('Max reconnect attempts reached, stopping WebSocket');
      return;
    }

    try {
      // Determine WebSocket URL based on current location
      const hostname = window.location.hostname;
      const wsHost = (hostname === 'localhost' || hostname === '127.0.0.1') 
        ? 'localhost' 
        : hostname;
      const wsUrl = `ws://${wsHost}:8000/ws?token=${accessToken}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (onMessage) {
            onMessage(message);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = () => {
        // Silently handle errors
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectAttemptsRef.current += 1;
        
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 5000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [accessToken, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((type: string, data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    sendMessage,
    connect,
    disconnect,
  };
}
