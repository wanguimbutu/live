<template>
  <div class="chart-wrap">
    <div class="chart-header" v-if="title">
      <span class="chart-title">{{ title }}</span>
      <span class="chart-legend" v-if="label">{{ label }}</span>
    </div>
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      :width="W" :height="H"
      class="chart-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient :id="`grad-${uid}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.18"/>
          <stop offset="100%" :stop-color="color" stop-opacity="0.01"/>
        </linearGradient>
      </defs>

      <!-- Zero line -->
      <line
        :x1="PAD.l" :y1="PAD.t + plotH"
        :x2="PAD.l + plotW" :y2="PAD.t + plotH"
        stroke="#f1f5f9" stroke-width="1"
      />

      <!-- Horizontal grid lines -->
      <line
        v-for="y in gridYs"
        :key="y"
        :x1="PAD.l" :y1="y"
        :x2="PAD.l + plotW" :y2="y"
        stroke="#f1f5f9" stroke-width="1"
      />

      <template v-if="points.length >= 2">
        <!-- Area fill -->
        <path :d="areaPath" :fill="`url(#grad-${uid})`" />
        <!-- Line -->
        <polyline :points="linePoints" :stroke="color" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Dots (only every N points to avoid clutter) -->
        <circle
          v-for="(p, i) in visibleDots"
          :key="i"
          :cx="p.x" :cy="p.y" r="3"
          :fill="color" stroke="#fff" stroke-width="1.5"
        />
      </template>

      <!-- X axis labels (sampled) -->
      <text
        v-for="(tick, i) in xTicks"
        :key="i"
        :x="tick.x"
        :y="PAD.t + plotH + 16"
        text-anchor="middle"
        font-size="9"
        fill="#94a3b8"
      >{{ tick.label }}</text>

      <!-- Y axis labels -->
      <text
        v-for="(lbl, i) in yLabels"
        :key="i"
        :x="PAD.l - 4"
        :y="lbl.y + 3"
        text-anchor="end"
        font-size="9"
        fill="#94a3b8"
      >{{ lbl.text }}</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{label, value}]
  color: { type: String, default: '#1d4ed8' },
  title: { type: String, default: '' },
  label: { type: String, default: '' },
  formatValue: { type: Function, default: v => v.toLocaleString() },
})

const W = 320
const H = 140
const PAD = { t: 10, r: 10, b: 28, l: 38 }
const plotW = W - PAD.l - PAD.r
const plotH = H - PAD.t - PAD.b
const uid = Math.random().toString(36).slice(2, 8)

const maxVal = computed(() => Math.max(...props.data.map(d => d.value), 1))

const points = computed(() => {
  const n = props.data.length
  if (n === 0) return []
  return props.data.map((d, i) => ({
    x: PAD.l + (n === 1 ? plotW / 2 : i * plotW / (n - 1)),
    y: PAD.t + plotH - (d.value / maxVal.value) * plotH,
    label: d.label,
    value: d.value,
  }))
})

const linePoints = computed(() =>
  points.value.map(p => `${p.x},${p.y}`).join(' ')
)

const areaPath = computed(() => {
  if (points.value.length < 2) return ''
  const line = points.value.map(p => `L${p.x},${p.y}`).join(' ')
  const last = points.value[points.value.length - 1]
  const first = points.value[0]
  return `M${first.x},${first.y} ${line} L${last.x},${PAD.t + plotH} L${first.x},${PAD.t + plotH} Z`
})

const visibleDots = computed(() => {
  const n = points.value.length
  if (n <= 10) return points.value
  // Show first, last, and every Nth
  const step = Math.ceil(n / 6)
  return points.value.filter((_, i) => i === 0 || i === n - 1 || i % step === 0)
})

const xTicks = computed(() => {
  const n = points.value.length
  if (n === 0) return []
  const maxTicks = 6
  const step = Math.max(1, Math.ceil(n / maxTicks))
  return points.value
    .filter((_, i) => i === 0 || i === n - 1 || i % step === 0)
    .map(p => ({ x: p.x, label: p.label }))
})

const gridYs = computed(() => {
  const steps = 4
  return Array.from({ length: steps }, (_, i) => PAD.t + (i * plotH) / steps)
})

const yLabels = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => {
    const fraction = 1 - i / steps
    const val = fraction * maxVal.value
    return {
      y: PAD.t + i * plotH / steps,
      text: val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val.toFixed(0),
    }
  })
})
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.chart-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.chart-legend {
  font-size: 0.72rem;
  color: #94a3b8;
}
.chart-svg {
  width: 100%;
  height: auto;
  overflow: visible;
}
</style>
