<template>
    <div class="container mx-auto p-6 max-w-md">
      <h1 class="text-2xl font-bold mb-4">Create New Sales Order</h1>

      <!-- Offline notice -->
      <div v-if="!isOnline" class="mb-4 flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        You're offline. Orders saved here will sync automatically when you reconnect.
      </div>

      <!-- Saved feedback -->
      <div v-if="savedOffline" class="mb-4 flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        Order saved offline. It will sync when you're back online.
      </div>

      <form @submit.prevent="createSalesOrder" class="space-y-4">
        <!-- Customer Selection -->
        <div>
          <label for="customer" class="block text-sm font-medium text-gray-700">Select Customer:</label>
          <select
            id="customer"
            v-model="newSalesOrder.customer"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="" disabled>Select a customer</option>
            <option v-for="customer in customers" :key="customer.name" :value="customer.name">
              {{ customer.customer_name || customer.name }}
            </option>
          </select>
        </div>
  
        <!-- Items Selection -->
        <div>
          <label for="items" class="block text-sm font-medium text-gray-700">Add Items:</label>
          <div v-for="(item, index) in newSalesOrder.items" :key="index" class="mb-4 border p-4 rounded-md">
            <div class="flex space-x-2 mb-2">
              <select
                v-model="item.item_code"
                required
                class="flex-1 border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="" disabled>Select an item</option>
                <option v-for="itemOption in items" :key="itemOption.name" :value="itemOption.name">
                  {{ itemOption.item_name || itemOption.name }}
                </option>
              </select>
              <input
                v-model.number="item.qty"
                type="number"
                placeholder="Qty"
                required
                min="1"
                class="w-20 border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                v-model.number="item.rate"
                type="number"
                placeholder="Rate"
                required
                min="0"
                class="w-28 border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <!-- Warehouse Selection -->
            <div>
              <label for="warehouse" class="block text-sm font-medium text-gray-700">Delivery Warehouse:</label>
              <select
                v-model="item.warehouse"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="" disabled>Select a warehouse</option>
                <option v-for="warehouse in warehouses" :key="warehouse.name" :value="warehouse.name">
                  {{ warehouse.warehouse_name || warehouse.name }}
                </option>
              </select>
            </div>
            <button
              type="button"
              @click="removeItem(index)"
              class="mt-2 text-red-500 font-bold"
            >
              Remove Item
            </button>
          </div>
          <button
            type="button"
            @click="addItem"
            class="text-blue-500 font-bold"
          >
            + Add Item
          </button>
        </div>
  
        <!-- Delivery Date -->
        <div>
          <label for="delivery_date" class="block text-sm font-medium text-gray-700">Delivery Date:</label>
          <input
            id="delivery_date"
            v-model="newSalesOrder.delivery_date"
            type="date"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
  
        <!-- Action Buttons -->
        <div class="flex space-x-4">
          <button
            type="submit"
            class="bg-blue-600 text-white px-4 py-2 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Save Order
          </button>
          <button
            type="button"
            @click="submitSalesOrder"
            class="bg-green-600 text-white px-4 py-2 rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Submit Order
          </button>
          <button
            type="button"
            @click="cancelSalesOrder"
            class="bg-red-600 text-white px-4 py-2 rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Cancel Order
          </button>
          <button
            type="button"
            @click="navigateBack"
            class="bg-gray-300 text-gray-700 px-4 py-2 rounded-md shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
          >
            Back
          </button>
        </div>
      </form>
    </div>
</template>
  
<script>
import { useOfflineQueue, addToQueue } from '../composables/useOfflineQueue'

