<template>
  <ion-page>
    <ion-content :fullscreen="true">
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

usePresence()
</script>

<style scoped>
.home-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 80px;
}
</style>
