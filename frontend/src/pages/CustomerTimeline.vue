<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="tl-root">

        <!-- Header -->
        <div class="tl-header">
          <button class="back-btn" @click="$router.back()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div class="tl-header-info">
            <h1 class="tl-title">{{ customerName || 'Customer' }}</h1>
            <p class="tl-sub">Timeline</p>
          </div>
          <button class="remind-btn" @click="reminderOpen = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            Remind
          </button>
        </div>

        <!-- Summary strip -->
        <div class="summary-strip" v-if="!loading">
          <div class="strip-item">
            <span class="strip-val">{{ orders.length }}</span>
            <span class="strip-lbl">Orders</span>
          </div>
          <div class="strip-divider"></div>
          <div class="strip-item">
            <span class="strip-val">{{ visits.length }}</span>
            <span class="strip-lbl">Visits</span>
          </div>
          <div class="strip-divider"></div>
          <div class="strip-item">
            <span class="strip-val">{{ fmtKES(totalOutstanding) }}</span>
            <span class="strip-lbl">Outstanding</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="tl-loading">
          <div class="spinner"></div>
        </div>

        <!-- Timeline -->
        <div v-else class="timeline">
          <div
            v-for="(event, i) in timeline"
            :key="i"
            class="tl-event"
            :class="`tl-${event.type}`"
          >
            <!-- Dot + line -->
            <div class="tl-rail">
              <div class="tl-dot" :class="`dot-${event.type}`">
                <!-- Visit icon -->
                <svg v-if="event.type === 'visit'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                <!-- Order icon -->
                <svg v-else-if="event.type === 'order'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10">
                  <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>
                </svg>
                <!-- Invoice icon -->
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="tl-line" v-if="i < timeline.length - 1"></div>
            </div>

            <!-- Card -->
            <div class="tl-card">
              <div class="tl-card-top">
                <span class="tl-type-badge" :class="`badge-${event.type}`">
                  {{ event.typeLabel }}
                </span>
                <span class="tl-date">{{ fmtDate(event.date) }}</span>
              </div>
              <p class="tl-card-title">{{ event.title }}</p>
              <p class="tl-card-sub" v-if="event.sub">{{ event.sub }}</p>

              <!-- Visit-specific -->
              <div v-if="event.type === 'visit'" class="tl-visit-meta">
                <span v-if="event.duration" class="tl-chip">{{ event.duration }} min</span>
                <span v-if="event.linked_order" class="tl-chip tl-chip-blue">Order placed</span>
                <span v-if="event.notes" class="tl-notes">{{ event.notes }}</span>
              </div>

              <!-- Order-specific -->
              <div v-if="event.type === 'order'" class="tl-order-meta">
                <span class="tl-status" :class="statusClass(event.status)">{{ event.status }}</span>
                <span class="tl-amount">{{ fmtKES(event.amount) }}</span>
                <button class="tl-view-btn" @click="viewOrder(event.ref)">View →</button>
              </div>
            </div>
          </div>

          <div v-if="timeline.length === 0" class="tl-empty">
            No activity found for this customer.
          </div>
        </div>

        <!-- Reminder modal -->
        <div v-if="reminderOpen" class="modal-backdrop" @click.self="reminderOpen = false">
          <div class="modal-sheet">
            <div class="modal-header">
              <h3 class="modal-title">Set Follow-up Reminder</h3>
              <button class="modal-close" @click="reminderOpen = false">✕</button>
            </div>
            <div class="modal-body">
              <label class="modal-label">Date &amp; Time</label>
              <input v-model="newReminder.date" type="datetime-local" class="modal-input" />
              <label class="modal-label">Note</label>
              <textarea v-model="newReminder.note" class="modal-textarea" rows="2" placeholder="e.g. Follow up on pending invoice…"></textarea>
              <button class="modal-save" @click="saveReminder">Set Reminder</button>
              <div v-if="reminderSaved" class="modal-success">Reminder set!</div>
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
import { useRoute, useRouter } from 'vue-router'
import { useReminders } from '../composables/useReminders'

