<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">Dashboard Amministratore</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ currentUser?.email }}</span>
            <button @click="logout" class="btn-secondary">Logout</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <BuildingOfficeIcon class="h-8 w-8 text-primary-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ stats.totalCompanies }}</h3>
              <p class="text-sm text-gray-600">Aziende Registrate</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UserGroupIcon class="h-8 w-8 text-success-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ stats.totalSuppliers }}</h3>
              <p class="text-sm text-gray-600">Fornitori Totali</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <DocumentCheckIcon class="h-8 w-8 text-warning-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ stats.completedAssessments }}</h3>
              <p class="text-sm text-gray-600">Assessment Completati</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ShieldCheckIcon class="h-8 w-8 text-success-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ stats.conformSuppliers }}</h3>
              <p class="text-sm text-gray-600">Fornitori Conformi</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Create Company -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Crea Nuova Azienda</h3>
          <form @submit.prevent="createCompany" class="space-y-4">
            <div>
              <label class="form-label">Nome Azienda</label>
              <input v-model="newCompany.name" type="text" class="form-input" required>
            </div>
            <div>
              <label class="form-label">Email Amministratore</label>
              <input v-model="newCompany.adminEmail" type="email" class="form-input" required>
            </div>
            <div>
              <label class="form-label">Settore</label>
              <select v-model="newCompany.sector" class="form-select" required>
                <option value="">Seleziona settore</option>
                <option value="energy">Energia</option>
                <option value="transport">Trasporti</option>
                <option value="banking">Servizi Bancari</option>
                <option value="health">Sanità</option>
                <option value="water">Servizi Idrici</option>
                <option value="digital">Infrastrutture Digitali</option>
                <option value="public">Amministrazione Pubblica</option>
                <option value="space">Settore Spaziale</option>
              </select>
            </div>
            <button type="submit" class="btn-primary w-full" :disabled="loading">
              {{ loading ? 'Creazione...' : 'Crea Azienda' }}
            </button>
          </form>
        </div>

        <!-- Upload Manifest -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Gestione Questionario</h3>
          <div class="space-y-4">
            <div>
              <label class="form-label">Upload Manifest JSON</label>
              <input @change="handleFileUpload" type="file" accept=".json" class="form-input">
            </div>
            <button @click="uploadManifest" class="btn-primary w-full" :disabled="!selectedFile || loading">
              {{ loading ? 'Caricamento...' : 'Carica Manifest' }}
            </button>
            <div class="text-sm text-gray-600">
              <p>Il manifest contiene la struttura del questionario NIS2.</p>
              <p class="mt-1">Versione attuale: <span class="font-medium">{{ manifestVersion || 'Non caricato' }}</span></p>
            </div>
          </div>
        </div>
      </div>

      <!-- Companies List -->
      <div class="card">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-medium text-gray-900">Aziende Registrate</h3>
          <button @click="loadCompanies" class="btn-secondary">Aggiorna</button>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azienda</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Settore</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fornitori</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assessment</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Creata</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="company in companies" :key="company.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ company.name }}</div>
                    <div class="text-sm text-gray-500">{{ company.admin_email }}</div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="badge-primary">{{ company.sector }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ company.suppliers_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ company.assessments_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(company.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="viewCompany(company.id)" class="text-primary-600 hover:text-primary-900 mr-3">
                    Visualizza
                  </button>
                  <button @click="deleteCompany(company.id)" class="text-danger-600 hover:text-danger-900">
                    Elimina
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  DocumentCheckIcon, 
  ShieldCheckIcon 
} from '@heroicons/vue/24/outline'
import { apiClient } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const companies = ref([])
const stats = ref({
  totalCompanies: 0,
  totalSuppliers: 0,
  completedAssessments: 0,
  conformSuppliers: 0
})

const newCompany = ref({
  name: '',
  adminEmail: '',
  sector: ''
})

const selectedFile = ref(null)
const manifestVersion = ref('')

const currentUser = computed(() => authStore.user)

// Lifecycle
onMounted(() => {
  loadStats()
  loadCompanies()
  loadManifestInfo()
})

// Methods
const loadStats = async () => {
  try {
    const response = await apiClient.get('/admin/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Errore caricamento statistiche:', error)
  }
}

const loadCompanies = async () => {
  try {
    const response = await apiClient.get('/admin/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Errore caricamento aziende:', error)
  }
}

const loadManifestInfo = async () => {
  try {
    const response = await apiClient.get('/admin/manifest/info')
    manifestVersion.value = response.data.version
  } catch (error) {
    console.error('Errore caricamento info manifest:', error)
  }
}

const createCompany = async () => {
  loading.value = true
  try {
    await apiClient.post('/admin/companies', newCompany.value)
    newCompany.value = { name: '', adminEmail: '', sector: '' }
    await loadCompanies()
    await loadStats()
  } catch (error) {
    console.error('Errore creazione azienda:', error)
  } finally {
    loading.value = false
  }
}

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0]
}

const uploadManifest = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('manifest', selectedFile.value)
    
    await apiClient.post('/admin/manifest/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    selectedFile.value = null
    await loadManifestInfo()
  } catch (error) {
    console.error('Errore upload manifest:', error)
  } finally {
    loading.value = false
  }
}

const viewCompany = (id) => {
  router.push(`/admin/companies/${id}`)
}

const deleteCompany = async (id) => {
  if (!confirm('Sei sicuro di voler eliminare questa azienda?')) return
  
  try {
    await apiClient.delete(`/admin/companies/${id}`)
    await loadCompanies()
    await loadStats()
  } catch (error) {
    console.error('Errore eliminazione azienda:', error)
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('it-IT')
}
</script> 