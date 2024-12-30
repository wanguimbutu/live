<template>
  <div class="container mx-auto p-6 max-w-md">
    <h1 class="text-2xl font-bold mb-4">Create New Customer</h1>
    <form @submit.prevent="addCustomer" class="space-y-4">
      <div>
        <label for="newCustomerName" class="block text-sm font-medium text-gray-700">Customer Name:</label>
        <input
          id="newCustomerName"
          v-model="newCustomer.customer_name"
          type="text"
          required
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div>
        <label for="newCustomerID" class="block text-sm font-medium text-gray-700">Customer ID:</label>
        <input
          id="newCustomerID"
          v-model="newCustomer.name"
          type="text"
          required
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <div class="flex space-x-4">
        <button
          type="submit"
          class="bg-blue-600 text-white px-4 py-2 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Create Customer
        </button>
        <button
          type="button"
          @click="navigateBack"
          class="bg-gray-300 text-gray-700 px-4 py-2 rounded-md shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      newCustomer: {
        name: "", // Customer ID
        customer_name: "", // Customer Name
      },
    };
  },
  methods: {
    async addCustomer() {
      try {
        const response = await axios.post("/api/resource/Customer", {
          customer_name: this.newCustomer.customer_name,
          name: this.newCustomer.name,
        });

        console.log("Customer created successfully:", response.data);
        alert("Customer created successfully!");

        // Navigate back to the customer list
        this.navigateBack();
      } catch (error) {
        console.error("Error creating customer:", error);
        alert("Failed to create customer. Please try again.");
      }
    },
    navigateBack() {
      this.$router.push({ name: "CustomerList" });
    },
  },
};
</script>

<style scoped>
/* No additional styles needed as Tailwind CSS handles styling */
</style>
