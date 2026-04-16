<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="visits-root">

        <!-- Header -->
        <div class="visits-header">
          <div>
            <h1 class="visits-title">Visits</h1>
            <p class="visits-date">{{ todayLabel }}</p>
          </div>
          <button class="map-toggle-btn" @click="showMap = !showMap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
              <line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>
            </svg>
            {{ showMap ? 'Hide map' : 'My trail' }}
          </button>
        </div>

        <!-- Day trail map -->
        <div v-show="showMap" class="trail-map-card">
          <div id="trail-map" class="trail-map"></div>
          <div class="trail-legend">
            <span class="legend-dot dot-trail"></span> Trail
            <span class="legend-dot dot-visit" style="margin-left:12px"></span> Visits
          </div>
        </div>

        <!-- Active visit banner -->
        <div v-if="activeVisit" class="active-visit-banner">
          <div class="active-visit-pulse"></div>
          <div class="active-visit-info">
            <p class="active-customer">{{ activeVisit.customer_name }}</p>
            <p class="active-timer">{{ formatDuration(elapsedSeconds) }}</p>
          </div>
          <button class="end-visit-btn" @click="openEndSheet">End visit</button>
        </div>

        <!-- Start visit section -->
        <div v-if="!activeVisit" class="start-section">
          <div class="search-wrap">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              v-model="customerSearch"
              class="search-input"
              placeholder="Search customer to visit…"
              @input="searchCustomers"
            />
          </div>

          <div v-if="searchResults.length" class="search-results">
            <div
              v-for="c in searchResults"
              :key="c.name"
              class="search-result-item"
              @click="selectCustomer(c)"
            >
              <div class="result-avatar">{{ c.customer_name[0].toUpperCase() }}</div>
              <div class="result-info">
                <p class="result-name">{{ c.customer_name }}</p>
                <p class="result-id">{{ c.name }}</p>
              </div>
              <button class="visit-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
                  <circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.5 8 14 8 14s8-8.5 8-14a8 8 0 0 0-8-8z"/>
                </svg>
                Visit
              </button>
            </div>
          </div>
          <div v-else-if="customerSearch.length > 1 && !searching" class="search-empty">
            No customers found for "{{ customerSearch }}"
          </div>
        </div>

        <!-- Error -->
        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

        <!-- Today's visits -->
        <div class="section-label">Today's Visits ({{ todayVisits.length }})</div>

        <div v-if="loadingVisits" class="visits-loading"><div class="page-spinner"></div></div>
        <div v-else-if="todayVisits.length === 0" class="visits-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36" style="color:#cbd5e1">
            <circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.5 8 14 8 14s8-8.5 8-14a8 8 0 0 0-8-8z"/>
          </svg>
          <p>No visits recorded today</p>
        </div>
        <div v-else class="visit-cards">
          <div
            v-for="v in todayVisits"
            :key="v.name"
            class="visit-card"
            :class="{ 'visit-card-active': activeVisit && activeVisit.name === v.name }"
          >
            <div class="visit-card-top">
              <div class="visit-avatar">{{ (v.customer_name || '?')[0].toUpperCase() }}</div>
              <div class="visit-card-info">
                <p class="visit-customer">{{ v.customer_name }}</p>
                <p class="visit-time">{{ formatTime(v.start_time) }} {{ v.end_time ? '→ ' + formatTime(v.end_time) : '(ongoing)' }}</p>
              </div>
              <div class="visit-duration" v-if="v.duration_minutes">
                {{ v.duration_minutes }}<span style="font-size:0.65rem;font-weight:500">m</span>
              </div>
            </div>
            <div class="visit-card-body" v-if="v.notes || v.sales_order">
              <p class="visit-note" v-if="v.notes">{{ v.notes }}</p>
              <span class="visit-order-tag" v-if="v.sales_order">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="11" height="11">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                {{ v.sales_order }}
              </span>
            </div>
          </div>
        </div>

        <!-- End Visit Bottom Sheet -->
        <div v-if="showEndSheet" class="sheet-backdrop" @click.self="showEndSheet = false">
          <div class="sheet">
            <div class="sheet-handle"></div>
            <h3 class="sheet-title">End Visit</h3>
            <p class="sheet-subtitle">{{ activeVisit?.customer_name }} · {{ formatDuration(elapsedSeconds) }}</p>

            <!-- Inline new order option -->
            <div class="sheet-section-label">Sales Order (optional)</div>
            <div class="so-choice">
              <button
                class="so-choice-btn"
                :class="orderMode === 'none' ? 'so-choice-active' : ''"
                @click="orderMode = 'none'"
              >None</button>
              <button
                class="so-choice-btn"
                :class="orderMode === 'existing' ? 'so-choice-active' : ''"
                @click="orderMode = 'existing'; loadOrdersForCustomer()"
              >Pick existing</button>
              <button
                class="so-choice-btn"
                :class="orderMode === 'new' ? 'so-choice-active' : ''"
                @click="orderMode = 'new'"
              >Create new</button>
            </div>

            <div v-if="orderMode === 'existing'" class="order-picker">
              <div v-if="loadingOrders" class="mini-loading"><div class="mini-spinner"></div></div>
              <div v-else-if="customerOrders.length === 0" class="picker-empty">No orders for this customer</div>
              <div
                v-for="o in customerOrders"
                :key="o.name"
                class="order-pick-item"
                :class="{ 'order-selected': selectedOrder === o.name }"
                @click="selectedOrder = o.name"
              >
                <div>
                  <p class="op-name">{{ o.name }}</p>
                  <p class="op-meta">{{ o.status }} · {{ formatDate(o.transaction_date) }}</p>
                </div>
                <span v-if="selectedOrder === o.name" class="op-check">✓</span>
              </div>
            </div>

            <div v-if="orderMode === 'new'" class="new-order-note">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              End this visit first, then you'll be taken to the new order form with this customer pre-filled.
            </div>

            <div class="sheet-section-label">Notes</div>
            <textarea
              v-model="endNotes"
              class="notes-input"
              placeholder="What was discussed? Any follow-ups…"
              rows="3"
            ></textarea>

            <button class="end-confirm-btn" :disabled="endingVisit" @click="confirmEndVisit">
              <span v-if="endingVisit" class="btn-spinner"></span>
              <span v-else>Save &amp; End Visit</span>
            </button>
          </div>
        </div>

      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix leaflet icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

