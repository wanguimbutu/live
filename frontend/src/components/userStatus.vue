<template>
  <div class="attendance-root">
    <!-- Device status bar -->
    <div class="device-bar">
      <div class="device-item">
        <div class="device-icon-wrap" :class="batteryColor">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <rect x="2" y="7" width="18" height="10" rx="2"/>
            <line x1="22" y1="11" x2="22" y2="13"/>
            <rect class="battery-fill-icon" :x="3" y="8" :width="Math.max(0, Math.round((battery / 100) * 16))" height="8" rx="1" fill="currentColor" stroke="none"/>
          </svg>
        </div>
        <div>
          <p class="device-value">{{ battery != null ? battery + '%' : '—' }} <span v-if="isCharging">⚡</span></p>
          <p class="device-label">Battery</p>
        </div>
      </div>
      <div class="device-divider"></div>
      <div class="device-item">
        <div class="device-icon-wrap" :class="isOnline ? 'icon-green' : 'icon-gray'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/>
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>
          </svg>
        </div>
        <div>
          <p class="device-value">{{ isOnline ? 'Online' : 'Offline' }}</p>
          <p class="device-label">Connection</p>
        </div>
      </div>
      <div class="device-divider"></div>
      <div class="device-item">
        <div class="device-icon-wrap icon-blue">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.5 8 14 8 14s8-8.5 8-14a8 8 0 0 0-8-8z"/>
          </svg>
        </div>
        <div>
          <p class="device-value" style="font-size:0.75rem">{{ locationLabel }}</p>
          <p class="device-label">Location</p>
        </div>
      </div>
    </div>

    <!-- Month header + nav -->
    <div class="calendar-nav">
      <button class="nav-btn" @click="prevMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <h2 class="calendar-month">{{ monthLabel }}</h2>
      <button class="nav-btn" @click="nextMonth" :disabled="isCurrentMonth">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>

    <!-- Month stats -->
    <div class="month-stats">
      <div class="mstat">
        <p class="mstat-val">{{ monthStats.present }}</p>
        <p class="mstat-lbl">Present</p>
      </div>
      <div class="mstat">
        <p class="mstat-val absent">{{ monthStats.absent }}</p>
        <p class="mstat-lbl">Absent</p>
      </div>
      <div class="mstat">
        <p class="mstat-val">{{ monthStats.checkins }}</p>
        <p class="mstat-lbl">Check-ins</p>
      </div>
    </div>

    <!-- Calendar grid -->
    <div class="cal-grid" v-if="!loadingCalendar">
      <div class="cal-dow" v-for="d in ['S','M','T','W','T','F','S']" :key="d">{{ d }}</div>
      <div
        v-for="cell in calendarCells"
        :key="cell.key"
        class="cal-cell"
        :class="{
          'cell-empty': !cell.day,
          'cell-today': cell.isToday,
          'cell-checked-in': cell.hasCheckIn,
          'cell-weekend': cell.isWeekend && !cell.hasCheckIn,
        }"
      >
        <span v-if="cell.day">{{ cell.day }}</span>
      </div>
    </div>
    <div v-else class="cal-loading"><div class="mini-spinner"></div></div>

    <!-- Recent check-in log -->
    <div class="section-label">Recent Activity</div>
    <div v-if="loadingLog" class="log-loading"><div class="mini-spinner"></div></div>
    <div v-else-if="checkInLog.length === 0" class="log-empty">No check-in records found</div>
    <div v-else class="log-list">
      <div
        v-for="(log, i) in checkInLog"
        :key="i"
        class="log-item"
      >
        <div class="log-badge" :class="log.log_type === 'IN' ? 'badge-in' : 'badge-out'">
          {{ log.log_type }}
        </div>
        <div class="log-info">
          <p class="log-time">{{ formatDateTime(log.time) }}</p>
          <p class="log-loc" v-if="log.latitude">{{ Number(log.latitude).toFixed(4) }}, {{ Number(log.longitude).toFixed(4) }}</p>
        </div>
        <div class="log-ago">{{ timeAgo(log.time) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { session } from '@/data/session'

const battery = ref(null)
const isCharging = ref(false)
const isOnline = ref(navigator.onLine)
const location = ref(null)
const locationLabel = ref('Fetching…')
const loadingCalendar = ref(true)
const loadingLog = ref(true)
const checkInLog = ref([])
const employeeId = ref(null)

const now = new Date()
const viewYear = ref(now.getFullYear())
const viewMonth = ref(now.getMonth()) // 0-indexed

const monthLabel = computed(() => {
  return new Date(viewYear.value, viewMonth.value).toLocaleString('en-US', { month: 'long', year: 'numeric' })
})

const isCurrentMonth = computed(() => {
  const n = new Date()
  return viewYear.value === n.getFullYear() && viewMonth.value === n.getMonth()
})

function prevMonth() {
  if (viewMonth.value === 0) { viewMonth.value = 11; viewYear.value-- }
  else viewMonth.value--
  buildCalendar()
}

function nextMonth() {
  if (isCurrentMonth.value) return
  if (viewMonth.value === 11) { viewMonth.value = 0; viewYear.value++ }
  else viewMonth.value++
  buildCalendar()
}

// Track which days have check-ins
const checkInDays = ref(new Set())

const calendarCells = ref([])

async function buildCalendar() {
  loadingCalendar.value = true
  await fetchMonthCheckins()
  const firstDay = new Date(viewYear.value, viewMonth.value, 1).getDay()
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const todayDate = new Date()

  const cells = []
  for (let i = 0; i < firstDay; i++) cells.push({ key: `e${i}`, day: null })
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const isToday = viewYear.value === todayDate.getFullYear() &&
                    viewMonth.value === todayDate.getMonth() &&
                    d === todayDate.getDate()
    const dow = new Date(viewYear.value, viewMonth.value, d).getDay()
    cells.push({
      key: iso,
      day: d,
      isToday,
      hasCheckIn: checkInDays.value.has(iso),
      isWeekend: dow === 0 || dow === 6,
    })
  }
  calendarCells.value = cells
  loadingCalendar.value = false
}

const monthStats = computed(() => {
  const total = calendarCells.value.filter(c => c.day && !c.isWeekend).length
  const present = calendarCells.value.filter(c => c.day && c.hasCheckIn).length
  const workdays = Math.min(
    calendarCells.value.filter(c => c.day && !c.isWeekend).length,
    isCurrentMonth.value ? new Date().getDate() : 31
  )
  return {
    present,
    absent: Math.max(0, workdays - present),
    checkins: checkInLog.value.filter(l => {
      if (!l.time) return false
      const d = new Date(l.time)
      return d.getFullYear() === viewYear.value && d.getMonth() === viewMonth.value && l.log_type === 'IN'
    }).length,
  }
})

async function fetchEmployeeId() {
  try {
    const res = await fetch(
      `/api/resource/Employee?filters=[["user_id","=","${session.user}"]]&fields=["name"]&limit=1`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    if (data?.length > 0) employeeId.value = data[0].name
  } catch (e) { console.error(e) }
}

async function fetchMonthCheckins() {
  if (!employeeId.value) return
  try {
    const y = viewYear.value
    const m = viewMonth.value + 1
    const from = `${y}-${String(m).padStart(2,'0')}-01`
    const to = `${y}-${String(m).padStart(2,'0')}-31`
    const res = await fetch(
      `/api/resource/Employee%20Checkin?filters=[["employee","=","${employeeId.value}"],["time",">=","${from}"],["time","<=","${to}"]]&fields=["time","log_type"]&limit=200`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    const days = new Set()
    ;(data || []).forEach(r => {
      if (r.time) {
        const d = new Date(r.time)
        const iso = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        days.add(iso)
      }
    })
    checkInDays.value = days
  } catch (e) { console.error(e) }
}

async function fetchRecentLog() {
  if (!employeeId.value) return
  loadingLog.value = true
  try {
    const res = await fetch(
      `/api/resource/Employee%20Checkin?filters=[["employee","=","${employeeId.value}"]]&fields=["log_type","time","latitude","longitude"]&order_by=time%20desc&limit=30`,
      { credentials: 'include' }
    )
    const { data } = await res.json()
    checkInLog.value = data || []
  } catch (e) { console.error(e) }
  finally { loadingLog.value = false }
}

async function fetchBattery() {
  if (!('getBattery' in navigator)) return
  try {
    const b = await navigator.getBattery()
    battery.value = Math.round(b.level * 100)
    isCharging.value = b.charging
    b.addEventListener('levelchange', () => { battery.value = Math.round(b.level * 100) })
    b.addEventListener('chargingchange', () => { isCharging.value = b.charging })
  } catch (e) {}
}

function fetchLocation() {
  if (!navigator.geolocation) { locationLabel.value = 'Not supported'; return }
  navigator.geolocation.getCurrentPosition(
    pos => {
      location.value = pos.coords
      locationLabel.value = `${pos.coords.latitude.toFixed(3)}, ${pos.coords.longitude.toFixed(3)}`
    },
    () => { locationLabel.value = 'Unavailable' },
    { enableHighAccuracy: false, timeout: 8000 }
  )
}

const batteryColor = computed(() => {
  if (battery.value == null) return 'icon-gray'
  if (isCharging.value) return 'icon-green'
  if (battery.value > 50) return 'icon-green'
  if (battery.value > 20) return 'icon-amber'
  return 'icon-red'
})

function formatDateTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true })
}

