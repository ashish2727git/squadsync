import { createContext, useContext, useEffect, ReactNode } from 'react'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'

interface AuthContextType {
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const { refreshToken: refreshTokenValue, updateAccessToken } = useAuthStore()

  const refreshToken = async () => {
    if (!refreshTokenValue) return

    try {
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshTokenValue,
      })
      updateAccessToken(response.data.access_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      useAuthStore.getState().clearAuth()
    }
  }

  useEffect(() => {
    // Set up token refresh interceptor
    const interceptor = apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && refreshTokenValue) {
          await refreshToken()
          // Retry original request
          return apiClient.request(error.config)
        }
        return Promise.reject(error)
      }
    )

    return () => {
      apiClient.interceptors.response.eject(interceptor)
    }
  }, [refreshTokenValue])

  return (
    <AuthContext.Provider value={{ refreshToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
