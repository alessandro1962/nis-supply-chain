<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header Mobile-First -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-lg font-semibold text-gray-900">Questionario NIS2</h1>
            <p class="text-sm text-gray-600">{{ supplierInfo?.company_name }}</p>
          </div>
          <div class="text-right">
            <div class="text-sm font-medium text-primary-600">
              {{ currentSection + 1 }} / {{ questionnaire.length }}
            </div>
            <div class="text-xs text-gray-500">Sezioni</div>
          </div>
        </div>
        
        <!-- Progress Bar -->
        <div class="mt-4">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                 :style="{ width: progressPercentage + '%' }"></div>
          </div>
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>Progresso: {{ progressPercentage }}%</span>
            <span>{{ answeredQuestions }} / {{ totalQuestions }} domande</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-6">
      <!-- Welcome Screen -->
      <div v-if="showWelcome" class="text-center py-12">
        <div class="mb-8">
          <ShieldCheckIcon class="mx-auto h-24 w-24 text-primary-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          Benvenuto nel Questionario NIS2
        </h2>
        <p class="text-gray-600 mb-8 max-w-2xl mx-auto">
          Questo questionario valuterà la conformità della tua azienda alla Direttiva NIS2. 
          Il completamento richiede circa 30-45 minuti. Puoi salvare i progressi e continuare in seguito.
        </p>
        
        <!-- Supplier Info -->
        <div class="card max-w-md mx-auto mb-8">
          <h3 class="font-medium text-gray-900 mb-4">Informazioni Azienda</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Azienda:</span>
              <span class="font-medium">{{ supplierInfo?.company_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Settore:</span>
              <span class="font-medium">{{ supplierInfo?.sector }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Paese:</span>
              <span class="font-medium">{{ supplierInfo?.country }}</span>
            </div>
          </div>
        </div>

        <button @click="startQuestionnaire" class="btn-primary text-lg px-8 py-3">
          Inizia Questionario
        </button>
      </div>

      <!-- Questionnaire Content -->
      <div v-else-if="!loading && questionnaire.length > 0">
        <!-- Section Header -->
        <div class="card mb-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h2 class="text-xl font-semibold text-gray-900">
                {{ currentSectionData.codice_argomento }} - {{ currentSectionData.titolo_argomento }}
              </h2>
              <p class="text-sm text-gray-600 mt-2">
                Domanda {{ currentQuestionIndex + 1 }} di {{ currentSectionData.questions.length }}
              </p>
            </div>
            <button @click="saveProgress" class="btn-secondary text-sm" :disabled="saving">
              {{ saving ? 'Salvataggio...' : 'Salva Progresso' }}
            </button>
          </div>

          <!-- Current Question -->
          <div class="current-question">
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">
                {{ currentQuestion.testo_domanda }}
              </h3>

              <!-- Answer Options -->
              <div class="space-y-3">
                <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                       :class="{ 'border-primary-500 bg-primary-50': currentAnswer === 'SÌ' }">
                  <input type="radio" 
                         :value="'SÌ'" 
                         v-model="currentAnswer" 
                         class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300">
                  <span class="ml-3 text-gray-900 font-medium">SÌ</span>
                </label>

                <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                       :class="{ 'border-danger-500 bg-danger-50': currentAnswer === 'NO' }">
                  <input type="radio" 
                         :value="'NO'" 
                         v-model="currentAnswer" 
                         class="h-4 w-4 text-danger-600 focus:ring-danger-500 border-gray-300">
                  <span class="ml-3 text-gray-900 font-medium">NO</span>
                </label>

                <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                       :class="{ 'border-gray-500 bg-gray-50': currentAnswer === 'NON_APPLICABILE' }">
                  <input type="radio" 
                         :value="'NON_APPLICABILE'" 
                         v-model="currentAnswer" 
                         class="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300">
                  <span class="ml-3 text-gray-900 font-medium">Non Applicabile</span>
                </label>
              </div>

              <!-- Help Text -->
              <div v-if="currentAnswer" class="mt-4 p-4 rounded-lg" 
                   :class="currentAnswer === 'SÌ' ? 'bg-success-50 border border-success-200' : 'bg-warning-50 border border-warning-200'">
                <p class="text-sm" :class="currentAnswer === 'SÌ' ? 'text-success-800' : 'text-warning-800'">
                  {{ currentAnswer === 'SÌ' ? currentQuestion.se_si : currentQuestion.se_no }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-between items-center">
          <button @click="previousQuestion" 
                  :disabled="isFirstQuestion" 
                  class="btn-secondary"
                  :class="{ 'opacity-50 cursor-not-allowed': isFirstQuestion }">
            ← Precedente
          </button>

          <div class="flex space-x-2">
            <button v-if="!isLastQuestion" 
                    @click="nextQuestion" 
                    :disabled="!currentAnswer"
                    class="btn-primary"
                    :class="{ 'opacity-50 cursor-not-allowed': !currentAnswer }">
              Successiva →
            </button>

            <button v-else 
                    @click="completeQuestionnaire" 
                    :disabled="!currentAnswer || completing"
                    class="btn-success px-6"
                    :class="{ 'opacity-50 cursor-not-allowed': !currentAnswer || completing }">
              {{ completing ? 'Finalizzazione...' : 'Completa Questionario' }}
            </button>
          </div>
        </div>

        <!-- Section Navigation (Mobile Swipe Indicator) -->
        <div class="mt-8 flex justify-center space-x-2">
          <div v-for="(section, index) in questionnaire" :key="section.codice_argomento"
               class="w-3 h-3 rounded-full"
               :class="index === currentSection ? 'bg-primary-600' : 'bg-gray-300'">
          </div>
        </div>
      </div>

      <!-- Completion Screen -->
      <div v-else-if="completed" class="text-center py-12">
        <div class="mb-8">
          <CheckCircleIcon class="mx-auto h-24 w-24 text-success-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          Questionario Completato!
        </h2>
        <p class="text-gray-600 mb-8 max-w-2xl mx-auto">
          Grazie per aver completato il questionario NIS2. La tua valutazione è stata inviata e 
          riceverai i risultati via email entro 24 ore.
        </p>
        
        <div class="card max-w-md mx-auto">
          <h3 class="font-medium text-gray-900 mb-4">Riepilogo</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Domande risposte:</span>
              <span class="font-medium">{{ answeredQuestions }} / {{ totalQuestions }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Completamento:</span>
              <span class="font-medium">{{ progressPercentage }}%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Data completamento:</span>
              <span class="font-medium">{{ new Date().toLocaleDateString('it-IT') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Caricamento questionario...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="mb-8">
          <ExclamationTriangleIcon class="mx-auto h-24 w-24 text-danger-600" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-4">Errore</h2>
        <p class="text-gray-600 mb-8">{{ error }}</p>
        <button @click="loadQuestionnaire" class="btn-primary">Riprova</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { 
  ShieldCheckIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/vue/24/outline'
import { supplierAPI } from '../services/api'

const route = useRoute()

const loading = ref(true)
const saving = ref(false)
const completing = ref(false)
const error = ref('')
const showWelcome = ref(true)
const completed = ref(false)

const supplierInfo = ref(null)
const questionnaire = ref([])
const answers = ref({})

const currentSection = ref(0)
const currentQuestionIndex = ref(0)

// Computed
const currentSectionData = computed(() => questionnaire.value[currentSection.value] || {})
const currentQuestion = computed(() => currentSectionData.value.questions?.[currentQuestionIndex.value] || {})
const currentQuestionId = computed(() => currentQuestion.value.numero_domanda)

const currentAnswer = computed({
  get() {
    const sectionCode = currentSectionData.value.codice_argomento
    return answers.value[sectionCode]?.[currentQuestionId.value]
  },
  set(value) {
    const sectionCode = currentSectionData.value.codice_argomento
    if (!answers.value[sectionCode]) {
      answers.value[sectionCode] = {}
    }
    answers.value[sectionCode][currentQuestionId.value] = value
  }
})

const totalQuestions = computed(() => {
  return questionnaire.value.reduce((total, section) => total + section.questions.length, 0)
})

const answeredQuestions = computed(() => {
  let count = 0
  for (const section of questionnaire.value) {
    const sectionAnswers = answers.value[section.codice_argomento] || {}
    count += Object.keys(sectionAnswers).length
  }
  return count
})

const progressPercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((answeredQuestions.value / totalQuestions.value) * 100)
})

const isFirstQuestion = computed(() => {
  return currentSection.value === 0 && currentQuestionIndex.value === 0
})

const isLastQuestion = computed(() => {
  const lastSection = questionnaire.value.length - 1
  const lastQuestion = questionnaire.value[lastSection]?.questions?.length - 1 || 0
  return currentSection.value === lastSection && currentQuestionIndex.value === lastQuestion
})

// Lifecycle
onMounted(() => {
  loadQuestionnaire()
})

// Watch for auto-save
watch(answers, () => {
  if (!showWelcome.value && !completed.value) {
    autoSave()
  }
}, { deep: true })

// Methods
const loadQuestionnaire = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const hash = route.params.hash
    const response = await supplierAPI.getQuestionnaire(hash)
    
    supplierInfo.value = response.data.supplier
    questionnaire.value = response.data.questionnaire
    
    // Load existing progress
    try {
      const progressResponse = await supplierAPI.getQuestionnaireProgress(hash)
      if (progressResponse.data.answers) {
        answers.value = progressResponse.data.answers
        showWelcome.value = false
      }
    } catch (progressError) {
      // No existing progress, start fresh
      console.log('No existing progress found')
    }
    
  } catch (err) {
    error.value = 'Errore nel caricamento del questionario. Verifica che il link sia corretto.'
    console.error('Error loading questionnaire:', err)
  } finally {
    loading.value = false
  }
}

const startQuestionnaire = () => {
  showWelcome.value = false
}

const nextQuestion = () => {
  if (!currentAnswer.value) return

  const currentSectionQuestions = currentSectionData.value.questions.length
  
  if (currentQuestionIndex.value < currentSectionQuestions - 1) {
    currentQuestionIndex.value++
  } else if (currentSection.value < questionnaire.value.length - 1) {
    currentSection.value++
    currentQuestionIndex.value = 0
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  } else if (currentSection.value > 0) {
    currentSection.value--
    const previousSectionQuestions = questionnaire.value[currentSection.value].questions.length
    currentQuestionIndex.value = previousSectionQuestions - 1
  }
}

let autoSaveTimeout = null
const autoSave = () => {
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  autoSaveTimeout = setTimeout(() => {
    saveProgress()
  }, 3000) // Auto-save dopo 3 secondi di inattività
}

const saveProgress = async () => {
  if (saving.value) return
  
  saving.value = true
  try {
    const hash = route.params.hash
    await supplierAPI.saveProgress(hash, answers.value)
  } catch (err) {
    console.error('Error saving progress:', err)
  } finally {
    saving.value = false
  }
}

const completeQuestionnaire = async () => {
  if (completing.value) return
  
  completing.value = true
  try {
    const hash = route.params.hash
    
    // Final save
    await supplierAPI.submitAnswers(hash, answers.value)
    await supplierAPI.completeQuestionnaire(hash)
    
    completed.value = true
  } catch (err) {
    error.value = 'Errore nel completamento del questionario. Riprova.'
    console.error('Error completing questionnaire:', err)
  } finally {
    completing.value = false
  }
}
</script>

<style scoped>
/* Mobile-first responsive adjustments */
@media (max-width: 640px) {
  .card {
    margin: 0 -1rem;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
  
  .current-question h3 {
    font-size: 1.1rem;
    line-height: 1.5;
  }
}

/* Custom radio button styling */
input[type="radio"]:checked {
  background-color: currentColor;
  border-color: transparent;
}

/* Animation for progress bar */
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style> 