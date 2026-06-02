<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="dash-root">

        <!-- ── Top bar ──────────────────────────────────────────────────────── -->
        <div class="topbar">
          <div class="topbar-left">
            <button class="icon-btn" @click="$router.back()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div>
              <h1 class="topbar-title">Analytics</h1>
              <p class="topbar-sub">{{ formatDateRange }}</p>
            </div>
          </div>
          <div class="topbar-right">
            <button class="ghost-btn" @click="filterOpen = !filterOpen">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/></svg>
              {{ formatDateRange }}
            </button>
            <button class="icon-btn" @click="exportAll" title="Export all to Excel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </button>
          </div>
        </div>

        <!-- ── Filter panel ────────────────────────────────────────────────── -->
        <transition name="slide">
          <div v-if="filterOpen" class="filter-panel">
            <div class="filter-grid">
              <div class="filter-field">
                <label class="field-lbl">From</label>
                <input v-model="filters.fromDate" type="date" class="field-input" />
              </div>
              <div class="filter-field">
                <label class="field-lbl">To</label>
                <input v-model="filters.toDate" type="date" class="field-input" />
              </div>
              <div class="filter-field" v-if="teamMembers.length">
                <label class="field-lbl">Sales Rep</label>
                <select v-model="filters.salesPerson" class="field-input">
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
        </transition>

        <!-- ── Tab nav ────────────────────────────────────────────────────── -->
        <div class="tab-nav">
          <button
            v-for="t in tabs" :key="t.key"
            class="tab-btn" :class="{ active: activeTab === t.key }"
            @click="activeTab = t.key"
          >{{ t.label }}</button>
        </div>

        <!-- ── Loading ────────────────────────────────────────────────────── -->
        <div v-if="loading" class="dash-loading">
          <div class="spin-ring"></div>
          <p class="loading-label">Loading data…</p>
        </div>

        <template v-else>

          <!-- ══ OVERVIEW ══════════════════════════════════════════════════ -->
          <div v-if="activeTab === 'overview'" class="content">

            <!-- Metric row -->
            <div class="metric-row">
              <div class="metric-card">
                <p class="metric-label">Total Revenue</p>
                <p class="metric-value">{{ fmtKES(kpis.total_revenue) }}</p>
                <p class="metric-sub">
                  <span class="trend-up" v-if="(kpis.today_revenue || 0) > 0">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12"><polyline points="18 15 12 9 6 15"/></svg>
                    {{ fmtKESShort(kpis.today_revenue) }} today
                  </span>
                  <span v-else class="metric-sub-dim">{{ fmtKESShort(kpis.week_revenue) }} this week</span>
                </p>
              </div>
              <div class="metric-card">
                <p class="metric-label">Total Orders</p>
                <p class="metric-value">{{ kpis.total_orders ?? 0 }}</p>
                <p class="metric-sub">
                  <span class="trend-up" v-if="(kpis.today_orders || 0) > 0">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12"><polyline points="18 15 12 9 6 15"/></svg>
                    {{ kpis.today_orders }} today
                  </span>
                  <span v-else class="metric-sub-dim">{{ kpis.week_orders ?? 0 }} this week</span>
                </p>
              </div>
              <div class="metric-card">
                <p class="metric-label">Avg Order Value</p>
                <p class="metric-value">{{ fmtKESShort(kpis.avg_order_value) }}</p>
                <p class="metric-sub metric-sub-dim">per order</p>
              </div>
              <div class="metric-card metric-card-warn">
                <p class="metric-label">Outstanding</p>
                <p class="metric-value">{{ fmtKESShort(kpis.outstanding) }}</p>
                <p class="metric-sub metric-sub-dim">unpaid invoices</p>
              </div>
            </div>

            <!-- Activity row -->
            <div class="activity-row">
              <div class="stat-tile">
                <p class="stat-tile-val">{{ kpis.total_visits ?? 0 }}</p>
                <p class="stat-tile-lbl">Visits</p>
              </div>
              <div class="stat-tile">
                <p class="stat-tile-val">{{ kpis.visits_with_order ?? 0 }}</p>
                <p class="stat-tile-lbl">Orders from visits</p>
              </div>
              <div class="stat-tile">
                <p class="stat-tile-val" :class="(kpis.visit_conversion || 0) >= 50 ? 'val-green' : 'val-amber'">{{ kpis.visit_conversion ?? 0 }}%</p>
                <p class="stat-tile-lbl">Conversion rate</p>
              </div>
              <div class="stat-tile">
                <p class="stat-tile-val" :class="(kpis.attendance_rate || 0) >= 80 ? 'val-green' : 'val-red'">{{ kpis.attendance_rate ?? 0 }}%</p>
                <p class="stat-tile-lbl">Attendance</p>
              </div>
            </div>

            <!-- Revenue chart -->
            <div class="chart-card">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Revenue Trend</p>
                  <p class="chart-subtitle">Daily revenue for the selected period</p>
                </div>
              </div>
              <SvgLineChart :data="revenueChartData" color="#6366f1" :formatValue="fmtKESShort" />
            </div>

            <!-- Orders chart -->
            <div class="chart-card">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Orders per Day</p>
                  <p class="chart-subtitle">Number of orders placed each day</p>
                </div>
              </div>
              <SvgLineChart :data="ordersChartData" color="#0ea5e9" />
            </div>

          </div>

          <!-- ══ SALES ══════════════════════════════════════════════════════ -->
          <div v-if="activeTab === 'sales'" class="content">

            <div class="two-col">
              <div class="chart-card">
                <div class="chart-head">
                  <p class="chart-title">Daily Revenue</p>
                </div>
                <SvgLineChart :data="revenueChartData" color="#6366f1" :formatValue="fmtKESShort" />
              </div>
              <div class="chart-card">
                <div class="chart-head">
                  <p class="chart-title">Daily Orders</p>
                </div>
                <SvgLineChart :data="ordersChartData" color="#0ea5e9" />
              </div>
            </div>

            <!-- Orders table -->
            <div class="chart-card">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Orders by Day</p>
                  <p class="chart-subtitle">Only days with at least one order shown</p>
                </div>
                <button class="dl-btn" @click="exportOrders">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead><tr><th>Date</th><th>Orders</th><th>Revenue (KES)</th></tr></thead>
                  <tbody>
                    <tr v-for="row in trendTable" :key="row.date">
                      <td>{{ row.date }}</td>
                      <td><span class="badge-num">{{ row.orders }}</span></td>
                      <td class="td-right">{{ fmtKES(row.revenue) }}</td>
                    </tr>
                    <tr v-if="!trendTable.length">
                      <td colspan="3" class="empty-td">No orders in this period</td>
                    </tr>
                  </tbody>
                  <tfoot v-if="trendTable.length">
                    <tr>
                      <td class="tf-label">Total</td>
                      <td><span class="badge-num badge-num-primary">{{ kpis.total_orders }}</span></td>
                      <td class="td-right tf-val">{{ fmtKES(kpis.total_revenue) }}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

          </div>

          <!-- ══ COLLECTIONS ══════════════════════════════════════════════════ -->
          <div v-if="activeTab === 'collections'" class="content">

            <!-- Outstanding hero -->
            <div class="hero-card">
              <div class="hero-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
              </div>
              <div>
                <p class="hero-label">Total Outstanding</p>
                <p class="hero-value">{{ fmtKES(kpis.outstanding) }}</p>
                <p class="hero-sub">Across all unpaid invoices</p>
              </div>
            </div>

            <!-- Aging cards -->
            <div class="aging-grid">
              <div v-for="(a, i) in aging" :key="a.bucket" class="aging-tile" :class="`aging-tile-${i}`">
                <p class="aging-bucket">{{ a.bucket }}</p>
                <p class="aging-amount">{{ fmtKESShort(a.amount) }}</p>
                <p class="aging-count">{{ a.count }} invoice{{ a.count !== 1 ? 's' : '' }}</p>
                <div class="aging-bar-bg">
                  <div
                    class="aging-bar-fill"
                    :style="{ width: totalAging > 0 ? `${(a.amount / totalAging) * 100}%` : '0%' }"
                    :class="`aging-fill-${i}`"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Aging bar chart -->
            <div class="chart-card" v-if="aging.length">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Aging Distribution</p>
                  <p class="chart-subtitle">Outstanding amounts by age bucket</p>
                </div>
                <button class="dl-btn" @click="exportAging">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <SvgBarChart
                :data="agingData"
                :colors="['#10b981','#f59e0b','#f97316','#ef4444']"
                :formatValue="fmtKESShort"
              />
            </div>

            <!-- Aging table -->
            <div class="chart-card">
              <div class="chart-head">
                <p class="chart-title">Aging Detail</p>
                <button class="dl-btn" @click="exportAging">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead><tr><th>Age Bucket</th><th>Invoices</th><th>Amount (KES)</th><th>% of Total</th></tr></thead>
                  <tbody>
                    <tr v-for="(a, i) in aging" :key="a.bucket">
                      <td><span class="age-dot" :class="`age-dot-${i}`"></span>{{ a.bucket }}</td>
                      <td>{{ a.count }}</td>
                      <td class="td-right">{{ fmtKES(a.amount) }}</td>
                      <td class="td-right">{{ totalAging > 0 ? ((a.amount / totalAging) * 100).toFixed(1) : 0 }}%</td>
                    </tr>
                    <tr v-if="!aging.length"><td colspan="4" class="empty-td">No outstanding invoices</td></tr>
                  </tbody>
                  <tfoot v-if="aging.length">
                    <tr>
                      <td class="tf-label">Total</td>
                      <td>{{ aging.reduce((s, a) => s + a.count, 0) }}</td>
                      <td class="td-right tf-val">{{ fmtKES(totalAging) }}</td>
                      <td class="td-right">100%</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

          </div>

          <!-- ══ TEAM ══════════════════════════════════════════════════════ -->
          <div v-if="activeTab === 'team'" class="content">

            <!-- Leaderboard chart -->
            <div class="chart-card" v-if="leaderboard.length">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Revenue by Rep</p>
                  <p class="chart-subtitle">Top performers in the selected period</p>
                </div>
                <button class="dl-btn" @click="exportLeaderboard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <SvgBarChart
                :data="leaderboardData"
                :formatValue="fmtKESShort"
                :horizontal="true"
              />
            </div>

            <!-- Rep table -->
            <div class="chart-card">
              <div class="chart-head">
                <p class="chart-title">Rep Performance</p>
                <button class="dl-btn" @click="exportLeaderboard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead><tr><th>Rank</th><th>Sales Rep</th><th>Orders</th><th>Revenue</th></tr></thead>
                  <tbody>
                    <tr v-for="(r, i) in leaderboard" :key="r.user">
                      <td>
                        <span class="rank-pill" :class="i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : i === 2 ? 'rank-3' : 'rank-n'">{{ i + 1 }}</span>
                      </td>
                      <td>
                        <div class="rep-row">
                          <span class="rep-avatar">{{ initials(r.name) }}</span>
                          <span class="rep-name">{{ r.name }}</span>
                        </div>
                      </td>
                      <td>{{ r.order_count }}</td>
                      <td class="td-right">{{ fmtKES(r.revenue) }}</td>
                    </tr>
                    <tr v-if="!leaderboard.length"><td colspan="4" class="empty-td">No data for this period</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Inactive alerts -->
            <div class="chart-card" v-if="activityAlerts.length">
              <p class="chart-title" style="margin-bottom:12px">Inactive Reps</p>
              <div class="alert-list">
                <div v-for="a in activityAlerts" :key="a.user" class="alert-row-item">
                  <span class="dot-warn"></span>
                  {{ a.message }}
                </div>
              </div>
            </div>

            <!-- Live Locations Map -->
            <div class="chart-card">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Live Field Map</p>
                  <p class="chart-subtitle">
                    {{ activeReps.length }} active · {{ allReps.length }} tracked today
                    <button class="refresh-link" @click="loadLocations">↻ Refresh</button>
                  </p>
                </div>
                <div class="map-legend-inline">
                  <span v-for="(rep, i) in allReps.slice(0, 5)" :key="rep.user" class="legend-rep">
                    <span class="legend-dot-sm" :style="{ background: REP_COLORS[i % REP_COLORS.length] }"></span>
                    {{ rep.full_name.split(' ')[0] }}
                  </span>
                </div>
              </div>
              <div id="team-map" class="team-map"></div>
              <div class="map-key">
                <span class="mk-item"><span class="mk-dot mk-active"></span> Active (&lt;30 min)</span>
                <span class="mk-item"><span class="mk-dot mk-idle"></span> Idle</span>
                <span class="mk-item"><span class="mk-line"></span> Trail</span>
                <span class="mk-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="10" height="10"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/></svg>
                  Visit
                </span>
              </div>
            </div>

            <!-- Distance / Stipend table -->
            <div class="chart-card">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Distance Log</p>
                  <p class="chart-subtitle">Kilometers covered per rep — used for stipend calculation</p>
                </div>
                <button class="dl-btn" @click="exportDistance">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Export Excel
                </button>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Sales Rep</th>
                      <th>Date</th>
                      <th>Distance (km)</th>
                      <th>Miles</th>
                      <th>Pings</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in distanceSummary" :key="`${row.user}-${row.date}`">
                      <td>
                        <div class="rep-row">
                          <span class="rep-avatar">{{ initials(row.full_name) }}</span>
                          <span class="rep-name">{{ row.full_name }}</span>
                        </div>
                      </td>
                      <td>{{ row.date }}</td>
                      <td>
                        <div class="dist-bar-wrap">
                          <div class="dist-bar" :style="{ width: maxDistKm > 0 ? `${Math.min((row.total_km / maxDistKm) * 100, 100)}%` : '0%' }"></div>
                          <span class="dist-val">{{ row.total_km }} km</span>
                        </div>
                      </td>
                      <td class="td-right">{{ row.miles }}</td>
                      <td class="td-right">{{ row.pings }}</td>
                    </tr>
                    <tr v-if="!distanceSummary.length">
                      <td colspan="5" class="empty-td">No location data for this period</td>
                    </tr>
                  </tbody>
                  <tfoot v-if="distanceSummary.length">
                    <tr>
                      <td class="tf-label" colspan="2">Total</td>
                      <td>{{ distanceSummary.reduce((s, r) => +(s + r.total_km).toFixed(3), 0) }} km</td>
                      <td class="td-right">{{ distanceSummary.reduce((s, r) => +(s + r.miles).toFixed(3), 0) }}</td>
                      <td class="td-right">{{ distanceSummary.reduce((s, r) => s + r.pings, 0) }}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

          </div>

          <!-- ══ VISITS ══════════════════════════════════════════════════════ -->
          <div v-if="activeTab === 'visits'" class="content">

            <div class="stat-row">
              <div class="stat-card">
                <p class="stat-val">{{ kpis.total_visits ?? 0 }}</p>
                <p class="stat-lbl">Total Visits</p>
              </div>
              <div class="stat-card">
                <p class="stat-val">{{ kpis.visits_with_order ?? 0 }}</p>
                <p class="stat-lbl">With Orders</p>
              </div>
              <div class="stat-card">
                <p class="stat-val" :class="(kpis.visit_conversion || 0) >= 50 ? 'val-green' : 'val-amber'">{{ kpis.visit_conversion ?? 0 }}%</p>
                <p class="stat-lbl">Conversion</p>
              </div>
            </div>

            <!-- Map -->
            <div class="chart-card" v-if="visitPins.length">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Visit Locations</p>
                  <p class="chart-subtitle">{{ visitPins.length }} visits in the selected period</p>
                </div>
              </div>
              <div id="dash-map" class="dash-map"></div>
              <div class="map-legend">
                <span class="leg-dot leg-blue"></span><span>Order placed</span>
                <span class="leg-dot leg-gray"></span><span>Visit only</span>
              </div>
            </div>
            <div class="chart-card empty-card" v-else>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" style="color:#d1d5db">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              <p>No visit location data for this period</p>
            </div>

            <!-- Reminders -->
            <div class="chart-card" v-if="overdue.length || upcoming.length">
              <div class="chart-head">
                <div>
                  <p class="chart-title">Reminders</p>
                </div>
                <span v-if="unreadCount" class="badge-red">{{ unreadCount }} overdue</span>
              </div>
              <div class="reminder-list">
                <div
                  v-for="r in [...overdue, ...upcoming].slice(0, 6)"
                  :key="r.id"
                  class="reminder-row"
                  :class="{ overdue: overdue.find(o => o.id === r.id) }"
                >
                  <div class="reminder-dot" :class="overdue.find(o => o.id === r.id) ? 'rdot-red' : 'rdot-indigo'"></div>
                  <div class="reminder-body">
                    <p class="r-name">{{ r.customerName }}</p>
                    <p class="r-time">{{ fmtDatetime(r.date) }}</p>
                    <p class="r-note" v-if="r.note">{{ r.note }}</p>
                  </div>
                  <button class="dismiss-btn" @click="markRead(r.id)">✕</button>
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
const allReps = ref([])
const distanceSummary = ref([])
let leafletMap = null
let teamMap = null

