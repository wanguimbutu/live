<template>
  <div class="quicklinks-root">
    <p class="quicklinks-label">Quick Actions</p>
    <div class="quicklinks-grid">
      <button
        v-for="link in links"
        :key="link.to"
        class="ql-card"
        @click="$router.push(link.to)"
      >
        <div class="ql-icon" :style="{ background: link.bg }">
          <component :is="link.icon" />
        </div>
        <span class="ql-label">{{ link.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { h } from 'vue'

function Icon(paths) {
  return () => h('svg', {
    viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', 'stroke-width': '2',
    width: '20', height: '20',
  }, paths.map(p =>
    typeof p === 'string'
      ? h('path', { d: p })
      : h(p.tag, p.attrs)
  ))
}

const links = [
  {
    label: 'New Order',
    to: '/add-sales-order',
    bg: '#eff6ff',
    icon: Icon([
      { tag: 'rect', attrs: { x: '2', y: '3', width: '20', height: '14', rx: '2' } },
      { tag: 'line', attrs: { x1: '8', y1: '21', x2: '16', y2: '21' } },
      { tag: 'line', attrs: { x1: '12', y1: '17', x2: '12', y2: '21' } },
    ]),
  },
  {
    label: 'My Orders',
    to: '/salesOrderList',
    bg: '#fdf4ff',
    icon: Icon([
      { tag: 'path', attrs: { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' } },
      { tag: 'polyline', attrs: { points: '14 2 14 8 20 8' } },
      { tag: 'line', attrs: { x1: '16', y1: '13', x2: '8', y2: '13' } },
      { tag: 'line', attrs: { x1: '16', y1: '17', x2: '8', y2: '17' } },
      { tag: 'polyline', attrs: { points: '10 9 9 9 8 9' } },
    ]),
  },
  {
    label: 'Collections',
    to: '/collections',
    bg: '#f0fdf4',
    icon: Icon([
      { tag: 'rect', attrs: { x: '2', y: '5', width: '20', height: '14', rx: '2' } },
      { tag: 'line', attrs: { x1: '2', y1: '10', x2: '22', y2: '10' } },
    ]),
  },
  {
    label: 'Customers',
    to: '/customerList',
    bg: '#fff7ed',
    icon: Icon([
      { tag: 'path', attrs: { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' } },
      { tag: 'circle', attrs: { cx: '9', cy: '7', r: '4' } },
      { tag: 'path', attrs: { d: 'M23 21v-2a4 4 0 0 0-3-3.87' } },
      { tag: 'path', attrs: { d: 'M16 3.13a4 4 0 0 1 0 7.75' } },
    ]),
  },
  {
    label: 'Dashboard',
    to: '/dashboard',
    bg: '#fdf4ff',
    icon: Icon([
      { tag: 'line', attrs: { x1: '18', y1: '20', x2: '18', y2: '10' } },
      { tag: 'line', attrs: { x1: '12', y1: '20', x2: '12', y2: '4' } },
      { tag: 'line', attrs: { x1: '6', y1: '20', x2: '6', y2: '14' } },
    ]),
  },
  {
    label: 'Catalog',
    to: '/catalog',
    bg: '#ecfdf5',
    icon: Icon([
      'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z',
    ]),
  },
  {
    label: 'Approvals',
    to: '/approvals',
    bg: '#fff1f2',
    icon: Icon([
      { tag: 'path', attrs: { d: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2' } },
      { tag: 'rect', attrs: { x: '9', y: '3', width: '6', height: '4', rx: '1' } },
      { tag: 'path', attrs: { d: 'M9 12l2 2 4-4' } },
    ]),
  },
]
</script>

<style scoped>
.quicklinks-root {
  margin: 8px 16px 0;
}

.quicklinks-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 10px;
}

.quicklinks-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.ql-card {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  text-align: left;
  transition: box-shadow 0.15s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.ql-card:active { box-shadow: 0 4px 16px rgba(29,78,216,0.1); }

.ql-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e293b;
}

.ql-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
}
</style>
