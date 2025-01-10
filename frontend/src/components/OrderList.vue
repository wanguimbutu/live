<template>
  <div class="p-6 relative">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Sales Orders</h1>

    <!-- Search Bars -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
      <!-- Search by Customer Name -->
      <div>
        <input
          v-model="customerSearchQuery"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder="Search by Customer Name"
          @input="searchByCustomerName"
        />
      </div>

      <!-- Search by Sales Order Name -->
      <div>
        <input
          v-model="salesOrderSearchQuery"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder="Search by Sales Order Name"
          @input="searchBySalesOrderName"
        />
      </div>
    </div>

    <!-- Sales Orders List -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="order in salesOrders"
        :key="order.name"
        class="bg-gray-100 border border-gray-300 rounded-lg p-4 shadow hover:shadow-lg transition-transform transform hover:scale-105 cursor-pointer"
        @click="goToOrderDetails(order)"
      >
        <h2 class="text-lg font-semibold text-gray-800">{{ order.name }}</h2>
        <p class="text-gray-700"><strong>Customer:</strong> {{ order.customer_name }}</p>
        <p class="text-gray-700"><strong>Date:</strong> {{ order.transaction_date }}</p>
        <p class="text-gray-700">
          <strong>Status:</strong>
          <span
            :class="{
              'text-green-600 font-bold': order.status === 'Submitted' || order.status === 'Completed',
              'text-red-600 font-bold': order.status === 'Draft' || order.status === 'Cancelled' || order.status === 'Overdue',
              'text-orange-600 font-semibold': order.status === 'To Deliver and Bill',
              'text-gray-500 font-bold': order.status === 'Closed',
            }"
          >
            {{ order.status }}
          </span>
        </p>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMore" class="mt-6 flex justify-center">
      <button
        class="px-6 py-2 bg-blue-500 text-white font-medium rounded-lg shadow hover:bg-blue-600 transition-colors"
        @click="loadMore"
      >
        Load More
      </button>
    </div>

    <!-- Floating Action Button -->
    <button
      class="fixed bottom-6 right-6 bg-blue-500 text-white rounded-full p-4 shadow-lg hover:bg-blue-600 transition-transform transform hover:scale-110"
      @click="goToAddSalesOrder"
      aria-label="Add Sales Order"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
      </svg>
    </button>
  </div>
</template>
<script>
export default {
  data() {
    return {
      salesOrders: [],
      limitStart: 0,
      limitPageLength: 10,
      hasMore: true,
      customerSearchQuery: "", // For searching by customer name
      salesOrderSearchQuery: "", // For searching by sales order name
    };
  },
  methods: {
    async fetchSalesOrders(filters = [], isSearch = false) {
      try {
        const payload = {
          doctype: "Sales Order",
          fields: ["name", "customer_name", "transaction_date", "status"],
          order_by: "creation desc",
          limit_start: isSearch ? 0 : this.limitStart,
          limit_page_length: this.limitPageLength,
          filters: filters.length > 0 ? filters : undefined,
        };

        console.log("Payload:", payload);

        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const message = data?.message || {};
        const keys = message.keys || [];
        const values = message.values || [];

        const orders = values.map((row) =>
          row.reduce((obj, value, index) => {
            obj[keys[index]] = value;
            return obj;
          }, {})
        );

        if (isSearch) {
          this.salesOrders = orders;
          this.limitStart = this.limitPageLength; // Reset pagination for search results
        } else if (orders.length > 0) {
          this.salesOrders = [...this.salesOrders, ...orders];
          this.limitStart += this.limitPageLength;
        } else {
          this.hasMore = false;
        }
      } catch (error) {
        console.error("Error fetching sales orders:", error);
      }
    },

    searchByCustomerName() {
      this.hasMore = true;
      this.fetchSalesOrders([["customer_name", "like", `%${this.customerSearchQuery}%`]], true);
    },

    searchBySalesOrderName() {
      this.hasMore = true;
      this.fetchSalesOrders([["name", "like", `%${this.salesOrderSearchQuery}%`]], true);
    },

    loadMore() {
      this.fetchSalesOrders();
    },

    goToOrderDetails(order) {
      this.$router.push({ name: "OrderDetails", params: { id: order.name } });
    },

    goToAddSalesOrder() {
      this.$router.push({ name: "AddSalesOrder" });
    },
  },
  created() {
    this.fetchSalesOrders();
  },
};
</script>
