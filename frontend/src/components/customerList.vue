<template>
  <div class="customers-root">
    <!-- Header -->
    <div class="customers-header">
      <h1 class="customers-title">Customers</h1>
      <button class="add-btn" @click="showAddCustomerModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
      </button>
    </div>

    <!-- Search -->
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        class="search-input"
        v-model="searchQuery"
        @input="handleSearch"
        placeholder="Search customers…"
        type="text"
      />
    </div>

    <!-- Customer cards -->
    <div v-if="customers.length === 0 && !loadingCustomers" class="empty-state">
      <p>No customers found</p>
    </div>
    <div v-if="loadingCustomers" class="loading-state">
      <div class="page-spinner"></div>
    </div>
    <div v-else class="customer-list">
      <div
        v-for="customer in customers"
        :key="customer.name"
        class="customer-card"
        @click="viewCustomerDetails(customer)"
      >
        <div class="customer-avatar">{{ (customer.customer_name || '?')[0].toUpperCase() }}</div>
        <div class="customer-info">
          <p class="customer-name">{{ customer.customer_name }}</p>
          <p class="customer-id">{{ customer.name }}</p>
        </div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="customer-chevron">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </div>
    </div>

    <!-- Load more -->
    <div class="load-more-wrap" v-if="hasMore && !loadingCustomers">
      <button class="load-more-btn" @click="loadMore">Load more</button>
    </div>


    <!-- ── Add Customer Modal ── -->
    <div v-if="showAddCustomerModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-sheet">
        <div class="modal-header">
          <h3 class="modal-title">New Customer</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="addError" class="form-error">{{ addError }}</div>
          <div class="form-group">
            <label class="form-label">Customer Name</label>
            <input v-model="newCustomer.customer_name" type="text" class="form-input" placeholder="e.g. Acme Ltd" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn-primary" :disabled="addLoading" @click="addCustomer">
              <span v-if="addLoading" class="btn-spinner"></span>
              <span v-else>Create</span>
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- ── Customer Visit Modal ── -->
    <div v-if="showCustomerVisitModal" class="modal-backdrop" @click.self="closeVisitModal">
      <div class="modal-sheet modal-tall">
        <div class="modal-header">
          <div>
            <h3 class="modal-title">{{ currentCustomer.customer_name }}</h3>
            <p class="modal-subtitle">Customer Visit</p>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <button class="btn-timeline" @click="$router.push(`/customer/${currentCustomer.name}/timeline`); closeVisitModal()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
              Timeline
            </button>
            <button class="modal-close" @click="closeVisitModal">✕</button>
          </div>
        </div>
        <div class="modal-body">
          <!-- Visit timer -->
          <div class="visit-timer-card" :class="visitInProgress ? 'timer-active' : ''">
            <div class="timer-display">{{ timer }}</div>
            <p class="timer-label">{{ visitInProgress ? 'Visit in progress' : 'Not started' }}</p>
          </div>

          <div class="visit-actions">
            <button v-if="!visitInProgress" class="btn-primary" @click="startVisit">Start Visit</button>
            <button v-else class="btn-danger" @click="endVisit">End Visit &amp; Record</button>
          </div>

          <!-- Sales Order section -->
          <div class="section-divider">
            <span>Sales Order</span>
          </div>

          <div class="so-tabs">
            <button
              class="so-tab"
              :class="soMode === 'existing' ? 'so-tab-active' : ''"
              @click="soMode = 'existing'; loadExistingOrders()"
            >Pick Existing</button>
            <button
              class="so-tab"
              :class="soMode === 'new' ? 'so-tab-active' : ''"
              @click="soMode = 'new'; $router.push('/add-sales-order')"
            >Create New</button>
          </div>

          <div v-if="soMode === 'existing'" class="so-picker">
            <div v-if="loadingOrders" class="so-loading">
              <div class="mini-spinner"></div>
            </div>
            <div v-else-if="existingOrders.length === 0" class="so-empty">
              No existing orders for this customer
            </div>
            <div
              v-else
              v-for="order in existingOrders"
              :key="order.name"
              class="so-item"
              :class="selectedOrder === order.name ? 'so-item-selected' : ''"
              @click="selectedOrder = order.name"
            >
              <div class="so-item-info">
                <p class="so-name">{{ order.name }}</p>
                <p class="so-meta">{{ order.status }} · {{ formatDate(order.transaction_date) }}</p>
              </div>
              <div v-if="selectedOrder === order.name" class="so-check">✓</div>
            </div>
          </div>

          <!-- Location capture -->
          <div class="section-divider"><span>Location</span></div>

          <button class="btn-secondary full-width" @click="captureLocationAndSave" :disabled="locLoading">
            <span v-if="locLoading" class="btn-spinner-dark"></span>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/>
            </svg>
            {{ locLoading ? 'Getting location…' : locationCaptured ? 'Update Location' : 'Capture Location' }}
          </button>

          <div v-if="locationCaptured" class="loc-info">
            <p class="loc-coords">{{ capturedLocation }}</p>
            <p class="loc-area" v-if="capturedArea">{{ capturedArea }}</p>
            <div id="visit-map" class="visit-map"></div>
          </div>

          <div v-if="locError" class="form-error mt-8">{{ locError }}</div>
        </div>
      </div>
    </div>


    <!-- ── Feedback Modal ── -->
    <div v-if="showFeedbackModal" class="modal-backdrop" @click.self="closeFeedbackModal">
      <div class="modal-sheet">
        <div class="modal-header">
          <h3 class="modal-title">Record Visit</h3>
          <button class="modal-close" @click="closeFeedbackModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="feedback-meta">
            <strong>{{ currentCustomer.customer_name }}</strong> · {{ timer }}
            <span v-if="selectedOrder"> · {{ selectedOrder }}</span>
          </p>
          <div v-if="feedbackError" class="form-error">{{ feedbackError }}</div>
          <div class="form-group">
            <label class="form-label">Notes / Feedback</label>
            <textarea
              v-model="feedbackText"
              class="form-textarea"
              rows="4"
              placeholder="What was discussed? Any follow-ups?"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeFeedbackModal">Skip</button>
            <button type="button" class="btn-primary" :disabled="feedbackLoading" @click="submitFeedback">
              <span v-if="feedbackLoading" class="btn-spinner"></span>
              <span v-else>Save Visit</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useRouter } from 'vue-router'

