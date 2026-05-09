<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="admin-root">

        <div class="admin-header">
          <button class="back-btn" @click="$router.back()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div>
            <h1 class="admin-title">App Settings</h1>
            <p class="admin-sub">System Manager only</p>
          </div>
        </div>

        <!-- Access denied -->
        <div v-if="!isSystemManager && !loading" class="access-denied">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48" style="color:#fca5a5">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p>Access denied. This page is only available to System Managers.</p>
        </div>

        <!-- Loading -->
        <div v-else-if="loading" class="admin-loading"><div class="spinner"></div></div>

        <!-- Settings form -->
        <div v-else class="admin-body">

          <div v-if="saved" class="banner banner-green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="20 6 9 17 4 12"/></svg>
            Settings saved successfully.
          </div>
          <div v-if="errorMsg" class="banner banner-red">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ errorMsg }}
          </div>

          <!-- Ordering Defaults -->
          <div class="section-card">
            <p class="section-title">Ordering Defaults</p>

            <div class="field-group">
              <label class="field-label">Default Price List</label>
              <div class="searchable-select" :class="{ open: plDropOpen }">
                <div class="select-display" @click="plDropOpen = !plDropOpen">
                  <span v-if="form.default_price_list" class="select-value">{{ form.default_price_list }}</span>
                  <span v-else class="select-placeholder">Select price list…</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
                <div v-if="plDropOpen" class="select-dropdown">
                  <input v-model="plSearch" class="select-search" placeholder="Search…" @click.stop />
                  <div class="select-option" @click="form.default_price_list = ''; plDropOpen = false">
                    <em style="color:#94a3b8">— None —</em>
                  </div>
                  <div
                    v-for="pl in filteredPriceLists"
                    :key="pl.name"
                    class="select-option"
                    :class="{ selected: form.default_price_list === pl.name }"
                    @click="form.default_price_list = pl.name; plDropOpen = false; plSearch = ''"
                  >{{ pl.name }}</div>
                </div>
              </div>
              <p class="field-hint">Pre-selected on every new order. Sales reps can change it.</p>
            </div>

            <div class="field-group">
              <label class="field-label">Default Warehouse <span class="required">*</span></label>
              <div class="searchable-select" :class="{ open: whDropOpen }">
                <div class="select-display" @click="whDropOpen = !whDropOpen">
                  <span v-if="form.default_warehouse" class="select-value">{{ form.default_warehouse }}</span>
                  <span v-else class="select-placeholder">Select warehouse…</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
                <div v-if="whDropOpen" class="select-dropdown">
                  <input v-model="whSearch" class="select-search" placeholder="Search…" @click.stop />
                  <div
                    v-for="wh in filteredWarehouses"
                    :key="wh.name"
                    class="select-option"
                    :class="{ selected: form.default_warehouse === wh.name }"
                    @click="form.default_warehouse = wh.name; whDropOpen = false; whSearch = ''"
                  >{{ wh.name }}</div>
                </div>
              </div>
              <p class="field-hint">Applied to all order lines. Not shown to sales reps.</p>
            </div>

            <div class="field-group">
              <label class="field-label">Approval Threshold (KES)</label>
              <input v-model.number="form.approval_threshold" type="number" class="field-input" placeholder="100000" min="0" />
              <p class="field-hint">Orders above this value are routed to manager approval before being submitted to ERPNext.</p>
            </div>
          </div>

          <!-- Branding -->
          <div class="section-card">
            <p class="section-title">Branding</p>

            <div class="field-group">
              <label class="field-label">App Title</label>
              <input v-model="form.app_title" type="text" class="field-input" placeholder="Live Sales" />
            </div>

            <div class="field-group">
              <label class="field-label">Welcome Message</label>
              <textarea v-model="form.welcome_message" class="field-textarea" rows="2" placeholder="Shown on the home screen…"></textarea>
            </div>
          </div>

          <button class="save-btn" :disabled="saving" @click="saveSettings">
            <span v-if="saving" class="btn-spin"></span>
            <span v-else>Save Settings</span>
          </button>
        </div>

      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'

const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const errorMsg = ref('')
const isSystemManager = ref(false)

const priceLists = ref([])
const warehouses = ref([])
const plSearch = ref('')
const whSearch = ref('')
const plDropOpen = ref(false)
const whDropOpen = ref(false)

const form = ref({
  default_price_list: '',
  default_warehouse: 'Finished Goods - CAL',
  approval_threshold: 100000,
  app_title: 'Live Sales',
  welcome_message: '',
})

