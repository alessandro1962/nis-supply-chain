import axios from 'axios'
import { useAuthStore } from '../stores/auth'

// Base URL del backend API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Crea l'istanza Axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor per aggiungere automaticamente il token di autenticazione
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor per gestire le risposte e gli errori
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const authStore = useAuthStore()
    
    // Se ricevo 401 Unauthorized, il token è scaduto
    if (error.response?.status === 401) {
      authStore.logout()
      window.location.href = '/login'
    }
    
    // Log dell'errore per debugging
    console.error('API Error:', {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      url: error.config?.url,
    })
    
    return Promise.reject(error)
  }
)

// Servizi API specifici
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  refreshToken: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  getCurrentUser: () => apiClient.get('/auth/me'),
}

export const adminAPI = {
  // Statistiche globali
  getStats: () => apiClient.get('/admin/stats'),
  
  // Gestione aziende
  getCompanies: () => apiClient.get('/admin/companies'),
  createCompany: (companyData) => apiClient.post('/admin/companies', companyData),
  getCompany: (id) => apiClient.get(`/admin/companies/${id}`),
  deleteCompany: (id) => apiClient.delete(`/admin/companies/${id}`),
  
  // Gestione fornitori globale
  getAllSuppliers: () => apiClient.get('/admin/suppliers'),
  getSupplier: (id) => apiClient.get(`/admin/suppliers/${id}`),
  
  // Gestione manifest questionario
  getManifestInfo: () => apiClient.get('/admin/manifest/info'),
  uploadManifest: (file) => {
    const formData = new FormData()
    formData.append('manifest', file)
    return apiClient.post('/admin/manifest/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

export const companyAPI = {
  // Dashboard azienda
  getDashboard: () => apiClient.get('/company/dashboard'),
  
  // Gestione fornitori
  getSuppliers: () => apiClient.get('/company/suppliers'),
  createSupplier: (supplierData) => apiClient.post('/company/suppliers', supplierData),
  getSupplier: (id) => apiClient.get(`/company/suppliers/${id}`),
  updateSupplier: (id, supplierData) => apiClient.put(`/company/suppliers/${id}`, supplierData),
  deleteSupplier: (id) => apiClient.delete(`/company/suppliers/${id}`),
  
  // Gestione questionari
  generateQuestionnaireLink: (supplierId) => apiClient.post(`/company/suppliers/${supplierId}/questionnaire`),
  getAssessmentReport: (supplierId) => apiClient.get(`/company/suppliers/${supplierId}/assessment`),
  downloadPassport: (supplierId) => apiClient.get(`/company/suppliers/${supplierId}/download-passport`, { responseType: 'blob' }),
  downloadRecall: (supplierId) => apiClient.get(`/company/suppliers/${supplierId}/download-recall`, { responseType: 'blob' }),
}

export const supplierAPI = {
  // Accesso questionario tramite hash
  getQuestionnaire: (hash) => apiClient.get(`/supplier/questionnaire/${hash}`),
  getQuestionnaireProgress: (hash) => apiClient.get(`/supplier/questionnaire/${hash}/progress`),
  
  // Invio risposte
  submitAnswers: (hash, answers) => apiClient.post(`/supplier/questionnaire/${hash}/submit`, { answers }),
  saveProgress: (hash, answers) => apiClient.post(`/supplier/questionnaire/${hash}/save`, { answers }),
  
  // Finalizzazione
  completeQuestionnaire: (hash) => apiClient.post(`/supplier/questionnaire/${hash}/complete`),
}

export const publicAPI = {
  // Verifica pubblica via QR code
  verifyAssessment: (hash) => apiClient.get(`/v/${hash}`),
}

// Esporta il client principale
export { apiClient }

// Utility per gestire i download di file
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Utility per formattare errori API
export const formatAPIError = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'Si è verificato un errore imprevisto'
} 