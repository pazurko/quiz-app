<template>
  <div class="container" style="padding-top: 48px; padding-bottom: 64px;">
    <h1 class="serif" style="margin-bottom: 6px;">
      Dobrý deň<span v-if="auth.user">, {{ firstName }}</span> 👋
    </h1>
    <p class="text-muted" style="margin-bottom: 40px;">What would you like to study today?</p>

    <!-- Mode cards -->
    <div class="mode-grid">
      <RouterLink to="/review" class="mode-card card">
        <div class="mode-icon">📖</div>
        <h2>Review</h2>
        <p class="text-muted">Go through questions one by one. See answers as you go. Good for learning.</p>
      </RouterLink>

      <RouterLink to="/quiz" class="mode-card card">
        <div class="mode-icon">⏱️</div>
        <h2>Custom Quiz</h2>
        <p class="text-muted">Set the number of questions, time limit, and topic. Test yourself.</p>
      </RouterLink>

      <RouterLink to="/history" class="mode-card card">
        <div class="mode-icon">📊</div>
        <h2>History</h2>
        <p class="text-muted">Review your past quiz attempts and see where you went wrong.</p>
      </RouterLink>
    </div>

    <!-- Recent stats (if available) -->
    <div v-if="recentSessions.length" style="margin-top: 48px;">
      <h3 style="margin-bottom: 16px;">Recent activity</h3>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <RouterLink
          v-for="s in recentSessions"
          :key="s.id"
          :to="`/history/${s.id}`"
          class="session-row card"
        >
          <div>
            <span class="text-muted mono" style="font-size: 12px;">{{ formatDate(s.completed_at) }}</span>
            <div style="font-size: 15px; margin-top: 2px;">{{ s.subjects?.name ?? 'Quiz' }}</div>
          </div>
          <div style="text-align: right;">
            <div :class="scoreClass(s.score, s.total_questions)" style="font-size: 1.1rem; font-weight: 600;">
              {{ s.score }}/{{ s.total_questions }}
            </div>
            <div class="text-muted" style="font-size: 12px;">{{ pct(s.score, s.total_questions) }}%</div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'

const auth = useAuthStore()
const recentSessions = ref([])

const firstName = computed(() => {
  const email = auth.user?.email ?? ''
  return email.split('@')[0]
})

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('sk-SK', { day: 'numeric', month: 'short', year: 'numeric' })
}
function pct(score, total) { return total ? Math.round((score / total) * 100) : 0 }
function scoreClass(score, total) {
  const p = pct(score, total)
  return p >= 70 ? 'text-accent' : p >= 50 ? '' : 'text-red'
}

onMounted(async () => {
  try {
    const data = await api.getHistory({ limit: 5 })
    recentSessions.value = data
  } catch {}
})
</script>

<style scoped>
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.mode-card {
  display: block;
  text-decoration: none;
  color: var(--text);
  transition: all 0.15s;
  border-color: var(--border);
}
.mode-card:hover {
  border-color: var(--text-dim);
  background: var(--bg-hover);
  transform: translateY(-2px);
}
.mode-icon { font-size: 1.8rem; margin-bottom: 12px; }
.mode-card h2 { margin-bottom: 8px; }

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
