<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">Sales Order: {{ order?.name }}</h1>
    
    <div v-if="loading" class="text-center text-gray-500">
      <p>Loading order details...</p>
    </div>
    
    <div v-else-if="order" class="bg-gray-100 p-6 rounded-lg border border-gray-300">
      <p class="mb-4">
        <strong class="text-gray-700">Customer:</strong>
        <span>{{ order.customer_name }}</span>
      </p>
      <p class="mb-4">
        <strong class="text-gray-700">Transaction Date:</strong>
        <span>{{ order.transaction_date }}</span>
      </p>
      <p class="mb-4">
        <strong class="text-gray-700">Delivery Date:</strong>
        <span>{{ order.delivery_date }}</span>
      </p>
      <p class="mb-4">
        <strong class="text-gray-700">Status:</strong> {{ order.status }}
      </p>

      <!-- Items Section -->
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
            <td class="border border-gray-300 px-4 py-2">{{ item.item_name }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ item.qty }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ item.rate }}</td>
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

      <!-- Cancel Button is always available unless status is 'Draft' -->
      <div v-if="order.status !== 'Draft'" class="mt-6">
        <button
          @click="cancelOrder"
          class="px-4 py-2 bg-yellow-500 text-black font-medium rounded shadow hover:bg-yellow-600 mr-2"
        >
          Cancel
        </button>
      </div>

      <!-- Amend Button available when order is 'Cancelled' -->
      <div v-if="order.status === 'Cancelled'" class="mt-6">
        <button
          @click="amendOrder"
          class="px-4 py-2 bg-gray-500 text-white font-medium rounded shadow hover:bg-gray-600"
        >
          Amend
        </button>
      </div>
    </div>
    
    <div v-else>
      <p class="text-gray-700">Could not load order details. Please try again later.</p>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    id: String, // Expecting the order ID as a prop from the router
  },
  data() {
    return {
      order: null, // To store order data
      loading: true, // To manage loading state
    };
  },
  async created() {
    await this.fetchOrderDetails();
  },
  beforeRouteUpdate(to, from, next) {
    // Only refetch the data if the order ID changes
    if (to.params.id !== from.params.id) {
      this.fetchOrderDetails().finally(() => next());
    } else {
      next(); // Continue navigation if no change in ID
    }
  },
  methods: {
    async fetchOrderDetails() {
      this.loading = true;
      try {
        const { id } = this.$route.params;
        const response = await fetch(`/api/resource/Sales Order/${id}`);
        if (!response.ok) throw new Error("Failed to fetch order details.");
        const data = await response.json();
        this.order = data.data;
      } catch (error) {
        console.error("Error fetching order details:", error);
        alert("Could not load order details.");
      } finally {
        this.loading = false;
      }
    },

    async saveOrder() {
      try {
        const response = await fetch(`/api/resource/Sales Order/${this.order.name}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.order),
        });
        if (!response.ok) throw new Error("Failed to save order");
        alert("Order saved successfully!");
        this.fetchOrderDetails(); // Refresh the order details
      } catch (error) {
        console.error("Error saving order:", error);
        alert("Could not save the order.");
      }
    },

    async submitOrder() {
      try {
        const response = await fetch(`/api/resource/Sales Order/${this.order.name}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...this.order,
            status: "Submitted",
          }),
        });
        if (!response.ok) throw new Error("Failed to submit order");
        alert("Order submitted successfully!");
        this.fetchOrderDetails(); // Refresh the order details
      } catch (error) {
        console.error("Error submitting order:", error);
        alert("Could not submit the order.");
      }
    },

    async cancelOrder() {
      try {
        const response = await fetch(`/api/resource/Sales Order/${this.order.name}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: "Cancelled" }),
        });
        if (!response.ok) throw new Error("Failed to cancel order");
        alert("Order cancelled successfully!");
        this.fetchOrderDetails(); // Refresh the order details
      } catch (error) {
        console.error("Error cancelling order:", error);
        alert("Could not cancel the order.");
      }
    },

    async amendOrder() {
      try {
        const response = await fetch("/api/resource/Sales Order", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...this.order,
            status: "Draft",
            amended_from: this.order.name,
          }),
        });
        if (!response.ok) throw new Error("Failed to amend order");
        const data = await response.json();
        alert("Order amended successfully!");
        this.$router.push({ name: "OrderDetails", params: { id: data.data.name } });
      } catch (error) {
        console.error("Error amending order:", error);
        alert("Could not amend the order.");
      }
    },
  },
};
</script>

<style scoped>
/* Styles for Loading state */
.text-center {
  text-align: center;
}

/* Button styling */
button {
  cursor: pointer;
}

button:hover {
  opacity: 0.9;
}

/* Table and Input Field Styling */
table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  text-align: left;
  font-size: 14px;
}

th {
  background-color: #f4f4f4;
}

input[type="number"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
