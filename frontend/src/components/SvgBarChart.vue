<template>
  <div class="chart-wrap">

    <!-- Horizontal bars (leaderboard style) -->
    <div v-if="horizontal" class="h-bars">
      <div v-for="(item, i) in data" :key="i" class="h-row">
        <div class="h-label" :title="item.label">{{ item.label }}</div>
        <div class="h-bar-track">
          <div
            class="h-bar-fill"
            :style="{
              width: maxVal > 0 ? `${(item.value / maxVal) * 100}%` : '0%',
              background: itemColor(i),
            }"
          ></div>
        </div>
        <div class="h-value">{{ formatValue(item.value) }}</div>
      </div>
    </div>

    <!-- Vertical bars -->
    <svg
      v-else
      :viewBox="`0 0 ${W} ${H}`"
      class="chart-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- Grid lines -->
      <line
        v-for="y in gridYs"
        :key="y"
        :x1="PAD.l" :y1="y"
        :x2="PAD.l + plotW" :y2="y"
        stroke="#f0f0f0" stroke-width="1"
      />

      <template v-if="data.length">
        <rect
          v-for="(item, i) in data"
          :key="i"
          :x="barX(i)"
          :y="barY(item.value)"
          :width="barW"
          :height="barHeight(item.value)"
          :fill="itemColor(i)"
          rx="4"
        />
        <text
          v-for="(item, i) in data"
          :key="`lbl-${i}`"
          :x="barX(i) + barW / 2"
          :y="H - 5"
          text-anchor="middle"
          font-size="10"
          fill="#9ca3af"
          font-family="system-ui,sans-serif"
        >{{ item.label }}</text>
      </template>

      <!-- Y labels -->
      <text
        v-for="(lbl, i) in yLabels"
        :key="i"
        :x="PAD.l - 5"
        :y="lbl.y + 4"
        text-anchor="end"
        font-size="10"
        fill="#9ca3af"
        font-family="system-ui,sans-serif"
      >{{ lbl.text }}</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  color: { type: String, default: '#6366f1' },
  colors: { type: Array, default: () => [] },
  horizontal: { type: Boolean, default: false },
  formatValue: { type: Function, default: v => {
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
    if (v >= 1_000) return `${(v / 1_000).toFixed(0)}k`
    return String(v)
  }},
})

const PALETTE = ['#6366f1','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#14b8a6']

function itemColor(i) {
  if (props.colors && props.colors[i]) return props.colors[i]
  return PALETTE[i % PALETTE.length]
}

const maxVal = computed(() => Math.max(...props.data.map(d => d.value), 1))

const W = 400
const H = 110
const PAD = { t: 8, r: 10, b: 22, l: 38 }
const plotW = W - PAD.l - PAD.r
const plotH = H - PAD.t - PAD.b
const gap = 8

const barW = computed(() => {
  const n = props.data.length
  if (n === 0) return 20
  return Math.max(10, (plotW - (n - 1) * gap) / n)
})

function barX(i) { return PAD.l + i * (barW.value + gap) }
function barY(val) { return PAD.t + plotH - (val / maxVal.value) * plotH }
function barHeight(val) { return Math.max(3, (val / maxVal.value) * plotH) }

const gridYs = computed(() =>
  Array.from({ length: 5 }, (_, i) => PAD.t + (i * plotH) / 4)
)

const yLabels = computed(() =>
  Array.from({ length: 5 }, (_, i) => {
    const fraction = 1 - i / 4
    const val = fraction * maxVal.value
    let text
    if (val >= 1_000_000) text = `${(val / 1_000_000).toFixed(1)}M`
    else if (val >= 1_000) text = `${(val / 1_000).toFixed(0)}k`
    else text = val.toFixed(0)
    return { y: PAD.t + (i * plotH) / 4, text }
  })
)
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart-svg { width: 100%; height: auto; display: block; }

.h-bars { display: flex; flex-direction: column; gap: 10px; }
.h-row { display: flex; align-items: center; gap: 10px; }
.h-label {
  width: 80px; font-size: 0.8rem; font-weight: 500;
  color: #374151; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; flex-shrink: 0;
}
.h-bar-track {
  flex: 1; background: #f3f4f6;
  border-radius: 6px; height: 10px; overflow: hidden;
}
.h-bar-fill {
  height: 100%; border-radius: 6px;
  transition: width 0.5s cubic-bezier(.4,0,.2,1);
  min-width: 3px;
}
.h-value {
  font-size: 0.78rem; font-weight: 700; color: #111827;
  min-width: 56px; text-align: right; flex-shrink: 0;
}
</style>
