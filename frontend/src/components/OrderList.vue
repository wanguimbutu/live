<template>
  <div class="orders-root">
    <!-- Header -->
    <div class="orders-header">
      <h1 class="orders-title">Sales Orders</h1>
      <button class="new-order-btn" @click="$router.push('/add-sales-order')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        New
      </button>
    </div>

    <!-- Offline queue -->
    <div v-if="queue.length > 0" class="queue-section">
      <div class="queue-header">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ queue.length }} order{{ queue.length > 1 ? 's' : '' }} pending sync
      </div>
      <div
        v-for="entry in queue"
        :key="entry.id"
        class="queue-item"
      >
        <div class="queue-item-info">
          <p class="queue-customer">{{ entry.order?.customer || 'Unknown customer' }}</p>
          <p class="queue-meta">{{ entry.order?.items?.length || 0 }} item(s) · {{ formatSavedAt(entry.savedAt) }}</p>
        </div>
        <span class="queue-badge" :class="entry.status === 'failed' ? 'badge-failed' : 'badge-pending'">
          {{ entry.status === 'syncing' ? 'Syncing…' : entry.status === 'failed' ? 'Failed' : 'Pending' }}
        </span>
      </div>
    </div>

    <!-- Search -->
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="searchQuery"
        class="search-input"
        placeholder="Search orders or customers…"
        @input="handleSearch"
      />
      <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''; handleSearch()">✕</button>
    </div>

    <!-- Status filter tabs -->
    <div class="status-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.key"
        class="status-tab"
        :class="{ 'tab-active': activeTab === tab.key }"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="list-loading">
      <div class="page-spinner"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="salesOrders.length === 0" class="list-empty">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" style="color:#cbd5e1;margin-bottom:12px">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <p>No orders found</p>
    </div>

    <!-- List -->
    <div v-else class="orders-list">
      <div
        v-for="order in salesOrders"
        :key="order.name"
        class="order-card"
        @click="$router.push({ name: 'OrderDetails', params: { id: order.name } })"
      >
        <div class="order-card-top">
          <div>
            <p class="order-name">{{ order.name }}</p>
            <p class="order-customer">{{ order.customer_name }}</p>
          </div>
          <span class="status-badge" :class="statusClass(order.status)">{{ order.status }}</span>
        </div>
        <div class="order-card-bottom">
          <div class="order-meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
              <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            {{ formatDate(order.transaction_date) }}
          </div>
          <div class="order-meta-item" v-if="order.delivery_date">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            Due {{ formatDate(order.delivery_date) }}
          </div>
          <div class="order-amount" v-if="order.grand_total">
            {{ formatCurrency(order.grand_total) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Load more -->
    <div class="load-more-wrap" v-if="hasMore && !loading">
      <button class="load-more-btn" @click="loadMore">Load more</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useOfflineQueue } from '../composables/useOfflineQueue'

const { queue } = useOfflineQueue()

const ORDERS_CACHE = 'live_orders_cache'
const salesOrders = ref([])
const loading = ref(false)
const hasMore = ref(true)
const limitStart = ref(0)
const LIMIT = 15
const searchQuery = ref('')
const activeTab = ref('all')

const statusTabs = [
  { key: 'all', label: 'All' },
  { key: 'Draft', label: 'Draft' },
  { key: 'To Deliver and Bill', label: 'Active' },
  { key: 'Completed', label: 'Completed' },
]

function statusClass(status) {
  if (!status) return ''
  if (['Submitted', 'Completed'].includes(status)) return 'badge-green'
  if (['Draft'].includes(status)) return 'badge-gray'
  if (['Cancelled'].includes(status)) return 'badge-red'
  if (['To Deliver and Bill', 'To Bill', 'To Deliver'].includes(status)) return 'badge-blue'
  if (['Overdue'].includes(status)) return 'badge-orange'
  return 'badge-gray'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrency(n) {
  if (!n) return ''
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(n)
}

function formatSavedAt(iso) {
  if (!iso) return ''
  const diff = Math.round((Date.now() - new Date(iso)) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff}m ago`
  return `${Math.round(diff / 60)}h ago`
}

async function fetchOrders(reset = false) {
  if (reset) {
    limitStart.value = 0
    hasMore.value = true

    // Show cache instantly on first "all" load with no search
    if (!searchQuery.value && activeTab.value === 'all') {
      const cached = localStorage.getItem(ORDERS_CACHE)
      if (cached) {
        salesOrders.value = JSON.parse(cached)
        // Refresh in background
        fetchOrdersFromServer(true, true)
        return
      }
    }
    salesOrders.value = []
  }
  await fetchOrdersFromServer(reset, false)
}

async function fetchOrdersFromServer(reset = false, background = false) {
  if (!background) loading.value = true
  try {
    const filters = []
    if (searchQuery.value) filters.push(['customer_name', 'like', `%${searchQuery.value}%`])
    if (activeTab.value !== 'all') filters.push(['status', '=', activeTab.value])

    const payload = {
      doctype: 'Sales Order',
      fields: ['name', 'customer_name', 'transaction_date', 'delivery_date', 'status', 'grand_total'],
      order_by: 'creation desc',
      limit_start: reset || background ? 0 : limitStart.value,
      limit_page_length: LIMIT,
      filters: filters.length ? filters : undefined,
    }

    const res = await fetch('/api/method/frappe.desk.reportview.get', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    const keys = data?.message?.keys || []
    const values = data?.message?.values || []
    const orders = values.map(row =>
      row.reduce((obj, val, i) => { obj[keys[i]] = val; return obj }, {})
    )

    if (reset || background) {
      salesOrders.value = orders
      limitStart.value = orders.length
    } else {
      salesOrders.value = [...salesOrders.value, ...orders]
      limitStart.value += orders.length
    }
    hasMore.value = orders.length >= LIMIT

    // Cache the first page (no filter) for instant next load
    if (!searchQuery.value && activeTab.value === 'all' && (reset || background)) {
      localStorage.setItem(ORDERS_CACHE, JSON.stringify(orders))
    }
  } catch (e) {
    console.error('Error fetching orders:', e)
  } finally {
    if (!background) loading.value = false
  }
}

function handleSearch() {
  fetchOrders(true)
}

function switchTab(key) {
  activeTab.value = key
  fetchOrders(true)
}

function loadMore() {
  fetchOrdersFromServer(false, false)
}

fetchOrders(true)
</script>

<style scoped>
.orders-root {
  background: #f8fafc;
  min-height: 100%;
  padding: 0 0 80px;
}

.orders-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 16px 12px;
}
.orders-title { font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0; }
.new-order-btn {
  display: flex; align-items: center; gap: 6px;
  background: #1d4ed8; color: #fff; border: none;
  border-radius: 10px; padding: 8px 14px;
  font-size: 0.85rem; font-weight: 700; cursor: pointer;
}

/* Queue */
.queue-section {
  margin: 0 16px 12px;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 12px; overflow: hidden;
}
.queue-header {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 14px; font-size: 0.78rem; font-weight: 700;
  color: #92400e; border-bottom: 1px solid #fde68a;
}
.queue-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-bottom: 1px solid #fef9c3;
}
.queue-item:last-child { border-bottom: none; }
.queue-customer { font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0; }
.queue-meta { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.queue-badge {
  font-size: 0.65rem; font-weight: 700; padding: 3px 8px;
  border-radius: 6px; flex-shrink: 0;
}
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-failed { background: #fee2e2; color: #991b1b; }

/* Search */
.search-wrap {
  position: relative; margin: 0 16px 10px;
}
.search-icon {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: #94a3b8; pointer-events: none;
}
.search-input {
  width: 100%; padding: 10px 36px 10px 36px;
  border: 1.5px solid #e2e8f0; border-radius: 12px;
  background: #fff; font-size: 0.9rem; color: #1e293b; box-sizing: border-box;
}
.search-input:focus { outline: none; border-color: #1d4ed8; }
.search-clear {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 0.85rem;
}

/* Tabs */
.status-tabs {
  display: flex; gap: 6px; padding: 0 16px 12px;
  overflow-x: auto; scrollbar-width: none;
}
.status-tabs::-webkit-scrollbar { display: none; }
.status-tab {
  flex-shrink: 0; padding: 6px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 20px;
  background: #fff; font-size: 0.8rem; font-weight: 600;
  color: #64748b; cursor: pointer; white-space: nowrap;
}
.tab-active { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }

/* States */
.list-loading { text-align: center; padding: 60px 20px; }
.page-spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto;
}
.list-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 20px;
  color: #94a3b8; font-size: 0.9rem;
}

/* Cards */
.orders-list { padding: 0 16px; display: flex; flex-direction: column; gap: 10px; }
.order-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 14px; padding: 14px 16px;
  cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.order-card:active { box-shadow: 0 4px 16px rgba(29,78,216,0.1); }
.order-card-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 10px;
}
.order-name { font-size: 0.9rem; font-weight: 700; color: #0f172a; margin: 0; }
.order-customer { font-size: 0.8rem; color: #64748b; margin: 2px 0 0; }
.order-card-bottom {
  display: flex; align-items: center; gap: 12px;
  flex-wrap: wrap;
}
.order-meta-item {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.72rem; color: #94a3b8;
}
.order-amount {
  margin-left: auto; font-size: 0.9rem; font-weight: 700; color: #1e293b;
}

/* Status badges */
.status-badge {
  font-size: 0.65rem; font-weight: 700;
  padding: 3px 9px; border-radius: 8px;
  white-space: nowrap; flex-shrink: 0;
}
.badge-green { background: #dcfce7; color: #166534; }
.badge-gray { background: #f1f5f9; color: #475569; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-orange { background: #fff7ed; color: #c2410c; }

.load-more-wrap { text-align: center; padding: 16px; }
.load-more-btn {
  padding: 9px 24px; background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 10px; color: #475569; font-size: 0.85rem;
  font-weight: 600; cursor: pointer;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
