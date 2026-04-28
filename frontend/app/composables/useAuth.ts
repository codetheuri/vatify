import { ref, computed } from 'vue'


export const useAuth = () => {
  const user = useState<any | null>('auth_user', () => null)
  const token = useState<string | null>('auth_token', () => null)
  const refreshToken = useState<string | null>('auth_refresh_token', () => null)
  const mfaEmail = useState<string | null>('mfa_email', () => null)

  const setUser = (userData: any, accessToken: string, newRefreshToken?: string) => {
    user.value = userData
    token.value = accessToken
    if (newRefreshToken) refreshToken.value = newRefreshToken

    if (import.meta.client) {
      localStorage.setItem('vatify_user', JSON.stringify(userData))
      localStorage.setItem('vatify_token', accessToken)
      if (newRefreshToken) localStorage.setItem('vatify_refresh_token', newRefreshToken)
    }
  }

  const logout = () => {
    // Fire and forget logout call to backend if we have a token
    if (token.value) {
      const api = useApi()
      api.post('/users/logout', {}).catch(() => {})
    }
    
    user.value = null
    token.value = null
    refreshToken.value = null

    if (import.meta.client) {
      localStorage.removeItem('vatify_user')
      localStorage.removeItem('vatify_token')
      localStorage.removeItem('vatify_refresh_token')
    }
    
    navigateTo('/login')
  }

  // Initialize from localStorage on client side
  if (import.meta.client) {
    const savedUser = localStorage.getItem('vatify_user')
    const savedToken = localStorage.getItem('vatify_token')
    const savedRefresh = localStorage.getItem('vatify_refresh_token')

    if (savedUser && savedToken) {
      try {
        user.value = JSON.parse(savedUser)
        token.value = savedToken
        refreshToken.value = savedRefresh
      } catch (e) {
        console.error('Failed to parse saved user', e)
      }
    }
  }

  return {
    user,
    token,
    refreshToken,
    mfaEmail,
    setUser,
    logout,
    isAuthenticated: computed(() => !!token.value)
  }
}
