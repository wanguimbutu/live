/**
 * usePresence — tracks location + battery and syncs to ERPNext.
 *
 * Battery-friendly design:
 *  - Uses LOW accuracy (cell/WiFi towers, not GPS chip) — biggest battery win
 *  - Polls with setTimeout instead of watchPosition — no continuous GPS wake-up
 *  - 5-minute poll interval (not 2 minutes)
 *  - Skips sync entirely when battery ≤ 15% and not charging
 *  - Only sends a network request when the user has moved > 100 m
 *  - Stops polling when the page is hidden (background tab / locked screen)
 */
import { ref, onUnmounted } from 'vue'

const SYNC_INTERVAL_MS = 5 * 60 * 1000  // 5 minutes
const MIN_DISTANCE_METERS = 100           // only push if moved > 100 m
const LOW_BATTERY_THRESHOLD = 15          // % — pause tracking below this

// ─── module-level singletons (one instance for the whole app) ─────────────────
let syncTimer = null
let batteryRef = null
let boundOnVisible = null
let lastSyncedLat = null
let lastSyncedLng = null

const latitude = ref(null)
const longitude = ref(null)
const accuracy = ref(null)
const battery = ref(null)
const isCharging = ref(false)
const syncError = ref(null)
const lastSynced = ref(null)

// ─── helpers ─────────────────────────────────────────────────────────────────
function haversineMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000
  const toRad = (d) => (d * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function isBatteryLow() {
  return battery.value !== null && battery.value <= LOW_BATTERY_THRESHOLD && !isCharging.value
}

// ─── single location read (no continuous watchPosition) ──────────────────────
function readLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) { resolve(false); return }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        latitude.value = pos.coords.latitude
        longitude.value = pos.coords.longitude
        accuracy.value  = pos.coords.accuracy
        resolve(true)
      },
      () => resolve(false),
      {
        enableHighAccuracy: false,  // use network/WiFi — much less battery
        timeout: 10000,
        maximumAge: 4 * 60 * 1000, // accept a cached fix up to 4 min old
      }
    )
  })
}

// ─── sync ─────────────────────────────────────────────────────────────────────
async function syncPresence() {
  // Skip when battery is low or page is hidden
  if (isBatteryLow() || document.hidden) return

  const gotFix = await readLocation()
  if (!gotFix || latitude.value === null) return

  // Skip if haven't moved enough
  if (
    lastSyncedLat !== null &&
    haversineMeters(lastSyncedLat, lastSyncedLng, latitude.value, longitude.value) <
      MIN_DISTANCE_METERS
  ) return

  try {
    const res = await fetch('/api/method/live.api.presence.update_presence', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      credentials: 'include',
      body: JSON.stringify({
        latitude: latitude.value,
        longitude: longitude.value,
        accuracy: accuracy.value,
        battery_level: battery.value,
        is_charging: isCharging.value ? 1 : 0,
      }),
    })
    if (!res.ok) throw new Error(await res.text())
    lastSyncedLat = latitude.value
    lastSyncedLng = longitude.value
    lastSynced.value = new Date()
    syncError.value = null
  } catch (err) {
    syncError.value = err.message
  }
}

function schedulePoll() {
  syncTimer = setTimeout(async () => {
    await syncPresence()
    schedulePoll() // reschedule only after previous call finishes
  }, SYNC_INTERVAL_MS)
}

// ─── battery ─────────────────────────────────────────────────────────────────
async function initBattery() {
  if (!('getBattery' in navigator)) return
  try {
    batteryRef = await navigator.getBattery()
    const read = () => {
      battery.value = Math.round(batteryRef.level * 100)
      isCharging.value = batteryRef.charging
    }
    read()
    batteryRef.addEventListener('levelchange', read)
    batteryRef.addEventListener('chargingchange', read)
  } catch (e) {
    console.warn('[presence] battery API:', e.message)
  }
}

// ─── composable ──────────────────────────────────────────────────────────────
export function usePresence() {
  initBattery()

  // First sync after 8s (let the app settle), then on a schedule
  const initTimer = setTimeout(() => {
    syncPresence()
    schedulePoll()
  }, 8000)

  // Sync when tab becomes visible again after being hidden
  boundOnVisible = () => { if (!document.hidden) syncPresence() }
  document.addEventListener('visibilitychange', boundOnVisible)

  onUnmounted(() => {
    clearTimeout(initTimer)
    clearTimeout(syncTimer)
    document.removeEventListener('visibilitychange', boundOnVisible)
    if (batteryRef) {
      batteryRef.removeEventListener('levelchange', () => {})
      batteryRef.removeEventListener('chargingchange', () => {})
    }
  })

  return { latitude, longitude, accuracy, battery, isCharging, lastSynced, syncError }
}
