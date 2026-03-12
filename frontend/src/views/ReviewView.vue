<template>
  <div class="container" style="padding: 48px 24px 64px;">

    <!-- ── Initial load ── -->
    <div v-if="initialLoading" style="text-align: center;">
      <p class="text-muted">Loading…</p>
    </div>

    <!-- ── Subject selection screen ── -->
    <template v-else-if="!subjectSelected">
      <RouterLink to="/" class="text-muted" style="font-size: 13px;">← Back</RouterLink>
      <h1 class="serif" style="margin-top: 16px; margin-bottom: 8px;">Review Mode</h1>
      <p class="text-muted" style="margin-bottom: 32px;">Go through questions at your own pace, reveal answers when ready.</p>

      <div v-if="subjectLoading" style="padding: 40px 0; text-align: center;">
        <p class="text-muted">Loading subject…</p>
      </div>

      <div v-else style="display: flex; flex-direction: column; gap: 12px; max-width: 560px;">
        <button
          v-for="s in subjects"
          :key="s.id"
          class="subject-card"
          @click="selectSubject(s)"
        >
          <div>
            <p style="font-size: 15px; font-weight: 500; text-align: left; color: var(--text);">{{ s.name }}</p>
            <p v-if="s.description" style="margin-top: 4px; text-align: left; font-size: 14px; color: var(--text-muted);">{{ s.description }}</p>
          </div>
          <span style="color: var(--text-dim); font-size: 18px;">→</span>
        </button>
        <p v-if="!subjects.length" class="text-muted">No subjects available.</p>
      </div>
    </template>

    <!-- ── Sidebar + question layout ── -->
    <template v-else>
      <div style="margin-bottom: 28px; display: flex; align-items: center; gap: 16px;">
        <button class="btn btn-ghost" style="padding: 8px 14px; font-size: 13px;" @click="subjectSelected = false">
          ← All subjects
        </button>
        <h1 class="serif" style="font-size: 1.6rem; line-height: 1.2;">Review Mode</h1>
      </div>

      <div style="display: grid; grid-template-columns: 272px 1fr; gap: 24px; align-items: start;">

        <!-- ── Sidebar ── -->
        <aside style="position: sticky; top: 24px; max-height: calc(100vh - 80px); overflow-y: auto;">
          <div class="card" style="padding: 20px;">
            <p style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 4px;">Subject</p>
            <h3 style="margin-bottom: 20px; line-height: 1.3;">{{ activeSubject?.name }}</h3>

            <!-- Categories -->
            <div v-for="cat in categoriesWithStats" :key="cat.id" style="margin-bottom: 18px;">

              <!-- Category header row -->
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <p class="category-label">{{ cat.name }}</p>
                <button
                  v-if="confirmingReset !== cat.id"
                  class="reset-btn"
                  @click="confirmingReset = cat.id"
                >
                  Reset
                </button>
              </div>

              <!-- Inline category reset confirmation -->
              <div v-if="confirmingReset === cat.id" class="confirm-row" style="margin-bottom: 6px;">
                <span style="font-size: 12px; color: var(--text-muted);">Reset this category?</span>
                <div style="display: flex; gap: 6px;">
                  <button class="confirm-yes" @click="resetCategory(cat.id)">Yes</button>
                  <button class="confirm-cancel" @click="confirmingReset = null">Cancel</button>
                </div>
              </div>

              <!-- Filter rows -->
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <button
                  class="filter-btn"
                  :class="{ active: isActiveFilter(cat.id, 'unreviewed'), dim: cat.unreviewed === 0 }"
                  :disabled="cat.unreviewed === 0"
                  @click="loadBatch(cat.id, 'unreviewed')"
                >
                  <span>Unreviewed</span>
                  <span class="badge badge-gray">{{ cat.unreviewed }}</span>
                </button>
                <button
                  class="filter-btn"
                  :class="{ active: isActiveFilter(cat.id, 'repeat'), dim: cat.repeat === 0 }"
                  :disabled="cat.repeat === 0"
                  @click="loadBatch(cat.id, 'repeat')"
                >
                  <span>Repeat</span>
                  <span class="badge" style="background: var(--red-dim); color: var(--red);">{{ cat.repeat }}</span>
                </button>
                <div class="filter-done">
                  <span>Done</span>
                  <span class="badge badge-green">{{ cat.done }}</span>
                </div>
              </div>
            </div>

            <!-- Subject-level reset -->
            <hr>
            <div v-if="confirmingReset === 'subject'" class="confirm-row" style="margin-top: 4px;">
              <span style="font-size: 12px; color: var(--text-muted);">Reset entire subject?</span>
              <div style="display: flex; gap: 6px;">
                <button class="confirm-yes" @click="resetSubject">Yes</button>
                <button class="confirm-cancel" @click="confirmingReset = null">Cancel</button>
              </div>
            </div>
            <button
              v-else
              class="btn btn-ghost"
              style="width: 100%; justify-content: center; font-size: 13px;"
              @click="confirmingReset = 'subject'"
            >
              Reset entire subject
            </button>
          </div>
        </aside>

        <!-- ── Right panel ── -->
        <main>

          <!-- Nothing selected yet -->
          <div v-if="!activeBatch.length && !batchDone" class="card" style="text-align: center; padding: 64px 24px;">
            <p style="font-size: 1.4rem; margin-bottom: 12px; color: var(--text-dim);">←</p>
            <p class="text-muted">Pick a category from the sidebar to start reviewing.</p>
          </div>

          <!-- Batch complete -->
          <div v-else-if="batchDone" class="card" style="text-align: center; padding: 48px 24px;">
            <p style="font-size: 2rem; margin-bottom: 16px; color: var(--accent);">✓</p>
            <h2 style="margin-bottom: 8px;">Batch complete!</h2>
            <p class="text-muted" style="margin-bottom: 28px;">
              You went through all {{ activeBatch.length }} question{{ activeBatch.length !== 1 ? 's' : '' }} in this batch.
            </p>
            <div
              v-if="repeatCountForActive > 0"
              style="margin-bottom: 20px; padding: 16px; background: var(--bg-surface); border-radius: var(--radius); border: 1px solid var(--border); text-align: left;"
            >
              <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 12px;">
                <strong style="color: var(--text);">{{ repeatCountForActive }}</strong>
                question{{ repeatCountForActive !== 1 ? 's' : '' }} in this category still need more practice.
              </p>
              <button class="btn btn-primary" @click="loadRepeatBatch">
                Review Repeat pile →
              </button>
            </div>
            <button class="btn btn-ghost" @click="clearBatch">Back to sidebar</button>
          </div>

          <!-- Question -->
          <div v-else>
            <!-- Progress -->
            <div style="margin-bottom: 20px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-mono); font-size: 13px; display: flex; align-items: center; gap: 6px;">
                  <button class="nav-arrow" :disabled="currentIndex === 0" @click="jumpTo(currentIndex)">‹</button>
                  <span class="text-muted">Question</span>
                  <input
                    type="number"
                    :value="currentIndex + 1"
                    :min="1"
                    :max="activeBatch.length"
                    @change="jumpTo($event.target.value)"
                    style="width: 52px; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 4px; color: var(--text); font-family: var(--font-mono); font-size: 13px; padding: 2px 6px; text-align: center;"
                  />
                  <span class="text-muted">/ {{ activeBatch.length }}</span>
                  <button class="nav-arrow" :disabled="currentIndex === activeBatch.length - 1" @click="jumpTo(currentIndex + 2)">›</button>
                </span>
                <span class="text-muted" style="font-size: 13px;">{{ progressPct }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
              </div>
            </div>

            <!-- Question card -->
            <div class="card">
              <div style="margin-bottom: 8px; display: flex; gap: 8px; align-items: center;">
                <span class="text-muted" style="font-family: var(--font-mono); font-size: 12px;">#{{ current.question_number }}</span>
                <span v-if="current.type === 'multiple_correct'" class="badge badge-gray">Multiple correct</span>
              </div>
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 24px;">{{ current.question_text }}</p>

              <!-- Options -->
              <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px;">
                <button
                  v-for="[key, text] in visibleOptions"
                  :key="key"
                  class="option-btn"
                  :class="optionClass(key)"
                  :disabled="revealed"
                  @click="toggleOption(key)"
                >
                  <span class="option-key">{{ key }}</span>
                  <span>{{ text }}</span>
                </button>
              </div>

              <!-- Action buttons -->
              <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
                <button
                  v-if="!revealed"
                  class="btn btn-primary"
                  :disabled="revealLoading"
                  @click="revealAnswer"
                >
                  {{ revealLoading ? 'Loading…' : 'Reveal Answer' }}
                </button>
                <button
                  v-if="!revealed"
                  class="btn btn-ghost"
                  @click="skipQuestion"
                >
                  Skip →
                </button>
                <template v-else>
                  <button class="btn btn-primary" @click="markAndNext('done')">
                    Got it ✓
                  </button>
                  <button class="btn btn-ghost" @click="markAndNext('repeat')">
                    Need more practice
                  </button>
                </template>
              </div>
              <p v-if="actionError" class="text-red" style="margin-top: 12px; font-size: 13px;">{{ actionError }}</p>
            </div>
          </div>

        </main>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/lib/api'

// ── Global state ──────────────────────────────────────────────────────────────

const initialLoading  = ref(true)
const subjectLoading  = ref(false)
const subjects        = ref([])
const subjectSelected = ref(false)
const activeSubject   = ref(null)
const questions       = ref([])       // all questions for the active subject
const reviewStateMap  = ref({})       // { question_id: status } — only rows that exist in DB

// ── Review session state ──────────────────────────────────────────────────────

const activeBatch     = ref([])       // current slice of questions to review
const activeFilter    = ref(null)     // { category_id, status }
const currentIndex    = ref(0)
const selectedOptions = ref(new Set())
const revealed        = ref(false)
const correctSet      = ref(new Set())
const revealLoading   = ref(false)
const batchDone       = ref(false)
const actionError     = ref('')

// ── Reset confirmation ────────────────────────────────────────────────────────
// null | 'subject' | <category_id string>
const confirmingReset = ref(null)

// ── Computed ──────────────────────────────────────────────────────────────────

const categoriesWithStats = computed(() => {
  // Show all categories from the subject — no filtering by question count
  return (activeSubject.value?.categories ?? []).map(cat => {
    const catQs = questions.value.filter(q => q.category_id === cat.id)
    const counts = { unreviewed: 0, repeat: 0, done: 0 }
    for (const q of catQs) {
      counts[reviewStateMap.value[q.id] ?? 'unreviewed']++
    }
    return { ...cat, ...counts }
  })
})

const current = computed(() => activeBatch.value[currentIndex.value])

const visibleOptions = computed(() => {
  if (!current.value?.options) return []
  return Object.entries(current.value.options).filter(([, text]) => text)
})

const progressPct = computed(() =>
  Math.round(((currentIndex.value + 1) / activeBatch.value.length) * 100)
)

const repeatCountForActive = computed(() => {
  if (!activeFilter.value) return 0
  return questions.value.filter(q =>
    q.category_id === activeFilter.value.category_id &&
    reviewStateMap.value[q.id] === 'repeat'
  ).length
})

// ── Helpers ───────────────────────────────────────────────────────────────────

function isActiveFilter(category_id, status) {
  return activeFilter.value?.category_id === category_id &&
         activeFilter.value?.status === status
}

function optionClass(key) {
  if (!revealed.value) {
    return selectedOptions.value.has(key) ? 'selected' : ''
  }
  const isCorrect  = correctSet.value.has(key)
  const isSelected = selectedOptions.value.has(key)
  if (isCorrect && isSelected)  return 'correct'  // hit: green
  if (!isCorrect && isSelected) return 'wrong'    // wrong pick: red
  if (isCorrect && !isSelected) return 'missed'   // forgot this one: yellow
  return ''                                        // irrelevant: grey
}

function toggleOption(key) {
  const next = new Set(selectedOptions.value)
  next.has(key) ? next.delete(key) : next.add(key)
  selectedOptions.value = next
}

// ── Batch actions ─────────────────────────────────────────────────────────────

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function loadBatch(category_id, status) {
  const batch = questions.value.filter(q =>
    q.category_id === category_id &&
    (reviewStateMap.value[q.id] ?? 'unreviewed') === status
  )
  activeBatch.value = batch
  activeFilter.value = { category_id, status }
  currentIndex.value = 0
  selectedOptions.value = new Set()
  revealed.value = false
  correctSet.value = new Set()
  batchDone.value = false
  actionError.value = ''
  confirmingReset.value = null
}

function loadRepeatBatch() {
  loadBatch(activeFilter.value.category_id, 'repeat')
}

function clearBatch() {
  activeBatch.value = []
  batchDone.value = false
  activeFilter.value = null
}

function jumpTo(value) {
  const index = parseInt(value) - 1
  if (index >= 0 && index < activeBatch.value.length) {
    currentIndex.value = index
    selectedOptions.value = new Set()
    revealed.value = false
    correctSet.value = new Set()
    actionError.value = ''
  }
}

function skipQuestion() {
  if (currentIndex.value + 1 >= activeBatch.value.length) {
    batchDone.value = true
  } else {
    currentIndex.value++
    selectedOptions.value = new Set()
    revealed.value = false
    correctSet.value = new Set()
    actionError.value = ''
  }
}

async function revealAnswer() {
  revealLoading.value = true
  actionError.value = ''
  try {
    const data = await api.getAnswer(current.value.id)
    const opts = Array.isArray(data.correct_options)
      ? data.correct_options
      : [data.correct_options]
    correctSet.value = new Set(opts)
    revealed.value = true
  } catch (e) {
    actionError.value = e.message
  } finally {
    revealLoading.value = false
  }
}

async function markAndNext(status) {
  const qId = current.value.id

  // Update local map immediately so sidebar counts reflect the change
  reviewStateMap.value = { ...reviewStateMap.value, [qId]: status }

  // Advance to the next question without waiting for the network
  if (currentIndex.value + 1 >= activeBatch.value.length) {
    batchDone.value = true
  } else {
    currentIndex.value++
    selectedOptions.value = new Set()
    revealed.value = false
    correctSet.value = new Set()
  }

  // Persist to DB in the background — a failure here won't block the review flow
  api.updateReviewState(qId, status).catch(e => {
    console.error('Failed to save review state:', e)
  })
}

// ── Reset actions ─────────────────────────────────────────────────────────────

async function resetCategory(category_id) {
  try {
    await api.resetReviewState(activeSubject.value.id, category_id)
    // Remove state entries for all questions in this category
    const newMap = { ...reviewStateMap.value }
    for (const q of questions.value) {
      if (q.category_id === category_id) delete newMap[q.id]
    }
    reviewStateMap.value = newMap
    if (activeFilter.value?.category_id === category_id) clearBatch()
  } catch (e) {
    console.error('Category reset failed:', e)
  } finally {
    confirmingReset.value = null
  }
}

async function resetSubject() {
  try {
    await api.resetReviewState(activeSubject.value.id, null)
    reviewStateMap.value = {}
    clearBatch()
  } catch (e) {
    console.error('Subject reset failed:', e)
  } finally {
    confirmingReset.value = null
  }
}

// ── Initialisation ────────────────────────────────────────────────────────────

async function selectSubject(subject) {
  subjectLoading.value = true
  try {
    activeSubject.value = subject

    // Use allSettled so a failing review-state fetch doesn't block the question load
    const [questionsResult, stateResult] = await Promise.allSettled([
      fetchAllQuestions(subject.id),
      api.getReviewState(subject.id),
    ])

    if (questionsResult.status === 'fulfilled') {
      questions.value = questionsResult.value
    } else {
      console.error('Failed to load questions:', questionsResult.reason)
      questions.value = []
    }

    const map = {}
    if (stateResult.status === 'fulfilled') {
      for (const row of stateResult.value) map[row.question_id] = row.status
    } else {
      console.error('Failed to load review state:', stateResult.reason)
    }
    reviewStateMap.value = map

    clearBatch()
    subjectSelected.value = true
  } catch (e) {
    console.error('Unexpected error selecting subject:', e)
    subjectSelected.value = true  // still enter the sidebar view
  } finally {
    subjectLoading.value = false
  }
}

async function fetchAllQuestions(subject_id) {
  // Paginate in chunks of 500 (API max) to handle large subjects like biology (1250+)
  const PAGE = 500
  const all = []
  let offset = 0
  while (true) {
    const page = await api.getQuestions({ subject_id, limit: PAGE, offset })
    all.push(...page)
    if (page.length < PAGE) break
    offset += PAGE
  }
  return all
}

onMounted(async () => {
  try {
    subjects.value = await api.getSubjects()
  } finally {
    initialLoading.value = false
  }
})
</script>

<style scoped>
/* Subject selection cards */
.subject-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.15s ease;
  width: 100%;
  color: var(--text);
}
.subject-card:hover {
  border-color: var(--text-dim);
  background: var(--bg-hover);
}

