<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="dash-root">

        <!-- ─── Header ──────────────────────────────────────────────────────── -->
        <div class="dash-header">
          <div class="dash-header-top">
            <button class="back-btn" @click="$router.back()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <div class="dash-title-group">
              <h1 class="dash-title">Analytics</h1>
              <p class="dash-sub">{{ formatDateRange }}</p>
            </div>
            <button class="export-all-btn" @click="exportAll" title="Export all reports">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </button>
            <button class="filter-btn" @click="filterOpen = !filterOpen">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                <line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/>
              </svg>
              Filter
            </button>
          </div>

          <!-- Tab bar -->
          <div class="tab-row">
            <button
              v-for="t in tabs"
              :key="t.key"
              class="tab-btn"
              :class="{ active: activeTab === t.key }"
              @click="activeTab = t.key"
            >{{ t.label }}</button>
          </div>
        </div>

        <!-- ─── Filter drawer ─────────────────────────────────────────────── -->
        <div v-if="filterOpen" class="filter-drawer">
          <div class="filter-grid">
            <div class="filter-field">
              <label class="filter-label">From</label>
              <input v-model="filters.fromDate" type="date" class="filter-input" />
            </div>
            <div class="filter-field">
              <label class="filter-label">To</label>
              <input v-model="filters.toDate" type="date" class="filter-input" />
            </div>
            <div class="filter-field" v-if="teamMembers.length">
              <label class="filter-label">Sales Rep</label>
              <select v-model="filters.salesPerson" class="filter-input">
                <option value="">All reps</option>
                <option v-for="m in teamMembers" :key="m.user" :value="m.user">{{ m.name }}</option>
              </select>
            </div>
          </div>
          <div class="filter-actions">
            <button class="btn-ghost" @click="resetFilters">Reset</button>
            <button class="btn-primary" @click="applyFilters">Apply</button>
          </div>
        </div>

        <!-- ─── Alerts ────────────────────────────────────────────────────── -->
        <template v-if="alerts.length && activeTab === 'overview'">
          <div v-for="(a, i) in alerts.slice(0, 3)" :key="i" class="alert-banner" :class="`alert-${a.severity}`">
            <div class="alert-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <span class="alert-msg">{{ a.message }}</span>
            <router-link v-if="a.type === 'pending_approvals'" to="/approvals" class="alert-link">Review →</router-link>
          </div>
        </template>

        <!-- ─── Loading ───────────────────────────────────────────────────── -->
        <div v-if="loading" class="dash-loading">
          <div class="spinner"></div>
          <p class="loading-text">Loading dashboard…</p>
        </div>

        <template v-else>

          <!-- ══════════════ OVERVIEW TAB ══════════════════════════════════ -->
          <div v-if="activeTab === 'overview'" class="tab-content">

            <!-- Today spotlight -->
            <div class="spotlight-row">
              <div class="spotlight-card spotlight-blue">
                <p class="spotlight-label">Today's Orders</p>
                <p class="spotlight-value">{{ kpis.today_orders ?? 0 }}</p>
                <p class="spotlight-sub">vs {{ kpis.week_orders ?? 0 }} this week</p>
              </div>
              <div class="spotlight-card spotlight-green">
                <p class="spotlight-label">Today's Revenue</p>
                <p class="spotlight-value">{{ fmtKESShort(kpis.today_revenue) }}</p>
                <p class="spotlight-sub">{{ fmtKESShort(kpis.week_revenue) }} this week</p>
              </div>
            </div>

            <!-- Period KPIs -->
            <p class="section-label">This Period</p>
            <div class="kpi-grid-4">
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.total_orders ?? 0 }}</p>
                <p class="kpi-chip-lbl">Orders</p>
              </div>
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ fmtKESShort(kpis.total_revenue) }}</p>
                <p class="kpi-chip-lbl">Revenue</p>
              </div>
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ fmtKESShort(kpis.avg_order_value) }}</p>
                <p class="kpi-chip-lbl">Avg Order</p>
              </div>
              <div class="kpi-chip kpi-chip-amber">
                <p class="kpi-chip-val">{{ fmtKESShort(kpis.outstanding) }}</p>
                <p class="kpi-chip-lbl">Outstanding</p>
              </div>
            </div>

            <!-- Activity row -->
            <div class="kpi-grid-3">
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.total_visits ?? 0 }}</p>
                <p class="kpi-chip-lbl">Visits</p>
              </div>
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.visit_conversion ?? 0 }}%</p>
                <p class="kpi-chip-lbl">Conversion</p>
              </div>
              <div class="kpi-chip" :class="(kpis.attendance_rate ?? 0) < 80 ? 'kpi-chip-red' : 'kpi-chip-green'">
                <p class="kpi-chip-val">{{ kpis.attendance_rate ?? 0 }}%</p>
                <p class="kpi-chip-lbl">Attendance</p>
              </div>
            </div>

            <!-- Revenue sparkline -->
            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Revenue Trend</p>
                <span class="chart-badge">{{ trend.length }}d</span>
              </div>
              <SvgLineChart :data="revenueChartData" color="#6366f1" :formatValue="fmtKESShort" />
            </div>

          </div>

          <!-- ══════════════ SALES TAB ══════════════════════════════════════ -->
          <div v-if="activeTab === 'sales'" class="tab-content">

            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Daily Orders</p>
                <button class="dl-btn" @click="exportOrders">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <SvgLineChart :data="ordersChartData" color="#8b5cf6" />
            </div>

            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Daily Revenue</p>
              </div>
              <SvgLineChart :data="revenueChartData" color="#6366f1" :formatValue="fmtKESShort" />
            </div>

            <!-- Orders table -->
            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Orders Summary</p>
                <button class="dl-btn" @click="exportOrders">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <div class="data-table-wrap">
                <table class="data-table">
                  <thead>
                    <tr><th>Date</th><th>Orders</th><th>Revenue</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in trendTable" :key="row.date">
                      <td>{{ row.date }}</td>
                      <td>{{ row.orders }}</td>
                      <td>{{ fmtKES(row.revenue) }}</td>
                    </tr>
                    <tr v-if="!trendTable.length"><td colspan="3" class="empty-cell">No orders in period</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          <!-- ══════════════ COLLECTIONS TAB ════════════════════════════════ -->
          <div v-if="activeTab === 'collections'" class="tab-content">

            <!-- Aging summary cards -->
            <div class="aging-cards">
              <div
                v-for="(a, i) in aging"
                :key="a.bucket"
                class="aging-card"
                :class="['aging-card-0','aging-card-1','aging-card-2','aging-card-3'][i]"
              >
                <p class="aging-bucket">{{ a.bucket }}</p>
                <p class="aging-val">{{ fmtKESShort(a.amount) }}</p>
                <p class="aging-count">{{ a.count }} invoice{{ a.count !== 1 ? 's' : '' }}</p>
              </div>
            </div>

            <!-- Aging bar chart + download -->
            <div class="chart-card" v-if="aging.length">
              <div class="chart-card-head">
                <p class="chart-card-title">Aging Breakdown</p>
                <button class="dl-btn" @click="exportAging">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <SvgBarChart
                :data="agingData"
                :colors="['#22c55e','#f59e0b','#f97316','#ef4444']"
                :formatValue="fmtKESShort"
              />
            </div>

            <!-- Outstanding total -->
            <div class="stat-banner">
              <div class="stat-banner-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="22" height="22">
                  <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
                </svg>
              </div>
              <div>
                <p class="stat-banner-val">{{ fmtKES(kpis.outstanding) }}</p>
                <p class="stat-banner-lbl">Total Outstanding</p>
              </div>
            </div>

            <!-- Aging detail table -->
            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Detail</p>
                <button class="dl-btn" @click="exportAging">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <div class="data-table-wrap">
                <table class="data-table">
                  <thead><tr><th>Bucket</th><th>Invoices</th><th>Amount (KES)</th></tr></thead>
                  <tbody>
                    <tr v-for="a in aging" :key="a.bucket">
                      <td>{{ a.bucket }}</td>
                      <td>{{ a.count }}</td>
                      <td>{{ fmtKES(a.amount) }}</td>
                    </tr>
                    <tr v-if="!aging.length"><td colspan="3" class="empty-cell">No outstanding invoices</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          <!-- ══════════════ TEAM TAB ════════════════════════════════════════ -->
          <div v-if="activeTab === 'team'" class="tab-content">

            <div class="chart-card" v-if="leaderboard.length">
              <div class="chart-card-head">
                <p class="chart-card-title">Top Sales Reps — Revenue</p>
                <button class="dl-btn" @click="exportLeaderboard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <SvgBarChart
                :data="leaderboardData"
                :formatValue="fmtKESShort"
                :horizontal="true"
              />
            </div>

            <!-- Leaderboard table -->
            <div class="chart-card">
              <div class="chart-card-head">
                <p class="chart-card-title">Rep Breakdown</p>
                <button class="dl-btn" @click="exportLeaderboard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Excel
                </button>
              </div>
              <div class="data-table-wrap">
                <table class="data-table">
                  <thead><tr><th>#</th><th>Sales Rep</th><th>Orders</th><th>Revenue</th></tr></thead>
                  <tbody>
                    <tr v-for="(r, i) in leaderboard" :key="r.user">
                      <td>
                        <span class="rank-badge" :class="i === 0 ? 'rank-gold' : i === 1 ? 'rank-silver' : i === 2 ? 'rank-bronze' : ''">
                          {{ i + 1 }}
                        </span>
                      </td>
                      <td class="rep-cell">
                        <span class="rep-avatar">{{ initials(r.name) }}</span>
                        {{ r.name }}
                      </td>
                      <td>{{ r.order_count }}</td>
                      <td>{{ fmtKES(r.revenue) }}</td>
                    </tr>
                    <tr v-if="!leaderboard.length"><td colspan="4" class="empty-cell">No data for this period</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Activity alerts -->
            <div class="chart-card" v-if="activityAlerts.length">
              <p class="chart-card-title" style="margin-bottom:10px">Inactive Reps</p>
              <div class="alert-list">
                <div v-for="a in activityAlerts" :key="a.user" class="alert-row">
                  <span class="alert-dot alert-warning-dot"></span>
                  {{ a.message }}
                </div>
              </div>
            </div>

          </div>

          <!-- ══════════════ VISITS TAB ══════════════════════════════════════ -->
          <div v-if="activeTab === 'visits'" class="tab-content">

            <!-- Visit stats row -->
            <div class="kpi-grid-3">
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.total_visits ?? 0 }}</p>
                <p class="kpi-chip-lbl">Total Visits</p>
              </div>
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.visits_with_order ?? 0 }}</p>
                <p class="kpi-chip-lbl">With Orders</p>
              </div>
              <div class="kpi-chip">
                <p class="kpi-chip-val">{{ kpis.visit_conversion ?? 0 }}%</p>
                <p class="kpi-chip-lbl">Conversion</p>
              </div>
            </div>

            <!-- Map -->
            <div class="chart-card map-card" v-if="visitPins.length">
              <div class="chart-card-head">
                <p class="chart-card-title">Visit Locations</p>
                <span class="chart-badge">{{ visitPins.length }} pins</span>
              </div>
              <div id="dash-map" class="dash-map"></div>
              <div class="map-legend">
                <span class="legend-dot legend-blue"></span><span>Order placed</span>
                <span class="legend-dot legend-gray" style="margin-left:12px"></span><span>Visit only</span>
              </div>
            </div>
            <div class="chart-card empty-state" v-else>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36" style="color:#cbd5e1">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              <p>No visit data for this period</p>
            </div>

            <!-- Reminders -->
            <div class="chart-card" v-if="overdue.length || upcoming.length">
              <div class="chart-card-head">
                <p class="chart-card-title">Reminders</p>
                <span v-if="unreadCount" class="badge-red">{{ unreadCount }}</span>
              </div>
              <div class="reminder-list">
                <div
                  v-for="r in [...overdue, ...upcoming].slice(0, 6)"
                  :key="r.id"
                  class="reminder-item"
                  :class="{ 'reminder-overdue': overdue.find(o => o.id === r.id) }"
                >
                  <div class="reminder-dot" :class="overdue.find(o => o.id === r.id) ? 'dot-red' : 'dot-blue'"></div>
                  <div class="reminder-info">
                    <p class="reminder-customer">{{ r.customerName }}</p>
                    <p class="reminder-date">{{ fmtDatetime(r.date) }}</p>
                    <p class="reminder-note" v-if="r.note">{{ r.note }}</p>
                  </div>
                  <button class="reminder-dismiss" @click="markRead(r.id)">✕</button>
                </div>
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
import * as XLSX from 'xlsx'
import SvgLineChart from '../components/SvgLineChart.vue'
import SvgBarChart from '../components/SvgBarChart.vue'
import { useReminders } from '../composables/useReminders'

