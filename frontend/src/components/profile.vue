<template>
  <div class="profile-bar">
    <!-- Left: greeting -->
    <div class="profile-greeting">
      <p class="greeting-label">Good {{ timeOfDay }},</p>
      <p class="greeting-name">{{ fullName || currentUser || 'there' }}</p>
    </div>

    <!-- Right: avatar + dropdown trigger -->
    <div class="profile-avatar-wrap" ref="avatarRef">
      <button class="avatar-btn" @click="dropdownOpen = !dropdownOpen">
        <img
          v-if="userImage"
          :src="userImage"
          alt="Profile"
          class="avatar-img"
        />
        <span v-else class="avatar-initials">{{ initials }}</span>
      </button>

      <!-- Dropdown -->
      <div v-if="dropdownOpen" class="profile-dropdown" @click.stop>
        <div class="dropdown-info">
          <p class="dropdown-name">{{ fullName || currentUser }}</p>
          <p class="dropdown-email">{{ currentUser }}</p>
        </div>
        <button class="dropdown-item danger" @click="logout" :disabled="loggingOut">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          {{ loggingOut ? 'Logging out…' : 'Log out' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { session } from '@/data/session'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentUser = session.user
const fullName = ref('')
const userImage = ref('')
const dropdownOpen = ref(false)
const loggingOut = ref(false)
const avatarRef = ref(null)

const initials = computed(() => {
  if (!fullName.value && !currentUser) return '?'
  const name = fullName.value || currentUser
  return name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase()
})

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
})

async function fetchUserDetails() {
  if (!currentUser) return
  try {
    const res = await fetch(`/api/resource/User/${encodeURIComponent(currentUser)}`, {
      credentials: 'include',
    })
    if (res.ok) {
      const { data } = await res.json()
      fullName.value = data.full_name || ''
      userImage.value = data.user_image || ''
    }
  } catch (e) {
    console.error('Failed to fetch user details:', e)
  }
}

async function logout() {
  loggingOut.value = true
  try {
    session.logout.submit()
  } catch (e) {
    console.error('Logout error:', e)
    loggingOut.value = false
  }
}

function handleOutsideClick(e) {
  if (avatarRef.value && !avatarRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  fetchUserDetails()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.profile-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px 8px;
}

.greeting-label {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 500;
}

.greeting-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.profile-avatar-wrap {
  position: relative;
}

.avatar-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: 50%;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e2e8f0;
}

.avatar-initials {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #1d4ed8;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e2e8f0;
}

.profile-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  min-width: 200px;
  z-index: 100;
  overflow: hidden;
}

.dropdown-info {
  padding: 14px 16px 12px;
  border-bottom: 1px solid #f1f5f9;
}

.dropdown-name {
  font-weight: 700;
  color: #111827;
  font-size: 0.9rem;
  margin: 0;
}

.dropdown-email {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 2px 0 0;
  word-break: break-all;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  color: #374151;
}
.dropdown-item:hover { background: #f8fafc; }
.dropdown-item.danger { color: #dc2626; }
.dropdown-item.danger:hover { background: #fef2f2; }
.dropdown-item:disabled { opacity: 0.55; cursor: not-allowed; }
</style>
