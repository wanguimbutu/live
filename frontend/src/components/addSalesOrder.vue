<template>
  <div class="so-form-root">
    <!-- Header -->
    <div class="so-form-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <h1 class="so-form-title">New Sales Order</h1>
    </div>

    <!-- Offline / saved banners -->
    <div v-if="!isOnline" class="banner banner-amber">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      You're offline — orders will sync automatically when reconnected.
    </div>
    <div v-if="savedOffline" class="banner banner-green">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="20 6 9 17 4 12"/></svg>
      Saved offline. Will sync when back online.
    </div>
    <div v-if="savedMsg" class="banner banner-green">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="20 6 9 17 4 12"/></svg>
      {{ savedMsg }}
    </div>
    <div v-if="errorMsg" class="banner banner-red">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      {{ errorMsg }}
    </div>

    <div class="so-form-body">
      <!-- Customer -->
      <div class="field-group">
        <label class="field-label">Customer <span class="required">*</span></label>
        <div class="searchable-select" :class="{ open: customerDropOpen }">
          <div class="select-display" @click="customerDropOpen = !customerDropOpen">
            <span v-if="newSalesOrder.customer" class="select-value">
              {{ customers.find(c => c.name === newSalesOrder.customer)?.customer_name || newSalesOrder.customer }}
            </span>
            <span v-else class="select-placeholder">Search or select customer…</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="select-chevron">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <div v-if="customerDropOpen" class="select-dropdown">
            <input
              v-model="customerSearch"
              class="select-search"
              placeholder="Type to filter…"
              @click.stop
              ref="customerSearchInput"
            />
            <div v-if="loadingData" class="select-loading">Loading…</div>
            <div
              v-for="c in filteredCustomers"
              :key="c.name"
              class="select-option"
              :class="{ selected: newSalesOrder.customer === c.name }"
              @click="newSalesOrder.customer = c.name; customerDropOpen = false; customerSearch = ''"
            >
              {{ c.customer_name || c.name }}
            </div>
            <div v-if="!loadingData && filteredCustomers.length === 0" class="select-empty">No customers found</div>
          </div>
        </div>
      </div>

      <!-- Delivery date -->
      <div class="field-group">
        <label class="field-label">Delivery Date <span class="required">*</span></label>
        <input
          v-model="newSalesOrder.delivery_date"
          type="date"
          class="field-input"
          :min="today"
        />
      </div>

      <!-- Items -->
      <div class="field-group">
        <div class="items-header">
          <label class="field-label" style="margin:0">Items <span class="required">*</span></label>
          <button type="button" class="add-item-btn" @click="addItem">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add item
          </button>
        </div>

        <div v-for="(item, index) in newSalesOrder.items" :key="index" class="item-card">
          <div class="item-card-top">
            <span class="item-num">Item {{ index + 1 }}</span>
            <button type="button" class="remove-item-btn" @click="removeItem(index)" v-if="newSalesOrder.items.length > 1">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
              </svg>
            </button>
          </div>

          <!-- Item select -->
          <div class="field-group" style="margin-bottom:10px">
            <label class="field-label-sm">Product</label>
            <div class="searchable-select" :class="{ open: itemDropOpen[index] }">
              <div class="select-display" @click="toggleItemDrop(index)">
                <span v-if="item.item_code" class="select-value">
                  {{ items.find(i => i.name === item.item_code)?.item_name || item.item_code }}
                </span>
                <span v-else class="select-placeholder">Select item…</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="select-chevron">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div v-if="itemDropOpen[index]" class="select-dropdown">
                <input v-model="itemSearch[index]" class="select-search" placeholder="Search items…" @click.stop />
                <div
                  v-for="it in filteredItems(index)"
                  :key="it.name"
                  class="select-option"
                  :class="{ selected: item.item_code === it.name }"
                  @click="selectItem(index, it)"
                >
                  {{ it.item_name || it.name }}
                </div>
                <div v-if="filteredItems(index).length === 0" class="select-empty">No items found</div>
              </div>
            </div>
          </div>

          <!-- Qty / Rate -->
          <div class="item-row">
            <div class="item-field">
              <label class="field-label-sm">Qty</label>
              <input v-model.number="item.qty" type="number" min="1" class="field-input" placeholder="1" />
            </div>
            <div class="item-field">
              <label class="field-label-sm">Rate</label>
              <input v-model.number="item.rate" type="number" min="0" step="0.01" class="field-input" placeholder="0.00" />
            </div>
            <div class="item-field">
              <label class="field-label-sm">Amount</label>
              <div class="amount-display">{{ formatCurrency(item.qty * item.rate) }}</div>
            </div>
          </div>

          <!-- Warehouse -->
          <div class="field-group" style="margin-top:10px;margin-bottom:0">
            <label class="field-label-sm">Delivery Warehouse</label>
            <div class="searchable-select" :class="{ open: warehouseDropOpen[index] }">
              <div class="select-display" @click="toggleWarehouseDrop(index)">
                <span v-if="item.warehouse" class="select-value">
                  {{ warehouses.find(w => w.name === item.warehouse)?.warehouse_name || item.warehouse }}
                </span>
                <span v-else class="select-placeholder">Select warehouse…</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="select-chevron">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div v-if="warehouseDropOpen[index]" class="select-dropdown">
                <input v-model="warehouseSearch[index]" class="select-search" placeholder="Search warehouse…" @click.stop />
                <div
                  v-for="wh in filteredWarehouses(index)"
                  :key="wh.name"
                  class="select-option"
                  :class="{ selected: item.warehouse === wh.name }"
                  @click="item.warehouse = wh.name; closeWarehouseDrop(index)"
                >
                  {{ wh.warehouse_name || wh.name }}
                </div>
                <div v-if="filteredWarehouses(index).length === 0" class="select-empty">No warehouses found</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Order total -->
      <div class="order-total" v-if="orderTotal > 0">
        <span class="total-label">Estimated Total</span>
        <span class="total-value">{{ formatCurrency(orderTotal) }}</span>
      </div>

      <!-- Notes -->
      <div class="field-group">
        <label class="field-label">Notes (optional)</label>
        <textarea v-model="newSalesOrder.notes" class="field-textarea" rows="2" placeholder="Any special instructions…"></textarea>
      </div>
    </div>

    <!-- Bottom actions -->
    <div class="so-form-actions">
      <button type="button" class="btn-save" :disabled="submitting" @click="createSalesOrder(false)">
        <span v-if="submitting === 'save'" class="btn-spinner"></span>
        <span v-else>Save Draft</span>
      </button>
      <button type="button" class="btn-submit" :disabled="submitting" @click="createSalesOrder(true)">
        <span v-if="submitting === 'submit'" class="btn-spinner"></span>
        <span v-else>Save &amp; Submit</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOfflineQueue, addToQueue } from '../composables/useOfflineQueue'

