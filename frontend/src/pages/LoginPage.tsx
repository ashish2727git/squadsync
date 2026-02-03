import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'
import './LoginPage.css'

export function LoginPage() {
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await apiClient.post('/auth/login', formData)
      const { access_token, refresh_token } = res.data
      const userRes = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      })
      setAuth(access_token, refresh_token, userRes.data)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* Animated Background */}
      <div className="login-bg">
        <div className="bg-grid"></div>
        <div className="bg-glow bg-glow-1"></div>
        <div className="bg-glow bg-glow-2"></div>
        <div className="bg-glow bg-glow-3"></div>
        <div className="particles">
          {[...Array(20)].map((_, i) => (
            <div key={i} className="particle" style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${10 + Math.random() * 20}s`
            }}></div>
          ))}
        </div>
      </div>

      <div className="login-container fade-in">
        {/* Logo & Branding */}
        <div className="login-header">
          <div className="logo-3d">
            <div className="logo-inner">
              <span>⚔️</span>
            </div>
            <div className="logo-ring"></div>
          </div>
          <h1 className="title-glow">SQUADSYNC</h1>
          <p className="subtitle">Rally Your Squad. Dominate Together.</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-box">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="input-group">
            <label>USERNAME OR EMAIL</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your username"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="input-group">
            <label>PASSWORD</label>
            <div className="input-wrapper">
              <span className="input-icon">🔒</span>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
                disabled={loading}
              />
            </div>
          </div>

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                <span>CONNECTING...</span>
              </>
            ) : (
              <>
                <span>ENTER THE ARENA</span>
                <span className="btn-arrow">→</span>
              </>
            )}
          </button>

          <div className="divider">
            <span>NEW PLAYER?</span>
          </div>

          <Link to="/register" className="btn-register">
            CREATE ACCOUNT
          </Link>
        </form>

        {/* Features */}
        <div className="features">
          <div className="feature">
            <span className="feature-icon">⚡</span>
            <span>Real-time</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🎯</span>
            <span>Summons</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🎙️</span>
            <span>Voice</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🎨</span>
            <span>Whiteboard</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
