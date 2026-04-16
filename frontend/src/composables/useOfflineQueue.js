/**
 * useOfflineQueue — stores pending Sales Orders in localStorage and syncs
 * them to ERPNext when connectivity is restored.
 *
 * Module-level state means every component that calls useOfflineQueue()
 * shares the same queue — no duplication, no prop drilling.
 */
import { ref, computed, onUnmounted } from 'vue'

const STORAGE_KEY = 'live_offline_orders'

// ─── module-level shared state ───────────────────────────────────────────────
const queue = ref([])
const isOnline = ref(navigator.onLine)
const isSyncing = ref(false)
const lastSyncResult = ref(null) // { synced, failed, at }

// ─── persistence ─────────────────────────────────────────────────────────────
function loadQueue() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    queue.value = raw ? JSON.parse(raw) : []
  } catch {
    queue.value = []
  }
}

function persistQueue() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(queue.value))
}

loadQueue()

// ─── public helpers ───────────────────────────────────────────────────────────
function generateId() {
  return `offline_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
}

/**
 * Save an order payload to the offline queue.
 * Returns the generated local ID so the caller can reference it.
 */
export function addToQueue(orderData) {
  const entry = {
    id: generateId(),
    order: { ...orderData },
    savedAt: new Date().toISOString(),
    status: 'pending', // 'pending' | 'syncing' | 'failed'
    error: null,
  }
  queue.value.push(entry)
  persistQueue()
  return entry.id
}

/**
 * Remove a single entry from the queue (e.g. after the user deletes it).
 */
export function removeFromQueue(id) {
  queue.value = queue.value.filter((e) => e.id !== id)
  persistQueue()
}

// ─── sync logic ───────────────────────────────────────────────────────────────
async function syncEntry(entry) {
  const res = await fetch('/api/resource/Sales Order', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
    },
    credentials: 'include',
    body: JSON.stringify(entry.order),
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(txt || `HTTP ${res.status}`)
  }
  return res.json()
}

/**
 * Attempt to sync all pending / previously-failed entries.
 * Safe to call even when offline — it will bail out immediately.
 */
export async function syncAll() {
  if (!isOnline.value || isSyncing.value) return

  const pending = queue.value.filter(
    (e) => e.status === 'pending' || e.status === 'failed'
  )
  if (!pending.length) return

  isSyncing.value = true
  let synced = 0
  let failed = 0

  for (const entry of pending) {
    entry.status = 'syncing'
    try {
      await syncEntry(entry)
      queue.value = queue.value.filter((e) => e.id !== entry.id)
      synced++
    } catch (err) {
      entry.status = 'failed'
      entry.error = err.message
      failed++
    }
  }

  persistQueue()
  isSyncing.value = false
  lastSyncResult.value = { synced, failed, at: new Date() }
}

// ─── connectivity listeners (module-level, registered once) ──────────────────
function onOnline() {
  isOnline.value = true
  syncAll()
}
function onOffline() {
  isOnline.value = false
}
window.addEventListener('online', onOnline)
window.addEventListener('offline', onOffline)

// ─── composable ──────────────────────────────────────────────────────────────
export function useOfflineQueue() {
  return {
    queue,
    isOnline,
    isSyncing,
    lastSyncResult,
    pendingCount: computed(
      () => queue.value.filter((e) => e.status !== 'synced').length
    ),
    addToQueue,
    removeFromQueue,
    syncAll,
  }
}