const router = useRouter()
const { isOnline } = useOfflineQueue()

const customers = ref([])
const items = ref([])
const warehouses = ref([])
const loadingData = ref(false)
const submitting = ref(false)
const savedOffline = ref(false)
const savedMsg = ref('')
const errorMsg = ref('')

const customerSearch = ref('')
const customerDropOpen = ref(false)
const itemDropOpen = ref([])
const itemSearch = ref([])
const warehouseDropOpen = ref([])
const warehouseSearch = ref([])

const today = new Date().toISOString().split('T')[0]

const newSalesOrder = ref({
  customer: '',
  delivery_date: '',
  items: [{ item_code: '', qty: 1, rate: 0, warehouse: '' }],
  notes: '',
})

const orderTotal = computed(() =>
  newSalesOrder.value.items.reduce((sum, i) => sum + (i.qty || 0) * (i.rate || 0), 0)
)

const filteredCustomers = computed(() => {
  const q = customerSearch.value.toLowerCase()
  return customers.value.filter(c =>
    (c.customer_name || c.name).toLowerCase().includes(q)
  )
})

function filteredItems(index) {
  const q = (itemSearch.value[index] || '').toLowerCase()
  return items.value.filter(i =>
    (i.item_name || i.name).toLowerCase().includes(q)
  )
}

function filteredWarehouses(index) {
  const q = (warehouseSearch.value[index] || '').toLowerCase()
  return warehouses.value.filter(w =>
    (w.warehouse_name || w.name).toLowerCase().includes(q)
  )
}

function addItem() {
  newSalesOrder.value.items.push({ item_code: '', qty: 1, rate: 0, warehouse: '' })
  itemDropOpen.value.push(false)
  itemSearch.value.push('')
  warehouseDropOpen.value.push(false)
  warehouseSearch.value.push('')
}

function removeItem(index) {
  newSalesOrder.value.items.splice(index, 1)
  itemDropOpen.value.splice(index, 1)
  itemSearch.value.splice(index, 1)
  warehouseDropOpen.value.splice(index, 1)
  warehouseSearch.value.splice(index, 1)
}

