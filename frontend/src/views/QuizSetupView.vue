<template>
  <div class="container" style="padding-top: 48px;">
    <div style="margin-bottom: 32px;">
      <RouterLink to="/" class="text-muted" style="font-size: 13px;">← Back</RouterLink>
      <h1 class="serif" style="margin-top: 12px;">Custom Quiz</h1>
      <p class="text-muted" style="margin-top: 4px;">Configure your quiz, then start the clock.</p>
    </div>

    <div class="card" style="max-width: 500px;">
      <!-- Subject -->
      <div style="margin-bottom: 20px;">
        <label>Subject</label>
        <select v-model="settings.subject_id" class="input" @change="onSubjectChange">
          <option value="">Select a subject...</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <!-- Category multi-select -->
      <div v-if="categories.length" style="margin-bottom: 20px;">
        <label>Categories</label>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <label v-for="c in categories" :key="c.id" style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: var(--text);">
            <input type="checkbox" :value="c.id" v-model="settings.category_ids" style="accent-color: var(--accent);" />
            {{ c.name }}
          </label>
        </div>
      </div>

      <!-- Question count -->
      <div style="margin-bottom: 20px;">
        <label>Number of questions</label>
        <input v-model.number="settings.question_count" type="number" class="input" min="5" max="100" />
      </div>

      <!-- Time limit -->
      <div style="margin-bottom: 28px;">
        <label>Time limit (minutes, 0 = no limit)</label>
        <input v-model.number="timeLimitMinutes" type="number" class="input" min="0" max="180" />
      </div>

      <button
        class="btn btn-primary"
        :disabled="!settings.subject_id || loading"
        @click="startQuiz"
      >
        {{ loading ? 'Creating quiz...' : 'Start Quiz →' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'

const router = useRouter()
const subjects = ref([])
const loading = ref(false)
const timeLimitMinutes = ref(0)

const settings = ref({
  subject_id: '',
  category_ids: [],
  question_count: 20,
  mode: 'custom_quiz',
})

const categories = computed(() => {
  const s = subjects.value.find(s => s.id === settings.value.subject_id)
  return s?.categories ?? []
})

function onSubjectChange() {
  settings.value.category_ids = []
}

async function startQuiz() {
  loading.value = true
  try {
    const payload = {
      ...settings.value,
      time_limit_seconds: timeLimitMinutes.value > 0 ? timeLimitMinutes.value * 60 : null,
      category_ids: settings.value.category_ids.length ? settings.value.category_ids : null,
    }
    const session = await api.createSession(payload)
    // Pass session data via router state (avoids extra API call)
    router.push({ name: 'QuizPlay', state: { session: JSON.stringify(session) } })
  } finally {
    loading.value = false
  }
}

import { onMounted } from 'vue'
onMounted(async () => {
  subjects.value = await api.getSubjects()
})
</script>
