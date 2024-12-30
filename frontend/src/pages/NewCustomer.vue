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
        <ion-title>New Customer</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content>   
     <AddCustomer name="newCustomer"/>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
  import { IonHeader, IonToolbar, IonTitle, IonContent, IonPage } from '@ionic/vue';
 // import{TextInput} from 'frappe-ui'
import AddCustomer from '../components/addCustomer.vue';
import AddCustomer from '../components/addCustomer.vue';

  export default {
    components: { IonHeader, IonToolbar, IonTitle, IonContent, IonPage,AddCustomer},
  };
</script>