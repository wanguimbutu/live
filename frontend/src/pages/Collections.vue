<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="col-root">
        <!-- Header -->
        <div class="col-header">
          <h1 class="col-title">Collections</h1>
          <p class="col-subtitle">Outstanding customer balances</p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="col-center">
          <div class="spinner"></div>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="col-error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
          <button class="retry-btn" @click="loadOutstanding">Retry</button>
        </div>

        <!-- Content -->
        <template v-else>
          <!-- Summary bar -->
          <div class="summary-bar">
            <div class="summary-item">
              <span class="summary-label">Total Outstanding</span>
              <span class="summary-value">{{ formatCurrency(totalOutstanding) }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Customers</span>
              <span class="summary-value">{{ customerGroups.length }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Invoices</span>
              <span class="summary-value">{{ invoices.length }}</span>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="customerGroups.length === 0" class="col-center col-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48" style="color:#cbd5e1">
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
              <rect x="9" y="3" width="6" height="4" rx="1"/>
              <path d="M9 12h6M9 16h4"/>
            </svg>
            <p class="empty-text">No outstanding invoices</p>
          </div>

          <!-- Customer cards -->
          <div
            v-for="group in customerGroups"
            :key="group.customer"
            class="customer-card"
          >
            <div class="customer-header" @click="toggleCustomer(group.customer)">
              <div class="customer-avatar">{{ initials(group.customer_name) }}</div>
              <div class="customer-info">
                <p class="customer-name">{{ group.customer_name }}</p>
                <p class="customer-meta">{{ group.invoices.length }} unpaid invoice{{ group.invoices.length !== 1 ? 's' : '' }}</p>
              </div>
              <div class="customer-right">
                <span class="customer-outstanding" :class="{ overdue: group.hasOverdue }">
                  {{ formatCurrency(group.total) }}
                </span>
                <svg
                  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                  width="16" height="16" class="chevron"
                  :class="{ rotated: expandedCustomers[group.customer] }"
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
            </div>

            <!-- Invoice list -->
            <div v-if="expandedCustomers[group.customer]" class="invoice-list">
              <div
                v-for="inv in group.invoices"
                :key="inv.name"
                class="invoice-item"
                :class="{ overdue: isOverdue(inv.due_date) }"
              >
                <div class="invoice-left">
                  <p class="invoice-id">{{ inv.name }}</p>
                  <p class="invoice-date">Issued {{ formatDate(inv.posting_date) }}</p>
                  <p class="invoice-due" :class="{ 'due-overdue': isOverdue(inv.due_date) }">
                    Due {{ formatDate(inv.due_date) }}
                    <span v-if="isOverdue(inv.due_date)" class="overdue-tag">OVERDUE</span>
                  </p>
                </div>
                <div class="invoice-right">
                  <p class="invoice-outstanding">{{ formatCurrency(inv.outstanding_amount) }}</p>
                  <p class="invoice-total-label">of {{ formatCurrency(inv.grand_total) }}</p>
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
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'

const invoices = ref([])
const loading = ref(true)
const error = ref('')
const expandedCustomers = ref({})

const totalOutstanding = computed(() =>
  invoices.value.reduce((sum, inv) => sum + (inv.outstanding_amount || 0), 0)
)

const customerGroups = computed(() => {
  const groups = {}
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (const inv of invoices.value) {
    if (!groups[inv.customer]) {
      groups[inv.customer] = {
        customer: inv.customer,
        customer_name: inv.customer_name || inv.customer,
        invoices: [],
        total: 0,
        hasOverdue: false,
      }
    }
    groups[inv.customer].invoices.push(inv)
    groups[inv.customer].total += inv.outstanding_amount || 0
    if (inv.due_date && new Date(inv.due_date) < today) {
      groups[inv.customer].hasOverdue = true
    }
  }
  return Object.values(groups).sort((a, b) => b.total - a.total)
})

function toggleCustomer(customer) {
  expandedCustomers.value = {
    ...expandedCustomers.value,
    [customer]: !expandedCustomers.value[customer],
  }
}

function isOverdue(dueDate) {
  if (!dueDate) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(dueDate) < today
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 2 }).format(n)
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function loadOutstanding() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/method/live.api.customers.get_my_outstanding', { credentials: 'include' })
    if (!res.ok) throw new Error(`Server error ${res.status}`)
    const { message } = await res.json()
    invoices.value = message || []
  } catch (e) {
    error.value = e.message || 'Failed to load outstanding invoices'
  } finally {
    loading.value = false
  }
}

onMounted(loadOutstanding)
</script>

<style scoped>
.col-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 90px;
}

.col-header {
  background: #fff;
  padding: 20px 16px 14px;
  border-bottom: 1px solid #f1f5f9;
}
.col-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 2px;
}
.col-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

/* Summary */
.summary-bar {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  padding: 14px 16px;
  gap: 0;
}
.summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.summary-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.summary-value {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}
.summary-divider {
  width: 1px;
  height: 32px;
  background: #f1f5f9;
}

/* Loading / empty */
.col-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 16px;
  gap: 16px;
}
.col-empty { color: #94a3b8; }
.empty-text { font-size: 0.9rem; color: #94a3b8; margin: 0; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #1d4ed8;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Error */
.col-error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
  color: #991b1b;
  padding: 12px 16px;
  font-size: 0.85rem;
}
.retry-btn {
  margin-left: auto;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

/* Customer cards */
.customer-card {
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  margin: 10px 12px 0;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.customer-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 14px;
  cursor: pointer;
}
.customer-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.customer-info { flex: 1; min-width: 0; }
.customer-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.customer-meta {
  font-size: 0.72rem;
  color: #94a3b8;
  margin: 2px 0 0;
}
.customer-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}
.customer-outstanding {
  font-size: 0.95rem;
  font-weight: 800;
  color: #1d4ed8;
}
.customer-outstanding.overdue { color: #dc2626; }
.chevron {
  color: #94a3b8;
  transition: transform 0.2s;
}
.chevron.rotated { transform: rotate(180deg); }

/* Invoice list */
.invoice-list {
  border-top: 1px solid #f1f5f9;
}
.invoice-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid #f8fafc;
}
.invoice-item:last-child { border-bottom: none; }
.invoice-item.overdue { background: #fff8f8; }
.invoice-left { flex: 1; min-width: 0; }
.invoice-id {
  font-size: 0.82rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.invoice-date {
  font-size: 0.72rem;
  color: #94a3b8;
  margin: 2px 0 0;
}
.invoice-due {
  font-size: 0.72rem;
  color: #64748b;
  margin: 2px 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.invoice-due.due-overdue { color: #dc2626; }
.overdue-tag {
  background: #fee2e2;
  color: #dc2626;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 1px 5px;
  border-radius: 4px;
}
.invoice-right {
  text-align: right;
  flex-shrink: 0;
}
.invoice-outstanding {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.invoice-total-label {
  font-size: 0.7rem;
  color: #94a3b8;
  margin: 2px 0 0;
}
</style>
