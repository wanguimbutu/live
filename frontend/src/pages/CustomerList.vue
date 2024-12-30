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
        <ion-title>Customers</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content>
        <CustomerList name="customerList"/>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
  import { IonHeader, IonToolbar, IonTitle, IonContent, IonPage } from '@ionic/vue';
  import CustomerList from '../components/customerList.vue';
  export default {
    components: { IonHeader, IonToolbar, IonTitle, IonContent, IonPage,CustomerList },
  };
</script>