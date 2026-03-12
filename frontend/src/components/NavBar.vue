<template>
  <nav class="navbar">
    <div class="container nav-inner">
      <RouterLink to="/" class="nav-logo">
        <span class="serif">quiz</span><span class="text-accent">.</span>
      </RouterLink>

      <div class="nav-links">
        <RouterLink to="/"         class="nav-link">Dashboard</RouterLink>
        <RouterLink to="/review"   class="nav-link">Review</RouterLink>
        <RouterLink to="/quiz"     class="nav-link">Custom Quiz</RouterLink>
        <RouterLink to="/history"  class="nav-link">History</RouterLink>
      </div>

      <button class="btn btn-ghost" style="padding: 6px 14px; font-size: 13px;" @click="auth.signOut">
        Sign out
      </button>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.navbar {
  border-bottom: 1px solid var(--border);
  padding: 12px 0;
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 100;
}
.nav-inner {
  display: flex;
  align-items: center;
  gap: 32px;
}
.nav-logo {
  font-size: 1.2rem;
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
}
.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}
.nav-link {
  padding: 6px 12px;
  border-radius: var(--radius);
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.12s;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: var(--text);
  background: var(--bg-hover);
}
</style>