const router = useRouter()

// Fix leaflet default icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

let mapInstance = null

const CACHE_KEY = 'live_customers_cache'
const customers = ref([])
const searchQuery = ref('')
const hasMore = ref(true)
const loadingCustomers = ref(false)
const showAddCustomerModal = ref(false)
const newCustomer = ref({ customer_name: '' })
const addLoading = ref(false)
const addError = ref('')
const limitStart = ref(0)
const LIMIT = 20
const isAdmin = ref(false)
const currentUser = ref('')

const showCustomerVisitModal = ref(false)
const showFeedbackModal = ref(false)
const currentCustomer = ref({})
const visitInProgress = ref(false)
const timer = ref('00:00')
const feedbackText = ref('')
const feedbackLoading = ref(false)
const feedbackError = ref('')
let visitInterval = null
let visitSeconds = 0

const capturedLocation = ref('')
const capturedArea = ref('')
const locationCaptured = ref(false)
const locLoading = ref(false)
const locError = ref('')

const soMode = ref('existing')
const existingOrders = ref([])
const loadingOrders = ref(false)
const selectedOrder = ref(null)

async function fetchCustomers(isSearch = false) {
  // Show cached data immediately on first load
  if (!isSearch && limitStart.value === 0) {
    const cached = localStorage.getItem(CACHE_KEY)
    if (cached) {
      customers.value = JSON.parse(cached)
      hasMore.value = true
      // Refresh in background without showing spinner
      fetchCustomersFromServer(false, true)
      return
    }
  }
  await fetchCustomersFromServer(isSearch, false)
}

