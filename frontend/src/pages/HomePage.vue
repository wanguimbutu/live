<style scoped>
  .example-content {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
</style>

<template>
  <ion-page>
    <ion-header>
    </ion-header>
    <ion-content>
        <Profile/>
        <CheckIn/>
        <QuickLinks/>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonHeader, IonContent, IonPage } from '@ionic/vue'
import CheckIn from '../components/CheckIn.vue'
import QuickLinks from '../components/QuickLinks.vue'
import Profile from '../components/profile.vue'
import { usePresence } from '../composables/usePresence'

// Start tracking location + battery for this user session
usePresence()
</script>