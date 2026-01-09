/**
 * Type definitions for Summon Modal component
 */

export interface SummonData {
  id: string;
  squad_id: string;
  squad_name: string;
  created_by_id: string;
  created_by_username: string;
  title: string;
  description?: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED' | 'CANCELLED';
  expires_at?: string;
  created_at: string;
}

export interface SummonModalProps {
  summon: SummonData;
  userId: string;
  apiBaseUrl: string;
  authToken: string;
  onResponseSubmitted: (summonId: string, response: 'ACCEPT' | 'DECLINE') => void;
  onError?: (error: Error) => void;
}

export type ResponseType = 'ACCEPT' | 'DECLINE';
