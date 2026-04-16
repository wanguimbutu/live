<template>
  <!-- Android / Desktop: native browser install prompt -->
  <Transition name="slide-up">
    <div v-if="showAndroidBanner" class="install-banner">
      <div class="install-banner-icon">
        <img src="/logo.png" alt="Sales Live" />
      </div>
      <div class="install-banner-text">
        <p class="install-title">Install Sales Live</p>
        <p class="install-sub">Works offline &amp; feels like a native app</p>
      </div>
      <div class="install-banner-actions">
        <button class="btn-install" @click="triggerInstall">Install</button>
        <button class="btn-dismiss" @click="dismiss" aria-label="Dismiss">✕</button>
      </div>
    </div>
  </Transition>

  <!-- iOS Safari: no install API — show manual guide -->
  <Transition name="slide-up">
    <div v-if="showIosGuide" class="ios-guide-backdrop" @click.self="dismiss">
      <div class="ios-guide">
        <button class="ios-guide-close" @click="dismiss">✕</button>
        <img src="/logo.png" alt="Sales Live" class="ios-guide-logo" />
        <h2 class="ios-guide-title">Install Sales Live</h2>
        <p class="ios-guide-sub">Add this app to your home screen for the best experience</p>
        <ol class="ios-guide-steps">
          <li>
            <span class="step-icon">
              <!-- Share icon -->
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                <polyline points="16 6 12 2 8 6"/>
                <line x1="12" y1="2" x2="12" y2="15"/>
              </svg>
            </span>
            Tap the <strong>Share</strong> button in Safari's toolbar
          </li>
          <li>
            <span class="step-icon">
              <!-- Plus-square icon -->
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </span>
            Scroll down and tap <strong>Add to Home Screen</strong>
          </li>
          <li>
            <span class="step-icon">
              <!-- Check icon -->
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </span>
            Tap <strong>Add</strong> to confirm
          </li>
        </ol>
        <!-- Arrow pointing at the share button (bottom center on iPhone) -->
        <div class="ios-arrow">↓</div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const DISMISSED_KEY = 'live_install_dismissed'

const showAndroidBanner = ref(false)
const showIosGuide = ref(false)
let deferredPrompt = null

function isDismissed() {
  return !!localStorage.getItem(DISMISSED_KEY)
}

function dismiss() {
  showAndroidBanner.value = false
  showIosGuide.value = false
  localStorage.setItem(DISMISSED_KEY, '1')
}

async function triggerInstall() {
  if (!deferredPrompt) return
  deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice
  deferredPrompt = null
  showAndroidBanner.value = false
  if (outcome === 'accepted') {
    localStorage.setItem(DISMISSED_KEY, '1')
  }
}

function isIos() {
  return /iphone|ipad|ipod/i.test(navigator.userAgent)
}

function isInStandaloneMode() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    ('standalone' in window.navigator && window.navigator.standalone)
  )
}

onMounted(() => {
  // Already installed or user dismissed — don't show anything
  if (isInStandaloneMode() || isDismissed()) return

  if (isIos()) {
    // iOS doesn't fire beforeinstallprompt — show the manual guide after a delay
    setTimeout(() => { showIosGuide.value = true }, 3000)
    return
  }

  // Android / Chrome / Edge: capture the browser's install event
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e
    setTimeout(() => { showAndroidBanner.value = true }, 3000)
  })

  // Hide if user installs via browser menu while banner is visible
  window.addEventListener('appinstalled', () => {
    showAndroidBanner.value = false
    localStorage.setItem(DISMISSED_KEY, '1')
  })
})
</script>

<style scoped>
/* ── Android install banner ──────────────────────────────────────────────── */
.install-banner {
  position: fixed;
  bottom: 72px; /* above tab bar */
  left: 12px;
  right: 12px;
  z-index: 1000;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
}

.install-banner-icon img {
  width: 44px;
  height: 44px;
  border-radius: 10px;
}

.install-banner-text {
  flex: 1;
  min-width: 0;
}

.install-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.install-sub {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 2px 0 0;
}

.install-banner-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-install {
  background: #1d4ed8;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-dismiss {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 4px;
  line-height: 1;
}

/* ── iOS guide ───────────────────────────────────────────────────────────── */
.ios-guide-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.ios-guide {
  background: #fff;
  border-radius: 24px 24px 0 0;
  padding: 28px 24px 40px;
  width: 100%;
  max-width: 480px;
  position: relative;
  text-align: center;
}

.ios-guide-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 0.8rem;
  cursor: pointer;
  color: #6b7280;
}

.ios-guide-logo {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  margin-bottom: 12px;
}

.ios-guide-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 6px;
}

.ios-guide-sub {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0 0 20px;
}

.ios-guide-steps {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: left;
}

.ios-guide-steps li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  color: #374151;
}

.step-icon {
  width: 32px;
  height: 32px;
  background: #eff6ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-icon svg {
  width: 18px;
  height: 18px;
  color: #1d4ed8;
}

.ios-arrow {
  font-size: 1.5rem;
  color: #1d4ed8;
  animation: bounce 1s ease infinite;
}

/* ── Transitions ─────────────────────────────────────────────────────────── */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(6px); }
}
</style>
