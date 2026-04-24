<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="dash-root">

        <!-- ─── Header ─────────────────────────────────────────────────────── -->
        <div class="dash-header">
          <div>
            <h1 class="dash-title">Dashboard</h1>
            <p class="dash-sub">{{ formatDateRange }}</p>
          </div>
          <button class="filter-btn" @click="filterOpen = !filterOpen">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/>
            </svg>
            Filter
          </button>
        </div>

        <!-- ─── Filter drawer ──────────────────────────────────────────────── -->
        <div v-if="filterOpen" class="filter-drawer">
          <div class="filter-row">
            <label class="filter-label">From</label>
            <input v-model="filters.fromDate" type="date" class="filter-input" />
          </div>
          <div class="filter-row">
            <label class="filter-label">To</label>
            <input v-model="filters.toDate" type="date" class="filter-input" />
          </div>
          <div class="filter-row" v-if="teamMembers.length">
            <label class="filter-label">Sales Rep</label>
            <select v-model="filters.salesPerson" class="filter-input">
              <option value="">All</option>
              <option v-for="m in teamMembers" :key="m.user" :value="m.user">{{ m.name }}</option>
            </select>
          </div>
          <button class="apply-btn" @click="applyFilters">Apply</button>
        </div>

        <!-- ─── Alerts ─────────────────────────────────────────────────────── -->
        <template v-if="alerts.length">
          <div
            v-for="(a, i) in alerts"
            :key="i"
            class="alert-banner"
            :class="`alert-${a.severity}`"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ a.message }}
            <router-link v-if="a.type === 'pending_approvals'" to="/approvals" class="alert-link">Review →</router-link>
          </div>
        </template>

        <!-- ─── Loading ────────────────────────────────────────────────────── -->
        <div v-if="loading" class="dash-loading">
          <div class="spinner"></div>
        </div>

        <template v-else>
          <!-- ─── KPI grid ──────────────────────────────────────────────── -->
          <div class="section-label">Today</div>
          <div class="kpi-grid">
            <KpiCard label="Orders" :value="kpis.today_orders" variant="blue" />
            <KpiCard label="Revenue" :value="fmtKES(kpis.today_revenue)" variant="green" />
          </div>

          <div class="section-label">This Period</div>
          <div class="kpi-grid kpi-grid-4">
            <KpiCard label="Total Orders" :value="kpis.total_orders" />
            <KpiCard label="Revenue" :value="fmtKESShort(kpis.total_revenue)" />
            <KpiCard label="Avg Order" :value="fmtKESShort(kpis.avg_order_value)" />
            <KpiCard label="Outstanding" :value="fmtKESShort(kpis.outstanding)" variant="amber" />
          </div>

          <div class="kpi-grid kpi-grid-3">
            <KpiCard label="Visits" :value="kpis.total_visits" />
            <KpiCard
              label="Conversion"
              :value="`${kpis.visit_conversion}%`"
              :sub="`${kpis.visits_with_order} with orders`"
            />
            <KpiCard
              label="Attendance"
              :value="`${kpis.attendance_rate}%`"
              :variant="kpis.attendance_rate < 80 ? 'red' : 'green'"
            />
          </div>

          <!-- ─── Revenue trend ─────────────────────────────────────────── -->
          <div class="chart-card">
            <SvgLineChart
              title="Daily Revenue"
              :label="`${trend.length} days`"
              :data="revenueChartData"
              color="#1d4ed8"
              :formatValue="fmtKESShort"
            />
          </div>

          <!-- ─── Orders trend ──────────────────────────────────────────── -->
          <div class="chart-card">
            <SvgLineChart
              title="Daily Orders"
              :data="ordersChartData"
              color="#8b5cf6"
            />
          </div>

          <!-- ─── Leaderboard ───────────────────────────────────────────── -->
          <div class="chart-card" v-if="leaderboard.length">
            <SvgBarChart
              title="Top Sales Reps — Revenue"
              :data="leaderboardData"
              :formatValue="fmtKESShort"
              :horizontal="true"
              :showRank="true"
            />
          </div>

          <!-- ─── Outstanding aging ─────────────────────────────────────── -->
          <div class="chart-card" v-if="aging.length">
            <p class="card-title">Outstanding Aging</p>
            <SvgBarChart
              :data="agingData"
              :colors="['#22c55e','#f59e0b','#ef4444','#7f1d1d']"
              :formatValue="fmtKESShort"
            />
            <div class="aging-totals">
              <div v-for="a in aging" :key="a.bucket" class="aging-row">
                <span class="aging-bucket">{{ a.bucket }}</span>
                <span class="aging-amount">{{ fmtKES(a.amount) }}</span>
                <span class="aging-count">{{ a.count }} inv.</span>
              </div>
            </div>
          </div>

          <!-- ─── Visit map ─────────────────────────────────────────────── -->
          <div class="chart-card map-card" v-if="visitPins.length">
            <p class="card-title">Visit Locations (last 7 days)</p>
            <div id="dash-map" class="dash-map"></div>
          </div>

          <!-- ─── Reminders ─────────────────────────────────────────────── -->
          <div class="chart-card" v-if="overdue.length || upcoming.length">
            <p class="card-title">
              Reminders
              <span v-if="unreadCount" class="badge-count">{{ unreadCount }}</span>
            </p>
            <div class="reminder-list">
              <div
                v-for="r in [...overdue, ...upcoming].slice(0, 5)"
                :key="r.id"
                class="reminder-item"
                :class="{ 'reminder-overdue': overdue.find(o => o.id === r.id) }"
              >
                <div class="reminder-info">
                  <p class="reminder-customer">{{ r.customerName }}</p>
                  <p class="reminder-date">{{ fmtDatetime(r.date) }}</p>
                  <p class="reminder-note" v-if="r.note">{{ r.note }}</p>
                </div>
                <button class="reminder-dismiss" @click="markRead(r.id)">✕</button>
              </div>
            </div>
          </div>

        </template>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'
