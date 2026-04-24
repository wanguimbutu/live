<template>
  <div class="chart-wrap">
    <div class="chart-header" v-if="title">
      <span class="chart-title">{{ title }}</span>
    </div>

    <!-- Horizontal bars (leaderboard style) -->
    <div v-if="horizontal" class="h-bars">
      <div v-for="(item, i) in data" :key="i" class="h-row">
        <div class="h-rank" v-if="showRank">{{ i + 1 }}</div>
        <div class="h-label" :title="item.label">{{ item.label }}</div>
        <div class="h-bar-wrap">
          <div
            class="h-bar"
            :style="{
              width: maxVal > 0 ? `${(item.value / maxVal) * 100}%` : '0%',
              background: itemColor(i),
            }"
          ></div>
        </div>
        <div class="h-value">{{ formatValue(item.value) }}</div>
      </div>
    </div>

    <!-- Vertical bars (aging / trend style) -->
    <svg
      v-else
      :viewBox="`0 0 ${W} ${H}`"
      class="chart-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <template v-if="data.length">
        <rect
          v-for="(item, i) in data"
          :key="i"
          :x="barX(i)"
          :y="barY(item.value)"
          :width="barW"
          :height="barHeight(item.value)"
          :fill="itemColor(i)"
          rx="3"
        />
        <!-- X labels -->
        <text
          v-for="(item, i) in data"
          :key="`lbl-${i}`"
          :x="barX(i) + barW / 2"
          :y="H - 4"
          text-anchor="middle"
          font-size="9"
          fill="#94a3b8"
        >{{ item.label }}</text>
        <!-- Value labels on top of bars -->
        <text
          v-for="(item, i) in data"
          :key="`val-${i}`"
          :x="barX(i) + barW / 2"
          :y="barY(item.value) - 3"
          text-anchor="middle"
          font-size="9"
          :fill="itemColor(i)"
        >{{ formatValue(item.value) }}</text>
      </template>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{label, value}]
  color: { type: String, default: '#1d4ed8' },
  colors: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  horizontal: { type: Boolean, default: false },
  showRank: { type: Boolean, default: false },
  formatValue: { type: Function, default: v => {
    if (v >= 1000000) return `${(v/1000000).toFixed(1)}M`
    if (v >= 1000) return `${(v/1000).toFixed(0)}k`
    return String(v)
  }},
})

const PALETTE = ['#1d4ed8', '#0ea5e9', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#14b8a6', '#f97316', '#6366f1']

function itemColor(i) {
  if (props.colors && props.colors[i]) return props.colors[i]
  return PALETTE[i % PALETTE.length]
}

const maxVal = computed(() => Math.max(...props.data.map(d => d.value), 1))

// Vertical bar chart geometry
const W = 280
const H = 100
const PAD = { t: 14, r: 8, b: 20, l: 8 }
const plotW = W - PAD.l - PAD.r
const plotH = H - PAD.t - PAD.b
const gap = 6
const barW = computed(() => {
  const n = props.data.length
  if (n === 0) return 20
  return Math.max(8, (plotW - (n - 1) * gap) / n)
})

function barX(i) {
  return PAD.l + i * (barW.value + gap)
}
function barY(val) {
  return PAD.t + plotH - (val / maxVal.value) * plotH
}
function barHeight(val) {
  return Math.max(2, (val / maxVal.value) * plotH)
}
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart-header { margin-bottom: 10px; }
.chart-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.chart-svg { width: 100%; height: auto; }

/* Horizontal bars */
.h-bars { display: flex; flex-direction: column; gap: 8px; }
.h-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.h-rank {
  width: 18px;
  font-size: 0.72rem;
  font-weight: 800;
  color: #94a3b8;
  text-align: center;
  flex-shrink: 0;
}
.h-label {
  width: 90px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}
.h-bar-wrap {
  flex: 1;
  background: #f1f5f9;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
}
.h-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
  min-width: 2px;
}
.h-value {
  font-size: 0.72rem;
  font-weight: 700;
  color: #1e293b;
  min-width: 48px;
  text-align: right;
  flex-shrink: 0;
}
</style>
