import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCompany = computed(() => user.value?.role === 'company')
  const currentUserRole = computed(() => user.value?.role)

  // Actions
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await authAPI.login(credentials)
      const { access_token, refresh_token, user: userData } = response.data

      // Salva i token
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      // Persisti nel localStorage
      localStorage.setItem('authToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))

      return { success: true }
    } catch (error) {
      console.error('Errore durante il login:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Errore durante il login'
      }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    // Pulisci lo state
    user.value = null
    token.value = null
    refreshToken.value = null

    // Pulisci il localStorage
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  const refreshAuthToken = async () => {
    if (!refreshToken.value) {
      logout()
      return false
    }

    try {
      const response = await authAPI.refreshToken(refreshToken.value)
      const { access_token, refresh_token: newRefreshToken } = response.data

      token.value = access_token
      refreshToken.value = newRefreshToken

      localStorage.setItem('authToken', access_token)
      localStorage.setItem('refreshToken', newRefreshToken)

      return true
    } catch (error) {
      console.error('Errore refresh token:', error)
      logout()
      return false
    }
  }

  const loadUserFromStorage = () => {
    try {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    } catch (error) {
      console.error('Errore caricamento utente dal localStorage:', error)
      logout()
    }
  }

  const getCurrentUser = async () => {
    if (!token.value) return false

    try {
      const response = await authAPI.getCurrentUser()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return true
    } catch (error) {
      console.error('Errore caricamento utente corrente:', error)
      logout()
      return false
    }
  }

  const checkTokenValidity = async () => {
    if (!token.value) return false

    try {
      await authAPI.getCurrentUser()
      return true
    } catch (error) {
      if (error.response?.status === 401) {
        // Token scaduto, prova il refresh
        return await refreshAuthToken()
      }
      return false
    }
  }

  // Inizializza l'utente dal localStorage al caricamento
  if (token.value) {
    loadUserFromStorage()
  }

  return {
    // State
    user,
    token,
    refreshToken,
    loading,
    
    // Getters
    isAuthenticated,
    isAdmin,
    isCompany,
    currentUserRole,
    
    // Actions
    login,
    logout,
    refreshAuthToken,
    loadUserFromStorage,
    getCurrentUser,
    checkTokenValidity,
  }
}) 