import KpiCard from '../components/KpiCard.vue'
import SvgLineChart from '../components/SvgLineChart.vue'
import SvgBarChart from '../components/SvgBarChart.vue'
import { useReminders } from '../composables/useReminders'

const { overdue, upcoming, unreadCount, markRead } = useReminders()

const loading = ref(true)
const filterOpen = ref(false)
const kpis = ref({})
const trend = ref([])
const leaderboard = ref([])
const aging = ref([])
const alerts = ref([])
const teamMembers = ref([])
const visitPins = ref([])
let leafletMap = null

const today = new Date().toISOString().split('T')[0]
const thirtyAgo = new Date(Date.now() - 29 * 86400000).toISOString().split('T')[0]

const filters = ref({ fromDate: thirtyAgo, toDate: today, salesPerson: '' })

const formatDateRange = computed(() => {
  const f = new Date(filters.value.fromDate)
  const t = new Date(filters.value.toDate)
  return `${f.toLocaleDateString('en-KE', { day: 'numeric', month: 'short' })} – ${t.toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })}`
})

const revenueChartData = computed(() =>
  trend.value.map(d => ({ label: shortDate(d.date), value: d.revenue }))
)

const ordersChartData = computed(() =>
  trend.value.map(d => ({ label: shortDate(d.date), value: d.orders }))
)

const leaderboardData = computed(() =>
  leaderboard.value.slice(0, 8).map(r => ({ label: firstName(r.name), value: r.revenue }))
)

const agingData = computed(() =>
  aging.value.map(a => ({ label: a.bucket.replace(' days', 'd'), value: a.amount }))
)

function shortDate(iso) {
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}`
}

function firstName(name) {
  return name ? name.split(' ')[0] : '?'
}

function fmtKES(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 }).format(n)
}

function fmtKESShort(n) {
  if (!n && n !== 0) return '0'
  if (n >= 1_000_000) return `KES ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `KES ${(n / 1_000).toFixed(0)}k`
  return `KES ${Math.round(n)}`
}

function fmtDatetime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

async function apiFetch(path) {
  const res = await fetch(path, { credentials: 'include' })
  if (!res.ok) throw new Error(`${res.status}`)
  const json = await res.json()
  return json.message !== undefined ? json.message : json
}

function buildQuery(extra = {}) {
  const p = new URLSearchParams({
    from_date: filters.value.fromDate,
    to_date: filters.value.toDate,
    ...(filters.value.salesPerson ? { sales_person: filters.value.salesPerson } : {}),
    ...extra,
  })
  return p.toString()
}

async function loadAll() {
  loading.value = true
  try {
    const q = buildQuery()
    const [kpiRes, trendRes, lbRes, agingRes, alertRes, mapRes] = await Promise.allSettled([
      apiFetch(`/api/method/live.api.dashboard.get_kpis?${q}`),
      apiFetch(`/api/method/live.api.dashboard.get_trend?${q}`),
      apiFetch(`/api/method/live.api.dashboard.get_leaderboard?${q}`),
      apiFetch(`/api/method/live.api.dashboard.get_outstanding_aging`),
      apiFetch(`/api/method/live.api.dashboard.get_alerts`),
      apiFetch(`/api/method/live.api.dashboard.get_visit_map?${buildQuery()}`),
    ])

    if (kpiRes.status === 'fulfilled') kpis.value = kpiRes.value || {}
    if (trendRes.status === 'fulfilled') trend.value = trendRes.value || []
    if (lbRes.status === 'fulfilled') leaderboard.value = lbRes.value || []
    if (agingRes.status === 'fulfilled') aging.value = agingRes.value || []
    if (alertRes.status === 'fulfilled') alerts.value = alertRes.value || []
    if (mapRes.status === 'fulfilled') visitPins.value = mapRes.value || []

    if (kpis.value.is_manager) {
      const members = await apiFetch('/api/method/live.api.dashboard.get_team_members').catch(() => [])
      teamMembers.value = members || []
    }

    if (visitPins.value.length) {
      await nextTick()
      initMap()
    }
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  filterOpen.value = false
  loadAll()
}

function initMap() {
  const L = window.L
  if (!L) return
  const el = document.getElementById('dash-map')
  if (!el || leafletMap) return

  const pins = visitPins.value.filter(p => p.latitude && p.longitude)
  if (!pins.length) return

  const center = [pins[0].latitude, pins[0].longitude]
  leafletMap = L.map(el, { zoomControl: false }).setView(center, 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap', maxZoom: 18,
  }).addTo(leafletMap)

  const hasOrder = L.divIcon({ className: '', html: '<div style="width:10px;height:10px;background:#1d4ed8;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.4)"></div>' })
  const noOrder  = L.divIcon({ className: '', html: '<div style="width:8px;height:8px;background:#94a3b8;border-radius:50%;border:2px solid #fff"></div>' })

  for (const p of pins) {
    L.marker([p.latitude, p.longitude], { icon: p.sales_order ? hasOrder : noOrder })
      .bindPopup(`<b>${p.customer_name}</b><br>${p.user_name}<br>${p.sales_order ? '✓ Order placed' : 'Visit only'}`)
      .addTo(leafletMap)
  }

  const bounds = L.latLngBounds(pins.map(p => [p.latitude, p.longitude]))
  leafletMap.fitBounds(bounds, { padding: [20, 20] })
}

