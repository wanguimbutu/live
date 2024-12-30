<template>
  <div class="p-6 bg-gray-50 rounded-lg">
    <!-- Header with title and add button -->
    <header class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-bold text-gray-800">Customer List</h1>
      <button
        class="bg-blue-500 text-white rounded-full w-10 h-10 text-2xl flex justify-center items-center hover:bg-blue-600"
        @click="showAddCustomerModal = true"
      >
        +
      </button>
    </header>

    <!-- Search input -->
    <input
      class="w-full p-3 mb-6 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      v-model="searchQuery"
      @input="handleSearch"
      placeholder="Search customers..."
      type="text"
    />

    <!-- Customers display -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="customer in customers"
        :key="customer.name"
        class="bg-white p-4 border border-gray-300 rounded-lg shadow hover:shadow-lg transition-transform transform hover:scale-105"
      >
        <strong class="text-lg font-semibold text-gray-800">{{ customer.customer_name }}</strong>
        <p class="text-gray-600">ID: {{ customer.name }}</p>
      </div>
    </div>

    <!-- Load More button -->
    <div class="mt-6 text-center">
      <button
        v-if="hasMore"
        @click="loadMore"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600"
      >
        Load More
      </button>
      <p v-else class="text-gray-500">No more customers to load.</p>
    </div>

    <!-- Modal for Adding Customer -->
    <div
      v-if="showAddCustomerModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeModal"
    >
      <div
        class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md"
        @click.stop
      >
        <h2 class="text-lg font-bold mb-4">Create New Customer</h2>
        <form @submit.prevent="addCustomer" class="space-y-4">
          <div>
            <label for="customerName" class="block text-sm font-medium text-gray-700">Customer Name:</label>
            <input
              id="customerName"
              v-model="newCustomer.customer_name"
              type="text"
              required
              class="w-full mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <div>
            <label for="customerId" class="block text-sm font-medium text-gray-700">Customer ID:</label>
            <input
              id="customerId"
              v-model="newCustomer.name"
              type="text"
              required
              class="w-full mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";

export default {
  name: "CustomerList",
  setup() {
    const customers = ref([]);
    const searchQuery = ref("");
    const hasMore = ref(true);
    const showAddCustomerModal = ref(false);
    const newCustomer = ref({ name: "", customer_name: "" });
    const limitStart = ref(0);
    const limitPageLength = 10;

    /**
     * Fetch customers from the API using fetch().
     * @param {boolean} isSearch - If true, resets the customers list and applies the search query.
     */
    const fetchCustomers = async (isSearch = false) => {
      try {
        const filters = searchQuery.value
          ? [["customer_name", "like", `%${searchQuery.value}%`]]
          : [];

        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            doctype: "Customer",
            fields: ["name", "customer_name"],
            order_by: "creation desc",
            filters: filters,
            limit_start: limitStart.value,
            limit_page_length: limitPageLength,
          }),
        });

        const data = await response.json();
        const fetchedCustomers = data?.message?.values?.map((val) => ({
          name: val[0],
          customer_name: val[1],
        })) || [];

        if (isSearch) {
          customers.value = fetchedCustomers;
        } else {
          customers.value = [...customers.value, ...fetchedCustomers];
        }

        hasMore.value = fetchedCustomers.length >= limitPageLength;
        if (!isSearch) limitStart.value += limitPageLength;
      } catch (error) {
        console.error("Error fetching customers:", error);
      }
    };

    /**
     * Load more customers for pagination.
     */
    const loadMore = () => {
      fetchCustomers();
    };

    /**
     * Handle search input and apply filters.
     */
    const handleSearch = () => {
      limitStart.value = 0;
      hasMore.value = true;
      fetchCustomers(true);
    };

    /**
     * Add a new customer using fetch().
     */
    const addCustomer = async () => {
      try {
        const response = await fetch("/api/resource/Customer", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(newCustomer.value),
        });

        if (response.ok) {
          alert("Customer created successfully");
          newCustomer.value = { name: "", customer_name: "" };
          showAddCustomerModal.value = false;
          limitStart.value = 0;
          customers.value = [];
          fetchCustomers();
        } else {
          alert("Failed to create customer.");
        }
      } catch (error) {
        console.error("Error adding customer:", error);
        alert("Failed to create customer.");
      }
    };

    /**
     * Close the add customer modal.
     */
    const closeModal = () => {
      showAddCustomerModal.value = false;
    };

    // Initial fetch of customers
    fetchCustomers();

    return {
      customers,
      searchQuery,
      hasMore,
      showAddCustomerModal,
      newCustomer,
      loadMore,
      handleSearch,
      addCustomer,
      closeModal,
    };
  },
};
</script>
