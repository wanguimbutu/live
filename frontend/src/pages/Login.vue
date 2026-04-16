<template>
  <ion-page>
    <div class="login-root">
      <!-- Brand -->
      <div class="login-brand">
        <div class="brand-icon">
          <img src="/logo.png" alt="Live" class="brand-img" />
        </div>
        <h1 class="brand-name">Sales Live</h1>
        <p class="brand-tagline">Sign in to continue</p>
      </div>

      <!-- Form card -->
      <div class="login-card">
        <form @submit.prevent="submit" class="login-form" novalidate>
          <!-- Error banner -->
          <div v-if="errorMsg" class="error-banner">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ errorMsg }}
          </div>

          <!-- Email -->
          <div class="field-group">
            <label class="field-label">Email / User ID</label>
            <div class="input-wrap" :class="{ focused: focusedField === 'email' }">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              <input
                v-model="email"
                type="text"
                name="email"
                placeholder="you@company.com"
                autocomplete="username"
                required
                class="field-input"
                @focus="focusedField = 'email'"
                @blur="focusedField = null"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="field-group">
            <label class="field-label">Password</label>
            <div class="input-wrap" :class="{ focused: focusedField === 'password' }">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                name="password"
                placeholder="••••••••"
                autocomplete="current-password"
                required
                class="field-input"
                @focus="focusedField = 'password'"
                @blur="focusedField = null"
              />
              <button type="button" class="eye-btn" @click="showPassword = !showPassword" tabindex="-1">
                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">Sign In</span>
            <span v-else class="btn-spinner"></span>
          </button>
        </form>
      </div>

      <p class="login-footer">Connected to {{ serverLabel }}</p>
    </div>
  </ion-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IonPage } from '@ionic/vue'
import { session } from '../data/session'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const focusedField = ref(null)
const errorMsg = ref('')

const loading = computed(() => session.login.loading)

const serverLabel = computed(() => {
  const url = import.meta.env.VITE_FRAPPE_URL
  if (!url) return 'local instance'
  try { return new URL(url).hostname } catch { return url }
})

function submit() {
  errorMsg.value = ''
  if (!email.value || !password.value) {
    errorMsg.value = 'Please enter your email and password.'
    return
  }
  session.login.submit(
    { email: email.value, password: password.value },
    {
      onError(err) {
        errorMsg.value =
          err?.messages?.[0] || err?.message || 'Invalid credentials. Please try again.'
      },
    }
  )
}
</script>

<style scoped>
.login-root {
  height: 100%;
  width: 100%;
  background: linear-gradient(165deg, #0f172a 0%, #1e3a5f 55%, #1d4ed8 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 20px;
  overflow-y: auto;
}

.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
  animation: rise 0.5s ease both;
}

.brand-icon {
  width: 72px;
  height: 72px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.15);
  margin-bottom: 16px;
}

.brand-img {
  width: 44px;
  height: 44px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 6px;
}

.brand-tagline {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 20px;
  padding: 28px 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  animation: rise 0.5s 0.1s ease both;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.875rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-wrap {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  padding: 0 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrap.focused {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
  background: #fff;
}

.input-icon {
  color: #9ca3af;
  flex-shrink: 0;
}

.field-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 12px 10px;
  font-size: 0.95rem;
  color: #111827;
}

.field-input::placeholder {
  color: #d1d5db;
}

.eye-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #9ca3af;
  display: flex;
  align-items: center;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.submit-btn:active { transform: scale(0.98); }
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

.login-footer {
  margin-top: 20px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.4);
  animation: rise 0.5s 0.2s ease both;
}

@keyframes rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>