const route = useRoute()
const router = useRouter()
const { addReminder } = useReminders()

const customerId = route.params.id
const customerName = ref('')
const visits = ref([])
const orders = ref([])
const invoices = ref([])
const loading = ref(true)
const reminderOpen = ref(false)
const reminderSaved = ref(false)
const newReminder = ref({ date: '', note: '' })

const totalOutstanding = computed(() =>
  invoices.value.reduce((s, inv) => s + (inv.outstanding_amount || 0), 0)
)

const timeline = computed(() => {
  const events = []

  for (const v of visits.value) {
    events.push({
      type: 'visit',
      typeLabel: 'Visit',
      date: v.start_time,
      title: `Visit to ${customerName.value}`,
      sub: v.end_time ? null : 'In progress',
      duration: v.duration_minutes,
      linked_order: v.sales_order,
      notes: v.notes,
      ref: v.name,
    })
  }

  for (const o of orders.value) {
    events.push({
      type: 'order',
      typeLabel: 'Order',
      date: o.transaction_date,
      title: o.name,
      sub: null,
      status: o.status,
      amount: o.grand_total,
      ref: o.name,
    })
  }

  for (const inv of invoices.value.filter(i => i.outstanding_amount > 0)) {
    events.push({
      type: 'invoice',
      typeLabel: 'Invoice',
      date: inv.posting_date,
      title: inv.name,
      sub: `Outstanding: ${fmtKES(inv.outstanding_amount)}`,
      ref: inv.name,
    })
  }

  return events.sort((a, b) => new Date(b.date) - new Date(a.date))
})

function fmtKES(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 }).format(n)
}

function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function statusClass(status) {
  if (['Completed'].includes(status)) return 'status-green'
  if (['Draft'].includes(status)) return 'status-gray'
  if (['Cancelled'].includes(status)) return 'status-red'
  return 'status-blue'
}

function viewOrder(id) {
  router.push({ name: 'OrderDetails', params: { id } })
}

function saveReminder() {
  if (!newReminder.value.date) return
  addReminder({
    customer: customerId,
    customerName: customerName.value,
    date: newReminder.value.date,
    note: newReminder.value.note,
  })
  reminderSaved.value = true
  newReminder.value = { date: '', note: '' }
  setTimeout(() => {
    reminderSaved.value = false
    reminderOpen.value = false
  }, 1500)
}