async function fetchCustomersFromServer(isSearch = false, background = false) {
  if (!background) loadingCustomers.value = true
  try {
    const params = new URLSearchParams({
      limit_start: String(isSearch || background ? 0 : limitStart.value),
      limit_page_length: String(LIMIT),
      ...(searchQuery.value ? { search: searchQuery.value } : {}),
    })
    const res = await fetch(`/api/method/live.api.customers.get_my_customers?${params}`, { credentials: 'include' })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const { message } = await res.json()
    const data = message || []
    const fetched = data.map(c => ({ name: c.name, customer_name: c.customer_name }))
    if (isSearch || background) {
      customers.value = fetched
      limitStart.value = fetched.length
    } else {
      customers.value = [...customers.value, ...fetched]
      limitStart.value += fetched.length
    }
    hasMore.value = fetched.length >= LIMIT
    // Cache the first page for instant load next time
    if (!searchQuery.value && (isSearch || background || limitStart.value <= LIMIT)) {
      localStorage.setItem(CACHE_KEY, JSON.stringify(customers.value.slice(0, LIMIT)))
    }
  } catch (e) {
    console.error('Error fetching customers:', e)
  } finally {
    if (!background) loadingCustomers.value = false
  }
}

function loadMore() { fetchCustomersFromServer(false, false) }

function handleSearch() {
  limitStart.value = 0
  hasMore.value = true
  fetchCustomersFromServer(true, false)
}

async function addCustomer() {
  if (!newCustomer.value.customer_name.trim()) {
    addError.value = 'Customer name is required'
    return
  }
  addError.value = ''
  addLoading.value = true
  try {
    const res = await fetch('/api/resource/Customer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ customer_name: newCustomer.value.customer_name }),
    })
    if (!res.ok) throw new Error('Failed to create customer')
    newCustomer.value = { customer_name: '' }
    showAddCustomerModal.value = false
    limitStart.value = 0
    localStorage.removeItem(CACHE_KEY)
    fetchCustomersFromServer(true, false)
  } catch (e) {
    addError.value = e.message || 'Failed to create customer'
  } finally {
    addLoading.value = false
  }
}

function closeModal() {
  showAddCustomerModal.value = false
  addError.value = ''
}

function viewCustomerDetails(customer) {
  currentCustomer.value = customer
  selectedOrder.value = null
  soMode.value = 'existing'
  existingOrders.value = []
  locationCaptured.value = false
  capturedLocation.value = ''
  capturedArea.value = ''
  locError.value = ''
  showCustomerVisitModal.value = true
  loadExistingOrders()
}

function closeVisitModal() {
  if (visitInProgress.value) clearInterval(visitInterval)
  visitInProgress.value = false
  showCustomerVisitModal.value = false
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
}

function startVisit() {
  visitInProgress.value = true
  timer.value = '00:00'
  visitSeconds = 0
  visitInterval = setInterval(() => {
    visitSeconds++
    const m = Math.floor(visitSeconds / 60)
    const s = visitSeconds % 60
    timer.value = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
  }, 1000)
}

function endVisit() {
  clearInterval(visitInterval)
  visitInProgress.value = false
  showFeedbackModal.value = true
}

