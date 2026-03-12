<template>
  <div class="container" style="padding-top: 32px; padding-bottom: 64px;">
    <!-- Header: progress + timer -->
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 8px;">
      <span class="text-muted mono" style="font-size: 13px;">{{ currentIndex + 1 }} / {{ questions.length }}</span>
      <div class="progress-bar" style="flex: 1;">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <span v-if="timeLeft !== null" :class="['mono', timeLeft < 60 ? 'text-red' : 'text-muted']" style="font-size: 13px; min-width: 40px; text-align: right;">
        {{ formatTime(timeLeft) }}
      </span>
    </div>

    <!-- Question card -->
    <div v-if="currentQuestion" class="card" style="margin-top: 24px;">
      <div class="text-muted mono" style="font-size: 12px; margin-bottom: 12px;">
        Otázka {{ currentQuestion.question_number }}
        <span v-if="currentQuestion.type === 'multiple_correct'" style="margin-left: 8px;" class="badge badge-gray">
          multiple correct
        </span>
      </div>

      <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 24px;">
        {{ currentQuestion.question_text }}
      </p>

      <!-- Options -->
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <button
          v-for="(text, key) in currentQuestion.options"
          :key="key"
          :class="['option-btn', optionClass(key)]"
          :disabled="revealed"
          @click="toggleOption(key)"
        >
          <span class="option-key">{{ key }}</span>
          <span>{{ text }}</span>
        </button>
      </div>

      <!-- Result feedback -->
      <div v-if="revealed" style="margin-top: 20px; padding: 14px; border-radius: var(--radius); background: var(--bg-surface);">
        <span v-if="lastIsCorrect" class="text-accent" style="font-weight: 600;">✓ Correct!</span>
        <span v-else class="text-red" style="font-weight: 600;">✗ Incorrect</span>
        <span v-if="!lastIsCorrect" class="text-muted" style="font-size: 13px; margin-left: 8px;">
          Correct: {{ correctOptions.join(', ') }}
        </span>
      </div>
    </div>

    <!-- Action buttons -->
    <div v-if="currentQuestion" style="margin-top: 20px; display: flex; gap: 12px;">
      <button
        v-if="!revealed"
        class="btn btn-primary"
        :disabled="selectedOptions.length === 0"
        @click="submitAnswer"
      >
        Submit Answer
      </button>
      <button
        v-if="revealed && currentIndex < questions.length - 1"
        class="btn btn-primary"
        @click="nextQuestion"
      >
        Next →
      </button>
      <button
        v-if="revealed && currentIndex === questions.length - 1"
        class="btn btn-primary"
        @click="finishQuiz"
      >
        Finish Quiz ✓
      </button>
    </div>

    <!-- Finished state -->
    <div v-if="finished" class="card" style="margin-top: 32px; text-align: center; padding: 40px;">
      <div class="serif" style="font-size: 3rem; margin-bottom: 8px;">{{ score }}/{{ questions.length }}</div>
      <div :class="scoreClass" style="font-size: 1.1rem; margin-bottom: 24px;">{{ pct }}% — {{ scoreLabel }}</div>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <RouterLink to="/quiz" class="btn btn-primary">New Quiz</RouterLink>
        <RouterLink to="/history" class="btn btn-ghost">View History</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'

const router = useRouter()

// Parse session data passed from QuizSetupView
const sessionData = JSON.parse(history.state?.session ?? 'null')
if (!sessionData) { router.push('/quiz') }

const sessionId = ref(sessionData?.session_id)
const questions = ref(sessionData?.questions ?? [])
const settings = ref(sessionData?.settings ?? {})

const currentIndex = ref(0)
const selectedOptions = ref([])
const revealed = ref(false)
const correctOptions = ref([])
const lastIsCorrect = ref(false)
const score = ref(0)
const finished = ref(false)
const timeLeft = ref(settings.value.time_limit_seconds ?? null)

let timer = null

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => ((currentIndex.value) / questions.value.length) * 100)

function optionClass(key) {
  if (!revealed.value) {
    return selectedOptions.value.includes(key) ? 'selected' : ''
  }
  const isCorrect = correctOptions.value.includes(key)
  const isSelected = selectedOptions.value.includes(key)
  if (isCorrect) return 'correct'
  if (isSelected && !isCorrect) return 'wrong'
  return ''
}

function toggleOption(key) {
  const i = selectedOptions.value.indexOf(key)
  if (i === -1) selectedOptions.value.push(key)
  else selectedOptions.value.splice(i, 1)
}

async function submitAnswer() {
  const result = await api.submitAnswer(sessionId.value, {
    question_id: currentQuestion.value.id,
    selected_options: selectedOptions.value,
  })
  correctOptions.value = result.correct_options
  lastIsCorrect.value = result.is_correct
  if (result.is_correct) score.value++
  revealed.value = true
}

function nextQuestion() {
  currentIndex.value++
  selectedOptions.value = []
  revealed.value = false
  correctOptions.value = []
}

async function finishQuiz() {
  clearInterval(timer)
  const timeSpent = settings.value.time_limit_seconds
    ? settings.value.time_limit_seconds - (timeLeft.value ?? 0)
    : null
  await api.completeSession(sessionId.value, { time_spent_secs: timeSpent })
  finished.value = true
}

// Timer
function formatTime(secs) {
  const m = Math.floor(secs / 60)
  const s = secs % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

const pct = computed(() => Math.round((score.value / questions.value.length) * 100))
const scoreClass = computed(() => pct.value >= 70 ? 'text-accent' : pct.value >= 50 ? '' : 'text-red')
const scoreLabel = computed(() => pct.value >= 80 ? 'Excellent!' : pct.value >= 60 ? 'Good job' : 'Keep studying')

onMounted(() => {
  if (timeLeft.value !== null) {
    timer = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) {
        clearInterval(timer)
        finishQuiz()
      }
    }, 1000)
  }
})

onBeforeUnmount(() => clearInterval(timer))
</script>
