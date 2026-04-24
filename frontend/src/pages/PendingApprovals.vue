<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="ap-root">

        <!-- Header -->
        <div class="ap-header">
          <h1 class="ap-title">{{ isManager ? 'Approval Queue' : 'My Requests' }}</h1>
          <p class="ap-sub">{{ pending.length }} pending</p>
        </div>

        <!-- Tabs -->
        <div class="ap-tabs">
          <button v-for="t in tabs" :key="t.key" class="ap-tab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">
            {{ t.label }}
            <span v-if="t.key === 'Pending' && pending.length" class="tab-count">{{ pending.length }}</span>
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="ap-loading"><div class="spinner"></div></div>

        <!-- Empty -->
        <div v-else-if="filtered.length === 0" class="ap-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" style="color:#cbd5e1">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="M9 12h6M9 16h4"/>
          </svg>
          <p>No {{ activeTab.toLowerCase() }} requests</p>
        </div>

        <!-- List -->
        <div v-else class="ap-list">
          <div v-for="req in filtered" :key="req.name" class="ap-card">
            <!-- Card header -->
            <div class="card-top">
              <div>
                <p class="card-id">{{ req.name }}</p>
                <p class="card-customer">{{ req.customer_name }}</p>
                <p class="card-rep" v-if="isManager">by {{ req.sales_rep_name }}</p>
              </div>
              <div class="card-right">
                <span class="status-badge" :class="`status-${req.status.toLowerCase()}`">{{ req.status }}</span>
                <span class="card-amount">{{ fmtKES(req.total_amount) }}</span>
              </div>
            </div>

            <!-- Submitted at -->
            <p class="card-date">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="11" height="11">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              {{ fmtDatetime(req.submitted_at) }}
            </p>

            <!-- Reason -->
            <p class="card-reason" v-if="req.reason">{{ req.reason }}</p>

            <!-- Items preview -->
            <div class="card-items" v-if="req.order_items && req.order_items.length">
              <div v-for="(it, i) in req.order_items.slice(0, 3)" :key="i" class="card-item">
                <span>{{ it.item_code }}</span>
                <span class="item-qty">× {{ it.qty }}</span>
                <span class="item-rate">{{ fmtKES(it.rate) }}</span>
              </div>
              <p v-if="req.order_items.length > 3" class="more-items">+ {{ req.order_items.length - 3 }} more items</p>
            </div>

            <!-- Rejection reason -->
            <div v-if="req.status === 'Rejected' && req.rejection_reason" class="rejection-note">
              Rejected: {{ req.rejection_reason }}
            </div>

            <!-- Approved order link -->
            <div v-if="req.sales_order" class="approved-note">
              ✓ Order created:
              <button class="order-link" @click="viewOrder(req.sales_order)">{{ req.sales_order }} →</button>
            </div>

            <!-- Manager actions -->
            <div class="card-actions" v-if="isManager && req.status === 'Pending'">
              <button class="btn-approve" :disabled="actionLoading === req.name" @click="approve(req.name)">
                <span v-if="actionLoading === req.name + '-approve'" class="btn-spin"></span>
                <span v-else>✓ Approve</span>
              </button>
              <button class="btn-reject" :disabled="actionLoading === req.name" @click="openReject(req)">Reject</button>
            </div>
          </div>
        </div>

        <!-- Reject modal -->
        <div v-if="rejectModal.open" class="modal-backdrop" @click.self="rejectModal.open = false">
          <div class="modal-sheet">
            <div class="modal-header">
              <h3 class="modal-title">Reject Order</h3>
              <button class="modal-close" @click="rejectModal.open = false">✕</button>
            </div>
            <div class="modal-body">
              <p class="modal-desc">Rejecting {{ rejectModal.name }} — {{ rejectModal.customer }}</p>
              <label class="modal-label">Reason (required)</label>
              <textarea v-model="rejectModal.reason" class="modal-textarea" rows="3" placeholder="Explain why this order is rejected…"></textarea>
              <button class="modal-reject-btn" :disabled="!rejectModal.reason.trim()" @click="confirmReject">Confirm Rejection</button>
            </div>
          </div>
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
const loading = ref(true)
const rows = ref([])
const isManager = ref(false)
const activeTab = ref('Pending')
const actionLoading = ref('')
const rejectModal = ref({ open: false, name: '', customer: '', reason: '' })

const tabs = [
  { key: 'Pending', label: 'Pending' },
  { key: 'Approved', label: 'Approved' },
  { key: 'Rejected', label: 'Rejected' },
]

const pending = computed(() => rows.value.filter(r => r.status === 'Pending'))
const filtered = computed(() => rows.value.filter(r => r.status === activeTab.value))

function fmtKES(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 }).format(n)
}

function fmtDatetime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function viewOrder(id) {
  router.push({ name: 'OrderDetails', params: { id } })
}

async function loadApprovals() {
  loading.value = true
  try {
    const res = await fetch('/api/method/live.api.approval.get_pending_approvals', { credentials: 'include' })
    const { message } = await res.json()
    rows.value = (message?.rows || [])
    isManager.value = message?.is_manager || false
  } catch (e) {
    console.error('Approvals load error:', e)
  } finally {
    loading.value = false
  }
}

function getCsrf() {
  return window.csrf_token || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
}

async function approve(name) {
  actionLoading.value = `${name}-approve`
  try {
    const res = await fetch('/api/method/live.api.approval.process_approval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': getCsrf() },
      credentials: 'include',
      body: JSON.stringify({ approval_name: name, approved: 1 }),
    })
    if (!res.ok) throw new Error('Failed')
    await loadApprovals()
  } catch (e) {
    console.error('Approve error:', e)
  } finally {
    actionLoading.value = ''
  }
}

