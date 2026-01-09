/**
 * Summon Modal Component
 * Tactical, urgent modal that cannot be ignored - requires immediate response
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SummonModalProps, ResponseType } from './types';
import './SummonModal.css';

export const SummonModal: React.FC<SummonModalProps> = ({
  summon,
  userId,
  apiBaseUrl,
  authToken,
  onResponseSubmitted,
  onError,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  // Calculate time remaining if expires_at is set
  useEffect(() => {
    if (!summon.expires_at) {
      setTimeRemaining(null);
      return;
    }

    const updateTimeRemaining = () => {
      const expiresAt = new Date(summon.expires_at!).getTime();
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((expiresAt - now) / 1000));
      setTimeRemaining(remaining);
    };

    updateTimeRemaining();
    const interval = setInterval(updateTimeRemaining, 1000);

    return () => clearInterval(interval);
  }, [summon.expires_at]);

  // Format time remaining
  const formatTimeRemaining = (seconds: number): string => {
    if (seconds <= 0) return 'EXPIRED';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Submit response to API
  const submitResponse = useCallback(
    async (responseType: ResponseType) => {
      if (isSubmitting) return;

      setIsSubmitting(true);
      setError(null);

      try {
        const response = await fetch(`${apiBaseUrl}/api/v1/summons/${summon.id}/respond`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            response_type: responseType,
            message: null,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Failed to submit response' }));
          throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const responseData = await response.json();
        
        // Call callback to notify parent
        onResponseSubmitted(summon.id, responseType);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to submit response';
        setError(errorMessage);
        onError?.(err instanceof Error ? err : new Error(errorMessage));
      } finally {
        setIsSubmitting(false);
      }
    },
    [summon.id, apiBaseUrl, authToken, isSubmitting, onResponseSubmitted, onError]
  );

  // Handle ACCEPT button
  const handleAccept = useCallback(() => {
    submitResponse('ACCEPT');
  }, [submitResponse]);

  // Handle DECLINE button
  const handleDecline = useCallback(() => {
    submitResponse('DECLINE');
  }, [submitResponse]);

  // Prevent closing via ESC or clicking outside
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };

    window.addEventListener('keydown', handleEscape);
    document.addEventListener('click', handleClickOutside, true);

    return () => {
      window.removeEventListener('keydown', handleEscape);
      document.removeEventListener('click', handleClickOutside, true);
    };
  }, []);

  // Check if expired
  const isExpired = timeRemaining !== null && timeRemaining <= 0;

  return (
    <div className="summon-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="summon-title">
      <div className="summon-modal-container">
        {/* Urgent header with pulsing effect */}
        <div className="summon-modal-header">
          <div className="summon-alert-indicator">
            <div className="summon-pulse-ring"></div>
            <div className="summon-alert-icon">⚡</div>
          </div>
          <h2 id="summon-title" className="summon-modal-title">SUMMON</h2>
          {timeRemaining !== null && (
            <div className={`summon-timer ${isExpired ? 'expired' : ''}`}>
              {formatTimeRemaining(timeRemaining)}
            </div>
          )}
        </div>

        {/* Squad and creator info */}
        <div className="summon-modal-info">
          <div className="summon-squad-name">{summon.squad_name}</div>
          <div className="summon-creator">
            From: <strong>{summon.created_by_username}</strong>
          </div>
        </div>

        {/* Title and description */}
        <div className="summon-modal-content">
          <h3 className="summon-content-title">{summon.title}</h3>
          {summon.description && (
            <p className="summon-content-description">{summon.description}</p>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="summon-error-message" role="alert">
            {error}
          </div>
        )}

        {/* Action buttons */}
        <div className="summon-modal-actions">
          <button
            type="button"
            className="summon-btn summon-btn-accept"
            onClick={handleAccept}
            disabled={isSubmitting || isExpired}
            aria-label="Accept summon"
          >
            {isSubmitting ? 'SUBMITTING...' : 'ACCEPT'}
          </button>
          <button
            type="button"
            className="summon-btn summon-btn-decline"
            onClick={handleDecline}
            disabled={isSubmitting || isExpired}
            aria-label="Decline summon"
          >
            {isSubmitting ? 'SUBMITTING...' : 'DECLINE'}
          </button>
        </div>

        {/* Warning message */}
        <div className="summon-warning">
          Response required to continue
        </div>
      </div>
    </div>
  );
};

export default SummonModal;
