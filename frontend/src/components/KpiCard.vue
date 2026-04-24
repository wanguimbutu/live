<template>
  <div class="kpi-card" :class="variant">
    <div class="kpi-top">
      <span class="kpi-label">{{ label }}</span>
      <div class="kpi-icon" v-if="$slots.icon"><slot name="icon" /></div>
    </div>
    <div class="kpi-value">{{ value }}</div>
    <div class="kpi-sub" v-if="sub">{{ sub }}</div>
    <div class="kpi-trend" v-if="trend !== undefined">
      <svg v-if="trend >= 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12" class="trend-up">
        <polyline points="18 15 12 9 6 15"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12" class="trend-down">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
      <span :class="trend >= 0 ? 'trend-up' : 'trend-down'">{{ Math.abs(trend) }}%</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  sub: { type: String, default: '' },
  trend: { type: Number, default: undefined },
  variant: { type: String, default: 'default' }, // default | blue | green | amber | red
})
</script>

<style scoped>
.kpi-card {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.kpi-card.blue { background: #eff6ff; border-color: #bfdbfe; }
.kpi-card.green { background: #f0fdf4; border-color: #bbf7d0; }
.kpi-card.amber { background: #fffbeb; border-color: #fde68a; }
.kpi-card.red { background: #fef2f2; border-color: #fecaca; }

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.kpi-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}
.kpi-card.blue .kpi-label { color: #3b82f6; }
.kpi-card.green .kpi-label { color: #22c55e; }
.kpi-card.amber .kpi-label { color: #f59e0b; }
.kpi-card.red .kpi-label { color: #ef4444; }

.kpi-icon { color: #cbd5e1; }

.kpi-value {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}
.kpi-card.blue .kpi-value { color: #1d4ed8; }
.kpi-card.green .kpi-value { color: #166534; }
.kpi-card.amber .kpi-value { color: #92400e; }
.kpi-card.red .kpi-value { color: #991b1b; }

.kpi-sub {
  font-size: 0.72rem;
  color: #94a3b8;
}
.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.72rem;
  font-weight: 600;
  margin-top: 2px;
}
.trend-up { color: #22c55e; }
.trend-down { color: #ef4444; }
</style>