const router = useRouter()

// State
const customerSearch = ref('')
const searchResults = ref([])
const searching = ref(false)
let searchDebounce = null

const activeVisit = ref(null)   // { name, customer, customer_name, start_time }
const elapsedSeconds = ref(0)
let timerInterval = null
let trailInterval = null

const showMap = ref(false)
const showEndSheet = ref(false)
const endNotes = ref('')
const orderMode = ref('none')
const selectedOrder = ref(null)
const customerOrders = ref([])
const loadingOrders = ref(false)
const endingVisit = ref(false)
const errorMsg = ref('')

const todayVisits = ref([])
const loadingVisits = ref(true)

let mapInstance = null
let trailPolyline = null
const trailPoints = ref([])   // [{lat, lng}] for today
const visitMarkers = []

// Persist active visit in localStorage so a page refresh doesn't lose it
const ACTIVE_KEY = 'live_active_visit'

const todayLabel = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

// ── Customer search ──────────────────────────────────────────────────────────
function searchCustomers() {
  clearTimeout(searchDebounce)
  if (customerSearch.value.length < 2) { searchResults.value = []; return }
  searching.value = true
  searchDebounce = setTimeout(async () => {
    try {
      const res = await fetch('/api/method/frappe.desk.reportview.get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          doctype: 'Customer',
          fields: ['name', 'customer_name'],
          filters: [['customer_name', 'like', `%${customerSearch.value}%`]],
          limit_page_length: 10,
          order_by: 'customer_name asc',
        }),
      })
      const data = await res.json()
      searchResults.value = data?.message?.values?.map(v => ({ name: v[0], customer_name: v[1] })) || []
    } catch (e) { console.error(e) }
    finally { searching.value = false }
  }, 300)
}

