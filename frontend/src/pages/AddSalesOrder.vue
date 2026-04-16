<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <AddSalesOrder />
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonContent, IonPage } from '@ionic/vue'
import AddSalesOrder from '../components/addSalesOrder.vue'
</script>