async function load() {
  loading.value = true
  try {
    const [custRes, visitsRes, ordersRes, invoicesRes] = await Promise.all([
      fetch(`/api/resource/Customer/${encodeURIComponent(customerId)}?fields=["customer_name"]`, { credentials: 'include' }),
      fetch(`/api/resource/Customer%20Visits?filters=[["customer","=","${customerId}"]]&fields=["name","start_time","end_time","duration_minutes","notes","sales_order"]&order_by=start_time%20desc&limit=50`, { credentials: 'include' }),
      fetch(`/api/resource/Sales%20Order?filters=[["customer","=","${customerId}"],["docstatus","!=",2]]&fields=["name","transaction_date","status","grand_total"]&order_by=transaction_date%20desc&limit=50`, { credentials: 'include' }),
      fetch(`/api/resource/Sales%20Invoice?filters=[["customer","=","${customerId}"],["docstatus","=",1]]&fields=["name","posting_date","grand_total","outstanding_amount"]&order_by=posting_date%20desc&limit=50`, { credentials: 'include' }),
    ])

    const custData = (await custRes.json()).data
    customerName.value = custData?.customer_name || customerId

    visits.value = (await visitsRes.json()).data || []
    orders.value = (await ordersRes.json()).data || []
    invoices.value = (await invoicesRes.json()).data || []
  } catch (e) {
    console.error('Timeline load error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.tl-root {
  background: #f8fafc;
  min-height: 100%;
  padding-bottom: 90px;
}

.tl-header {
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
.tl-header-info { flex: 1; }
.tl-title { font-size: 1rem; font-weight: 800; color: #0f172a; margin: 0; }
.tl-sub { font-size: 0.72rem; color: #94a3b8; margin: 0; }
.remind-btn {
  display: flex; align-items: center; gap: 5px;
  background: #eff6ff; color: #1d4ed8; border: none;
  border-radius: 10px; padding: 7px 12px;
  font-size: 0.78rem; font-weight: 700; cursor: pointer; flex-shrink: 0;
}

.summary-strip {
  display: flex; align-items: center;
  background: #fff; border-bottom: 1px solid #f1f5f9;
  padding: 12px 16px; gap: 0;
}
.strip-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.strip-val { font-size: 1rem; font-weight: 800; color: #0f172a; }
.strip-lbl { font-size: 0.65rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; }
.strip-divider { width: 1px; height: 32px; background: #f1f5f9; }

.tl-loading { display: flex; justify-content: center; padding: 60px 20px; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

/* Timeline */
.timeline { padding: 16px; display: flex; flex-direction: column; }
.tl-event { display: flex; gap: 12px; }

.tl-rail { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.tl-dot {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 2px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,.1);
}
.dot-visit   { background: #eff6ff; color: #1d4ed8; }
.dot-order   { background: #f0fdf4; color: #166534; }
.dot-invoice { background: #fffbeb; color: #92400e; }
.tl-line { flex: 1; width: 2px; background: #f1f5f9; margin: 4px 0; min-height: 20px; }

.tl-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 14px; padding: 12px 14px;
  margin-bottom: 12px; flex: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.tl-card-top {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px;
}
.tl-type-badge {
  font-size: 0.6rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 2px 7px; border-radius: 6px;
}
.badge-visit   { background: #eff6ff; color: #1d4ed8; }
.badge-order   { background: #f0fdf4; color: #166534; }
.badge-invoice { background: #fffbeb; color: #92400e; }
.tl-date { font-size: 0.68rem; color: #94a3b8; }
.tl-card-title { font-size: 0.88rem; font-weight: 700; color: #0f172a; margin: 0 0 2px; }
.tl-card-sub { font-size: 0.75rem; color: #94a3b8; margin: 0; }

.tl-visit-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 8px; }
.tl-chip {
  font-size: 0.68rem; font-weight: 700; padding: 2px 8px;
  border-radius: 6px; background: #f1f5f9; color: #475569;
}
.tl-chip-blue { background: #eff6ff; color: #1d4ed8; }
.tl-notes { font-size: 0.75rem; color: #64748b; font-style: italic; width: 100%; }

.tl-order-meta { display: flex; align-items: center; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.tl-status {
  font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;
}
.status-green { background: #dcfce7; color: #166534; }
.status-gray  { background: #f1f5f9; color: #475569; }
.status-red   { background: #fee2e2; color: #991b1b; }
.status-blue  { background: #dbeafe; color: #1e40af; }
.tl-amount { font-size: 0.85rem; font-weight: 700; color: #1e293b; flex: 1; }
.tl-view-btn {
  background: none; border: none; color: #1d4ed8;
  font-size: 0.75rem; font-weight: 700; cursor: pointer; padding: 0;
}

.tl-empty { text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 40px 20px; }

/* Reminder modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  z-index: 200; display: flex; align-items: flex-end; justify-content: center;
}
.modal-sheet {
  background: #fff; border-radius: 24px 24px 0 0;
  width: 100%; max-width: 500px;
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
.modal-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 8px; }
.modal-label { font-size: 0.78rem; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.04em; }
.modal-input, .modal-textarea {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #1e293b; box-sizing: border-box;
}
.modal-textarea { resize: none; }
.modal-save {
  background: #1d4ed8; color: #fff; border: none; border-radius: 12px;
  padding: 13px; font-weight: 700; font-size: 0.9rem; cursor: pointer; margin-top: 4px;
}
.modal-success {
  text-align: center; color: #166534; font-size: 0.85rem;
  font-weight: 600; padding: 8px; background: #f0fdf4; border-radius: 8px;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
