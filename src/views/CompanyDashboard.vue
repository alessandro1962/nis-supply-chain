<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">Dashboard Azienda</h1>
            <span class="ml-4 text-sm text-gray-600">{{ currentUser?.company_name }}</span>
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
              <UserGroupIcon class="h-8 w-8 text-primary-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ dashboard.totalSuppliers }}</h3>
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
              <h3 class="text-lg font-medium text-gray-900">{{ dashboard.pendingAssessments }}</h3>
              <p class="text-sm text-gray-600">Assessment Pendenti</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ShieldCheckIcon class="h-8 w-8 text-success-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ dashboard.conformSuppliers }}</h3>
              <p class="text-sm text-gray-600">Fornitori Conformi</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ExclamationTriangleIcon class="h-8 w-8 text-danger-600" />
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">{{ dashboard.nonConformSuppliers }}</h3>
              <p class="text-sm text-gray-600">Fornitori Non Conformi</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Add New Supplier -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Aggiungi Nuovo Fornitore</h3>
          <form @submit.prevent="addSupplier" class="space-y-4">
            <div>
              <label class="form-label">Nome Azienda Fornitore</label>
              <input v-model="newSupplier.companyName" type="text" class="form-input" required>
            </div>
            <div>
              <label class="form-label">Email di Contatto</label>
              <input v-model="newSupplier.email" type="email" class="form-input" required>
            </div>
            <div>
              <label class="form-label">Settore</label>
              <select v-model="newSupplier.sector" class="form-select" required>
                <option value="">Seleziona settore</option>
                <option value="IT">Tecnologie Informatiche</option>
                <option value="Security">Servizi di Sicurezza</option>
                <option value="Consulting">Consulenza</option>
                <option value="Manufacturing">Manifatturiero</option>
                <option value="Logistics">Logistica</option>
                <option value="Other">Altro</option>
              </select>
            </div>
            <div>
              <label class="form-label">Paese</label>
              <input v-model="newSupplier.country" type="text" class="form-input" required>
            </div>
            <button type="submit" class="btn-primary w-full" :disabled="loading">
              {{ loading ? 'Aggiunta...' : 'Aggiungi Fornitore' }}
            </button>
          </form>
        </div>

        <!-- Quick Stats -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Riepilogo Conformità</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Tasso di Conformità</span>
              <span class="text-sm font-medium text-gray-900">{{ conformityRate }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-success-600 h-2 rounded-full" :style="{ width: conformityRate + '%' }"></div>
            </div>
            
            <div class="flex justify-between items-center pt-4">
              <span class="text-sm text-gray-600">Assessment Completati</span>
              <span class="text-sm font-medium text-gray-900">{{ dashboard.completedAssessments }}</span>
            </div>
            
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Media Punteggio</span>
              <span class="text-sm font-medium text-gray-900">{{ dashboard.averageScore }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Suppliers List -->
      <div class="card">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-medium text-gray-900">I Tuoi Fornitori</h3>
          <div class="flex space-x-2">
            <select v-model="statusFilter" class="form-select text-sm">
              <option value="">Tutti</option>
              <option value="pending">Assessment Pendenti</option>
              <option value="completed">Assessment Completati</option>
              <option value="conform">Conformi</option>
              <option value="non_conform">Non Conformi</option>
            </select>
            <button @click="loadSuppliers" class="btn-secondary">Aggiorna</button>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fornitore</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Settore</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status Assessment</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risultato</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aggiunto</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="supplier in filteredSuppliers" :key="supplier.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ supplier.company_name }}</div>
                    <div class="text-sm text-gray-500">{{ supplier.email }}</div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="badge-primary">{{ supplier.sector }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(supplier.assessment_status)">
                    {{ getStatusText(supplier.assessment_status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-if="supplier.latest_assessment">
                    <div class="text-sm font-medium" :class="getScoreColor(supplier.latest_assessment.final_score)">
                      {{ supplier.latest_assessment.final_score }}%
                    </div>
                    <div class="text-xs text-gray-500">{{ supplier.latest_assessment.result }}</div>
                  </div>
                  <span v-else class="text-sm text-gray-400">N/A</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(supplier.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button 
                    @click="generateQuestionnaireLink(supplier.id)" 
                    class="text-primary-600 hover:text-primary-900"
                    :disabled="supplier.assessment_status === 'completed'"
                  >
                    {{ supplier.assessment_status === 'pending' ? 'Genera Link' : 'Rigenera Link' }}
                  </button>
                  
                  <button 
                    v-if="supplier.latest_assessment" 
                    @click="viewAssessment(supplier.id)" 
                    class="text-success-600 hover:text-success-900"
                  >
                    Report
                  </button>
                  
                  <button 
                    v-if="supplier.results_url" 
                    @click="viewResults(supplier.results_url)" 
                    class="text-blue-600 hover:text-blue-900"
                  >
                    Visualizza Risultati
                  </button>
                  
                  <button 
                    v-if="supplier.latest_assessment?.result === 'CONFORME'" 
                    @click="downloadPassport(supplier.id)" 
                    class="text-success-600 hover:text-success-900"
                  >
                    Passaporto
                  </button>
                  
                  <button 
                    v-if="supplier.latest_assessment?.result === 'NON_CONFORME'" 
                    @click="downloadRecall(supplier.id)" 
                    class="text-danger-600 hover:text-danger-900"
                  >
                    Richiamo
                  </button>
                  
                  <button 
                    @click="deleteSupplier(supplier.id)" 
                    class="text-danger-600 hover:text-danger-900"
                  >
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  UserGroupIcon, 
  DocumentCheckIcon, 
  ShieldCheckIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/vue/24/outline'
import { companyAPI, downloadFile } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const suppliers = ref([])
const dashboard = ref({
  totalSuppliers: 0,
  pendingAssessments: 0,
  completedAssessments: 0,
  conformSuppliers: 0,
  nonConformSuppliers: 0,
  averageScore: 0
})

const statusFilter = ref('')

const newSupplier = ref({
  companyName: '',
  email: '',
  sector: '',
  country: ''
})

const currentUser = computed(() => authStore.user)

const conformityRate = computed(() => {
  if (dashboard.value.totalSuppliers === 0) return 0
  return Math.round((dashboard.value.conformSuppliers / dashboard.value.totalSuppliers) * 100)
})

const filteredSuppliers = computed(() => {
  if (!statusFilter.value) return suppliers.value
  
  return suppliers.value.filter(supplier => {
    switch (statusFilter.value) {
      case 'pending':
        return supplier.assessment_status === 'pending'
      case 'completed':
        return supplier.assessment_status === 'completed'
      case 'conform':
        return supplier.latest_assessment?.result === 'CONFORME'
      case 'non_conform':
        return supplier.latest_assessment?.result === 'NON_CONFORME'
      default:
        return true
    }
  })
})

// Lifecycle
onMounted(() => {
  loadDashboard()
  loadSuppliers()
})

// Methods
const loadDashboard = async () => {
  try {
    const response = await companyAPI.getDashboard()
    dashboard.value = response.data
  } catch (error) {
    console.error('Errore caricamento dashboard:', error)
  }
}

const loadSuppliers = async () => {
  try {
    const response = await companyAPI.getSuppliers()
    suppliers.value = response.data
  } catch (error) {
    console.error('Errore caricamento fornitori:', error)
  }
}

const addSupplier = async () => {
  loading.value = true
  try {
    await companyAPI.createSupplier({
      company_name: newSupplier.value.companyName,
      email: newSupplier.value.email,
      sector: newSupplier.value.sector,
      country: newSupplier.value.country
    })
    
    newSupplier.value = { companyName: '', email: '', sector: '', country: '' }
    await loadSuppliers()
    await loadDashboard()
  } catch (error) {
    console.error('Errore aggiunta fornitore:', error)
  } finally {
    loading.value = false
  }
}

const generateQuestionnaireLink = async (supplierId) => {
  try {
    const response = await companyAPI.generateQuestionnaireLink(supplierId)
    const questionnaireUrl = response.data.questionnaire_url
    
    // Copia il link negli appunti
    await navigator.clipboard.writeText(questionnaireUrl)
    alert(`Link del questionario generato e copiato negli appunti:\n${questionnaireUrl}`)
    
    await loadSuppliers()
  } catch (error) {
    console.error('Errore generazione link:', error)
    alert('Errore durante la generazione del link')
  }
}

const viewAssessment = (supplierId) => {
  router.push(`/company/suppliers/${supplierId}/assessment`)
}

const downloadPassport = async (supplierId) => {
  try {
    const response = await companyAPI.downloadPassport(supplierId)
    downloadFile(response.data, `passaporto-digitale-${supplierId}.pdf`)
  } catch (error) {
    console.error('Errore download passaporto:', error)
    alert('Errore durante il download del passaporto')
  }
}

const downloadRecall = async (supplierId) => {
  try {
    const response = await companyAPI.downloadRecall(supplierId)
    downloadFile(response.data, `report-richiamo-${supplierId}.pdf`)
  } catch (error) {
    console.error('Errore download richiamo:', error)
    alert('Errore durante il download del report di richiamo')
  }
}

const deleteSupplier = async (supplierId) => {
  if (!confirm('Sei sicuro di voler eliminare questo fornitore?')) return
  
  try {
    await companyAPI.deleteSupplier(supplierId)
    await loadSuppliers()
    await loadDashboard()
  } catch (error) {
    console.error('Errore eliminazione fornitore:', error)
    alert('Errore durante l\'eliminazione del fornitore')
  }
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'pending':
      return 'badge-warning'
    case 'in_progress':
      return 'badge-primary'
    case 'completed':
      return 'badge-success'
    default:
      return 'badge-primary'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending':
      return 'Pendente'
    case 'in_progress':
      return 'In Corso'
    case 'completed':
      return 'Completato'
    default:
      return 'Sconosciuto'
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return 'text-success-600'
  if (score >= 60) return 'text-warning-600'
  return 'text-danger-600'
}

const viewResults = (resultsUrl) => {
  // Apre la pagina dei risultati in una nuova finestra
  window.open(resultsUrl, '_blank')
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('it-IT')
}
</script> 