<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">Sales Order: {{ order?.name }}</h1>
    <div v-if="order" class="bg-gray-100 p-6 rounded-lg border border-gray-300">
      <p class="mb-4">
        <strong class="text-gray-700">Customer:</strong>
        <input
          v-model="order.customer_name"
          class="ml-2 border border-gray-300 rounded px-2 py-1 text-gray-700"
        />
      </p>
      <p class="mb-4">
        <strong class="text-gray-700">Transaction Date:</strong>
        <input
          type="date"
          v-model="order.transaction_date"
          class="ml-2 border border-gray-300 rounded px-2 py-1 text-gray-700"
        />
      </p>
      <p class="mb-4">
        <strong class="text-gray-700">Status:</strong> {{ order.status }}
      </p>

      <h3 class="text-xl font-semibold text-gray-800 mb-4">Items</h3>
      <table class="w-full border-collapse border border-gray-300">
        <thead class="bg-gray-200">
          <tr>
            <th class="border border-gray-300 px-4 py-2 text-left">Item</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Quantity</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Rate</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in order.items"
            :key="item.item_code"
            class="odd:bg-white even:bg-gray-50"
          >
            <td class="border border-gray-300 px-4 py-2">{{ item.item_code }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <input
                type="number"
                v-model="item.qty"
                class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700"
              />
            </td>
            <td class="border border-gray-300 px-4 py-2">
              <input
                type="number"
                v-model="item.rate"
                class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700"
              />
            </td>
            <td class="border border-gray-300 px-4 py-2">{{ item.amount }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Action Buttons -->
      <div v-if="order.status === 'Draft'" class="mt-6">
        <button
          @click="saveOrder"
          class="px-4 py-2 bg-blue-500 text-white font-medium rounded shadow hover:bg-blue-600 mr-2"
        >
          Save
        </button>
        <button
          @click="submitOrder"
          class="px-4 py-2 bg-green-500 text-white font-medium rounded shadow hover:bg-green-600"
        >
          Submit
        </button>
      </div>
      <div v-else-if="order.status === 'Submitted'" class="mt-6">
        <button
          @click="cancelOrder"
          class="px-4 py-2 bg-yellow-500 text-black font-medium rounded shadow hover:bg-yellow-600 mr-2"
        >
          Cancel
        </button>
        <button
          @click="amendOrder"
          class="px-4 py-2 bg-gray-500 text-white font-medium rounded shadow hover:bg-gray-600"
        >
          Amend
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: {
    id: String, // Expecting the order ID as a prop from the router
  },
  data() {
    return {
      order: null, // To store order data
    };
  },
  created() {
    this.fetchOrderDetails();
  },
  watch: {
    // Watch the route parameter 'id' for changes and refetch data
    $route(to, from) {
      if (to.params.id !== from.params.id) {
        this.fetchOrderDetails();
      }
    },
  },
  methods: {
    async fetchOrderDetails() {
      try {
        const { id } = this.$route.params;
        const response = await axios.get(`/api/resource/Sales Order/${id}`);
        this.order = response.data.data;
      } catch (error) {
        console.error("Error fetching order details:", error);
        alert("Could not load order details.");
      }
    },
    async saveOrder() {
      try {
        const response = await axios.put(`/api/resource/Sales Order/${this.order.name}`, this.order);
        alert("Order saved successfully!");
      } catch (error) {
        console.error("Error saving order:", error);
        alert("Could not save the order.");
      }
    },
    async submitOrder() {
      try {
        const response = await axios.put(`/api/resource/Sales Order/${this.order.name}`, {
          ...this.order,
          status: "Submitted",
        });
        alert("Order submitted successfully!");
        this.fetchOrderDetails(); // Refresh the order details
      } catch (error) {
        console.error("Error submitting order:", error);
        alert("Could not submit the order.");
      }
    },
    async cancelOrder() {
      try {
        const response = await axios.put(`/api/resource/Sales Order/${this.order.name}`, {
          status: "Cancelled",
        });
        alert("Order cancelled successfully!");
        this.fetchOrderDetails();
      } catch (error) {
        console.error("Error cancelling order:", error);
        alert("Could not cancel the order.");
      }
    },
    async amendOrder() {
      try {
        const response = await axios.post("/api/resource/Sales Order", {
          ...this.order,
          status: "Draft",
          amended_from: this.order.name,
        });
        alert("Order amended successfully!");
        this.order = response.data.data;
      } catch (error) {
        console.error("Error amending order:", error);
        alert("Could not amend the order.");
      }
    },
  },
};
</script>
