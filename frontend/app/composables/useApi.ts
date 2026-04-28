export const useApi = () => {
  const config = useRuntimeConfig()
  
  // Dynamically determine the backend URL based on current host
  const getBaseUrl = () => {
    if (import.meta.server) return 'http://localhost:8000/v1'
    const hostname = window.location.hostname
    return `http://${hostname}:8000/v1`
  }
  
  const baseUrl = getBaseUrl()

  const request = async (endpoint: string, options: any = {}): Promise<any> => {
    const auth = useAuth()
    
    try {
      const res = await $fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          ...(auth.token.value ? { 'Authorization': `Bearer ${auth.token.value}` } : {})
        }
      })
      return res
    } catch (err: any) {
      const status = err.response?.status
      
      // Handle 401 Unauthorized by attempting a token refresh
      if (status === 401 && auth.refreshToken.value && !options._retry) {
        options._retry = true
        try {
          // Token refresh logic without logs
          // Call refresh endpoint directly with $fetch to avoid recursion
          const refreshRes: any = await $fetch(`${baseUrl}/users/refresh`, {
            method: 'POST',
            body: { refresh_token: auth.refreshToken.value }
          })
          
          if (refreshRes.dataPayload?.data?.access_token) {
            const newToken = refreshRes.dataPayload.data.access_token
            // Update auth state (only updates access_token, keeps user/refresh_token)
            auth.setUser(auth.user.value, newToken, auth.refreshToken.value)
            
            // Retry the original request with the new token
            return request(endpoint, {
              ...options,
              headers: {
                ...options.headers,
                'Authorization': `Bearer ${newToken}`
              }
            })
          }
        } catch (refreshErr) {
          console.error('Token refresh failed. Logging out.')
          auth.logout()
          throw refreshErr
        }
      }
      
      const errorMsg = err.message || 'Unknown API Error'
      console.error(`API Error (${endpoint}):`, { message: errorMsg, status })
      throw err
    }
  }

  return {
    request,
    get: (endpoint: string) => request(endpoint, { method: 'GET' }),
    post: (endpoint: string, body: any) => request(endpoint, { method: 'POST', body }),
    delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
    upload: (endpoint: string, formData: FormData) => request(endpoint, {
      method: 'POST',
      body: formData,
    })
  }
}
