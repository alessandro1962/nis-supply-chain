<script setup>
import { ref, reactive, onMounted } from 'vue'

// State
const isLoggedIn = ref(false)
const showLogin = ref(false)
const showCreateCompany = ref(false)
const showCreateSupplier = ref(false)
const currentUser = ref(null)
const stats = reactive({ companies: 0, suppliers: 0, assessments: 0 })
const companyStats = reactive({ suppliers: 0, compliant: 0, nonCompliant: 0 })
const companies = ref([])
const suppliers = ref([])

const loginForm = reactive({
  username: '',
  password: ''
})

// Methods
const login = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm)
    })
    
    if (response.ok) {
      const data = await response.json()
      currentUser.value = data.user
      isLoggedIn.value = true
      showLogin.value = false
      loadDashboardData()
    } else {
      alert('Login fallito')
    }
  } catch (error) {
    console.error('Login error:', error)
    alert('Errore di connessione')
  }
}

const logout = () => {
  currentUser.value = null
  isLoggedIn.value = false
}

const loadDashboardData = async () => {
  if (currentUser.value?.role === 'admin') {
    // Load admin stats
    try {
      const response = await fetch('http://localhost:8000/api/admin/stats')
      if (response.ok) {
        const data = await response.json()
        Object.assign(stats, data)
      }
    } catch (error) {
      console.error('Error loading admin stats:', error)
    }
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-800'
    case 'pending': return 'bg-yellow-100 text-yellow-800'
    case 'expired': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

onMounted(() => {
  // Check if user is already logged in
  const token = localStorage.getItem('token')
  if (token) {
    // Validate token and set user
    isLoggedIn.value = true
  }
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">🛡️ Piattaforma NIS2</h1>
            <span class="ml-2 text-sm text-gray-500">Supplier Assessment</span>
          </div>
          <div class="flex items-center space-x-4">
            <button v-if="!isLoggedIn" @click="showLogin = true" 
                    class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Login
            </button>
            <div v-else class="flex items-center space-x-2">
              <span class="text-sm text-gray-700">{{ currentUser?.username }}</span>
              <button @click="logout" class="text-red-600 hover:text-red-800">Logout</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Login Modal -->
      <div v-if="showLogin" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
          <h2 class="text-2xl font-bold mb-6">Login</h2>
          <form @submit.prevent="login">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <input v-model="loginForm.username" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input v-model="loginForm.password" type="password" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <div class="flex space-x-3">
              <button type="submit" class="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">
                Login
              </button>
              <button type="button" @click="showLogin = false" 
                      class="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400">
                Annulla
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div v-if="isLoggedIn">
        <!-- Admin Dashboard -->
        <div v-if="currentUser?.role === 'admin'" class="space-y-6">
          <div class="bg-white shadow rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Dashboard Amministratore</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-medium text-blue-900">Aziende Registrate</h3>
                <p class="text-2xl font-bold text-blue-600">{{ stats.companies || 0 }}</p>
              </div>
              <div class="bg-green-50 p-4 rounded-lg">
                <h3 class="font-medium text-green-900">Fornitori Totali</h3>
                <p class="text-2xl font-bold text-green-600">{{ stats.suppliers || 0 }}</p>
              </div>
              <div class="bg-purple-50 p-4 rounded-lg">
                <h3 class="font-medium text-purple-900">Assessment Completati</h3>
                <p class="text-2xl font-bold text-purple-600">{{ stats.assessments || 0 }}</p>
              </div>
            </div>
          </div>

          <!-- Gestione Aziende -->
          <div class="bg-white shadow rounded-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold">Gestione Aziende</h2>
              <button @click="showCreateCompany = true" 
                      class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
                Nuova Azienda
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azienda</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Settore</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="company in companies" :key="company.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ company.ragione_sociale }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ company.email }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ company.tipo_soggetto }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button class="text-blue-600 hover:text-blue-900">Visualizza</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Company Dashboard -->
        <div v-else-if="currentUser?.role === 'company'" class="space-y-6">
          <div class="bg-white shadow rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Dashboard Azienda</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-medium text-blue-900">Fornitori</h3>
                <p class="text-2xl font-bold text-blue-600">{{ companyStats.suppliers || 0 }}</p>
              </div>
              <div class="bg-green-50 p-4 rounded-lg">
                <h3 class="font-medium text-green-900">Conformi</h3>
                <p class="text-2xl font-bold text-green-600">{{ companyStats.compliant || 0 }}</p>
              </div>
              <div class="bg-red-50 p-4 rounded-lg">
                <h3 class="font-medium text-red-900">Non Conformi</h3>
                <p class="text-2xl font-bold text-red-600">{{ companyStats.nonCompliant || 0 }}</p>
              </div>
            </div>
          </div>

          <!-- Gestione Fornitori -->
          <div class="bg-white shadow rounded-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold">Gestione Fornitori</h2>
              <button @click="showCreateSupplier = true" 
                      class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
                Nuovo Fornitore
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fornitore</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stato</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="supplier in suppliers" :key="supplier.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ supplier.ragione_sociale }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ supplier.email }}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="getStatusClass(supplier.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                        {{ supplier.status }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button class="text-blue-600 hover:text-blue-900 mr-2">Questionario</button>
                      <button class="text-green-600 hover:text-green-900">PDF</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Welcome Screen -->
      <div v-else class="text-center py-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">🛡️ Piattaforma NIS2 Supplier Assessment</h1>
        <p class="text-xl text-gray-600 mb-8">Valutazione conformità fornitori secondo Direttiva NIS2</p>
        <button @click="showLogin = true" 
                class="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-blue-700">
          Accedi alla Piattaforma
        </button>
      </div>
    </main>
  </div>
</template>

<style>
@import './style.css';
</style>
