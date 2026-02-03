import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProfilePage } from './pages/ProfilePage'
import { SquadDetailPage } from './pages/SquadDetailPage'
import { WarRoomPage } from './pages/WarRoomPage'
import { VaultPage } from './pages/VaultPage'
import { JoinSquadPage } from './pages/JoinSquadPage'
import { OnboardingPage } from './pages/OnboardingPage'
import { ErrorBoundary } from './components/ErrorBoundary'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        } />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } />
        <Route path="/squads/:squadId" element={
          <ProtectedRoute>
            <SquadDetailPage />
          </ProtectedRoute>
        } />
        <Route path="/squads/:squadId/war-room" element={
          <ProtectedRoute>
            <WarRoomPage />
          </ProtectedRoute>
        } />
        <Route path="/vault" element={
          <ProtectedRoute>
            <VaultPage />
          </ProtectedRoute>
        } />
        <Route path="/join/:squadId" element={
          <JoinSquadPage />
        } />
        <Route path="/onboarding" element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
        } />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
