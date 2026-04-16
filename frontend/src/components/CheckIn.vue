<template>
  <div class="checkin-card">
    <!-- Status header -->
    <div class="checkin-header">
      <div class="checkin-status-dot" :class="isCheckedIn ? 'dot-in' : 'dot-out'"></div>
      <div class="checkin-header-text">
        <p class="checkin-name">{{ fullName || currentUser || 'You' }}</p>
        <p class="checkin-status-label">{{ isCheckedIn ? 'Checked In' : 'Not checked in' }}</p>
      </div>
      <button class="checkin-history-btn" @click="showHistory = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
      </button>
    </div>

    <!-- Last times -->
    <div class="checkin-times" v-if="!loadingTimes">
      <div class="checkin-time-item">
        <span class="time-label">Last In</span>
        <span class="time-value">{{ lastCheckIn ? formatTime(lastCheckIn) : '—' }}</span>
      </div>
      <div class="checkin-time-divider"></div>
      <div class="checkin-time-item">
        <span class="time-label">Last Out</span>
        <span class="time-value">{{ lastCheckOut ? formatTime(lastCheckOut) : '—' }}</span>
      </div>
    </div>
    <div class="checkin-times-loading" v-else>
      <div class="mini-spinner"></div>
    </div>

    <!-- Error banner -->
    <div v-if="errorMsg" class="checkin-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {{ errorMsg }}
    </div>

    <!-- Employee not linked warning -->
    <div v-if="employeeError" class="checkin-warning">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      No Employee record linked to your account. Contact HR to link your Employee profile.
    </div>

    <!-- Action button -->
    <button
      class="checkin-btn"
      :class="isCheckedIn ? 'btn-checkout' : 'btn-checkin'"
      :disabled="actionLoading || employeeError || loadingEmployee"
      @click="handleCheckInOut"
    >
      <span v-if="actionLoading" class="btn-spinner"></span>
      <span v-else-if="loadingEmployee">Resolving employee…</span>
      <span v-else>{{ isCheckedIn ? 'Check Out' : 'Check In' }}</span>
    </button>

    <!-- History modal -->
    <div v-if="showHistory" class="modal-backdrop" @click.self="showHistory = false">
      <div class="modal-sheet">
        <div class="modal-header">
          <h3 class="modal-title">Check-In History</h3>
          <button class="modal-close" @click="showHistory = false">✕</button>
        </div>
        <div class="history-list">
          <div v-if="checkInList.length === 0" class="history-empty">No records found</div>
          <div
            v-for="(log, i) in checkInList"
            :key="i"
            class="history-item"
          >
            <div class="history-badge" :class="log.log_type === 'IN' ? 'badge-in' : 'badge-out'">
              {{ log.log_type === 'IN' ? 'IN' : 'OUT' }}
            </div>
            <div class="history-info">
              <p class="history-time">{{ formatDateTime(log.time) }}</p>
              <p class="history-loc" v-if="log.latitude">
                {{ Number(log.latitude).toFixed(4) }}, {{ Number(log.longitude).toFixed(4) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { session } from '@/data/session'

const currentUser = session.user
const fullName = ref('')
const employeeId = ref(null)
const employeeError = ref(false)
const loadingEmployee = ref(true)
const loadingTimes = ref(true)
const actionLoading = ref(false)
const errorMsg = ref('')
const isCheckedIn = ref(false)
const lastCheckIn = ref(null)
const lastCheckOut = ref(null)
const checkInList = ref([])
const showHistory = ref(false)

async function resolveEmployee() {
  try {
    const res = await fetch(
      `/api/resource/Employee?filters=[["user_id","=","${currentUser}"]]&fields=["name","employee_name"]&limit=1`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    if (data && data.length > 0) {
      employeeId.value = data[0].name
      fullName.value = data[0].employee_name || ''
    } else {
      employeeError.value = true
    }
  } catch (e) {
    console.error('Failed to resolve employee:', e)
    employeeError.value = true
  } finally {
    loadingEmployee.value = false
  }
}

async function fetchCheckInOutTimes() {
  if (!employeeId.value) return
  loadingTimes.value = true
  try {
    const res = await fetch(
      `/api/resource/Employee%20Checkin?filters=[["employee","=","${employeeId.value}"]]&fields=["log_type","time","latitude","longitude","name"]&order_by=creation%20desc&limit=20`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    checkInList.value = data || []
    const latestIn = data?.find(r => r.log_type === 'IN')
    const latestOut = data?.find(r => r.log_type === 'OUT')
    lastCheckIn.value = latestIn?.time || null
    lastCheckOut.value = latestOut?.time || null

    // Determine if checked in: last record is IN
    if (data && data.length > 0) {
      isCheckedIn.value = data[0].log_type === 'IN'
    }
  } catch (e) {
    console.error('Failed to fetch checkin times:', e)
  } finally {
    loadingTimes.value = false
  }
}

async function getCurrentLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve({ latitude: null, longitude: null })
    navigator.geolocation.getCurrentPosition(
      pos => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => resolve({ latitude: null, longitude: null }),
      { enableHighAccuracy: false, timeout: 8000 }
    )
  })
}

async function handleCheckInOut() {
  if (!employeeId.value) return
  errorMsg.value = ''
  actionLoading.value = true
  try {
    const logType = isCheckedIn.value ? 'OUT' : 'IN'
    const now = new Date()
    const pad = n => String(n).padStart(2, '0')
    const formattedTime = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`

    const { latitude, longitude } = await getCurrentLocation()

    const res = await fetch('/api/resource/Employee%20Checkin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        employee: employeeId.value,
        time: formattedTime,
        log_type: logType,
        ...(latitude != null && { latitude, longitude }),
      }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body?.exception || body?.message || 'Check-in failed')
    }

    isCheckedIn.value = logType === 'IN'
    await fetchCheckInOutTimes()
  } catch (e) {
    console.error('Check-in error:', e)
    errorMsg.value = e.message || 'Something went wrong. Please try again.'
    setTimeout(() => { errorMsg.value = '' }, 5000)
  } finally {
    actionLoading.value = false
  }
}

function formatTime(dt) {
  if (!dt) return '—'
  const d = new Date(dt)
  if (isNaN(d)) return dt
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

function formatDateTime(dt) {
  if (!dt) return '—'
  const d = new Date(dt)
  if (isNaN(d)) return dt
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true })
}

onMounted(async () => {
  if (!session.isLoggedIn) return
  await resolveEmployee()
  await fetchCheckInOutTimes()
})
</script>

<style scoped>
.checkin-card {
  background: #fff;
  border-radius: 20px;
  margin: 12px 16px;
  padding: 20px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  border: 1px solid #f1f5f9;
}

.checkin-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.checkin-status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-in { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,0.2); }
.dot-out { background: #94a3b8; }

.checkin-header-text { flex: 1; }

.checkin-name {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.checkin-status-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 2px 0 0;
}

.checkin-history-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkin-times {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 16px;
  gap: 16px;
}

.checkin-time-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.time-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
}

.checkin-time-divider {
  width: 1px;
  height: 32px;
  background: #e2e8f0;
}

.checkin-times-loading {
  display: flex;
  justify-content: center;
  padding: 12px;
  margin-bottom: 16px;
}

.checkin-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.8rem;
  margin-bottom: 14px;
}

.checkin-warning {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.8rem;
  margin-bottom: 14px;
  line-height: 1.4;
}

.checkin-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.15s;
}
.checkin-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-checkin { background: #1d4ed8; color: #fff; }
.btn-checkin:not(:disabled):hover { background: #1e40af; }
.btn-checkout { background: #fef2f2; color: #dc2626; border: 1.5px solid #fecaca; }
.btn-checkout:not(:disabled):hover { background: #fee2e2; }

.btn-spinner,
.mini-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.mini-spinner {
  border-color: rgba(100,116,139,0.3);
  border-top-color: #64748b;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.modal-sheet {
  background: #fff;
  border-radius: 24px 24px 0 0;
  width: 100%;
  max-width: 500px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom, 16px);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 12px;
  border-bottom: 1px solid #f1f5f9;
}
.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}
.modal-close {
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  color: #6b7280;
  font-size: 0.8rem;
}
.history-list {
  overflow-y: auto;
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.history-empty {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  padding: 24px;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 10px;
}
.history-badge {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  padding: 3px 8px;
  border-radius: 6px;
  flex-shrink: 0;
}
.badge-in { background: #dcfce7; color: #166534; }
.badge-out { background: #fee2e2; color: #991b1b; }
.history-info { flex: 1; }
.history-time { font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0; }
.history-loc { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
</style>
