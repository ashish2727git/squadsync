/**
 * WebSocket synchronization hook - handles all socket communication
 * Separated from drawing logic for clean architecture
 */

import { useEffect, useRef, useCallback } from 'react';
import { DrawingPath, DrawingEvent, Point } from '../types';
import { throttle } from '../utils/throttle';
// import throttle from "lodash/throttle";


interface UseWhiteboardSyncOptions {
  socket: WebSocket;
  userId: string;
  username: string;
  onRemotePath?: (path: DrawingPath) => void;
  onRemoteClear?: () => void;
  throttleMs?: number;
}

/**
 * Hook for managing WebSocket synchronization
 */
export function useWhiteboardSync(options: UseWhiteboardSyncOptions) {
  const {
    socket,
    userId,
    username,
    onRemotePath,
    onRemoteClear,
    throttleMs = 16, // ~60fps throttling
  } = options;

  const pathsRef = useRef<Map<string, DrawingPath>>(new Map());
  const pendingEventsRef = useRef<DrawingEvent[]>([]);
  const socketReadyRef = useRef(false);

  // Check if socket is ready
  useEffect(() => {
    socketReadyRef.current = socket.readyState === WebSocket.OPEN;

    const handleOpen = () => {
      socketReadyRef.current = true;
      // Send any pending events
      flushPendingEvents();
    };

    const handleClose = () => {
      socketReadyRef.current = false;
    };

    socket.addEventListener('open', handleOpen);
    socket.addEventListener('close', handleClose);

    return () => {
      socket.removeEventListener('open', handleOpen);
      socket.removeEventListener('close', handleClose);
    };
  }, [socket]);

  /**
   * Send pending events when socket becomes ready
   */
  const flushPendingEvents = useCallback(() => {
    if (!socketReadyRef.current || pendingEventsRef.current.length === 0) return;

    const events = [...pendingEventsRef.current];
    pendingEventsRef.current = [];

    events.forEach((event) => {
      if (socketReadyRef.current) {
        socket.send(JSON.stringify(event));
      } else {
        // Re-queue if socket closed
        pendingEventsRef.current.push(event);
      }
    });
  }, [socket]);

  /**
   * Send drawing event via WebSocket
   */
  const sendDrawingEvent = useCallback((event: DrawingEvent) => {
    if (socketReadyRef.current) {
      socket.send(JSON.stringify(event));
    } else {
      // Queue event if socket not ready
      pendingEventsRef.current.push(event);
    }
  }, [socket]);

  // Create throttled sender for move events
const throttledSendMove = useRef<((event: DrawingEvent) => void) | null>(null);

useEffect(() => {
  throttledSendMove.current = throttle(
    (event: DrawingEvent) => {
      sendDrawingEvent(event);
    },
    throttleMs
  );
}, [sendDrawingEvent, throttleMs]);

  /**
   * Broadcast drawing start event
   */
  const broadcastDrawStart = useCallback((pathId: string, point: Point, color: string, lineWidth: number) => {
    const event: DrawingEvent = {
      type: 'draw_start',
      pathId,
      userId,
      username,
      color,
      lineWidth,
      point,
      timestamp: Date.now(),
    };
    sendDrawingEvent(event);
  }, [userId, username, sendDrawingEvent]);

  /**
   * Broadcast drawing move event (throttled)
   */
  const broadcastDrawMove = useCallback((pathId: string, point: Point) => {
    const event: DrawingEvent = {
      type: 'draw_move',
      pathId,
      userId,
      username,
      color: '', // Not needed for move events
      lineWidth: 0, // Not needed for move events
      point,
      timestamp: Date.now(),
    };
    throttledSendMove.current?.(event);
  }, [userId, username]);

  /**
   * Broadcast drawing end event
   */
  const broadcastDrawEnd = useCallback((pathId: string) => {
    // Flush any pending move events first
    

        // const throttledSendMove = useRef<ReturnType<typeof throttle>>();

        // throttledSendMove.current = throttle(() => {
        //   // emit drawing move (no unused args)
        // }, 16);

        // cleanup
        // if (throttledSendMove.current) {
        //   // throttledSendMove.current.cancel();
        // }


    
    const event: DrawingEvent = {
      type: 'draw_end',
      pathId,
      userId,
      username,
      color: '',
      lineWidth: 0,
      timestamp: Date.now(),
    };
    sendDrawingEvent(event);
  }, [userId, username, sendDrawingEvent]);

  /**
   * Broadcast clear canvas event
   */
  const broadcastClear = useCallback(() => {
    const event: DrawingEvent = {
      type: 'clear',
      userId,
      username,
      color: '',
      lineWidth: 0,
      timestamp: Date.now(),
    };
    sendDrawingEvent(event);
  }, [userId, username, sendDrawingEvent]);

  /**
   * Handle incoming drawing event from WebSocket
   */
  const handleRemoteEvent = useCallback((event: DrawingEvent) => {
    // Ignore events from self
    if (event.userId === userId) return;

    switch (event.type) {
      case 'draw_start': {
        if (!event.pathId || !event.point) return;

        const newPath: DrawingPath = {
          id: event.pathId,
          userId: event.userId,
          username: event.username,
          color: event.color,
          lineWidth: event.lineWidth,
          points: [event.point],
          timestamp: event.timestamp,
        };

        pathsRef.current.set(event.pathId, newPath);
        onRemotePath?.(newPath);
        break;
      }

      case 'draw_move': {
        if (!event.pathId || !event.point) return;

        const path = pathsRef.current.get(event.pathId);
        if (path) {
          path.points.push(event.point);
          onRemotePath?.(path);
        }
        break;
      }

      case 'draw_end': {
        if (!event.pathId) return;

        const path = pathsRef.current.get(event.pathId);
        if (path) {
          onRemotePath?.(path);
        }
        break;
      }

      case 'clear': {
        pathsRef.current.clear();
        onRemoteClear?.();
        break;
      }
    }
  }, [userId, onRemotePath, onRemoteClear]);

  // Set up WebSocket message listener
  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
      try {
        const event: DrawingEvent = JSON.parse(e.data);
        handleRemoteEvent(event);
      } catch (error) {
        console.error('Failed to parse drawing event:', error);
      }
    };

    socket.addEventListener('message', handleMessage);

    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, handleRemoteEvent]);

  return {
    broadcastDrawStart,
    broadcastDrawMove,
    broadcastDrawEnd,
    broadcastClear,
    paths: pathsRef.current,
  };
}