/* Sidebar category label */
.category-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0;
}

/* Small inline reset button next to category name */
.reset-btn {
  font-size: 11px;
  font-family: var(--font-body);
  color: var(--text-dim);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.12s, background 0.12s;
  flex-shrink: 0;
}
.reset-btn:hover {
  color: var(--red);
  background: var(--red-dim);
}

/* Inline "Are you sure?" confirmation row */
.confirm-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  gap: 8px;
}
.confirm-yes {
  font-size: 12px;
  font-family: var(--font-body);
  padding: 3px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  background: var(--red-dim);
  color: var(--red);
  transition: all 0.12s;
}
.confirm-yes:hover { background: var(--red); color: #fff; }
.confirm-cancel {
  font-size: 12px;
  font-family: var(--font-body);
  padding: 3px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  transition: all 0.12s;
}
.confirm-cancel:hover { background: var(--bg-hover); color: var(--text); }

/* Sidebar filter buttons (Unreviewed / Repeat) */
.filter-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 6px 10px;
  border-radius: var(--radius);
  font-size: 13px;
  font-family: var(--font-body);
  color: var(--text-muted);
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.12s ease;
  text-align: left;
}
.filter-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text);
  border-color: var(--border);
}
.filter-btn.active {
  background: var(--accent-dim);
  color: var(--accent);
  border-color: var(--accent);
}
.filter-btn.dim,
.filter-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

/* Missed answer — correct option the user didn't select */
.option-btn.missed {
  border-color: var(--yellow);
  background: rgba(251, 191, 36, 0.1);
}

/* Done row (non-interactive) */
.filter-done {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  font-size: 13px;
  color: var(--text-dim);
}

/* Hide number input spinner arrows */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number] { -moz-appearance: textfield; }

/* Prev/next question arrows */
.nav-arrow {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 16px;
  line-height: 1;
  padding: 2px 8px;
  cursor: pointer;
  transition: all 0.12s;
}
.nav-arrow:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text);
  border-color: var(--text-dim);
}
.nav-arrow:disabled {
  opacity: 0.3;
  cursor: default;
}
</style>