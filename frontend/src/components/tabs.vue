<template>
    <ion-page>
      <ion-tabs>
        <ion-router-outlet></ion-router-outlet>
        <ion-tab-bar slot="bottom">
          <ion-tab-button tab="home" href="/homePage">
            <ion-icon :icon="home" />
            <ion-label>Home</ion-label>
          </ion-tab-button>
  
          <ion-tab-button tab="attendance" href="/attendance">
            <ion-icon :icon="fingerPrint" />
            <ion-label>Attendance</ion-label>
          </ion-tab-button>
  
          <ion-tab-button tab="sales" href="/salesOrderList">
            <ion-icon :icon="cart" />
            <ion-label>Sales Orders</ion-label>
          </ion-tab-button>
  
          <ion-tab-button tab="customer" href="/customerList">
            <ion-icon :icon="person" />
            <ion-label>Customers</ion-label>
          </ion-tab-button>
        </ion-tab-bar>
      </ion-tabs>
    </ion-page>
  </template>
  
  <script lang="ts">
    import { IonPage, IonTabs, IonRouterOutlet, IonTabBar, IonTabButton, IonLabel, IonIcon } from '@ionic/vue';
  
    import { home, fingerPrint, cart, person} from 'ionicons/icons';
  
    export default {
      components: { IonPage, IonTabs, IonRouterOutlet, IonTabBar, IonTabButton, IonLabel, IonIcon },
      data() {
        return {
          home,
          fingerPrint,
          cart,
          person
        };
      },
    };
  </script>