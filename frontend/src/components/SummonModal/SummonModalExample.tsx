/**
 * Example usage of SummonModal component
 * Shows how to integrate with WebSocket and display summons
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SummonModal } from './SummonModal';
import { useSummonListener } from './useSummonListener';
import { SummonData } from './types';

interface SummonModalExampleProps {
  socket: WebSocket;
  userId: string;
  apiBaseUrl: string;
  authToken: string;
}

export const SummonModalExample: React.FC<SummonModalExampleProps> = ({
  socket,
  userId,
  apiBaseUrl,
  authToken,
}) => {
  const [currentSummon, setCurrentSummon] = useState<SummonData | null>(null);
  const [respondedSummons, setRespondedSummons] = useState<Set<string>>(new Set());

  const handleSummonReceived = useCallback((summon: SummonData) => {
    // Only show if user hasn't already responded
    if (!respondedSummons.has(summon.id)) {
      setCurrentSummon(summon);
    }
  }, [respondedSummons]);

  const handleResponseSubmitted = useCallback((summonId: string, response: 'ACCEPT' | 'DECLINE') => {
    // Mark as responded
    setRespondedSummons((prev) => new Set(prev).add(summonId));
    
    // Close modal
    setCurrentSummon(null);
    
    console.log(`Summon ${summonId} responded with: ${response}`);
  }, []);

  const handleError = useCallback((error: Error) => {
    console.error('Summon modal error:', error);
    // Optionally show error notification to user
  }, []);

  // Listen for summon notifications
  useSummonListener({
    socket,
    userId,
    onSummonReceived: handleSummonReceived,
  });

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (currentSummon) {
      document.body.classList.add('summon-modal-open');
    } else {
      document.body.classList.remove('summon-modal-open');
    }

    return () => {
      document.body.classList.remove('summon-modal-open');
    };
  }, [currentSummon]);

  return (
    <>
      {currentSummon && (
        <SummonModal
          summon={currentSummon}
          userId={userId}
          apiBaseUrl={apiBaseUrl}
          authToken={authToken}
          onResponseSubmitted={handleResponseSubmitted}
          onError={handleError}
        />
      )}
    </>
  );
};

export default SummonModalExample;