function timeAgo(dt) {
  if (!dt) return ''
  const secs = Math.floor((Date.now() - new Date(dt)) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return `${Math.floor(secs / 86400)}d ago`
}

function handleOnline() { isOnline.value = true }
function handleOffline() { isOnline.value = false }

onMounted(async () => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  fetchBattery()
  fetchLocation()
  await fetchEmployeeId()
  await Promise.all([buildCalendar(), fetchRecentLog()])
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style scoped>
.attendance-root {
  background: #f8fafc;
  min-height: 100%;
  padding: 0 16px 80px;
}

/* Device bar */
.device-bar {
  display: flex; align-items: center;
  background: #fff; border-radius: 16px; padding: 14px 16px;
  margin: 16px 0 12px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.device-item { display: flex; align-items: center; gap: 10px; flex: 1; }
.device-divider { width: 1px; height: 36px; background: #f1f5f9; margin: 0 8px; }
.device-icon-wrap {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.icon-green { background: #f0fdf4; color: #22c55e; }
.icon-amber { background: #fffbeb; color: #f59e0b; }
.icon-red { background: #fef2f2; color: #ef4444; }
.icon-blue { background: #eff6ff; color: #1d4ed8; }
.icon-gray { background: #f8fafc; color: #94a3b8; }
.device-value { font-size: 0.85rem; font-weight: 700; color: #1e293b; margin: 0; }
.device-label { font-size: 0.68rem; color: #94a3b8; margin: 2px 0 0; }

/* Calendar nav */
.calendar-nav {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.nav-btn {
  width: 32px; height: 32px; background: #f1f5f9;
  border: none; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #374151;
}
.nav-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.calendar-month { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin: 0; }

/* Month stats */
.month-stats {
  display: flex; gap: 10px; margin-bottom: 14px;
}
.mstat {
  flex: 1; background: #fff; border-radius: 12px; border: 1px solid #f1f5f9;
  padding: 12px; text-align: center;
}
.mstat-val { font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0; }
.mstat-val.absent { color: #ef4444; }
.mstat-lbl { font-size: 0.68rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin: 2px 0 0; }

/* Calendar grid */
.cal-grid {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 4px; margin-bottom: 20px;
  background: #fff; border-radius: 16px; padding: 12px;
  border: 1px solid #f1f5f9;
}
.cal-dow {
  text-align: center; font-size: 0.65rem; font-weight: 700;
  color: #94a3b8; text-transform: uppercase; padding: 4px 0;
}
.cal-cell {
  aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
  border-radius: 8px; font-size: 0.8rem; font-weight: 500; color: #374151;
}
.cell-empty { background: transparent; }
.cell-today { background: #1d4ed8; color: #fff; font-weight: 800; }
.cell-checked-in { background: #dcfce7; color: #166534; font-weight: 700; }
.cell-weekend { color: #cbd5e1; }

.cal-loading { display: flex; justify-content: center; padding: 30px; }
.mini-spinner {
  width: 24px; height: 24px;
  border: 2px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

/* Log */
.section-label {
  font-size: 0.7rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.05em;
  margin: 0 0 10px;
}
.log-loading { display: flex; justify-content: center; padding: 20px; }
.log-empty { text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 24px; }
.log-list { display: flex; flex-direction: column; gap: 8px; }
.log-item {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 12px; padding: 12px 14px;
}
.log-badge {
  font-size: 0.65rem; font-weight: 800; letter-spacing: 0.05em;
  padding: 4px 8px; border-radius: 6px; flex-shrink: 0;
}
.badge-in { background: #dcfce7; color: #166534; }
.badge-out { background: #fee2e2; color: #991b1b; }
.log-info { flex: 1; }
.log-time { font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0; }
.log-loc { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; font-family: monospace; }
.log-ago { font-size: 0.72rem; color: #94a3b8; flex-shrink: 0; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
