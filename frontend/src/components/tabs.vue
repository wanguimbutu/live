<template>
  <ion-page>
    <!-- Sync/offline banner sits above all tab content -->
    <SyncBanner />
    <!-- PWA install prompt (Android native banner or iOS guide) -->
    <InstallPrompt />
    <ion-tabs>
      <ion-router-outlet></ion-router-outlet>
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="home" href="/homePage">
          <ion-icon :icon="home" />
          <ion-label>Home</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="visits" href="/visits">
          <ion-icon :icon="location" />
          <ion-label>Visits</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="sales" href="/salesOrderList">
          <ion-icon :icon="cart" />
          <ion-label>Orders</ion-label>
          <ion-badge v-if="pendingCount > 0" color="warning">{{ pendingCount }}</ion-badge>
        </ion-tab-button>

        <ion-tab-button tab="customer" href="/customerList">
          <ion-icon :icon="person" />
          <ion-label>Customers</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="attendance" href="/attendance">
          <ion-icon :icon="fingerPrint" />
          <ion-label>Attendance</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="collections" href="/collections">
          <ion-icon :icon="wallet" />
          <ion-label>Collections</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="dashboard" href="/dashboard">
          <ion-icon :icon="barChart" />
          <ion-label>Dashboard</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-page>
</template>

<script setup>
import { IonPage, IonTabs, IonRouterOutlet, IonTabBar, IonTabButton, IonLabel, IonIcon, IonBadge } from '@ionic/vue'
import { home, fingerPrint, cart, person, location, wallet, barChart } from 'ionicons/icons'
import SyncBanner from './SyncBanner.vue'
import InstallPrompt from './InstallPrompt.vue'
import { useOfflineQueue } from '../composables/useOfflineQueue'

const { pendingCount } = useOfflineQueue()
</script>