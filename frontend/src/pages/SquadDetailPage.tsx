import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'
import { SummonModal } from '../components/SummonModal'
import './SquadDetailPage.css'

interface Summon {
  id: string
  title: string
  description?: string
  status: string
  created_at: string
  response_summary: {
    ACCEPT: number
    DECLINE: number
    MAYBE: number
    PENDING: number
  }
}

export function SquadDetailPage() {
  const { squadId } = useParams<{ squadId: string }>()
  const { user } = useAuthStore()
  const [summons, setSummons] = useState<Summon[]>([])
  const [activeSummon, setActiveSummon] = useState<Summon | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (squadId) {
      fetchSummons()
    }
  }, [squadId])

  const fetchSummons = async () => {
    try {
      const response = await apiClient.get(`/summons/squad/${squadId}`)
      setSummons(response.data.summons || [])
    } catch (error) {
      console.error('Failed to fetch summons:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="squad-detail-page">
      <header className="page-header">
        <Link to="/dashboard">← Back to Dashboard</Link>
        <h1>Squad Details</h1>
      </header>
      <main className="squad-detail-main">
        <div className="squad-actions">
          <Link to={`/squads/${squadId}/war-room`} className="war-room-btn">
            Enter War Room
          </Link>
        </div>
        <div className="summons-section">
          <h2>Active Summons</h2>
          {loading ? (
            <div>Loading...</div>
          ) : summons.length === 0 ? (
            <div className="empty-state">No active summons</div>
          ) : (
            <div className="summons-list">
              {summons.map((summon) => (
                <div
                  key={summon.id}
                  className="summon-item"
                  onClick={() => setActiveSummon(summon)}
                >
                  <h3>{summon.title}</h3>
                  {summon.description && <p>{summon.description}</p>}
                  <div className="summon-responses">
                    <span>✓ {summon.response_summary.ACCEPT}</span>
                    <span>✗ {summon.response_summary.DECLINE}</span>
                    <span>? {summon.response_summary.MAYBE}</span>
                    <span>⏳ {summon.response_summary.PENDING}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      {activeSummon && (
        <SummonModal
          summon={{
            id: activeSummon.id,
            title: activeSummon.title,
            description: activeSummon.description,
            expires_at: null,
          }}
          userId={user?.id || ''}
          apiBaseUrl={import.meta.env.VITE_API_URL || 'http://localhost:8000'}
          authToken={useAuthStore.getState().accessToken || ''}
          onResponseSubmitted={() => {
            setActiveSummon(null)
            fetchSummons()
          }}
        />
      )}
    </div>
  )
}
