<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Attendance</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content :fullscreen="true">
      <UserStatus />
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonHeader, IonToolbar, IonTitle, IonContent, IonPage } from '@ionic/vue'
import UserStatus from '../components/userStatus.vue'
</script>
