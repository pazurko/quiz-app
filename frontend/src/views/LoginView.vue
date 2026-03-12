<template>
  <div class="login-page">
    <div class="login-box card">
      <h1 class="serif" style="font-size: 2.2rem; margin-bottom: 4px;">
        bio<span class="text-accent">quiz</span>
      </h1>
      <p class="text-muted" style="margin-bottom: 32px;">LF UPJŠ — príprava na prijímacie skúšky</p>

      <div style="display: flex; gap: 0; margin-bottom: 28px; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden;">
        <button
          :class="['tab-btn', { active: mode === 'login' }]"
          @click="mode = 'login'"
        >Sign in</button>
        <button
          :class="['tab-btn', { active: mode === 'signup' }]"
          @click="mode = 'signup'"
        >Create account</button>
      </div>

      <form @submit.prevent="submit">
        <div style="margin-bottom: 16px;">
          <label>Email</label>
          <input v-model="email" type="email" class="input" placeholder="your@email.com" required />
        </div>
        <div style="margin-bottom: 24px;">
          <label>Password</label>
          <input v-model="password" type="password" class="input" placeholder="••••••••" required />
        </div>

        <div v-if="error" class="text-red" style="font-size: 13px; margin-bottom: 16px;">{{ error }}</div>
        <div v-if="success" class="text-accent" style="font-size: 13px; margin-bottom: 16px;">{{ success }}</div>

        <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center;" :disabled="loading">
          {{ loading ? 'Please wait...' : (mode === 'login' ? 'Sign in' : 'Create account') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const mode = ref('login')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function submit() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await auth.signIn(email.value, password.value)
      router.push('/')
    } else {
      await auth.signUp(email.value, password.value)
      success.value = 'Account created! You can now sign in.'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.login-box {
  width: 100%;
  max-width: 400px;
}
.tab-btn {
  flex: 1;
  padding: 10px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.12s;
}
.tab-btn.active {
  background: var(--bg-hover);
  color: var(--text);
}
</style>
