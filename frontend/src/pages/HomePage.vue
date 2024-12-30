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

<script lang="ts">
  import { IonHeader, IonToolbar, IonTitle, IonContent, IonPage } from '@ionic/vue';
import CheckIn from '@/components/CheckIn.vue'
import QuickLinks from '@/components/QuickLinks.vue'
import Profile from '@/components/profile.vue'
  export default {
    components: { IonHeader, IonToolbar, IonTitle, IonContent, IonPage,CheckIn,QuickLinks, Profile},
  };
</script>