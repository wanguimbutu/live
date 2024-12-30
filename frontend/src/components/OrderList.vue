<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Sales Orders</h1>

    <!-- Search Bar -->
    <div class="mb-6">
      <input
        v-model="searchQuery"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        placeholder="Search by Customer Name, Sales Order ID, or Date"
        @input="handleSearch"
      />
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
      searchQuery: "", // Search query bound to the input field
    };
  },
  methods: {
    /**
     * Fetch sales orders from the API.
     * @param {boolean} isSearch - If true, resets the sales orders and applies the search query.
     */
    async fetchSalesOrders(isSearch = false) {
      try {
        const filters = [];

        // Apply search filters based on the query
        if (this.searchQuery) {
          filters.push([
            ["customer_name", "like", `%${this.searchQuery}%`],
            "or",
            ["name", "like", `%${this.searchQuery}%`],
            "or",
            ["transaction_date", "like", `%${this.searchQuery}%`],
          ]);
        }

        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            doctype: "Sales Order",
            fields: ["name", "customer_name", "transaction_date", "status"],
            order_by: "creation desc",
            filters: filters,
            limit_start: isSearch ? 0 : this.limitStart,
            limit_page_length: this.limitPageLength,
          }),
        });

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

    /**
     * Load more sales orders (pagination).
     */
    loadMore() {
      this.fetchSalesOrders();
    },

    /**
     * Handle search input and apply filters.
     */
    handleSearch() {
      this.hasMore = true;
      this.fetchSalesOrders(true); // Search mode
    },

    /**
     * Navigate to the sales order details page.
     */
    goToOrderDetails(order) {
      this.$router.push({ name: "OrderDetails", params: { id: order.name } });
    },
  },

  /**
   * Component created lifecycle hook to fetch initial data.
   */
  created() {
    this.fetchSalesOrders();
  },
};
</script>
