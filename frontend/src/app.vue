<template>
  <div v-if="!auth.loading">
    <NavBar v-if="auth.user" />
    <main>
      <RouterView />
    </main>
  </div>
  <div v-else class="flex-center" style="height: 100vh; color: var(--text-muted);">
    Loading...
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>