const filteredPriceLists = computed(() => {
  const q = plSearch.value.toLowerCase()
  return priceLists.value.filter(p => p.name.toLowerCase().includes(q))
})

const filteredWarehouses = computed(() => {
  const q = whSearch.value.toLowerCase()
  return warehouses.value.filter(w => w.name.toLowerCase().includes(q))
})

function getCsrf() {
  return window.csrf_token || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
}

async function loadSettings() {
  loading.value = true
  try {
    const [settingsRes, plRes, whRes] = await Promise.all([
      fetch('/api/method/live.api.settings.get_app_settings', { credentials: 'include' }),
      fetch('/api/method/live.api.settings.get_all_price_lists', { credentials: 'include' }),
      fetch('/api/method/live.api.settings.get_all_warehouses', { credentials: 'include' }),
    ])

    const { message: settings } = await settingsRes.json()
    if (settings) {
      isSystemManager.value = !!settings.is_admin
      const { is_admin, ...rest } = settings
      Object.assign(form.value, rest)
    }

    const { message: pls } = await plRes.json()
    priceLists.value = pls || []

    const { message: whs } = await whRes.json()
    warehouses.value = whs || []
  } catch (e) {
    console.error('Admin settings load error:', e)
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  errorMsg.value = ''
  saved.value = false
  try {
    const res = await fetch('/api/method/live.api.settings.save_app_settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': getCsrf() },
      credentials: 'include',
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('Failed to save')
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) {
    errorMsg.value = e.message || 'Could not save settings.'
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.admin-root { background: #f8fafc; min-height: 100%; padding-bottom: 40px; }

.admin-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 16px 12px; background: #fff;
  border-bottom: 1px solid #f1f5f9;
  position: sticky; top: 0; z-index: 10;
}
.back-btn {
  width: 36px; height: 36px; background: #f1f5f9; border: none;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #374151; flex-shrink: 0;
}
.admin-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0 0 2px; }
.admin-sub { font-size: 0.72rem; color: #94a3b8; margin: 0; }

.admin-loading { display: flex; justify-content: center; padding: 60px; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

.access-denied {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 80px 24px; gap: 16px;
  text-align: center; color: #94a3b8; font-size: 0.9rem;
}

.admin-body { padding: 16px; display: flex; flex-direction: column; gap: 16px; }

.banner {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-radius: 10px; font-size: 0.82rem;
}
.banner-green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
.banner-red { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }

.section-card {
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 16px; padding: 16px;
}
.section-title {
  font-size: 0.72rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 14px;
}

.field-group { margin-bottom: 16px; }
.field-label {
  display: block; font-size: 0.8rem; font-weight: 700; color: #374151;
  margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em;
}
.required { color: #ef4444; }
.field-hint { font-size: 0.72rem; color: #94a3b8; margin: 4px 0 0; }
.field-input {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0;
  border-radius: 10px; font-size: 0.9rem; color: #1e293b;
  background: #fff; box-sizing: border-box;
}
.field-input:focus { outline: none; border-color: #1d4ed8; }
.field-textarea {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0;
  border-radius: 10px; font-size: 0.9rem; color: #1e293b;
  background: #fff; box-sizing: border-box; resize: none;
}
.field-textarea:focus { outline: none; border-color: #1d4ed8; }

.searchable-select { position: relative; }
.select-display {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px;
  background: #fff; cursor: pointer; min-height: 42px;
}
.searchable-select.open .select-display { border-color: #1d4ed8; }
.select-value { font-size: 0.9rem; color: #1e293b; }
.select-placeholder { font-size: 0.9rem; color: #94a3b8; }
.select-dropdown {
  position: absolute; left: 0; right: 0; top: calc(100% + 4px);
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1); z-index: 50;
  max-height: 220px; overflow-y: auto;
}
.select-search {
  width: 100%; padding: 10px 12px; border: none;
  border-bottom: 1px solid #f1f5f9; font-size: 0.88rem;
  color: #1e293b; background: transparent; box-sizing: border-box;
}
.select-search:focus { outline: none; }
.select-option { padding: 10px 14px; font-size: 0.88rem; color: #374151; cursor: pointer; }
.select-option:hover { background: #f8fafc; }
.select-option.selected { background: #eff6ff; color: #1d4ed8; font-weight: 600; }

.save-btn {
  width: 100%; padding: 14px; background: #1d4ed8; color: #fff;
  border: none; border-radius: 12px; font-weight: 700; font-size: 0.95rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.save-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-spin {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