onMounted(loadAll)
</script>

<style scoped>
.dash-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 90px;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 16px 12px;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 10;
}
.dash-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 2px; }
.dash-sub { font-size: 0.75rem; color: #94a3b8; margin: 0; }

.filter-btn {
  display: flex; align-items: center; gap: 5px;
  background: #f1f5f9; border: none; border-radius: 10px;
  padding: 8px 12px; font-size: 0.8rem; font-weight: 600;
  color: #374151; cursor: pointer; flex-shrink: 0;
}

.filter-drawer {
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.filter-row { display: flex; align-items: center; gap: 10px; }
.filter-label { font-size: 0.78rem; font-weight: 600; color: #64748b; width: 70px; flex-shrink: 0; }
.filter-input {
  flex: 1; padding: 8px 10px;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.85rem; color: #1e293b; background: #fff;
}
.apply-btn {
  background: #1d4ed8; color: #fff; border: none;
  border-radius: 10px; padding: 10px; font-weight: 700;
  font-size: 0.85rem; cursor: pointer;
}

/* Alerts */
.alert-banner {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; font-size: 0.8rem; font-weight: 500;
  border-bottom: 1px solid transparent;
}
.alert-warning { background: #fffbeb; border-color: #fde68a; color: #92400e; }
.alert-danger  { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
.alert-info    { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.alert-link { margin-left: auto; font-weight: 700; color: inherit; text-decoration: none; flex-shrink: 0; }

/* Loading */
.dash-loading { display: flex; justify-content: center; padding: 60px 20px; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Layout */
.section-label {
  font-size: 0.68rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.06em;
  padding: 14px 16px 6px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 0 16px 10px;
}
.kpi-grid-4 { grid-template-columns: 1fr 1fr; }
.kpi-grid-3 { grid-template-columns: 1fr 1fr 1fr; }

.chart-card {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  margin: 0 12px 12px;
  padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-title {
  font-size: 0.78rem; font-weight: 700; color: #374151;
  text-transform: uppercase; letter-spacing: 0.04em;
  margin: 0 0 12px; display: flex; align-items: center; gap: 8px;
}
.badge-count {
  background: #ef4444; color: #fff;
  font-size: 0.65rem; font-weight: 800;
  padding: 2px 6px; border-radius: 9999px;
}

/* Aging */
.aging-totals { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; }
.aging-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.78rem; padding: 4px 0;
  border-bottom: 1px solid #f8fafc;
}
.aging-row:last-child { border-bottom: none; }
.aging-bucket { width: 80px; color: #64748b; font-weight: 600; flex-shrink: 0; }
.aging-amount { flex: 1; font-weight: 700; color: #1e293b; }
.aging-count { color: #94a3b8; font-size: 0.72rem; flex-shrink: 0; }

/* Map */
.map-card { padding: 14px 16px; }
.dash-map { height: 220px; border-radius: 10px; overflow: hidden; z-index: 0; }

/* Reminders */
.reminder-list { display: flex; flex-direction: column; gap: 8px; }
.reminder-item {
  display: flex; align-items: flex-start; justify-content: space-between;
  background: #f8fafc; border-radius: 10px; padding: 10px 12px;
  border-left: 3px solid #e2e8f0;
}
.reminder-item.reminder-overdue { border-left-color: #ef4444; background: #fff5f5; }
.reminder-info { flex: 1; }
.reminder-customer { font-size: 0.85rem; font-weight: 700; color: #0f172a; margin: 0; }
.reminder-date { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.reminder-note { font-size: 0.78rem; color: #64748b; margin: 4px 0 0; font-style: italic; }
.reminder-dismiss {
  background: none; border: none; color: #94a3b8; cursor: pointer;
  font-size: 0.8rem; padding: 0 4px; flex-shrink: 0;
}
</style>