const REP_COLORS = ['#6366f1','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#14b8a6','#f97316','#84cc16']

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

const revenueChartData = computed(() => trend.value.map(d => ({ label: shortDate(d.date), value: d.revenue })))
const ordersChartData = computed(() => trend.value.map(d => ({ label: shortDate(d.date), value: d.orders })))
const leaderboardData = computed(() => leaderboard.value.slice(0, 8).map(r => ({ label: firstName(r.name), value: r.revenue })))
const agingData = computed(() => aging.value.map(a => ({ label: a.bucket.replace(' days', 'd'), value: a.amount })))
const trendTable = computed(() => trend.value.filter(d => d.orders > 0).reverse())
const activityAlerts = computed(() => alerts.value.filter(a => a.type === 'low_activity'))
const totalAging = computed(() => aging.value.reduce((s, a) => s + a.amount, 0))
const activeReps = computed(() => allReps.value.filter(r => r.active))
const maxDistKm = computed(() => Math.max(...distanceSummary.value.map(r => r.total_km), 1))

// ── Excel exports ────────────────────────────────────────────────────────────
function downloadExcel(sheets, filename) {
  const wb = XLSX.utils.book_new()
  sheets.forEach(({ name, rows }) => {
    const ws = XLSX.utils.aoa_to_sheet(rows)
    ws['!cols'] = rows[0].map((_, ci) =>
      ({ wch: Math.min(Math.max(...rows.map(r => String(r[ci] ?? '').length)) + 2, 40) })
    )
    XLSX.utils.book_append_sheet(wb, ws, name)
  })
  XLSX.writeFile(wb, filename)
}