async function loadExistingOrders() {
  if (!currentCustomer.value.name) return
  loadingOrders.value = true
  try {
    const res = await fetch(
      `/api/resource/Sales%20Order?filters=[["customer","=","${encodeURIComponent(currentCustomer.value.name)}"]]&fields=["name","status","transaction_date","grand_total"]&order_by=creation%20desc&limit=10`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    existingOrders.value = data || []
  } catch (e) {
    console.error('Failed to load orders:', e)
  } finally {
    loadingOrders.value = false
  }
}

async function submitFeedback() {
  feedbackError.value = ''
  feedbackLoading.value = true
  try {
    const payload = {
      customer: currentCustomer.value.name,
      feedback: feedbackText.value,
      duration: timer.value,
      ...(selectedOrder.value && { sales_order: selectedOrder.value }),
      ...(capturedLocation.value && { location: capturedLocation.value }),
    }
    const res = await fetch('/api/resource/Customer%20Visits', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      // Customer Visits doctype may not exist yet — just close gracefully
      console.warn('Customer Visits doctype may not exist, skipping save')
    }
    feedbackText.value = ''
    showFeedbackModal.value = false
    showCustomerVisitModal.value = false
    if (mapInstance) { mapInstance.remove(); mapInstance = null }
  } catch (e) {
    feedbackError.value = e.message || 'Failed to save visit'
  } finally {
    feedbackLoading.value = false
  }
}

function closeFeedbackModal() {
  showFeedbackModal.value = false
  feedbackError.value = ''
}

async function reverseGeocode(lat, lng) {
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
    const data = await res.json()
    return data.display_name || ''
  } catch { return '' }
}

async function captureLocationAndSave() {
  if (!navigator.geolocation) {
    locError.value = 'Geolocation is not supported by your browser.'
    return
  }
  locError.value = ''
  locLoading.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      capturedLocation.value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`
      locationCaptured.value = true

      const area = await reverseGeocode(lat, lng)
      capturedArea.value = area

      // Save to customer record
      try {
        await fetch(`/api/resource/Customer/${encodeURIComponent(currentCustomer.value.name)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            custom_customer_location: `${lat}, ${lng}`,
            custom_area_name: area,
          }),
        })
      } catch (e) { console.warn('Could not save location to customer record:', e) }

      locLoading.value = false

      await nextTick()
      const el = document.getElementById('visit-map')
      if (el) {
        if (mapInstance) mapInstance.remove()
        mapInstance = L.map('visit-map').setView([lat, lng], 15)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap'
        }).addTo(mapInstance)
        L.marker([lat, lng]).addTo(mapInstance).bindPopup('You are here').openPopup()
      }
    },
    (err) => {
      locLoading.value = false
      locError.value = 'Could not get location. Please enable location services.'
      console.error(err)
    },
    { enableHighAccuracy: false, timeout: 10000 }
  )
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Init
fetchCustomers()
</script>

<style scoped>
.customers-root {
  padding: 16px 16px 80px;
  background: #f8fafc;
  min-height: 100%;
}

.customers-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.customers-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}
.add-btn {
  width: 40px;
  height: 40px;
  background: #1d4ed8;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-wrap {
  position: relative;
  margin-bottom: 16px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  font-size: 0.9rem;
  color: #1e293b;
  box-sizing: border-box;
}
.search-input:focus { outline: none; border-color: #1d4ed8; }

.empty-state, .loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
  font-size: 0.9rem;
}
.page-spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #1d4ed8;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto;
}