// ── Start visit ──────────────────────────────────────────────────────────────
async function selectCustomer(c) {
  errorMsg.value = ''
  const pos = await getLocation()
  try {
    const res = await fetch('/api/method/live.api.visits.start_visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        customer: c.name,
        latitude: pos?.latitude ?? null,
        longitude: pos?.longitude ?? null,
        accuracy: pos?.accuracy ?? null,
      }),
    })
    if (!res.ok) throw new Error('Failed to start visit')
    const { message } = await res.json()
    activeVisit.value = {
      name: message.name,
      customer: c.name,
      customer_name: c.customer_name,
      start_time: message.start_time,
    }
    localStorage.setItem(ACTIVE_KEY, JSON.stringify(activeVisit.value))
    customerSearch.value = ''
    searchResults.value = []
    startTimer()
    startTrailTracking(pos)
    await loadTodayVisits()
  } catch (e) {
    errorMsg.value = 'Could not start visit. Please try again.'
    console.error(e)
  }
}

// ── Timer ────────────────────────────────────────────────────────────────────
function startTimer() {
  clearInterval(timerInterval)
  elapsedSeconds.value = activeVisit.value
    ? Math.floor((Date.now() - new Date(activeVisit.value.start_time)) / 1000)
    : 0
  timerInterval = setInterval(() => { elapsedSeconds.value++ }, 1000)
}

// ── Trail tracking ───────────────────────────────────────────────────────────
function startTrailTracking(initialPos) {
  if (initialPos) addTrailPoint(initialPos.latitude, initialPos.longitude, initialPos.accuracy)
  clearInterval(trailInterval)
  trailInterval = setInterval(async () => {
    if (!activeVisit.value) { clearInterval(trailInterval); return }
    const pos = await getLocation()
    if (pos) addTrailPoint(pos.latitude, pos.longitude, pos.accuracy)
  }, 60000) // every 60 seconds
}

async function addTrailPoint(lat, lng, accuracy) {
  trailPoints.value.push({ lat, lng })
  updateTrailOnMap()
  try {
    await fetch('/api/method/live.api.visits.add_trail_point', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ latitude: lat, longitude: lng, accuracy: accuracy ?? null }),
    })
  } catch (e) { console.warn('Trail point save failed:', e) }
}

// ── Map ──────────────────────────────────────────────────────────────────────
watch(showMap, async (val) => {
  if (val) {
    await nextTick()
    initMap()
  }
})

function initMap() {
  const el = document.getElementById('trail-map')
  if (!el) return
  if (mapInstance) { mapInstance.invalidateSize(); return }

  mapInstance = L.map('trail-map').setView([0, 0], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
  }).addTo(mapInstance)

  // Draw existing trail
  updateTrailOnMap()

  // Draw visit markers
  renderVisitMarkers()

  // Pan to last trail point or first visit
  if (trailPoints.value.length) {
    mapInstance.setView([trailPoints.value.at(-1).lat, trailPoints.value.at(-1).lng], 14)
  } else if (todayVisits.value.length) {
    const v = todayVisits.value.find(v => v.latitude)
    if (v) mapInstance.setView([v.latitude, v.longitude], 14)
  }
}

function updateTrailOnMap() {
  if (!mapInstance) return
  const latlngs = trailPoints.value.map(p => [p.lat, p.lng])
  if (trailPolyline) {
    trailPolyline.setLatLngs(latlngs)
  } else if (latlngs.length >= 2) {
    trailPolyline = L.polyline(latlngs, { color: '#1d4ed8', weight: 3, opacity: 0.7 }).addTo(mapInstance)
  }
  // Move map to latest point
  if (latlngs.length) {
    mapInstance.panTo(latlngs.at(-1))
  }
}