const { overdue, upcoming, unreadCount, markRead } = useReminders()

const loading = ref(true)
const filterOpen = ref(false)
const activeTab = ref('overview')
const kpis = ref({})
const trend = ref([])
const leaderboard = ref([])
const aging = ref([])
const alerts = ref([])
const teamMembers = ref([])
const visitPins = ref([])
let leafletMap = null

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'sales', label: 'Sales' },
  { key: 'collections', label: 'Collections' },
  { key: 'team', label: 'Team' },
  { key: 'visits', label: 'Visits' },
]

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
const trendTable = computed(() =>
  trend.value.filter(d => d.orders > 0).reverse()
)
const activityAlerts = computed(() =>
  alerts.value.filter(a => a.type === 'low_activity')
)

// ── Excel exports ────────────────────────────────────────────────────────────
function downloadExcel(sheets, filename) {
  const wb = XLSX.utils.book_new()
  sheets.forEach(({ name, rows }) => {
    const ws = XLSX.utils.aoa_to_sheet(rows)
    // Auto-width columns
    const colWidths = rows[0].map((_, ci) =>
      Math.max(...rows.map(r => String(r[ci] ?? '').length)) + 2
    )
    ws['!cols'] = colWidths.map(w => ({ wch: Math.min(w, 40) }))
    XLSX.utils.book_append_sheet(wb, ws, name)
  })
  XLSX.writeFile(wb, filename)
}

