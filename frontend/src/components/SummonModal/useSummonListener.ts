/**
 * Hook for listening to summon notifications via WebSocket
 */

import { useEffect, useState, useCallback } from 'react';
import { SummonData } from './types';

interface UseSummonListenerOptions {
  socket: WebSocket;
  userId: string;
  onSummonReceived: (summon: SummonData) => void;
}

/**
 * Hook to listen for summon notifications via WebSocket
 */
export function useSummonListener(options: UseSummonListenerOptions) {
  const { socket, userId, onSummonReceived } = options;
  const [activeSummon, setActiveSummon] = useState<SummonData | null>(null);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);

        // Check if this is a summon notification
        if (data.event_type === 'summon_created' && data.squad_id) {
          // Fetch full summon details from API
          // For now, construct from notification data
          const summon: SummonData = {
            id: data.summon_id,
            squad_id: data.squad_id,
            squad_name: data.squad_name || 'Squad',
            created_by_id: data.created_by_id,
            created_by_username: data.created_by_username,
            title: data.title,
            description: data.description,
            status: 'PENDING',
            expires_at: data.expires_at,
            created_at: data.timestamp || new Date().toISOString(),
          };

          setActiveSummon(summon);
          onSummonReceived(summon);
        }
      } catch (error) {
        console.error('Failed to parse summon notification:', error);
      }
    },
    [onSummonReceived]
  );

  useEffect(() => {
    if (socket.readyState === WebSocket.OPEN) {
      socket.addEventListener('message', handleMessage);
    }

    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, handleMessage]);

  const clearActiveSummon = useCallback(() => {
    setActiveSummon(null);
  }, []);

  return {
    activeSummon,
    clearActiveSummon,
  };
}