function renderVisitMarkers() {
  if (!mapInstance) return
  visitMarkers.forEach(m => m.remove())
  visitMarkers.length = 0

  todayVisits.value.forEach(v => {
    if (!v.latitude || !v.longitude) return
    const icon = L.divIcon({
      html: `<div class="visit-map-pin">${(v.customer_name || '?')[0]}</div>`,
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 32],
    })
    const m = L.marker([v.latitude, v.longitude], { icon })
      .addTo(mapInstance)
      .bindPopup(`<strong>${v.customer_name}</strong><br>${formatTime(v.start_time)}${v.duration_minutes ? ` · ${v.duration_minutes}m` : ''}${v.notes ? `<br><em>${v.notes}</em>` : ''}`)
    visitMarkers.push(m)
  })
}

// ── End visit ────────────────────────────────────────────────────────────────
function openEndSheet() {
  endNotes.value = ''
  orderMode.value = 'none'
  selectedOrder.value = null
  customerOrders.value = []
  showEndSheet.value = true
}

async function loadOrdersForCustomer() {
  if (!activeVisit.value) return
  loadingOrders.value = true
  try {
    const res = await fetch(
      `/api/resource/Sales%20Order?filters=[["customer","=","${encodeURIComponent(activeVisit.value.customer)}"]]&fields=["name","status","transaction_date","grand_total"]&order_by=creation%20desc&limit=10`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    customerOrders.value = data || []
  } catch (e) { console.error(e) }
  finally { loadingOrders.value = false }
}

async function confirmEndVisit() {
  if (!activeVisit.value) return
  endingVisit.value = true
  errorMsg.value = ''
  const pos = await getLocation()
  try {
    const body = {
      visit_name: activeVisit.value.name,
      notes: endNotes.value || null,
      sales_order: orderMode.value === 'existing' ? selectedOrder.value : null,
      latitude: pos?.latitude ?? null,
      longitude: pos?.longitude ?? null,
      accuracy: pos?.accuracy ?? null,
    }
    const res = await fetch('/api/method/live.api.visits.end_visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error('Failed to end visit')

    clearInterval(timerInterval)
    clearInterval(trailInterval)

    const goCreateOrder = orderMode.value === 'new'
    const customer = activeVisit.value.customer

    activeVisit.value = null
    localStorage.removeItem(ACTIVE_KEY)
    showEndSheet.value = false
    elapsedSeconds.value = 0

    await loadTodayVisits()
    renderVisitMarkers()

    if (goCreateOrder) {
      router.push({ path: '/add-sales-order', query: { customer } })
    }
  } catch (e) {
    errorMsg.value = 'Could not end visit. Please try again.'
    console.error(e)
  } finally {
    endingVisit.value = false
  }
}

// ── Data loading ─────────────────────────────────────────────────────────────
async function loadTodayVisits() {
  loadingVisits.value = true
  try {
    const res = await fetch('/api/method/live.api.visits.get_my_visits', {
      credentials: 'include',
    })
    const { message } = await res.json()
    todayVisits.value = message.visits || []

    // Populate trail from server points
    const pts = (message.trail || []).map(t => ({ lat: t.latitude, lng: t.longitude }))
    trailPoints.value = pts
    updateTrailOnMap()
    renderVisitMarkers()
  } catch (e) {
    console.error('Failed to load today visits:', e)
  } finally {
    loadingVisits.value = false
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function getLocation() {
  return new Promise(resolve => {
    if (!navigator.geolocation) return resolve(null)
    navigator.geolocation.getCurrentPosition(
      pos => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude, accuracy: pos.coords.accuracy }),
      () => resolve(null),
      { enableHighAccuracy: false, timeout: 8000 }
    )
  })
}

function formatDuration(secs) {
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  if (h > 0) return `${h}h ${String(m).padStart(2,'0')}m`
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
}

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(async () => {
  // Restore active visit from localStorage
  const saved = localStorage.getItem(ACTIVE_KEY)
  if (saved) {
    activeVisit.value = JSON.parse(saved)
    startTimer()
    startTrailTracking(null)
  }
  await loadTodayVisits()
})

onUnmounted(() => {
  clearInterval(timerInterval)
  clearInterval(trailInterval)
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
})
</script>

<style scoped>
.visits-root {
  background: #f8fafc;
  min-height: 100%;
  padding: 0 16px 90px;
}

/* Header */
.visits-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 20px 0 12px;
}
.visits-title { font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0; }
.visits-date { font-size: 0.78rem; color: #94a3b8; margin: 2px 0 0; }
.map-toggle-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; background: #fff;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.8rem; font-weight: 600; color: #475569;
  cursor: pointer; white-space: nowrap;
}

/* Trail map */
.trail-map-card {
  background: #fff; border-radius: 16px;
  border: 1px solid #f1f5f9; overflow: hidden;
  margin-bottom: 14px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.05);
}
.trail-map { height: 240px; width: 100%; }
.trail-legend {
  padding: 8px 14px; display: flex; align-items: center;
  font-size: 0.72rem; color: #64748b;
}
.legend-dot {
  display: inline-block; width: 10px; height: 10px;
  border-radius: 50%; margin-right: 5px;
}
.dot-trail { background: #1d4ed8; }
.dot-visit { background: #f59e0b; }

/* Active visit banner */
.active-visit-banner {
  display: flex; align-items: center; gap: 12px;
  background: #eff6ff; border: 1.5px solid #bfdbfe;
  border-radius: 14px; padding: 14px 16px;
  margin-bottom: 14px;
}
.active-visit-pulse {
  width: 12px; height: 12px; border-radius: 50%;
  background: #22c55e; flex-shrink: 0;
  box-shadow: 0 0 0 0 rgba(34,197,94,0.4);
  animation: pulse 1.5s ease infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  70% { box-shadow: 0 0 0 8px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.active-visit-info { flex: 1; }
.active-customer { font-size: 0.9rem; font-weight: 700; color: #1e3a8a; margin: 0; }
.active-timer { font-size: 1.1rem; font-weight: 800; color: #1d4ed8; margin: 2px 0 0; font-variant-numeric: tabular-nums; }
.end-visit-btn {
  padding: 8px 16px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 10px;
  font-size: 0.82rem; font-weight: 700; cursor: pointer;
  white-space: nowrap; flex-shrink: 0;
}

/* Search */
.start-section { margin-bottom: 14px; }
.search-wrap { position: relative; margin-bottom: 8px; }
.search-icon {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: #94a3b8; pointer-events: none;
}
.search-input {
  width: 100%; padding: 12px 12px 12px 36px;
  border: 1.5px solid #e2e8f0; border-radius: 12px;
  background: #fff; font-size: 0.9rem; color: #1e293b;
  box-sizing: border-box;
}
.search-input:focus { outline: none; border-color: #1d4ed8; }

.search-results {
  background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 14px; overflow: hidden;
}
.search-result-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-bottom: 1px solid #f8fafc;
  cursor: pointer;
}
.search-result-item:last-child { border-bottom: none; }
.search-result-item:active { background: #f8fafc; }
.result-avatar {
  width: 36px; height: 36px; background: #eff6ff; color: #1d4ed8;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem; flex-shrink: 0;
}
.result-info { flex: 1; min-width: 0; }
.result-name { font-size: 0.88rem; font-weight: 600; color: #1e293b; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.result-id { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.visit-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 6px 12px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 8px; font-size: 0.78rem; font-weight: 700;
  cursor: pointer; flex-shrink: 0;
}
.search-empty { text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 16px; }

.error-banner {
  background: #fef2f2; border: 1px solid #fecaca; color: #dc2626;
  border-radius: 10px; padding: 10px 14px; font-size: 0.82rem;
  margin-bottom: 12px;
}

/* Section label */
.section-label {
  font-size: 0.7rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.05em;
  margin: 0 0 10px;
}

/* States */
.visits-loading { display: flex; justify-content: center; padding: 40px; }
.page-spinner {
  width: 28px; height: 28px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.visits-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 32px 20px; color: #94a3b8; font-size: 0.85rem;
}

/* Visit cards */
.visit-cards { display: flex; flex-direction: column; gap: 10px; }
.visit-card {
  background: #fff; border: 1.5px solid #f1f5f9;
  border-radius: 14px; padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.visit-card-active { border-color: #bfdbfe; background: #eff6ff; }
.visit-card-top { display: flex; align-items: center; gap: 12px; }
.visit-avatar {
  width: 38px; height: 38px; background: #f1f5f9; color: #475569;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem; flex-shrink: 0;
}
.visit-card-info { flex: 1; min-width: 0; }
.visit-customer { font-size: 0.9rem; font-weight: 700; color: #0f172a; margin: 0; }
.visit-time { font-size: 0.75rem; color: #94a3b8; margin: 2px 0 0; }
.visit-duration {
  font-size: 1.1rem; font-weight: 800; color: #1d4ed8;
  flex-shrink: 0;
}
.visit-card-body { margin-top: 8px; padding-top: 8px; border-top: 1px solid #f8fafc; }
.visit-note { font-size: 0.82rem; color: #475569; margin: 0 0 6px; line-height: 1.4; }
.visit-order-tag {
  display: inline-flex; align-items: center; gap: 4px;
  background: #eff6ff; color: #1d4ed8; border-radius: 6px;
  padding: 3px 8px; font-size: 0.72rem; font-weight: 600;
}

/* End visit sheet */
.sheet-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  z-index: 300; display: flex; align-items: flex-end; justify-content: center;
}
.sheet {
  background: #fff; border-radius: 24px 24px 0 0;
  width: 100%; max-width: 540px;
  padding: 16px 20px calc(24px + env(safe-area-inset-bottom, 0px));
  max-height: 85vh; overflow-y: auto;
}
.sheet-handle {
  width: 40px; height: 4px; background: #e2e8f0;
  border-radius: 2px; margin: 0 auto 16px;
}
.sheet-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0 0 4px; }
.sheet-subtitle { font-size: 0.82rem; color: #94a3b8; margin: 0 0 16px; }
.sheet-section-label {
  font-size: 0.7rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.05em;
  margin: 14px 0 8px;
}

/* SO choice */
.so-choice { display: flex; gap: 6px; margin-bottom: 10px; }
.so-choice-btn {
  flex: 1; padding: 8px 6px; border: 1.5px solid #e2e8f0;
  border-radius: 10px; font-size: 0.78rem; font-weight: 600;
  color: #64748b; background: #fff; cursor: pointer;
}
.so-choice-active { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }

.order-picker { max-height: 180px; overflow-y: auto; margin-bottom: 4px; }
.mini-loading { display: flex; justify-content: center; padding: 16px; }
.mini-spinner {
  width: 20px; height: 20px;
  border: 2px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.picker-empty { text-align: center; color: #94a3b8; font-size: 0.82rem; padding: 12px; }
.order-pick-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px;
  cursor: pointer; margin-bottom: 6px;
}
.order-selected { border-color: #1d4ed8; background: #eff6ff; }
.op-name { font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0; }
.op-meta { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.op-check { color: #1d4ed8; font-weight: 800; }

.new-order-note {
  display: flex; align-items: flex-start; gap: 8px;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 8px; padding: 10px 12px;
  font-size: 0.8rem; color: #92400e; margin-bottom: 4px; line-height: 1.4;
}
.notes-input {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; background: #fff;
  box-sizing: border-box; resize: none;
  margin-bottom: 14px;
}
.notes-input:focus { outline: none; border-color: #1d4ed8; }

.end-confirm-btn {
  width: 100%; padding: 14px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.95rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.end-confirm-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>

<!-- Global styles for Leaflet visit pin -->
<style>
.visit-map-pin {
  width: 32px; height: 32px;
  background: #f59e0b; color: #fff;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.8rem;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.visit-map-pin span { transform: rotate(45deg); }
</style>