function exportOrders() {
  const rows = [['Date', 'Orders', 'Revenue (KES)']]
  trend.value.forEach(d => rows.push([d.date, d.orders, d.revenue]))
  downloadExcel([{ name: 'Orders Trend', rows }], `orders-trend-${filters.value.fromDate}-to-${filters.value.toDate}.xlsx`)
}

function exportAging() {
  const rows = [['Bucket', 'Invoices', 'Amount (KES)']]
  aging.value.forEach(a => rows.push([a.bucket, a.count, a.amount]))
  downloadExcel([{ name: 'Aging', rows }], `aging-report-${filters.value.toDate}.xlsx`)
}

function exportLeaderboard() {
  const rows = [['Rank', 'Sales Rep', 'Orders', 'Revenue (KES)']]
  leaderboard.value.forEach((r, i) => rows.push([i + 1, r.name, r.order_count, r.revenue]))
  downloadExcel([{ name: 'Leaderboard', rows }], `leaderboard-${filters.value.fromDate}-to-${filters.value.toDate}.xlsx`)
}

function exportAll() {
  const ordersRows = [['Date', 'Orders', 'Revenue (KES)'], ...trend.value.map(d => [d.date, d.orders, d.revenue])]
  const agingRows = [['Bucket', 'Invoices', 'Amount (KES)'], ...aging.value.map(a => [a.bucket, a.count, a.amount])]
  const lbRows = [['Rank', 'Sales Rep', 'Orders', 'Revenue (KES)'], ...leaderboard.value.map((r, i) => [i + 1, r.name, r.order_count, r.revenue])]
  downloadExcel([
    { name: 'Orders Trend', rows: ordersRows },
    { name: 'Aging', rows: agingRows },
    { name: 'Leaderboard', rows: lbRows },
  ], `analytics-report-${filters.value.fromDate}-to-${filters.value.toDate}.xlsx`)
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function shortDate(iso) {
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}`
}
function firstName(name) { return name ? name.split(' ')[0] : '?' }
function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
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

// ── Data loading ─────────────────────────────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(path, { credentials: 'include' })
  if (!res.ok) throw new Error(`${res.status}`)
  const json = await res.json()
  return json.message !== undefined ? json.message : json
}

function buildQuery(extra = {}) {
  return new URLSearchParams({
    from_date: filters.value.fromDate,
    to_date: filters.value.toDate,
    ...(filters.value.salesPerson ? { sales_person: filters.value.salesPerson } : {}),
    ...extra,
  }).toString()
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

function resetFilters() {
  filters.value = { fromDate: thirtyAgo, toDate: today, salesPerson: '' }
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
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM', maxZoom: 18 }).addTo(leafletMap)
  const mkBlue = L.divIcon({ className: '', html: '<div style="width:10px;height:10px;background:#4f46e5;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35)"></div>' })
  const mkGray = L.divIcon({ className: '', html: '<div style="width:8px;height:8px;background:#94a3b8;border-radius:50%;border:2px solid #fff"></div>' })
  for (const p of pins) {
    L.marker([p.latitude, p.longitude], { icon: p.sales_order ? mkBlue : mkGray })
      .bindPopup(`<b>${p.customer_name}</b><br>${p.user_name}<br>${p.sales_order ? '✓ Order placed' : 'Visit only'}`)
      .addTo(leafletMap)
  }
  leafletMap.fitBounds(L.latLngBounds(pins.map(p => [p.latitude, p.longitude])), { padding: [20, 20] })
}

onMounted(loadAll)
</script>

<style scoped>
/* ── Root ─────────────────────────────────────────────────────────────────── */
.dash-root {
  background: #f1f5f9;
  min-height: 100%;
  padding-bottom: 90px;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.dash-header {
  background: linear-gradient(135deg, #1e3a8a 0%, #4338ca 100%);
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 16px 16px 0;
}
.dash-header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.back-btn {
  width: 34px; height: 34px;
  background: rgba(255,255,255,0.15);
  border: none; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #fff; flex-shrink: 0;
}
.dash-title-group { flex: 1; }
.dash-title { font-size: 1.15rem; font-weight: 800; color: #fff; margin: 0 0 1px; }
.dash-sub { font-size: 0.72rem; color: rgba(255,255,255,0.65); margin: 0; }
.filter-btn {
  display: flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.18); border: none; border-radius: 10px;
  padding: 8px 12px; font-size: 0.78rem; font-weight: 600;
  color: #fff; cursor: pointer; flex-shrink: 0;
}
.export-all-btn {
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.18); border: none; border-radius: 10px;
  width: 34px; height: 34px; color: #fff; cursor: pointer; flex-shrink: 0;
}

/* ── Tab bar ──────────────────────────────────────────────────────────────── */
.tab-row {
  display: flex;
  gap: 2px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 0;
}
.tab-row::-webkit-scrollbar { display: none; }
.tab-btn {
  flex-shrink: 0;
  padding: 10px 14px;
  background: transparent; border: none;
  font-size: 0.8rem; font-weight: 600;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.tab-btn.active {
  color: #fff;
  border-bottom-color: #fff;
}

/* ── Filter drawer ────────────────────────────────────────────────────────── */
.filter-drawer {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  padding: 14px 16px;
}
.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.filter-field { display: flex; flex-direction: column; gap: 4px; }
.filter-label { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.filter-input {
  padding: 8px 10px; border: 1.5px solid #e2e8f0;
  border-radius: 8px; font-size: 0.85rem; color: #1e293b; background: #fff;
}
.filter-actions { display: flex; gap: 8px; }
.btn-ghost {
  flex: 1; padding: 10px; background: #f1f5f9;
  border: none; border-radius: 10px; font-weight: 600;
  font-size: 0.85rem; color: #64748b; cursor: pointer;
}
.btn-primary {
  flex: 1; padding: 10px; background: #4f46e5;
  border: none; border-radius: 10px; font-weight: 700;
  font-size: 0.85rem; color: #fff; cursor: pointer;
}

/* ── Alert banners ────────────────────────────────────────────────────────── */
.alert-banner {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; font-size: 0.8rem; font-weight: 500;
  border-bottom: 1px solid transparent;
}
.alert-warning { background: #fffbeb; border-color: #fde68a; color: #92400e; }
.alert-danger  { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
.alert-info    { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.alert-icon { flex-shrink: 0; }
.alert-msg { flex: 1; }
.alert-link { margin-left: auto; font-weight: 700; color: inherit; text-decoration: none; flex-shrink: 0; }

/* ── Loading ──────────────────────────────────────────────────────────────── */
.dash-loading {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 20px; gap: 12px;
}
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #4f46e5;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 0.82rem; color: #94a3b8; margin: 0; }

/* ── Tab content ──────────────────────────────────────────────────────────── */
.tab-content { padding: 14px 12px 0; display: flex; flex-direction: column; gap: 12px; }

/* ── Spotlight cards (Overview today) ────────────────────────────────────── */
.spotlight-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.spotlight-card {
  border-radius: 14px; padding: 16px 14px;
  display: flex; flex-direction: column; gap: 4px;
}
.spotlight-blue { background: linear-gradient(135deg, #1e3a8a, #3b5fc4); }
.spotlight-green { background: linear-gradient(135deg, #065f46, #059669); }
.spotlight-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.7); margin: 0; text-transform: uppercase; letter-spacing: 0.04em; }
.spotlight-value { font-size: 1.5rem; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }
.spotlight-sub { font-size: 0.7rem; color: rgba(255,255,255,0.6); margin: 0; }

/* ── KPI chips ────────────────────────────────────────────────────────────── */
.section-label {
  font-size: 0.68rem; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.06em;
  padding: 0 4px;
}
.kpi-grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; }
.kpi-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.kpi-chip {
  background: #fff; border-radius: 12px;
  padding: 12px 10px; text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-chip-val {
  font-size: 0.95rem; font-weight: 800; color: #1e293b;
  margin: 0 0 3px; line-height: 1.2;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.kpi-chip-lbl { font-size: 0.62rem; color: #94a3b8; margin: 0; text-transform: uppercase; font-weight: 600; }
.kpi-chip-amber .kpi-chip-val { color: #b45309; }
.kpi-chip-amber { background: #fffbeb; }
.kpi-chip-red .kpi-chip-val { color: #b91c1c; }
.kpi-chip-red { background: #fef2f2; }
.kpi-chip-green .kpi-chip-val { color: #065f46; }
.kpi-chip-green { background: #f0fdf4; }

/* ── Chart cards ──────────────────────────────────────────────────────────── */
.chart-card {
  background: #fff; border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.chart-card-head {
  display: flex; align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.chart-card-title {
  font-size: 0.78rem; font-weight: 700; color: #374151;
  text-transform: uppercase; letter-spacing: 0.04em; margin: 0;
}
.chart-badge {
  background: #eff6ff; color: #3b82f6;
  font-size: 0.65rem; font-weight: 700;
  padding: 2px 8px; border-radius: 9999px;
}
.badge-red {
  background: #ef4444; color: #fff;
  font-size: 0.65rem; font-weight: 800;
  padding: 2px 7px; border-radius: 9999px;
}
.dl-btn {
  display: flex; align-items: center; gap: 4px;
  background: #f1f5f9; border: none; border-radius: 8px;
  padding: 5px 10px; font-size: 0.72rem; font-weight: 600;
  color: #475569; cursor: pointer;
}
.dl-btn:active { background: #e2e8f0; }

/* ── Data tables ──────────────────────────────────────────────────────────── */
.data-table-wrap { overflow-x: auto; border-radius: 10px; }
.data-table {
  width: 100%; border-collapse: collapse; font-size: 0.8rem;
}
.data-table th {
  background: #f8fafc; color: #64748b;
  font-size: 0.68rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.04em;
  padding: 8px 10px; text-align: left;
  border-bottom: 1px solid #f1f5f9;
}
.data-table td {
  padding: 9px 10px; color: #1e293b;
  border-bottom: 1px solid #f8fafc;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f8fafc; }
.empty-cell { text-align: center; color: #94a3b8; padding: 20px; }

/* ── Aging cards ─────────────────────────────────────────────────────────── */
.aging-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.aging-card {
  border-radius: 14px; padding: 14px 12px;
  display: flex; flex-direction: column; gap: 2px;
}
.aging-card-0 { background: #f0fdf4; }
.aging-card-1 { background: #fffbeb; }
.aging-card-2 { background: #fff7ed; }
.aging-card-3 { background: #fef2f2; }
.aging-bucket { font-size: 0.7rem; font-weight: 700; color: #64748b; margin: 0; text-transform: uppercase; }
.aging-val { font-size: 1.05rem; font-weight: 800; color: #1e293b; margin: 0; }
.aging-count { font-size: 0.7rem; color: #94a3b8; margin: 0; }

/* ── Stat banner ─────────────────────────────────────────────────────────── */
.stat-banner {
  background: linear-gradient(135deg, #1e3a8a, #4338ca);
  border-radius: 14px; padding: 16px;
  display: flex; align-items: center; gap: 14px;
}
.stat-banner-icon { color: rgba(255,255,255,0.6); flex-shrink: 0; }
.stat-banner-val { font-size: 1.3rem; font-weight: 800; color: #fff; margin: 0 0 2px; }
.stat-banner-lbl { font-size: 0.72rem; color: rgba(255,255,255,0.65); margin: 0; }

/* ── Leaderboard table specifics ─────────────────────────────────────────── */
.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  font-size: 0.72rem; font-weight: 800;
  background: #f1f5f9; color: #64748b;
}
.rank-gold   { background: #fef3c7; color: #b45309; }
.rank-silver { background: #f1f5f9; color: #475569; }
.rank-bronze { background: #fdf0e8; color: #92400e; }
.rep-cell { display: flex; align-items: center; gap: 8px; }
.rep-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff; font-size: 0.62rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ── Alert list (team tab) ────────────────────────────────────────────────── */
.alert-list { display: flex; flex-direction: column; gap: 8px; }
.alert-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.82rem; color: #92400e; padding: 8px 10px;
  background: #fffbeb; border-radius: 8px;
}
.alert-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.alert-warning-dot { background: #f59e0b; }

/* ── Map ──────────────────────────────────────────────────────────────────── */
.map-card { padding: 14px 16px; }
.dash-map { height: 220px; border-radius: 10px; overflow: hidden; z-index: 0; }
.map-legend {
  display: flex; align-items: center; gap: 5px;
  margin-top: 10px; font-size: 0.72rem; color: #64748b;
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-blue { background: #4f46e5; }
.legend-gray { background: #94a3b8; }

/* ── Reminders ────────────────────────────────────────────────────────────── */
.reminder-list { display: flex; flex-direction: column; gap: 8px; }
.reminder-item {
  display: flex; align-items: flex-start; gap: 10px;
  background: #f8fafc; border-radius: 10px; padding: 10px 12px;
}
.reminder-item.reminder-overdue { background: #fff5f5; }
.reminder-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0; margin-top: 5px;
}
.dot-red { background: #ef4444; }
.dot-blue { background: #6366f1; }
.reminder-info { flex: 1; }
.reminder-customer { font-size: 0.85rem; font-weight: 700; color: #0f172a; margin: 0; }
.reminder-date { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.reminder-note { font-size: 0.78rem; color: #64748b; margin: 4px 0 0; font-style: italic; }
.reminder-dismiss { background: none; border: none; color: #cbd5e1; cursor: pointer; font-size: 0.8rem; padding: 0 2px; flex-shrink: 0; }

/* ── Empty state ──────────────────────────────────────────────────────────── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 10px; padding: 40px 20px; color: #94a3b8; font-size: 0.85rem;
}
</style>
