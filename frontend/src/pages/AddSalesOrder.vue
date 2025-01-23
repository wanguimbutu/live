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
      <ion-toolbar>
        <ion-title>New Sales Order</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content>
        <AddSalesOrder name="newSalesOrder"/>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
  import { IonHeader, IonToolbar, IonTitle, IonContent, IonPage } from '@ionic/vue';
import AddSalesOrder from '../components/addSalesOrder.vue';
  export default {
    components: { IonHeader, IonToolbar, IonTitle, IonContent, IonPage,AddSalesOrder },
  };
</script>