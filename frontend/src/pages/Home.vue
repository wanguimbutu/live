<template>
  <ion-page>
    <div class="splash-root">
      <div class="splash-content" :class="{ 'splash-ready': ready }">
        <div class="splash-logo">
          <img src="/logo.png" alt="Live" class="logo-img" />
        </div>
        <h1 class="splash-title">Sales Live</h1>
        <p class="splash-subtitle">Your field sales companion</p>
        <div class="splash-spinner" v-if="!ready">
          <div class="spinner-ring"></div>
        </div>
      </div>
    </div>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { IonPage } from '@ionic/vue'
import { useRouter } from 'vue-router'
import { session } from '../data/session'

const router = useRouter()
const ready = ref(false)

onMounted(() => {
  setTimeout(() => {
    ready.value = true
    setTimeout(() => {
      if (session.isLoggedIn) {
        router.replace('/homePage')
      } else {
        router.replace({ name: 'Login' })
      }
    }, 300)
  }, 400)
})
</script>

<style scoped>
.splash-root {
  height: 100%;
  width: 100%;
  background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.splash-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  opacity: 0;
  transform: translateY(24px);
  animation: rise 0.7s ease forwards;
}

.splash-content.splash-ready {
  animation: fadeout 0.4s ease forwards;
}

@keyframes rise {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeout {
  to { opacity: 0; transform: scale(0.95); }
}

.splash-logo {
  width: 88px;
  height: 88px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  margin-bottom: 8px;
}

.logo-img {
  width: 56px;
  height: 56px;
  object-fit: contain;
}

.splash-title {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.5px;
  margin: 0;
}

.splash-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.splash-spinner {
  margin-top: 24px;
}

.spinner-ring {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