function toggleItemDrop(index) {
  itemDropOpen.value = itemDropOpen.value.map((v, i) => i === index ? !v : false)
  warehouseDropOpen.value = warehouseDropOpen.value.map(() => false)
  customerDropOpen.value = false
}

function toggleWarehouseDrop(index) {
  warehouseDropOpen.value = warehouseDropOpen.value.map((v, i) => i === index ? !v : false)
  itemDropOpen.value = itemDropOpen.value.map(() => false)
  customerDropOpen.value = false
}

function closeWarehouseDrop(index) {
  warehouseDropOpen.value[index] = false
  warehouseSearch.value[index] = ''
}

function selectItem(index, it) {
  newSalesOrder.value.items[index].item_code = it.name
  // Pre-fill rate from standard selling rate if available
  if (it.standard_rate) newSalesOrder.value.items[index].rate = it.standard_rate
  itemDropOpen.value[index] = false
  itemSearch.value[index] = ''
}

function formatCurrency(n) {
  if (!n) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n)
}

function showError(msg) {
  errorMsg.value = msg
  setTimeout(() => { errorMsg.value = '' }, 5000)
}

function showSuccess(msg) {
  savedMsg.value = msg
  setTimeout(() => { savedMsg.value = '' }, 4000)
}

async function loadFormData() {
  // Load from cache immediately
  const cached = localStorage.getItem('live_form_cache')
  if (cached) {
    const c = JSON.parse(cached)
    customers.value = c.customers || []
    items.value = c.items || []
    warehouses.value = c.warehouses || []
  }

  if (!isOnline.value) return

  loadingData.value = true
  try {
    const [cRes, iRes, wRes] = await Promise.all([
      fetch('/api/resource/Customer?fields=["name","customer_name"]&limit_page_length=200', { credentials: 'include' }),
      fetch('/api/resource/Item?fields=["name","item_name","standard_rate"]&limit_page_length=200', { credentials: 'include' }),
      fetch('/api/resource/Warehouse?fields=["name","warehouse_name"]&limit_page_length=100', { credentials: 'include' }),
    ])
    customers.value = (await cRes.json()).data || []
    items.value = (await iRes.json()).data || []
    warehouses.value = (await wRes.json()).data || []
    localStorage.setItem('live_form_cache', JSON.stringify({
      customers: customers.value,
      items: items.value,
      warehouses: warehouses.value,
    }))
  } catch (e) {
    console.error('Error fetching form data:', e)
  } finally {
    loadingData.value = false
  }
}

