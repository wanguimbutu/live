<template>
  <!-- Offline warning — always visible when no connection -->
  <div v-if="!isOnline" class="banner banner-offline">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="1" y1="1" x2="23" y2="23"/>
      <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55M5 12.55a10.94 10.94 0 0 1 5.17-2.39M10.71 5.05A16 16 0 0 1 22.56 9M1.42 9a15.91 15.91 0 0 1 4.7-2.88M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/>
    </svg>
    <span>You're offline — orders will be saved locally</span>
  </div>

  <!-- Pending sync banner — visible when online and there are queued orders -->
  <div v-else-if="pendingCount > 0" class="banner banner-pending">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
      :class="{ 'spin': isSyncing }">
      <polyline points="1 4 1 10 7 10"/>
      <path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
    </svg>
    <span v-if="isSyncing">Syncing {{ pendingCount }} order{{ pendingCount > 1 ? 's' : '' }}…</span>
    <span v-else>{{ pendingCount }} order{{ pendingCount > 1 ? 's' : '' }} pending sync</span>
    <button v-if="!isSyncing" class="sync-btn" @click="syncAll">Sync now</button>
  </div>

  <!-- Success flash -->
  <div v-else-if="showSuccess" class="banner banner-success">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
    <span>All orders synced</span>
  </div>
</template>

<script setup>
import { watch, ref } from 'vue'
import { useOfflineQueue, syncAll } from '../composables/useOfflineQueue'

const { isOnline, isSyncing, pendingCount, lastSyncResult } = useOfflineQueue()

const showSuccess = ref(false)
let successTimer = null

watch(lastSyncResult, (result) => {
  if (result && result.synced > 0 && result.failed === 0) {
    showSuccess.value = true
    clearTimeout(successTimer)
    successTimer = setTimeout(() => { showSuccess.value = false }, 3000)
  }
})
</script>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 0.82rem;
  font-weight: 500;
  width: 100%;
}

.banner-offline {
  background: #1e293b;
  color: #94a3b8;
}

.banner-pending {
  background: #fef3c7;
  color: #92400e;
}

.banner-success {
  background: #d1fae5;
  color: #065f46;
}

.sync-btn {
  margin-left: auto;
  background: #d97706;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.sync-btn:active {
  opacity: 0.8;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