export default {
  setup() {
    const { isOnline } = useOfflineQueue()
    return { isOnline }
  },
  data() {
    return {
      customers: [],
      items: [],
      warehouses: [],
      savedOffline: false,
      newSalesOrder: {
        customer: "",
        items: [{ item_code: "", qty: 1, rate: 0, warehouse: "" }],
        delivery_date: "",
      },
    };
  },
  async created() {
    // Load from cache first so the form is instantly usable offline
    const cached = localStorage.getItem('live_form_cache')
    if (cached) {
      const { customers, items, warehouses } = JSON.parse(cached)
      this.customers = customers || []
      this.items = items || []
      this.warehouses = warehouses || []
    }
    // Refresh from server when online
    if (this.isOnline) {
      try {
        const [cRes, iRes, wRes] = await Promise.all([
          fetch("/api/resource/Customer?fields=[\"name\",\"customer_name\"]&limit_page_length=200"),
          fetch("/api/resource/Item?fields=[\"name\",\"item_name\"]&limit_page_length=200"),
          fetch("/api/resource/Warehouse?fields=[\"name\",\"warehouse_name\"]&limit_page_length=200"),
        ])
        this.customers = (await cRes.json()).data || []
        this.items     = (await iRes.json()).data || []
        this.warehouses = (await wRes.json()).data || []
        localStorage.setItem('live_form_cache', JSON.stringify({
          customers: this.customers,
          items: this.items,
          warehouses: this.warehouses,
        }))
      } catch (error) {
        console.error("Error fetching form data:", error)
      }
    }
  },
  methods: {
    addItem() {
      this.newSalesOrder.items.push({ item_code: "", qty: 1, rate: 0, warehouse: "" });
    },
    removeItem(index) {
      this.newSalesOrder.items.splice(index, 1);
    },
    async createSalesOrder() {
      // Save offline when there's no connection
      if (!this.isOnline) {
        addToQueue({ ...this.newSalesOrder })
        this.savedOffline = true
        this.newSalesOrder = {
          customer: "",
          items: [{ item_code: "", qty: 1, rate: 0, warehouse: "" }],
          delivery_date: "",
        }
        setTimeout(() => { this.savedOffline = false }, 4000)
        return
      }

      try {
        const response = await fetch("/api/resource/Sales Order", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.newSalesOrder),
        });

        if (!response.ok) {
          throw new Error(`Failed to create Sales Order: ${response.statusText}`);
        }

        const data = await response.json();
        alert("Sales Order saved successfully!");
        this.newSalesOrder.id = data.data.name;
      } catch (error) {
        // If the network call fails mid-flight, queue it for retry
        addToQueue({ ...this.newSalesOrder })
        this.savedOffline = true
        setTimeout(() => { this.savedOffline = false }, 4000)
      }
    },
      async submitSalesOrder() {
        if (!this.newSalesOrder.id) {
          alert("Please save the order first.");
          return;
        }
        try {
          const response = await fetch(`/api/resource/Sales Order/${this.newSalesOrder.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ docstatus: 1 }),
          });
  
          if (!response.ok) {
            throw new Error(`Failed to submit Sales Order: ${response.statusText}`);
          }
  
          console.log("Sales Order submitted successfully.");
          alert("Sales Order submitted successfully!");
        } catch (error) {
          console.error("Error submitting Sales Order:", error);
          alert("Failed to submit Sales Order. Please try again.");
        }
      },
      async cancelSalesOrder() {
        if (!this.newSalesOrder.id) {
          alert("Please save the order first.");
          return;
        }
        try {
          const response = await fetch(`/api/resource/Sales Order/${this.newSalesOrder.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ docstatus: 2 }), // docstatus: 2 indicates canceled
          });
  
          if (!response.ok) {
            throw new Error(`Failed to cancel Sales Order: ${response.statusText}`);
          }
  
          console.log("Sales Order canceled successfully.");
          alert("Sales Order canceled successfully!");
        } catch (error) {
          console.error("Error canceling Sales Order:", error);
          alert("Failed to cancel Sales Order. Please try again.");
        }
      },
      navigateBack() {
        this.$router.push('/salesOrderList');
      },
    },
  };
</script>
  
  <style scoped>
  /* Tailwind CSS handles styling */
  </style>
  