function openReject(req) {
  rejectModal.value = { open: true, name: req.name, customer: req.customer_name, reason: '' }
}

async function confirmReject() {
  const { name, reason } = rejectModal.value
  actionLoading.value = `${name}-reject`
  try {
    const res = await fetch('/api/method/live.api.approval.process_approval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': getCsrf() },
      credentials: 'include',
      body: JSON.stringify({ approval_name: name, approved: 0, rejection_reason: reason }),
    })
    if (!res.ok) throw new Error('Failed')
    rejectModal.value.open = false
    await loadApprovals()
  } catch (e) {
    console.error('Reject error:', e)
  } finally {
    actionLoading.value = ''
  }
}

onMounted(loadApprovals)
</script>

<style scoped>
.ap-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 90px;
}

.ap-header {
  padding: 20px 16px 10px;
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
}
.ap-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 2px; }
.ap-sub { font-size: 0.75rem; color: #94a3b8; margin: 0; }

.ap-tabs {
  display: flex; gap: 6px; padding: 10px 16px;
  background: #fff; border-bottom: 1px solid #f1f5f9;
}
.ap-tab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 5px;
  padding: 7px; border: 1.5px solid #e2e8f0; border-radius: 10px;
  background: #fff; font-size: 0.8rem; font-weight: 600; color: #64748b; cursor: pointer;
}
.ap-tab.active { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }
.tab-count {
  background: #ef4444; color: #fff;
  font-size: 0.6rem; font-weight: 800; padding: 1px 5px; border-radius: 9999px;
}

.ap-loading { display: flex; justify-content: center; padding: 60px 20px; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.ap-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 20px; gap: 12px; color: #94a3b8; font-size: 0.9rem;
}

.ap-list { padding: 12px 12px; display: flex; flex-direction: column; gap: 12px; }

.ap-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 16px; padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.card-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 8px;
}
.card-id { font-size: 0.75rem; font-weight: 700; color: #94a3b8; margin: 0; }
.card-customer { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin: 2px 0 0; }
.card-rep { font-size: 0.75rem; color: #64748b; margin: 2px 0 0; }
.card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.card-amount { font-size: 1rem; font-weight: 800; color: #1d4ed8; }

.status-badge {
  font-size: 0.62rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.04em; padding: 2px 8px; border-radius: 6px;
}
.status-pending  { background: #fef3c7; color: #92400e; }
.status-approved { background: #dcfce7; color: #166534; }
.status-rejected { background: #fee2e2; color: #991b1b; }

.card-date {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.72rem; color: #94a3b8; margin: 0 0 6px;
}
.card-reason { font-size: 0.8rem; color: #64748b; font-style: italic; margin: 0 0 8px; }

.card-items { display: flex; flex-direction: column; gap: 4px; margin: 0 0 8px; }
.card-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.78rem; color: #374151; padding: 4px 8px;
  background: #f8fafc; border-radius: 6px;
}
.item-qty { color: #94a3b8; }
.item-rate { margin-left: auto; font-weight: 600; color: #1e293b; }
.more-items { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; font-style: italic; }

.rejection-note {
  font-size: 0.78rem; color: #991b1b; background: #fef2f2;
  border-radius: 8px; padding: 8px 10px; margin-bottom: 8px;
}
.approved-note {
  font-size: 0.78rem; color: #166534; background: #f0fdf4;
  border-radius: 8px; padding: 8px 10px; margin-bottom: 8px;
  display: flex; align-items: center; gap: 6px;
}
.order-link {
  background: none; border: none; color: #1d4ed8;
  font-weight: 700; font-size: 0.78rem; cursor: pointer; padding: 0;
}

.card-actions { display: flex; gap: 8px; margin-top: 8px; }
.btn-approve {
  flex: 1; padding: 10px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 10px; font-weight: 700; font-size: 0.85rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.btn-approve:disabled { opacity: 0.55; }
.btn-reject {
  flex: 1; padding: 10px; background: #fef2f2; color: #dc2626;
  border: 1.5px solid #fecaca; border-radius: 10px;
  font-weight: 700; font-size: 0.85rem; cursor: pointer;
}
.btn-spin {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block;
}

/* Reject modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  z-index: 200; display: flex; align-items: flex-end;
}
.modal-sheet {
  background: #fff; border-radius: 24px 24px 0 0; width: 100%;
  padding-bottom: env(safe-area-inset-bottom, 16px);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 20px 12px; border-bottom: 1px solid #f1f5f9;
}
.modal-title { font-size: 1rem; font-weight: 700; color: #111827; margin: 0; }
.modal-close {
  background: #f3f4f6; border: none; border-radius: 50%;
  width: 28px; height: 28px; cursor: pointer; color: #6b7280;
}
.modal-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 10px; }
.modal-desc { font-size: 0.85rem; color: #64748b; margin: 0; }
.modal-label { font-size: 0.78rem; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.04em; }
.modal-textarea {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0;
  border-radius: 10px; font-size: 0.9rem; color: #1e293b; box-sizing: border-box; resize: none;
}
.modal-reject-btn {
  background: #dc2626; color: #fff; border: none; border-radius: 12px;
  padding: 13px; font-weight: 700; font-size: 0.9rem; cursor: pointer;
}
.modal-reject-btn:disabled { opacity: 0.45; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