function exportOrders() {
  const rows = [['Date', 'Orders', 'Revenue (KES)'], ...trend.value.map(d => [d.date, d.orders, d.revenue])]
  downloadExcel([{ name: 'Orders Trend', rows }], `orders-${filters.value.fromDate}-${filters.value.toDate}.xlsx`)
}
function exportAging() {
  const rows = [['Bucket', 'Invoices', 'Amount (KES)', '% of Total'],
    ...aging.value.map(a => [a.bucket, a.count, a.amount, totalAging.value > 0 ? ((a.amount / totalAging.value) * 100).toFixed(1) + '%' : '0%'])]
  downloadExcel([{ name: 'Aging', rows }], `aging-${filters.value.toDate}.xlsx`)
}
function exportLeaderboard() {
  const rows = [['Rank', 'Sales Rep', 'Orders', 'Revenue (KES)'],
    ...leaderboard.value.map((r, i) => [i + 1, r.name, r.order_count, r.revenue])]
  downloadExcel([{ name: 'Leaderboard', rows }], `leaderboard-${filters.value.fromDate}-${filters.value.toDate}.xlsx`)
}
function exportAll() {
  downloadExcel([
    { name: 'Orders Trend', rows: [['Date', 'Orders', 'Revenue (KES)'], ...trend.value.map(d => [d.date, d.orders, d.revenue])] },
    { name: 'Aging', rows: [['Bucket', 'Invoices', 'Amount (KES)'], ...aging.value.map(a => [a.bucket, a.count, a.amount])] },
    { name: 'Leaderboard', rows: [['Rank', 'Sales Rep', 'Orders', 'Revenue (KES)'], ...leaderboard.value.map((r, i) => [i + 1, r.name, r.order_count, r.revenue])] },
  ], `analytics-${filters.value.fromDate}-${filters.value.toDate}.xlsx`)
}
function exportDistance() {
  const rows = [['Sales Rep', 'Date', 'Distance (km)', 'Miles', 'Pings'],
    ...distanceSummary.value.map(r => [r.full_name, r.date, r.total_km, r.miles, r.pings])]
  downloadExcel([{ name: 'Distance Log', rows }], `distance-log-${filters.value.fromDate}-${filters.value.toDate}.xlsx`)
}

