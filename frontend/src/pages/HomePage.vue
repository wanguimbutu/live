<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <!-- Location denied warning — persists until user enables GPS -->
      <div v-if="locationDenied" class="location-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        Location is disabled. Please enable GPS in your device settings for accurate visit tracking.
      </div>
      <div class="home-root">
        <Profile />
        <CheckIn />
        <QuickLinks />
        <div v-if="isSystemManager" class="admin-bar">
          <button class="admin-link" @click="$router.push('/admin-settings')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            App Settings
          </button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { IonContent, IonPage } from '@ionic/vue'
import CheckIn from '../components/CheckIn.vue'
import QuickLinks from '../components/QuickLinks.vue'
import Profile from '../components/profile.vue'
import { usePresence } from '../composables/usePresence'

const { locationDenied } = usePresence()
const isSystemManager = ref(false)

onMounted(async () => {
  try {
    const res = await fetch('/api/method/live.api.settings.get_app_settings', { credentials: 'include' })
    const { message } = await res.json()
    isSystemManager.value = !!message?.is_admin
  } catch {}
})
</script>

<style scoped>
.home-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 80px;
}

.location-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fffbeb;
  border-bottom: 1px solid #fde68a;
  color: #92400e;
  padding: 12px 16px;
  font-size: 0.82rem;
  line-height: 1.4;
}

.location-banner svg {
  flex-shrink: 0;
  margin-top: 1px;
}

.admin-bar {
  padding: 8px 16px 0;
  display: flex;
  justify-content: flex-end;
}
.admin-link {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: #f1f5f9; color: #475569;
  border: none; border-radius: 8px;
  font-size: 0.75rem; font-weight: 600; cursor: pointer;
}
</style>
