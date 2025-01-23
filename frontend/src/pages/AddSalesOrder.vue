<template>
  <div class="container mx-auto p-6 max-w-md">
    <h1 class="text-2xl font-bold mb-4">Create New Sales Order</h1>
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
import { IonPage } from '@ionic/vue';

export default {
  components: {
    IonPage,
  },
  data() {
    return {
      customers: [],
      items: [],
      warehouses: [],
      newSalesOrder: {
        customer: "",
        items: [{ item_code: "", qty: 1, rate: 0, warehouse: "" }],
        delivery_date: "",
      },
    };
  },
  async created() {
    try {
      const customerResponse = await fetch("/api/resource/Customer");
      const customerData = await customerResponse.json();
      this.customers = customerData.data;

      const itemResponse = await fetch("/api/resource/Item");
      const itemData = await itemResponse.json();
      this.items = itemData.data;

      const warehouseResponse = await fetch("/api/resource/Warehouse");
      const warehouseData = await warehouseResponse.json();
      this.warehouses = warehouseData.data;
    } catch (error) {
      console.error("Error fetching data from ERPNext:", error);
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
        console.log("Sales Order saved successfully:", data);
        alert("Sales Order saved successfully!");
        this.newSalesOrder.id = data.data.name; // Save the ID for further actions
      } catch (error) {
        console.error("Error creating Sales Order:", error);
        alert("Failed to save Sales Order. Please try again.");
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
      this.$router.push({ name: "OrderList" });
    },
  },
};
</script>

<style scoped>
/* Tailwind CSS handles styling */
</style>
