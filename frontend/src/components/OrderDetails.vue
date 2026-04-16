<template>
  <div class="od-root">
    <!-- Header -->
    <div class="od-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <div class="od-header-info">
        <h1 class="od-title">{{ order?.name || 'Order Details' }}</h1>
        <span v-if="order" class="status-badge" :class="statusClass(order.status)">{{ order.status }}</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="od-loading">
      <div class="page-spinner"></div>
    </div>

    <!-- Error -->
    <div v-else-if="!order" class="od-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" style="color:#cbd5e1">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>Could not load order. Please try again.</p>
      <button class="retry-btn" @click="fetchOrderDetails">Retry</button>
    </div>

    <div v-else class="od-body">
      <!-- Toast -->
      <div v-if="toastMsg" class="od-toast" :class="toastType === 'error' ? 'toast-red' : 'toast-green'">
        {{ toastMsg }}
      </div>

      <!-- Meta cards -->
      <div class="od-meta-grid">
        <div class="meta-card">
          <p class="meta-label">Customer</p>
          <p class="meta-value">{{ order.customer_name }}</p>
        </div>
        <div class="meta-card">
          <p class="meta-label">Order Date</p>
          <p class="meta-value">{{ formatDate(order.transaction_date) }}</p>
        </div>
        <div class="meta-card">
          <p class="meta-label">Delivery Date</p>
          <p class="meta-value">{{ formatDate(order.delivery_date) || '—' }}</p>
        </div>
        <div class="meta-card highlight" v-if="order.grand_total">
          <p class="meta-label">Grand Total</p>
          <p class="meta-value meta-total">{{ formatCurrency(order.grand_total) }}</p>
        </div>
      </div>

      <!-- Items table -->
      <div class="od-section">
        <p class="section-label">Items ({{ order.items?.length || 0 }})</p>
        <div class="items-list">
          <div
            v-for="item in order.items"
            :key="item.item_code"
            class="item-row"
          >
            <div class="item-row-info">
              <p class="item-name">{{ item.item_name || item.item_code }}</p>
              <p class="item-code">{{ item.item_code }}</p>
            </div>
            <div class="item-row-nums">
              <span class="item-qty">× {{ item.qty }}</span>
              <span class="item-amount">{{ formatCurrency(item.amount) }}</span>
            </div>
          </div>
        </div>

        <!-- Totals -->
        <div class="od-totals">
          <div class="total-row" v-if="order.total_taxes_and_charges">
            <span>Tax</span>
            <span>{{ formatCurrency(order.total_taxes_and_charges) }}</span>
          </div>
          <div class="total-row grand">
            <span>Total</span>
            <span>{{ formatCurrency(order.grand_total) }}</span>
          </div>
        </div>
      </div>

      <!-- Billing/delivery addresses if present -->
      <div class="od-section" v-if="order.customer_address || order.shipping_address_name">
        <p class="section-label">Addresses</p>
        <div class="address-grid">
          <div class="address-card" v-if="order.customer_address">
            <p class="address-type">Billing</p>
            <p class="address-text">{{ order.customer_address }}</p>
          </div>
          <div class="address-card" v-if="order.shipping_address_name">
            <p class="address-type">Shipping</p>
            <p class="address-text">{{ order.shipping_address_name }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions bar -->
    <div v-if="order" class="od-actions">
      <template v-if="order.status === 'Draft'">
        <button class="btn-secondary" :disabled="actionLoading" @click="submitOrder">
          <span v-if="actionLoading === 'submit'" class="btn-spinner-dark"></span>
          <span v-else>Submit</span>
        </button>
        <button class="btn-danger-outline" :disabled="actionLoading" @click="cancelOrder">
          <span v-if="actionLoading === 'cancel'" class="btn-spinner-dark"></span>
          <span v-else>Cancel</span>
        </button>
      </template>
      <template v-else-if="order.status === 'Cancelled'">
        <button class="btn-primary" :disabled="actionLoading" @click="amendOrder">
          <span v-if="actionLoading === 'amend'" class="btn-spinner"></span>
          <span v-else>Amend Order</span>
        </button>
      </template>
      <template v-else-if="['To Deliver and Bill', 'To Bill', 'To Deliver'].includes(order.status)">
        <button class="btn-secondary" :disabled="actionLoading" @click="cancelOrder">
          <span v-if="actionLoading === 'cancel'" class="btn-spinner-dark"></span>
          <span v-else>Cancel Order</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(true)
const actionLoading = ref(false)
const toastMsg = ref('')
const toastType = ref('success')

function statusClass(status) {
  if (!status) return ''
  if (['Submitted', 'Completed'].includes(status)) return 'badge-green'
  if (status === 'Draft') return 'badge-gray'
  if (status === 'Cancelled') return 'badge-red'
  if (['To Deliver and Bill', 'To Bill', 'To Deliver'].includes(status)) return 'badge-blue'
  if (status === 'Overdue') return 'badge-orange'
  return 'badge-gray'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n)
}

function showToast(msg, type = 'success') {
  toastMsg.value = msg
  toastType.value = type
  setTimeout(() => { toastMsg.value = '' }, 4000)
}

