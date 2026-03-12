<template>
  <div class="container" style="padding-top: 48px; padding-bottom: 64px;">

    <!-- Header -->
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px;">
      <div>
        <h1 class="serif" style="margin-bottom: 6px;">History</h1>
        <p class="text-muted">Your past quiz attempts.</p>
      </div>
      <button v-if="sessions.length && !confirmClear" class="btn btn-danger" @click="confirmClear = true">
        Clear all
      </button>
    </div>

    <!-- Confirmation -->
    <div v-if="confirmClear" class="card" style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
      <span class="text-muted" style="font-size: 14px;">Delete all quiz history? This cannot be undone.</span>
      <div style="display: flex; gap: 8px; flex-shrink: 0;">
        <button class="btn btn-danger" @click="clearHistory">Yes, delete all</button>
        <button class="btn btn-ghost" @click="confirmClear = false">Cancel</button>
      </div>
    </div>

    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-else-if="sessions.length === 0" class="text-muted">No quizzes yet. <RouterLink to="/quiz">Start one!</RouterLink></div>
    <div v-else style="display: flex; flex-direction: column; gap: 10px;">
      <RouterLink
        v-for="s in sessions"
        :key="s.id"
        :to="`/history/${s.id}`"
        class="session-row card"
      >
        <div>
          <div class="text-muted mono" style="font-size: 12px;">{{ formatDate(s.completed_at) }}</div>
          <div style="margin-top: 2px;">{{ s.subjects?.name ?? 'Quiz' }}</div>
          <div class="text-muted" style="font-size: 13px;">{{ s.mode === 'review' ? 'Review' : 'Custom Quiz' }}</div>
        </div>
        <div style="text-align: right;">
          <div :class="scoreClass(s.score, s.total_questions)" style="font-size: 1.2rem; font-weight: 600;">
            {{ s.score }}/{{ s.total_questions }}
          </div>
          <div class="text-muted mono" style="font-size: 12px;">{{ pct(s.score, s.total_questions) }}%</div>
        </div>
      </RouterLink>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/lib/api'

const sessions = ref([])
const loading = ref(true)
const confirmClear = ref(false)

function formatDate(iso) {
  return new Date(iso).toLocaleString('sk-SK', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function pct(s, t) { return t ? Math.round((s / t) * 100) : 0 }
function scoreClass(s, t) { return pct(s, t) >= 70 ? 'text-accent' : pct(s, t) >= 50 ? '' : 'text-red' }

async function clearHistory() {
  await api.clearHistory()
  sessions.value = []
  confirmClear.value = false
}

onMounted(async () => {
  sessions.value = await api.getHistory({ limit: 50 })
  loading.value = false
})
</script>

<style scoped>
.session-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-decoration: none;
  color: var(--text);
  padding: 16px 20px;
  transition: background 0.12s;
}
.session-row:hover { background: var(--bg-hover); }
</style>