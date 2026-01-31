import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { squadAPI, SquadDetail } from '../api/services';
import './OnboardingPage.css';

export function JoinSquadPage() {
  const { squadId } = useParams<{ squadId: string }>();
  const navigate = useNavigate();
  const [squad, setSquad] = useState<SquadDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (squadId) {
      loadSquad();
    }
  }, [squadId]);

  const loadSquad = async () => {
    try {
      // Try to get squad info - may fail if user doesn't have access yet
      const response = await squadAPI.get(squadId!);
      setSquad(response.data);
    } catch (err: any) {
      console.log('Cannot load squad details before joining:', err);
      // If 403/401 (no access), create a minimal squad object for display
      if (err.response?.status === 403 || err.response?.status === 401) {
        setSquad({
          id: squadId!,
          name: 'Squad',
          description: 'Join to see details',
          member_count: 0,
          max_members: 50,
          members: [],
          team_id: '',
          created_at: '',
          updated_at: '',
          is_active: true,
        } as SquadDetail);
      } else {
        setError('Squad not found');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async () => {
    setJoining(true);
    setError('');
    
    try {
      await squadAPI.join(squadId!);
      navigate(`/squads/${squadId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join squad');
    } finally {
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="onboarding-page">
        <div className="onboarding-container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading squad...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="onboarding-page">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <h1>Join Squad</h1>
          {squad && <p>You've been invited to join {squad.name}</p>}
        </div>

        {error && <div className="error-banner">{error}</div>}

        {squad ? (
          <>
            <div className="info-card" style={{ marginBottom: '2rem' }}>
              <h3>👥 {squad.name}</h3>
              {squad.description && <p>{squad.description}</p>}
              <div className="squad-stats">
                <div className="stat-item">
                  <strong>{squad.member_count}/{squad.max_members}</strong>
                  <span>Members</span>
                </div>
                <div className="stat-item">
                  <strong>{squad.members.filter(m => m.is_leader).length}</strong>
                  <span>Leaders</span>
                </div>
              </div>
              <div className="members-preview">
                <p><strong>Current Members:</strong></p>
                {squad.members.slice(0, 5).map(member => (
                  <div key={member.id} className="member-chip">
                    {member.username} {member.is_leader && '👑'}
                  </div>
                ))}
                {squad.members.length > 5 && <span>+{squad.members.length - 5} more</span>}
              </div>
            </div>

            <button 
              className="btn-primary" 
              onClick={handleJoin}
              disabled={joining || squad.member_count >= squad.max_members}
            >
              {joining ? 'Joining...' : squad.member_count >= squad.max_members ? 'Squad is Full' : 'Join Squad'}
            </button>

            <div className="skip-link">
              <button onClick={() => navigate('/dashboard')}>
                Return to Dashboard
              </button>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <h3>Squad not found</h3>
            <button className="btn-primary" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default JoinSquadPage;
