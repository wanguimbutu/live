<template>
  <div class="border border-gray-300 rounded-lg shadow-lg bg-white max-w-xl mx-auto my-6 overflow-hidden">
    <!-- Card Header -->
    <div class="bg-gray-100 px-6 py-4 border-b border-gray-300">
      <h2 class="text-lg font-bold text-gray-800">Quick Links</h2>
    </div>

    <!-- Card Content -->
    <div class="divide-y divide-gray-300">
      <button
        class="w-full flex justify-between items-center px-6 py-4 hover:bg-gray-50"
        type="button"
        @click="$router.push('/add-sales-order')"
      >
        <div>
          <h3 class="text-base font-semibold text-gray-800">Create Sales Order</h3>
        </div>
        <span class="text-gray-500 text-xl">&gt;</span>
      </button>

      <button
        class="w-full flex justify-between items-center px-6 py-4 hover:bg-gray-50"
        type="button"
        @click="$router.push('/attendance')"
      >
        <div>
          <h3 class="text-base font-semibold text-gray-800">View Attendance</h3>
        </div>
      </button>

      <button
        class="w-full flex justify-between items-center px-6 py-4 hover:bg-gray-50"
        type="button"
        @click="$router.push('/add-customer')"
      >
        <div>
          <h3 class="text-base font-semibold text-gray-800">Create Customer</h3>
        </div>
        <span class="text-gray-500 text-xl">&gt;</span>
      </button>

      <button
        class="w-full flex justify-between items-center px-6 py-4 hover:bg-gray-50"
        type="button"
        @click="$router.push('/capture-customer-location')"
      >
        <div>
          <h3 class="text-base font-semibold text-gray-800">Capture Customer Location</h3>
        </div>
        <span class="text-gray-500 text-xl">&rsaquo;</span>
      </button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "CardWithLinks",
});
</script>