// ── Location / Team map ───────────────────────────────────────────────────────
async function loadLocations() {
  try {
    const [locRes, distRes] = await Promise.allSettled([
      apiFetch(`/api/method/live.api.location.get_active_locations?date=${today}`),
      apiFetch(`/api/method/live.api.location.get_distance_summary?from_date=${filters.value.fromDate}&to_date=${filters.value.toDate}`),
    ])
    if (locRes.status === 'fulfilled') allReps.value = locRes.value || []
    if (distRes.status === 'fulfilled') distanceSummary.value = distRes.value || []

    if (allReps.value.length) {
      await nextTick()
      initTeamMap()
    }
  } catch (e) {
    console.error('Location load error:', e)
  }
}

function initTeamMap() {
  const L = window.L
  if (!L) return
  const el = document.getElementById('team-map')
  if (!el) return

  // Destroy and recreate if already initialised (refresh)
  if (teamMap) { teamMap.remove(); teamMap = null }

  const reps = allReps.value.filter(r => r.trail && r.trail.length > 0)
  if (!reps.length) return

  // Collect all coords for bounds
  const allCoords = reps.flatMap(r => r.trail.map(p => [p.lat, p.lng]))
  const center = allCoords[0]
  teamMap = L.map(el, { zoomControl: true }).setView(center, 10)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM', maxZoom: 19 }).addTo(teamMap)

  reps.forEach((rep, idx) => {
    const color = REP_COLORS[idx % REP_COLORS.length]
    const trail = rep.trail.map(p => [p.lat, p.lng])

    // Draw trail polyline
    if (trail.length > 1) {
      L.polyline(trail, { color, weight: 3, opacity: 0.75 }).addTo(teamMap)
    }

    // Start marker (hollow circle)
    if (trail.length) {
      L.circleMarker(trail[0], { radius: 5, color, fillColor: '#fff', fillOpacity: 1, weight: 2 })
        .bindPopup(`<b>${rep.full_name}</b><br>Started here`)
        .addTo(teamMap)
    }

    // Current position marker
    const last = trail[trail.length - 1]
    const isActive = rep.active
    const dotHtml = `<div style="width:${isActive ? 14 : 10}px;height:${isActive ? 14 : 10}px;background:${color};border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);${isActive ? `animation:pulse-${idx} 2s ease-in-out infinite` : ''}"></div>`
    const icon = L.divIcon({ className: '', html: dotHtml, iconAnchor: [7, 7] })
    L.marker(last, { icon })
      .bindPopup(`<b>${rep.full_name}</b><br>${isActive ? '🟢 Active' : '⚪ Idle'}<br>📍 ${rep.trail.length} pings<br>📏 ${rep.total_km} km today`)
      .addTo(teamMap)
  })

  // Also show visit pins
  visitPins.value.filter(p => p.latitude && p.longitude).forEach(p => {
    const visitIcon = L.divIcon({
      className: '',
      html: `<div style="width:8px;height:8px;background:#6366f1;border-radius:50%;border:2px solid #fff;"></div>`,
      iconAnchor: [4, 4],
    })
    L.marker([p.latitude, p.longitude], { icon: visitIcon })
      .bindPopup(`<b>${p.customer_name}</b><br>${p.user_name}<br>${p.sales_order ? '✓ Order' : 'Visit only'}`)
      .addTo(teamMap)
  })

  teamMap.fitBounds(L.latLngBounds(allCoords), { padding: [20, 20] })
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function shortDate(iso) { const d = new Date(iso); return `${d.getDate()}/${d.getMonth() + 1}` }
function firstName(name) { return name ? name.split(' ')[0] : '?' }
function initials(name) { return name ? name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() : '?' }
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

// ── API ───────────────────────────────────────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(path, { credentials: 'include' })
  if (!res.ok) throw new Error(`${res.status}`)
  const json = await res.json()
  return json.message !== undefined ? json.message : json
}
function buildQuery(extra = {}) {
  return new URLSearchParams({ from_date: filters.value.fromDate, to_date: filters.value.toDate, ...(filters.value.salesPerson ? { sales_person: filters.value.salesPerson } : {}), ...extra }).toString()
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
      teamMembers.value = await apiFetch('/api/method/live.api.dashboard.get_team_members').catch(() => []) || []
    }
    if (visitPins.value.length) { await nextTick(); initMap() }
    loadLocations()
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}
function applyFilters() { filterOpen.value = false; loadAll() }
function resetFilters() { filters.value = { fromDate: thirtyAgo, toDate: today, salesPerson: '' }; filterOpen.value = false; loadAll() }
function initMap() {
  const L = window.L; if (!L) return
  const el = document.getElementById('dash-map'); if (!el || leafletMap) return
  const pins = visitPins.value.filter(p => p.latitude && p.longitude); if (!pins.length) return
  leafletMap = L.map(el, { zoomControl: false }).setView([pins[0].latitude, pins[0].longitude], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM', maxZoom: 18 }).addTo(leafletMap)
  const mkBlue = L.divIcon({ className: '', html: '<div style="width:11px;height:11px;background:#6366f1;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)"></div>' })
  const mkGray = L.divIcon({ className: '', html: '<div style="width:8px;height:8px;background:#9ca3af;border-radius:50%;border:2px solid #fff"></div>' })
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
/* ── Base ─────────────────────────────────────────────────────────────────── */
.dash-root {
  background: #f5f6fa;
  min-height: 100%;
  padding-bottom: 80px;
  font-family: system-ui, -apple-system, sans-serif;
}

/* ── Top bar ──────────────────────────────────────────────────────────────── */
.topbar {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 30;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.topbar-right { display: flex; align-items: center; gap: 8px; }
.topbar-title { font-size: 1rem; font-weight: 700; color: #111827; margin: 0 0 1px; }
.topbar-sub { font-size: 0.7rem; color: #9ca3af; margin: 0; }
.icon-btn {
  width: 32px; height: 32px;
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 8px; display: flex; align-items: center;
  justify-content: center; cursor: pointer; color: #6b7280;
  flex-shrink: 0;
}
.ghost-btn {
  display: flex; align-items: center; gap: 5px;
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 8px; padding: 6px 10px;
  font-size: 0.75rem; font-weight: 500; color: #374151;
  cursor: pointer; white-space: nowrap; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis;
}

/* ── Filter panel ─────────────────────────────────────────────────────────── */
.filter-panel {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 14px 16px;
}
.filter-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; margin-bottom: 12px;
}
.filter-field { display: flex; flex-direction: column; gap: 4px; }
.field-lbl { font-size: 0.7rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
.field-input {
  padding: 8px 10px; border: 1px solid #d1d5db;
  border-radius: 7px; font-size: 0.83rem; color: #111827;
  background: #fff; width: 100%; box-sizing: border-box;
}
.field-input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,0.12); }
.filter-actions { display: flex; gap: 8px; }
.btn-ghost {
  flex: 1; padding: 9px; background: #f9fafb;
  border: 1px solid #e5e7eb; border-radius: 8px;
  font-size: 0.83rem; font-weight: 600; color: #374151; cursor: pointer;
}
.btn-primary {
  flex: 1; padding: 9px; background: #6366f1;
  border: none; border-radius: 8px;
  font-size: 0.83rem; font-weight: 700; color: #fff; cursor: pointer;
}

/* ── Alert strip ──────────────────────────────────────────────────────────── */
.alert-strip {
  padding: 8px 12px;
  display: flex; flex-direction: column; gap: 6px;
}
.alert-pill {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 12px; border-radius: 8px;
  font-size: 0.78rem; font-weight: 500;
  border: 1px solid transparent;
}
.pill-warning { background: #fffbeb; border-color: #fde68a; color: #92400e; }
.pill-danger  { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
.pill-info    { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.pill-link { margin-left: auto; font-weight: 700; color: inherit; text-decoration: none; }

/* ── Tab nav ──────────────────────────────────────────────────────────────── */
.tab-nav {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 0 12px;
  position: sticky;
  top: 57px;
  z-index: 20;
}
.tab-nav::-webkit-scrollbar { display: none; }
.tab-btn {
  flex-shrink: 0; padding: 12px 14px;
  background: transparent; border: none;
  font-size: 0.83rem; font-weight: 500; color: #6b7280;
  cursor: pointer; border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.tab-btn.active { color: #6366f1; border-bottom-color: #6366f1; font-weight: 700; }

/* ── Loading ──────────────────────────────────────────────────────────────── */
.dash-loading { display: flex; flex-direction: column; align-items: center; padding: 64px 20px; gap: 12px; }
.spin-ring {
  width: 36px; height: 36px;
  border: 3px solid #e5e7eb; border-top-color: #6366f1;
  border-radius: 50%; animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-label { font-size: 0.83rem; color: #9ca3af; margin: 0; }

/* Slide transition */
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Content wrapper ──────────────────────────────────────────────────────── */
.content { padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }

/* ── Metric row ───────────────────────────────────────────────────────────── */
.metric-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.metric-card {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 12px; padding: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-card-warn { border-left: 3px solid #f59e0b; }
.metric-label { font-size: 0.7rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 6px; }
.metric-value { font-size: 1.25rem; font-weight: 800; color: #111827; margin: 0 0 5px; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.metric-sub { font-size: 0.72rem; margin: 0; display: flex; align-items: center; gap: 3px; }
.metric-sub-dim { color: #9ca3af; }
.trend-up { color: #059669; display: flex; align-items: center; gap: 2px; font-weight: 600; }

/* ── Activity tiles ───────────────────────────────────────────────────────── */
.activity-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; }
.stat-tile {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 10px; padding: 10px 8px; text-align: center;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.stat-tile-val { font-size: 1.05rem; font-weight: 800; color: #111827; margin: 0 0 3px; }
.stat-tile-lbl { font-size: 0.6rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; margin: 0; }
.val-green { color: #059669 !important; }
.val-amber { color: #d97706 !important; }
.val-red { color: #dc2626 !important; }

/* ── Chart cards ──────────────────────────────────────────────────────────── */
.chart-card {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.chart-head {
  display: flex; align-items: flex-start;
  justify-content: space-between; margin-bottom: 14px;
}
.chart-title { font-size: 0.88rem; font-weight: 700; color: #111827; margin: 0 0 2px; }
.chart-subtitle { font-size: 0.72rem; color: #9ca3af; margin: 0; }
.dl-btn {
  display: flex; align-items: center; gap: 5px; flex-shrink: 0;
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 7px; padding: 6px 10px;
  font-size: 0.72rem; font-weight: 600; color: #374151; cursor: pointer;
}
.dl-btn:active { background: #f3f4f6; }

/* ── Two column layout ────────────────────────────────────────────────────── */
.two-col { display: flex; flex-direction: column; gap: 12px; }

/* ── Tables ───────────────────────────────────────────────────────────────── */
.table-wrap { overflow-x: auto; margin: 0 -2px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.data-table th {
  background: #f9fafb; color: #6b7280;
  font-size: 0.68rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.04em;
  padding: 9px 12px; text-align: left;
  border-bottom: 1px solid #e5e7eb; white-space: nowrap;
}
.data-table td {
  padding: 10px 12px; color: #111827;
  border-bottom: 1px solid #f3f4f6;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fafafa; }
.data-table tfoot td {
  background: #f9fafb; font-weight: 700;
  border-top: 1px solid #e5e7eb; border-bottom: none;
  padding: 10px 12px;
}
.td-right { text-align: right; font-variant-numeric: tabular-nums; }
.tf-label { color: #6b7280; font-size: 0.75rem; text-transform: uppercase; }
.tf-val { color: #111827; }
.empty-td { text-align: center; color: #9ca3af; padding: 24px; }
.badge-num {
  display: inline-block; background: #f3f4f6; color: #374151;
  font-size: 0.72rem; font-weight: 700; padding: 2px 7px;
  border-radius: 9999px;
}
.badge-num-primary { background: #ede9fe; color: #6366f1; }

/* ── Hero card (collections) ──────────────────────────────────────────────── */
.hero-card {
  background: #6366f1; border-radius: 14px;
  padding: 18px 16px; display: flex; align-items: center; gap: 14px;
  box-shadow: 0 4px 16px rgba(99,102,241,0.25);
}
.hero-icon { color: rgba(255,255,255,0.6); flex-shrink: 0; }
.hero-label { font-size: 0.72rem; color: rgba(255,255,255,0.7); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 4px; }
.hero-value { font-size: 1.6rem; font-weight: 800; color: #fff; margin: 0 0 3px; }
.hero-sub { font-size: 0.72rem; color: rgba(255,255,255,0.6); margin: 0; }

/* ── Aging grid ───────────────────────────────────────────────────────────── */
.aging-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.aging-tile {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 12px; padding: 14px;
}
.aging-bucket { font-size: 0.7rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 6px; }
.aging-amount { font-size: 1.1rem; font-weight: 800; color: #111827; margin: 0 0 3px; }
.aging-count { font-size: 0.7rem; color: #9ca3af; margin: 0 0 8px; }
.aging-bar-bg { background: #f3f4f6; border-radius: 4px; height: 5px; overflow: hidden; }
.aging-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.aging-fill-0 { background: #10b981; }
.aging-fill-1 { background: #f59e0b; }
.aging-fill-2 { background: #f97316; }
.aging-fill-3 { background: #ef4444; }
.age-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.age-dot-0 { background: #10b981; }
.age-dot-1 { background: #f59e0b; }
.age-dot-2 { background: #f97316; }
.age-dot-3 { background: #ef4444; }

/* ── Team table ───────────────────────────────────────────────────────────── */
.rank-pill {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  font-size: 0.7rem; font-weight: 800;
}
.rank-1 { background: #fef3c7; color: #92400e; }
.rank-2 { background: #f1f5f9; color: #334155; }
.rank-3 { background: #fdf0e8; color: #7c2d12; }
.rank-n { background: #f3f4f6; color: #6b7280; }
.rep-row { display: flex; align-items: center; gap: 8px; }
.rep-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff; font-size: 0.6rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.rep-name { font-weight: 500; color: #111827; }

/* ── Alert list (team) ────────────────────────────────────────────────────── */
.alert-list { display: flex; flex-direction: column; gap: 6px; }
.alert-row-item {
  display: flex; align-items: center; gap: 8px;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 8px; padding: 9px 12px;
  font-size: 0.8rem; color: #78350f;
}
.dot-warn { width: 7px; height: 7px; border-radius: 50%; background: #f59e0b; flex-shrink: 0; }

/* ── Visits stats ─────────────────────────────────────────────────────────── */
.stat-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.stat-card {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 12px; padding: 14px 12px; text-align: center;
}
.stat-val { font-size: 1.4rem; font-weight: 800; color: #111827; margin: 0 0 4px; }
.stat-lbl { font-size: 0.68rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; margin: 0; }

/* ── Map ──────────────────────────────────────────────────────────────────── */
.dash-map { height: 240px; border-radius: 8px; overflow: hidden; z-index: 0; }
.map-legend {
  display: flex; align-items: center; gap: 6px;
  margin-top: 10px; font-size: 0.72rem; color: #6b7280;
}
.leg-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.leg-dot + span { margin-right: 12px; }
.leg-blue { background: #6366f1; }
.leg-gray { background: #9ca3af; }

/* ── Reminders ────────────────────────────────────────────────────────────── */
.badge-red {
  background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;
  font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 9999px;
}
.reminder-list { display: flex; flex-direction: column; gap: 8px; }
.reminder-row {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; background: #f9fafb; border-radius: 10px;
  border: 1px solid #f3f4f6;
}
.reminder-row.overdue { background: #fef2f2; border-color: #fecaca; }
.reminder-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.rdot-indigo { background: #6366f1; }
.rdot-red { background: #ef4444; }
.reminder-body { flex: 1; }
.r-name { font-size: 0.85rem; font-weight: 700; color: #111827; margin: 0; }
.r-time { font-size: 0.72rem; color: #9ca3af; margin: 2px 0 0; }
.r-note { font-size: 0.78rem; color: #6b7280; margin: 4px 0 0; font-style: italic; }
.dismiss-btn { background: none; border: none; color: #d1d5db; cursor: pointer; font-size: 0.8rem; flex-shrink: 0; }

/* ── Empty card ───────────────────────────────────────────────────────────── */
.empty-card {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 10px; padding: 40px 20px;
  color: #9ca3af; font-size: 0.85rem; text-align: center;
}

/* ── Team live map ────────────────────────────────────────────────────────── */
.team-map {
  height: 280px; border-radius: 8px; overflow: hidden; z-index: 0;
  border: 1px solid #e5e7eb;
}
.map-key {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  margin-top: 10px; font-size: 0.7rem; color: #6b7280;
}
.mk-item { display: flex; align-items: center; gap: 5px; }
.mk-dot {
  width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0;
  border: 2px solid #fff; box-shadow: 0 0 0 1px #d1d5db;
}
.mk-active { background: #10b981; box-shadow: 0 0 0 1px #10b981; }
.mk-idle   { background: #9ca3af; box-shadow: 0 0 0 1px #9ca3af; }
.mk-line {
  width: 20px; height: 3px; border-radius: 2px;
  background: linear-gradient(90deg, #6366f1, #0ea5e9);
}
.map-legend-inline {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  max-width: 180px;
}
.legend-rep {
  display: flex; align-items: center; gap: 3px;
  font-size: 0.68rem; color: #6b7280; white-space: nowrap;
}
.legend-dot-sm {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}

/* ── Distance bar in table ────────────────────────────────────────────────── */
.dist-bar-wrap {
  display: flex; align-items: center; gap: 8px; min-width: 120px;
}
.dist-bar {
  height: 8px; border-radius: 4px; background: #6366f1;
  min-width: 2px; transition: width 0.5s cubic-bezier(.4,0,.2,1);
  flex-shrink: 0;
}
.dist-val { font-size: 0.78rem; color: #374151; white-space: nowrap; }

/* ── Refresh button ───────────────────────────────────────────────────────── */
.refresh-link {
  display: inline; background: none; border: none;
  color: #6366f1; font-size: 0.72rem; font-weight: 600;
  cursor: pointer; padding: 0 0 0 6px; margin: 0;
}
.refresh-link:hover { text-decoration: underline; }
</style>
