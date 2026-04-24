import { ref, computed } from 'vue'

const STORAGE_KEY = 'live_reminders'

const reminders = ref([])

function load() {
  try {
    reminders.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    reminders.value = []
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reminders.value))
}

function requestPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}

function fireNotification(title, body) {
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification(title, { body, icon: '/logo.png' })
    } catch {}
  }
}

function checkDue() {
  const now = Date.now()
  let changed = false
  for (const r of reminders.value) {
    if (!r.notified && new Date(r.date).getTime() <= now) {
      fireNotification(
        `Reminder: ${r.customerName || r.customer}`,
        r.note || `Follow-up scheduled`
      )
      r.notified = true
      changed = true
    }
  }
  if (changed) persist()
}

// Check every minute while the app is open
setInterval(checkDue, 60_000)

load()
requestPermission()
checkDue()

export function useReminders() {
  function addReminder({ customer, customerName, date, note }) {
    const entry = {
      id: `rem_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      customer,
      customerName: customerName || customer,
      date,        // ISO string like "2026-04-25T09:00"
      note: note || '',
      createdAt: new Date().toISOString(),
      notified: false,
    }
    reminders.value.push(entry)
    persist()
    return entry
  }

  function removeReminder(id) {
    reminders.value = reminders.value.filter(r => r.id !== id)
    persist()
  }

  function markRead(id) {
    const r = reminders.value.find(r => r.id === id)
    if (r) { r.notified = true; persist() }
  }

  const upcoming = computed(() =>
    reminders.value
      .filter(r => !r.notified && new Date(r.date) > new Date())
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const overdue = computed(() =>
    reminders.value.filter(r => !r.notified && new Date(r.date) <= new Date())
  )

  const all = computed(() =>
    [...reminders.value].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  )

  const unreadCount = computed(() =>
    reminders.value.filter(r => !r.notified && new Date(r.date) <= new Date()).length
  )

  return { all, upcoming, overdue, unreadCount, addReminder, removeReminder, markRead }
}