async function fetchOrderDetails() {
  loading.value = true
  order.value = null
  try {
    const id = route.params.id
    const res = await fetch(`/api/resource/Sales%20Order/${encodeURIComponent(id)}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Not found')
    const { data } = await res.json()
    order.value = data
  } catch (e) {
    console.error('Failed to load order:', e)
  } finally {
    loading.value = false
  }
}

async function submitOrder() {
  actionLoading.value = 'submit'
  try {
    const res = await fetch(`/api/resource/Sales%20Order/${encodeURIComponent(order.value.name)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ docstatus: 1 }),
    })
    if (!res.ok) throw new Error('Failed to submit')
    showToast('Order submitted successfully!')
    await fetchOrderDetails()
  } catch (e) {
    showToast(e.message || 'Could not submit order.', 'error')
  } finally {
    actionLoading.value = false
  }
}

async function cancelOrder() {
  actionLoading.value = 'cancel'
  try {
    const res = await fetch(`/api/resource/Sales%20Order/${encodeURIComponent(order.value.name)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ docstatus: 2 }),
    })
    if (!res.ok) throw new Error('Failed to cancel')
    showToast('Order cancelled.')
    await fetchOrderDetails()
  } catch (e) {
    showToast(e.message || 'Could not cancel order.', 'error')
  } finally {
    actionLoading.value = false
  }
}

async function amendOrder() {
  actionLoading.value = 'amend'
  try {
    const res = await fetch('/api/resource/Sales%20Order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ ...order.value, docstatus: 0, amended_from: order.value.name }),
    })
    if (!res.ok) throw new Error('Failed to amend')
    const { data } = await res.json()
    router.push({ name: 'OrderDetails', params: { id: data.name } })
  } catch (e) {
    showToast(e.message || 'Could not amend order.', 'error')
  } finally {
    actionLoading.value = false
  }
}

onMounted(fetchOrderDetails)
</script>

<style scoped>
.od-root {
  background: #f8fafc;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.od-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 16px 12px;
  background: #fff; border-bottom: 1px solid #f1f5f9;
  position: sticky; top: 0; z-index: 10;
}
.back-btn {
  width: 36px; height: 36px; background: #f1f5f9; border: none;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #374151; flex-shrink: 0;
}
.od-header-info { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.od-title { font-size: 1rem; font-weight: 800; color: #0f172a; margin: 0; }

.status-badge {
  font-size: 0.65rem; font-weight: 700;
  padding: 3px 9px; border-radius: 8px;
}
.badge-green { background: #dcfce7; color: #166534; }
.badge-gray { background: #f1f5f9; color: #475569; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-orange { background: #fff7ed; color: #c2410c; }

.od-loading { display: flex; justify-content: center; padding: 60px 20px; }
.page-spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.od-error {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 20px;
  gap: 12px; color: #94a3b8; font-size: 0.9rem;
}
.retry-btn {
  padding: 8px 20px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 8px; font-weight: 600; cursor: pointer;
}

.od-body { padding: 16px 16px 100px; }

.od-toast {
  border-radius: 10px; padding: 10px 14px; font-size: 0.85rem;
  font-weight: 500; margin-bottom: 14px;
}
.toast-green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
.toast-red { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }

.od-meta-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; margin-bottom: 16px;
}
.meta-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 12px; padding: 12px 14px;
}
.meta-card.highlight { border-color: #bfdbfe; background: #eff6ff; }
.meta-label { font-size: 0.68rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 4px; }
.meta-value { font-size: 0.88rem; font-weight: 600; color: #1e293b; margin: 0; }
.meta-total { font-size: 1.1rem; font-weight: 800; color: #1d4ed8; }

.od-section { margin-bottom: 16px; }
.section-label {
  font-size: 0.7rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 10px;
}
.items-list {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 14px; overflow: hidden;
}
.item-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-bottom: 1px solid #f8fafc;
}
.item-row:last-child { border-bottom: none; }
.item-name { font-size: 0.875rem; font-weight: 600; color: #1e293b; margin: 0; }
.item-code { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
.item-row-nums { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.item-qty { font-size: 0.8rem; color: #94a3b8; }
.item-amount { font-size: 0.88rem; font-weight: 700; color: #1e293b; min-width: 70px; text-align: right; }

.od-totals {
  background: #f8fafc; border: 1px solid #f1f5f9;
  border-radius: 0 0 14px 14px; padding: 10px 14px;
  border-top: none; margin-top: -1px;
}
.total-row {
  display: flex; justify-content: space-between;
  font-size: 0.85rem; color: #64748b; padding: 4px 0;
}
.total-row.grand {
  font-size: 1rem; font-weight: 800; color: #0f172a;
  border-top: 1px solid #e2e8f0; margin-top: 6px; padding-top: 8px;
}

.address-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.address-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 12px; padding: 12px 14px;
}
.address-type { font-size: 0.68rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0 0 4px; }
.address-text { font-size: 0.82rem; color: #374151; margin: 0; line-height: 1.4; }

/* Actions */
.od-actions {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff; border-top: 1px solid #f1f5f9;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px));
  display: flex; gap: 10px; z-index: 20;
}
.btn-primary {
  flex: 1; padding: 13px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-primary:disabled { opacity: 0.55; }
.btn-secondary {
  flex: 1; padding: 13px; background: #f1f5f9; color: #374151;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-secondary:disabled { opacity: 0.55; }
.btn-danger-outline {
  flex: 1; padding: 13px; background: #fef2f2; color: #dc2626;
  border: 1.5px solid #fecaca; border-radius: 12px;
  font-weight: 700; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-danger-outline:disabled { opacity: 0.55; }
.btn-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.btn-spinner-dark {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(71,85,105,0.3); border-top-color: #475569;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