async function createSalesOrder(andSubmit) {
  const order = newSalesOrder.value
  if (!order.customer) return showError('Please select a customer.')
  if (!order.delivery_date) return showError('Please set a delivery date.')
  if (order.items.some(i => !i.item_code)) return showError('Please select an item for each line.')
  if (order.items.some(i => !i.warehouse)) return showError('Please select a warehouse for each item.')

  if (!isOnline.value) {
    addToQueue({ ...order })
    savedOffline.value = true
    setTimeout(() => { savedOffline.value = false }, 4000)
    resetForm()
    return
  }

  submitting.value = andSubmit ? 'submit' : 'save'
  try {
    const payload = {
      customer: order.customer,
      delivery_date: order.delivery_date,
      items: order.items.map(i => ({
        item_code: i.item_code,
        qty: i.qty,
        rate: i.rate,
        warehouse: i.warehouse,
      })),
    }

    const res = await fetch('/api/resource/Sales%20Order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body?.exception || body?.message || 'Failed to create order')
    }

    const { data } = await res.json()
    const orderId = data.name

    if (andSubmit) {
      // Submit via Frappe method
      const submitRes = await fetch(`/api/resource/Sales%20Order/${encodeURIComponent(orderId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ docstatus: 1 }),
      })
      if (!submitRes.ok) throw new Error('Saved but could not submit — open in ERPNext.')
      showSuccess(`Order ${orderId} submitted successfully!`)
    } else {
      showSuccess(`Order ${orderId} saved as draft.`)
    }

    resetForm()
    setTimeout(() => router.push('/order-list'), 1500)
  } catch (e) {
    // Queue on network failure
    addToQueue({ ...order })
    savedOffline.value = true
    setTimeout(() => { savedOffline.value = false }, 4000)
    console.error(e)
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  newSalesOrder.value = {
    customer: '',
    delivery_date: '',
    items: [{ item_code: '', qty: 1, rate: 0, warehouse: '' }],
    notes: '',
  }
  itemDropOpen.value = [false]
  itemSearch.value = ['']
  warehouseDropOpen.value = [false]
  warehouseSearch.value = ['']
}

onMounted(() => {
  // Init dropdown arrays for initial single item
  itemDropOpen.value = [false]
  itemSearch.value = ['']
  warehouseDropOpen.value = [false]
  warehouseSearch.value = ['']
  loadFormData()
})
</script>

<style scoped>
.so-form-root {
  background: #f8fafc;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.so-form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 16px 8px;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 10;
}
.back-btn {
  width: 36px; height: 36px;
  background: #f1f5f9; border: none; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #374151; flex-shrink: 0;
}
.so-form-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0; }

.banner {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; font-size: 0.8rem;
  border-bottom: 1px solid transparent;
}
.banner-amber { background: #fffbeb; border-color: #fde68a; color: #92400e; }
.banner-green { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.banner-red { background: #fef2f2; border-color: #fecaca; color: #991b1b; }

.so-form-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-bottom: 100px;
}

.field-group { margin-bottom: 16px; }
.field-label {
  display: block; font-size: 0.8rem; font-weight: 700;
  color: #374151; margin-bottom: 6px;
  text-transform: uppercase; letter-spacing: 0.04em;
}
.field-label-sm {
  display: block; font-size: 0.72rem; font-weight: 600;
  color: #94a3b8; margin-bottom: 4px;
}
.required { color: #ef4444; }
.field-input {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; background: #fff;
  box-sizing: border-box; appearance: none;
}
.field-input:focus { outline: none; border-color: #1d4ed8; }
.field-textarea {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; background: #fff;
  box-sizing: border-box; resize: none;
}
.field-textarea:focus { outline: none; border-color: #1d4ed8; }

/* Searchable select */
.searchable-select { position: relative; }
.select-display {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px;
  background: #fff; cursor: pointer; min-height: 42px;
}
.searchable-select.open .select-display { border-color: #1d4ed8; }
.select-value { font-size: 0.9rem; color: #1e293b; }
.select-placeholder { font-size: 0.9rem; color: #94a3b8; }
.select-chevron { color: #94a3b8; flex-shrink: 0; }
.select-dropdown {
  position: absolute; left: 0; right: 0; top: calc(100% + 4px);
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1); z-index: 50;
  max-height: 220px; overflow-y: auto;
}
.select-search {
  width: 100%; padding: 10px 12px;
  border: none; border-bottom: 1px solid #f1f5f9;
  font-size: 0.88rem; color: #1e293b; background: transparent;
  box-sizing: border-box;
}
.select-search:focus { outline: none; }
.select-option {
  padding: 10px 14px; font-size: 0.88rem; color: #374151;
  cursor: pointer;
}
.select-option:hover { background: #f8fafc; }
.select-option.selected { background: #eff6ff; color: #1d4ed8; font-weight: 600; }
.select-empty { padding: 12px 14px; font-size: 0.85rem; color: #94a3b8; text-align: center; }
.select-loading { padding: 12px 14px; font-size: 0.85rem; color: #94a3b8; text-align: center; }

/* Items */
.items-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px;
}
.add-item-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: #eff6ff; color: #1d4ed8;
  border: none; border-radius: 8px; font-size: 0.8rem; font-weight: 600;
  cursor: pointer;
}
.item-card {
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 14px;
  padding: 14px; margin-bottom: 10px;
}
.item-card-top {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px;
}
.item-num { font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.remove-item-btn {
  background: #fef2f2; border: none; border-radius: 6px;
  width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #dc2626;
}
.item-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.item-field { display: flex; flex-direction: column; }
.amount-display {
  padding: 10px 12px; background: #f8fafc; border: 1.5px solid #f1f5f9;
  border-radius: 10px; font-size: 0.88rem; font-weight: 600; color: #1e293b;
  min-height: 42px; display: flex; align-items: center;
}

.order-total {
  display: flex; justify-content: space-between; align-items: center;
  background: #eff6ff; border: 1.5px solid #bfdbfe;
  border-radius: 12px; padding: 14px 16px;
  margin-bottom: 16px;
}
.total-label { font-size: 0.8rem; font-weight: 700; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.04em; }
.total-value { font-size: 1.2rem; font-weight: 800; color: #1d4ed8; }

/* Actions */
.so-form-actions {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff; border-top: 1px solid #f1f5f9;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px));
  display: flex; gap: 10px;
  z-index: 20;
}
.btn-save {
  flex: 1; padding: 13px; background: #f1f5f9; color: #374151;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-save:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-submit {
  flex: 2; padding: 13px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-submit:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
