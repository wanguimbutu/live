<template>
    <ion-page>
      <ion-content>
        <OrderList/>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
   import {IonPage,IonContent} from '@ionic/vue'
   import OrderList from '../components/OrderList.vue';
  
   export default{
    components:{
      OrderList,IonContent,IonPage
      
    }
   }
  </script>