<template>
  <div class="container" style="padding-top: 48px; padding-bottom: 64px;">
    <RouterLink to="/history" class="text-muted" style="font-size: 13px;">← Back to History</RouterLink>

    <div v-if="loading" class="text-muted" style="margin-top: 32px;">Loading...</div>
    <div v-else-if="detail">
      <!-- Session summary -->
      <div class="card" style="margin-top: 24px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <div class="text-muted" style="font-size: 13px;">{{ formatDate(detail.session.completed_at) }}</div>
          <h2 style="margin-top: 4px;">{{ detail.session.mode === 'review' ? 'Review Session' : 'Custom Quiz' }}</h2>
        </div>
        <div style="text-align: right;">
          <div :class="scoreClass" style="font-size: 2rem; font-weight: 700; font-family: var(--font-serif);">
            {{ detail.session.score }}/{{ detail.session.total_questions }}
          </div>
          <div class="text-muted mono" style="font-size: 13px;">{{ pct }}%</div>
        </div>
      </div>

      <!-- Per-question breakdown -->
      <h3 style="margin-top: 32px; margin-bottom: 16px;">Question Breakdown</h3>
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <div
          v-for="(a, i) in detail.answers"
          :key="a.id"
          class="card"
          :style="{ borderColor: a.is_correct ? 'var(--accent-dim)' : 'var(--red-dim)' }"
        >
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span class="text-muted mono" style="font-size: 12px;">Q{{ i + 1 }}</span>
            <span :class="a.is_correct ? 'badge badge-green' : 'badge badge-red'">
              {{ a.is_correct ? 'Correct' : 'Wrong' }}
            </span>
          </div>
          <p style="font-size: 14px; margin-bottom: 12px;">{{ a.questions.question_text }}</p>
          <div style="font-size: 13px; color: var(--text-muted);">
            <span>Your answer: </span>
            <span class="mono">{{ a.selected_options.join(', ') }}</span>
            <span v-if="!a.is_correct"> · Correct: </span>
            <span v-if="!a.is_correct" class="mono text-accent">{{ a.questions.correct_options.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { api } from '@/lib/api'

const route = useRoute()
const detail = ref(null)
const loading = ref(true)

function formatDate(iso) {
  return new Date(iso).toLocaleString('sk-SK', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const pct = computed(() => {
  if (!detail.value) return 0
  const { score, total_questions } = detail.value.session
  return Math.round((score / total_questions) * 100)
})
const scoreClass = computed(() => pct.value >= 70 ? 'text-accent' : pct.value >= 50 ? '' : 'text-red')

onMounted(async () => {
  detail.value = await api.getSessionDetail(route.params.id)
  loading.value = false
})
</script>
