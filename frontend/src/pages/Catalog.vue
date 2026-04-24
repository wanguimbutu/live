<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="cat-root">

        <!-- Header -->
        <div class="cat-header">
          <h1 class="cat-title">Product Catalog</h1>
          <p class="cat-sub">Live stock · KES prices</p>
        </div>

        <!-- Search -->
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="search"
            class="search-input"
            placeholder="Search items…"
            @input="onSearch"
          />
          <button v-if="search" class="search-clear" @click="search = ''; onSearch()">✕</button>
        </div>

        <!-- Stock filter -->
        <div class="stock-tabs">
          <button
            v-for="t in stockTabs" :key="t.key"
            class="stock-tab" :class="{ active: stockFilter === t.key }"
            @click="stockFilter = t.key"
          >{{ t.label }}</button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="cat-loading">
          <div class="spinner"></div>
        </div>

        <!-- Empty -->
        <div v-else-if="visibleItems.length === 0" class="cat-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" style="color:#cbd5e1">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          </svg>
          <p>No items found</p>
        </div>

        <!-- Item grid -->
        <div v-else class="item-grid">
          <div
            v-for="item in visibleItems"
            :key="item.item_code"
            class="item-card"
          >
            <!-- Stock badge -->
            <div class="stock-badge" :class="`stock-${item.stock_status}`">
              <span v-if="item.stock_status === 'in'">In Stock</span>
              <span v-else-if="item.stock_status === 'low'">Low Stock</span>
              <span v-else>Out of Stock</span>
            </div>

            <div class="item-name">{{ item.item_name }}</div>
            <div class="item-code">{{ item.item_code }}</div>
            <div class="item-group">{{ item.item_group }}</div>

            <div class="item-footer">
              <div class="item-price-block">
                <span class="item-price">{{ fmtKES(item.standard_rate) }}</span>
                <span class="item-uom">/ {{ item.stock_uom }}</span>
              </div>
              <div class="item-qty-block" :class="`qty-${item.stock_status}`">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="11" height="11">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
                {{ item.available_qty }} {{ item.stock_uom }}
              </div>
            </div>

            <button
              class="add-btn"
              :class="{ 'add-btn-disabled': item.stock_status === 'out' }"
              @click="addToOrder(item)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="13" height="13">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Add to Order
            </button>
          </div>
        </div>

        <!-- Load more -->
        <div class="load-more-wrap" v-if="hasMore && !loading">
          <button class="load-more-btn" @click="loadMore" :disabled="loadingMore">
            <span v-if="loadingMore" class="spin-sm"></span>
            <span v-else>Load more</span>
          </button>
        </div>

      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const items = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const search = ref('')
const stockFilter = ref('all')
const page = ref(0)
const PAGE_SIZE = 30
const hasMore = ref(true)
let searchTimer = null

const stockTabs = [
  { key: 'all', label: 'All' },
  { key: 'in', label: 'In Stock' },
  { key: 'low', label: 'Low Stock' },
  { key: 'out', label: 'Out of Stock' },
]

const visibleItems = computed(() => {
  if (stockFilter.value === 'all') return items.value
  return items.value.filter(i => i.stock_status === stockFilter.value)
})

function fmtKES(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 2 }).format(n)
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadCatalog(true), 350)
}

async function loadCatalog(reset = false) {
  if (reset) {
    page.value = 0
    items.value = []
    hasMore.value = true
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const params = new URLSearchParams({
      page: page.value,
      page_size: PAGE_SIZE,
      ...(search.value ? { search: search.value } : {}),
    })
    const res = await fetch(`/api/method/live.api.stock.get_catalog?${params}`, { credentials: 'include' })
    if (!res.ok) throw new Error(`${res.status}`)
    const { message } = await res.json()
    const data = message || {}
    const newItems = data.items || []

    items.value = reset ? newItems : [...items.value, ...newItems]
    hasMore.value = newItems.length >= PAGE_SIZE
    page.value++
  } catch (e) {
    console.error('Catalog load error:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  loadCatalog(false)
}

function addToOrder(item) {
  // Pass item to the new order form via history state
  router.push({
    path: '/add-sales-order',
    state: {
      preloadItems: [{
        item_code: item.item_code,
        item_name: item.item_name,
        qty: 1,
        rate: item.standard_rate || 0,
        warehouse: 'FG Stores',
      }],
    },
  })
}

onMounted(() => loadCatalog(true))
</script>

<style scoped>
.cat-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 90px;
}

.cat-header {
  padding: 20px 16px 10px;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
}
.cat-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 2px; }
.cat-sub { font-size: 0.75rem; color: #94a3b8; margin: 0; }

.search-wrap {
  position: relative;
  margin: 12px 16px 0;
}
.search-icon {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: #94a3b8; pointer-events: none;
}
.search-input {
  width: 100%; padding: 10px 36px;
  border: 1.5px solid #e2e8f0; border-radius: 12px;
  background: #fff; font-size: 0.9rem; color: #1e293b; box-sizing: border-box;
}
.search-input:focus { outline: none; border-color: #1d4ed8; }
.search-clear {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: #94a3b8; cursor: pointer;
}

.stock-tabs {
  display: flex; gap: 6px; padding: 10px 16px;
  overflow-x: auto; scrollbar-width: none;
}
.stock-tabs::-webkit-scrollbar { display: none; }
.stock-tab {
  flex-shrink: 0; padding: 5px 12px;
  border: 1.5px solid #e2e8f0; border-radius: 20px;
  background: #fff; font-size: 0.78rem; font-weight: 600;
  color: #64748b; cursor: pointer;
}
.stock-tab.active { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }

.cat-loading, .cat-empty {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 20px; gap: 12px;
  color: #94a3b8; font-size: 0.9rem;
}
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

.item-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 8px 12px;
}

.item-card {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  position: relative;
}

.stock-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: 6px;
  align-self: flex-start;
  margin-bottom: 4px;
}
.stock-in  { background: #dcfce7; color: #166534; }
.stock-low { background: #fef9c3; color: #854d0e; }
.stock-out { background: #fee2e2; color: #991b1b; }

.item-name { font-size: 0.82rem; font-weight: 700; color: #0f172a; line-height: 1.3; }
.item-code { font-size: 0.68rem; color: #94a3b8; }
.item-group { font-size: 0.68rem; color: #94a3b8; }

.item-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 6px;
}
.item-price-block { display: flex; align-items: baseline; gap: 2px; }
.item-price { font-size: 0.88rem; font-weight: 800; color: #1d4ed8; }
.item-uom { font-size: 0.62rem; color: #94a3b8; }

.item-qty-block {
  display: flex; align-items: center; gap: 3px;
  font-size: 0.68rem; font-weight: 600;
}
.qty-in  { color: #166534; }
.qty-low { color: #854d0e; }
.qty-out { color: #991b1b; }

.add-btn {
  margin-top: 8px;
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 5px;
  padding: 8px;
  background: #eff6ff; color: #1d4ed8;
  border: none; border-radius: 9px;
  font-size: 0.78rem; font-weight: 700; cursor: pointer;
  transition: background 0.15s;
}
.add-btn:active { background: #dbeafe; }
.add-btn.add-btn-disabled { opacity: 0.45; pointer-events: none; }

.load-more-wrap { text-align: center; padding: 16px; }
.load-more-btn {
  padding: 10px 28px; background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 12px; color: #475569; font-size: 0.85rem;
  font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;
}
.spin-sm {
  width: 14px; height: 14px;
  border: 2px solid #e2e8f0; border-top-color: #475569;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
