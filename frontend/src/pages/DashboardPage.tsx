import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'
import './DashboardPage.css'

interface Squad {
  id: string
  name: string
  description?: string
  member_count: number
}

export function DashboardPage() {
  const { user } = useAuthStore()
  const [squads, setSquads] = useState<Squad[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch user's squads
    // For now, show placeholder
    setLoading(false)
  }, [])

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>SquadSync</h1>
        <div className="user-info">
          <span>{user?.username}</span>
          <button onClick={() => {
            useAuthStore.getState().clearAuth()
            window.location.href = '/login'
          }}>
            Logout
          </button>
        </div>
      </header>
      <main className="dashboard-main">
        <div className="dashboard-content">
          <h2>Your Squads</h2>
          {loading ? (
            <div>Loading...</div>
          ) : squads.length === 0 ? (
            <div className="empty-state">
              <p>You're not in any squads yet.</p>
            </div>
          ) : (
            <div className="squads-grid">
              {squads.map((squad) => (
                <Link key={squad.id} to={`/squads/${squad.id}`} className="squad-card">
                  <h3>{squad.name}</h3>
                  {squad.description && <p>{squad.description}</p>}
                  <div className="squad-meta">
                    <span>{squad.member_count} members</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
