import apiClient from './client';

// Types
export interface Organization {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface Team {
  id: string;
  name: string;
  game_title: string;
  organization_id: string;
  is_active: boolean;
  created_at: string;
}

export interface Squad {
  id: string;
  name: string;
  description?: string;
  team_id: string;
  max_members: number;
  member_count: number;
  is_active: boolean;
  created_at: string;
}

export interface SquadMember {
  id: string;
  username: string;
  is_leader: boolean;
}

export interface SquadDetail extends Squad {
  members: SquadMember[];
}

export interface VaultItem {
  id: string;
  name: string;
  description?: string;
  item_type: string;
  is_private: boolean;
  created_at: string;
}

export interface ScheduleEvent {
  id: string;
  title: string;
  description?: string;
  event_type: string;
  scheduled_at: string;
  duration_minutes: number;
  created_by: string;
  created_at: string;
}

export interface DailyGoal {
  id: string;
  description: string;
  target_date: string;
  is_completed: boolean;
  assigned_to?: string;
  created_at: string;
}

export interface Summon {
  id: string;
  squad_id: string;
  summoner_id: string;
  summoner_username: string;
  message?: string;
  urgency: string;
  status: string;
  created_at: string;
  expires_at?: string;
}

// Organization API
export const organizationAPI = {
  list: () => apiClient.get<Organization[]>('/organizations'),
  create: (data: { name: string; description?: string }) =>
    apiClient.post<Organization>('/organizations', data),
  get: (id: string) => apiClient.get<Organization>(`/organizations/${id}`),
};

// Team API
export const teamAPI = {
  list: (organizationId?: string) =>
    apiClient.get<Team[]>('/teams', { params: { organization_id: organizationId } }),
  create: (data: { name: string; game_title: string; organization_id: string }) =>
    apiClient.post<Team>('/teams', data),
  get: (id: string) => apiClient.get<Team>(`/teams/${id}`),
};

// Squad API
export const squadAPI = {
  list: () => apiClient.get<Squad[]>('/squads'),
  create: (data: {
    name: string;
    description?: string;
    team_id: string;
    max_members?: number;
  }) => apiClient.post<Squad>('/squads', data),
  quickCreate: (data: {
    squad_name: string;
    squad_description?: string;
    game_title?: string;
    max_members?: number;
  }) => apiClient.post<Squad>('/squads/quick-create', data),
  get: (id: string) => apiClient.get<SquadDetail>(`/squads/${id}`),
  join: (id: string, data?: { invite_code?: string }) =>
    apiClient.post(`/squads/${id}/join`, data || {}),
  leave: (id: string) => apiClient.post(`/squads/${id}/leave`),
};

// Vault API
export const vaultAPI = {
  list: () => apiClient.get<VaultItem[]>('/vault/items'),
  create: (data: {
    name: string;
    description?: string;
    item_type: string;
    is_private: boolean;
    data?: any;
  }) => apiClient.post<VaultItem>('/vault/items', data),
  get: (id: string) => apiClient.get<VaultItem>(`/vault/items/${id}`),
  delete: (id: string) => apiClient.delete(`/vault/items/${id}`),
  share: (id: string, squadId: string) =>
    apiClient.post(`/vault/items/${id}/share`, { squad_id: squadId }),
};

// Schedule API
export const scheduleAPI = {
  getEvents: (squadId: string) =>
    apiClient.get<ScheduleEvent[]>(`/squads/${squadId}/schedule/events`),
  createEvent: (
    squadId: string,
    data: {
      title: string;
      description?: string;
      event_type: string;
      scheduled_at: string;
      duration_minutes: number;
    }
  ) => apiClient.post<ScheduleEvent>(`/squads/${squadId}/schedule/events`, data),
  updateEvent: (eventId: string, data: Partial<ScheduleEvent>) =>
    apiClient.patch<ScheduleEvent>(`/schedule/events/${eventId}`, data),
  deleteEvent: (eventId: string) => apiClient.delete(`/schedule/events/${eventId}`),
  
  getGoals: (squadId: string) =>
    apiClient.get<DailyGoal[]>(`/squads/${squadId}/schedule/daily-goals`),
  createGoal: (
    squadId: string,
    data: { description: string; target_date: string; assigned_to?: string }
  ) => apiClient.post<DailyGoal>(`/squads/${squadId}/schedule/daily-goals`, data),
  updateGoal: (goalId: string, data: Partial<DailyGoal>) =>
    apiClient.patch<DailyGoal>(`/schedule/daily-goals/${goalId}`, data),
  deleteGoal: (goalId: string) => apiClient.delete(`/schedule/daily-goals/${goalId}`),
};

// Summon API
export const summonAPI = {
  listActive: () => apiClient.get<Summon[]>('/summons/active'),
  create: (data: { squad_id: string; title: string; description?: string; urgency?: string }) =>
    apiClient.post('/summons', data),
  respond: (
    summonId: string,
    data: { response_type: string; message?: string }
  ) => apiClient.post(`/summons/${summonId}/respond`, data),
};
