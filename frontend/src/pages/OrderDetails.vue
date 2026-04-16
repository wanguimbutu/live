<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <OrderDetails />
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonContent, IonPage } from '@ionic/vue'
import OrderDetails from '../components/OrderDetails.vue'
</script>
