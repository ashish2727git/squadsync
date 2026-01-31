import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { squadAPI } from '../api/services';
import './OnboardingPage.css';

export function OnboardingPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    squad_name: '',
    squad_description: '',
    game_title: 'General',
    max_members: 10,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await squadAPI.quickCreate(formData);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Failed to create squad:', err);
      setError(err.response?.data?.detail || 'Failed to create squad. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-page">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <h1>Create Your First Squad</h1>
          <p>Set up your gaming squad in seconds</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit} className="step-content">
          <div className="form-group">
            <label>Squad Name *</label>
            <input
              type="text"
              value={formData.squad_name}
              onChange={(e) => setFormData({ ...formData, squad_name: e.target.value })}
              placeholder="e.g., Alpha Squad"
              required
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label>Game</label>
            <input
              type="text"
              value={formData.game_title}
              onChange={(e) => setFormData({ ...formData, game_title: e.target.value })}
              placeholder="e.g., Valorant, Fortnite"
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.squad_description}
              onChange={(e) => setFormData({ ...formData, squad_description: e.target.value })}
              placeholder="Describe your squad..."
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label>Max Members</label>
            <input
              type="number"
              value={formData.max_members}
              onChange={(e) => setFormData({ ...formData, max_members: parseInt(e.target.value) || 10 })}
              min="2"
              max="50"
              disabled={loading}
            />
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Squad'}
          </button>
        </form>

        <div className="skip-link">
          <button onClick={() => navigate('/dashboard')} disabled={loading}>
            Skip for now
          </button>
        </div>
      </div>
    </div>
  );
}

export default OnboardingPage;
