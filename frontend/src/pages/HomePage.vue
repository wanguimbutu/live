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
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonContent, IonPage } from '@ionic/vue'
import CheckIn from '../components/CheckIn.vue'
import QuickLinks from '../components/QuickLinks.vue'
import Profile from '../components/profile.vue'
import { usePresence } from '../composables/usePresence'

const { locationDenied } = usePresence()
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
</style>