.customer-list { display: flex; flex-direction: column; gap: 10px; }
.customer-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.customer-card:active { box-shadow: 0 2px 12px rgba(29,78,216,0.1); }
.customer-avatar {
  width: 40px; height: 40px;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.1rem;
  flex-shrink: 0;
}
.customer-info { flex: 1; min-width: 0; }
.customer-name { font-weight: 600; color: #111827; margin: 0; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.customer-id { font-size: 0.75rem; color: #94a3b8; margin: 2px 0 0; }
.customer-chevron { color: #cbd5e1; flex-shrink: 0; }

.load-more-wrap { text-align: center; padding: 16px 0; }
.load-more-btn {
  padding: 8px 24px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

/* Modal */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 200;
  display: flex; align-items: flex-end; justify-content: center;
}
.modal-sheet {
  background: #fff;
  border-radius: 24px 24px 0 0;
  width: 100%;
  max-width: 520px;
  max-height: 75vh;
  display: flex; flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom, 16px);
}
.modal-tall { max-height: 92vh; }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 20px 14px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}
.modal-title { font-size: 1rem; font-weight: 700; color: #111827; margin: 0; }
.modal-subtitle { font-size: 0.75rem; color: #94a3b8; margin: 2px 0 0; }
.modal-close {
  background: #f3f4f6; border: none; border-radius: 50%;
  width: 28px; height: 28px; cursor: pointer; color: #6b7280; font-size: 0.8rem;
}
.btn-timeline {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px; background: #eff6ff; color: #1d4ed8;
  border: none; border-radius: 8px; font-size: 0.75rem; font-weight: 700; cursor: pointer;
}
.modal-body { overflow-y: auto; padding: 16px 20px; }

.form-error {
  background: #fef2f2; border: 1px solid #fecaca; color: #dc2626;
  border-radius: 8px; padding: 10px 14px; font-size: 0.8rem; margin-bottom: 14px;
}
.mt-8 { margin-top: 8px; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; box-sizing: border-box;
}
.form-input:focus { outline: none; border-color: #1d4ed8; }
.form-textarea {
  width: 100%; padding: 10px 12px;
  border: 1px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; box-sizing: border-box; resize: vertical;
}
.form-textarea:focus { outline: none; border-color: #1d4ed8; }

.modal-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 8px; }

.btn-primary {
  padding: 10px 20px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
}
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-secondary {
  padding: 10px 20px; background: #f1f5f9; color: #475569;
  border: none; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
}
.btn-danger {
  width: 100%; padding: 12px; background: #fef2f2; color: #dc2626;
  border: 1.5px solid #fecaca; border-radius: 12px;
  font-weight: 700; font-size: 0.9rem; cursor: pointer;
}
.full-width { width: 100%; justify-content: center; }

.btn-spinner {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.btn-spinner-dark {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(71,85,105,0.3); border-top-color: #475569;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.mini-spinner {
  width: 20px; height: 20px;
  border: 2px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
  margin: 12px auto;
}

/* Visit timer */
.visit-timer-card {
  background: #f8fafc; border-radius: 14px; padding: 20px;
  text-align: center; margin-bottom: 14px;
  border: 1.5px solid #e2e8f0; transition: border-color 0.2s;
}
.timer-active { border-color: #22c55e; background: #f0fdf4; }
.timer-display { font-size: 2.5rem; font-weight: 800; color: #0f172a; letter-spacing: -1px; }
.timer-label { font-size: 0.75rem; color: #94a3b8; margin: 4px 0 0; }
.visit-actions { margin-bottom: 16px; }

.section-divider {
  display: flex; align-items: center; gap: 10px;
  margin: 16px 0 12px; font-size: 0.75rem; font-weight: 600;
  color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;
}
.section-divider::before, .section-divider::after {
  content: ''; flex: 1; height: 1px; background: #f1f5f9;
}

/* SO picker */
.so-tabs { display: flex; gap: 8px; margin-bottom: 12px; }
.so-tab {
  flex: 1; padding: 8px; border: 1.5px solid #e2e8f0;
  border-radius: 10px; font-size: 0.8rem; font-weight: 600;
  color: #64748b; background: #fff; cursor: pointer;
}
.so-tab-active { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }
.so-picker { max-height: 160px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.so-loading, .so-empty { text-align: center; padding: 16px; font-size: 0.85rem; color: #94a3b8; }
.so-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 10px; border: 1.5px solid #e2e8f0;
  cursor: pointer; transition: border-color 0.15s;
}
.so-item-selected { border-color: #1d4ed8; background: #eff6ff; }
.so-name { font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0; }
.so-meta { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.so-check { color: #1d4ed8; font-weight: 700; }

/* Location */
.loc-info { margin-top: 10px; }
.loc-coords { font-size: 0.8rem; color: #475569; margin: 0 0 2px; font-family: monospace; }
.loc-area { font-size: 0.8rem; color: #94a3b8; margin: 0 0 8px; }
.visit-map { height: 160px; width: 100%; border-radius: 12px; overflow: hidden; }

/* Feedback */
.feedback-meta { font-size: 0.85rem; color: #475569; margin: 0 0 16px; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
