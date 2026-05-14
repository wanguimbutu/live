<template>
  <div class="chart-wrap">
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="chart-svg"
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient :id="`grad-${uid}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.15"/>
          <stop offset="100%" :stop-color="color" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <!-- Horizontal grid lines -->
      <line
        v-for="y in gridYs"
        :key="y"
        :x1="PAD.l" :y1="y"
        :x2="PAD.l + plotW" :y2="y"
        stroke="#f0f0f0" stroke-width="1"
      />

      <!-- Y axis labels -->
      <text
        v-for="(lbl, i) in yLabels"
        :key="i"
        :x="PAD.l - 6"
        :y="lbl.y + 4"
        text-anchor="end"
        font-size="16"
        fill="#9ca3af"
        font-family="system-ui,sans-serif"
      >{{ lbl.text }}</text>

      <template v-if="points.length >= 2">
        <!-- Area fill -->
        <path :d="areaPath" :fill="`url(#grad-${uid})`" />
        <!-- Smooth line -->
        <path :d="linePath" :stroke="color" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Hover dots -->
        <circle
          v-for="(p, i) in visibleDots"
          :key="i"
          :cx="p.x" :cy="p.y" r="3.5"
          :fill="color" stroke="#fff" stroke-width="2"
        />
      </template>

      <!-- X axis labels -->
      <text
        v-for="(tick, i) in xTicks"
        :key="i"
        :x="tick.x"
        :y="PAD.t + plotH + 18"
        text-anchor="middle"
        font-size="16"
        fill="#9ca3af"
        font-family="system-ui,sans-serif"
      >{{ tick.label }}</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  color: { type: String, default: '#6366f1' },
  formatValue: { type: Function, default: v => v.toLocaleString() },
})

const W = 400
const H = 120
const PAD = { t: 8, r: 12, b: 28, l: 52 }
const plotW = W - PAD.l - PAD.r
const plotH = H - PAD.t - PAD.b
const uid = Math.random().toString(36).slice(2, 8)

const maxVal = computed(() => Math.max(...props.data.map(d => d.value), 1))

const points = computed(() => {
  const n = props.data.length
  if (n === 0) return []
  return props.data.map((d, i) => ({
    x: PAD.l + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW),
    y: PAD.t + plotH - (d.value / maxVal.value) * plotH,
    label: d.label,
    value: d.value,
  }))
})

// Smooth bezier curve path
function smooth(pts) {
  if (pts.length < 2) return ''
  let d = `M${pts[0].x},${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1]
    const curr = pts[i]
    const cpx = (prev.x + curr.x) / 2
    d += ` C${cpx},${prev.y} ${cpx},${curr.y} ${curr.x},${curr.y}`
  }
  return d
}

const linePath = computed(() => smooth(points.value))

const areaPath = computed(() => {
  const pts = points.value
  if (pts.length < 2) return ''
  const line = smooth(pts)
  const last = pts[pts.length - 1]
  const first = pts[0]
  const baseline = PAD.t + plotH
  return `${line} L${last.x},${baseline} L${first.x},${baseline} Z`
})

const visibleDots = computed(() => {
  const n = points.value.length
  if (n <= 12) return points.value
  const step = Math.ceil(n / 8)
  return points.value.filter((_, i) => i === 0 || i === n - 1 || i % step === 0)
})

const xTicks = computed(() => {
  const n = points.value.length
  if (n === 0) return []
  const maxTicks = 7
  const step = Math.max(1, Math.ceil(n / maxTicks))
  return points.value
    .filter((_, i) => i % step === 0 || i === n - 1)
    .map(p => ({ x: p.x, label: p.label }))
})

const gridYs = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => PAD.t + (i * plotH) / steps)
})

const yLabels = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => {
    const fraction = 1 - i / steps
    const val = fraction * maxVal.value
    let text
    if (val >= 1_000_000) text = `${(val / 1_000_000).toFixed(1)}M`
    else if (val >= 1_000) text = `${(val / 1_000).toFixed(0)}k`
    else text = val.toFixed(0)
    return { y: PAD.t + (i * plotH) / steps, text }
  })
})
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart-svg {
  width: 100%;
  height: auto;
  max-height: 110px;
  display: block;
  overflow: visible;
}
</style>
