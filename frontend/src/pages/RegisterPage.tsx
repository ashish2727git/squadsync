import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'
import './RegisterPage.css'

export function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const checkPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++
    setPasswordStrength(strength)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
    if (name === 'password') {
      checkPasswordStrength(value)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    if (formData.password.length > 72) {
      setError('Password must be no more than 72 characters')
      return
    }

    if (passwordStrength < 3) {
      setError('Password is too weak. Use a mix of uppercase, lowercase, numbers, and special characters')
      return
    }

    setLoading(true)

    try {
      // Register
      console.log('Step 1: Registering user...')
      const registerResponse = await apiClient.post('/auth/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      })
      console.log('✅ Registration successful:', registerResponse.data)

      // Wait a moment for database commit
      await new Promise(resolve => setTimeout(resolve, 500))

      // Auto-login after registration
      console.log('Step 2: Logging in...')
      const loginResponse = await apiClient.post('/auth/login', {
        username: formData.username,
        password: formData.password,
      })
      console.log('✅ Login successful:', loginResponse.data)

      const { access_token, refresh_token } = loginResponse.data
      
      // Get user info
      console.log('Step 3: Fetching user info...')
      const userResponse = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      })
      console.log('✅ User info fetched:', userResponse.data)

      // Set auth state
      setAuth(access_token, refresh_token, userResponse.data)
      
      // Navigate to dashboard (skip onboarding for now)
      console.log('✅ Navigating to dashboard...')
      navigate('/dashboard')
    } catch (err: any) {
      console.error('❌ Registration error:', err)
      console.error('Error response:', err.response)
      console.error('Error data:', err.response?.data)
      
      // Better error messages
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Username or email already exists')
      } else if (err.response?.status === 401) {
        setError('Login failed after registration. Please try logging in manually.')
      } else {
        setError(err.response?.data?.detail || 'Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const getPasswordStrengthLabel = () => {
    if (passwordStrength === 0) return { text: '', color: '' }
    if (passwordStrength <= 2) return { text: 'Weak', color: '#ef4444' }
    if (passwordStrength === 3) return { text: 'Fair', color: '#f59e0b' }
    if (passwordStrength === 4) return { text: 'Good', color: '#10b981' }
    return { text: 'Strong', color: '#059669' }
  }

  const strengthLabel = getPasswordStrengthLabel()

  return (
    <div className="auth-page">
      <div className="auth-container fade-in">
        <div className="auth-header">
          <div className="logo-badge">
            <span className="logo-icon">🎮</span>
          </div>
          <h1>Join SquadSync</h1>
          <p>Create your account and start coordinating</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-banner">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              disabled={loading}
              minLength={3}
              maxLength={50}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password (8-72 characters)</label>
            <input
              id="password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              required
              disabled={loading}
              minLength={8}
              maxLength={72}
            />
            {formData.password && (
              <div className="password-strength">
                <div className="strength-bars">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <div
                      key={level}
                      className={`strength-bar ${level <= passwordStrength ? 'active' : ''}`}
                      style={{ backgroundColor: level <= passwordStrength ? strengthLabel.color : '#e5e7eb' }}
                    />
                  ))}
                </div>
                {strengthLabel.text && (
                  <span className="strength-label" style={{ color: strengthLabel.color }}>
                    {strengthLabel.text}
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? (
              <>
                <span className="loading"></span>
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <span>Create Account</span>
                <span>→</span>
              </>
            )}
          </button>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <div className="auth-footer">
            <p>Already have an account?</p>
            <Link to="/login" className="btn btn-secondary btn-full">
              Sign In
            </Link>
          </div>
        </form>

        <div className="auth-features">
          <div className="feature-item">
            <span className="feature-icon">✨</span>
            <span>Free Forever</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <span>Secure & Private</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <span>Instant Setup</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
