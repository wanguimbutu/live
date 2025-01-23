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
        class="bg-white p-4 border border-gray-300 rounded-lg shadow hover:shadow-lg transition-transform transform hover:scale-105 cursor-pointer"
        @click="viewCustomerDetails(customer)"
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

   <!-- Modal for Customer Visit -->
<div
  v-if="showCustomerVisitModal"
  class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  @click="closeVisitModal"
>
  <div
    class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md"
    @click.stop
  >
    <h2 class="text-lg font-bold mb-4">Customer Visit</h2>
    <p class="mb-4">Customer: {{ currentCustomer.customer_name }}</p>
    
    <div class="space-y-4">
      <!-- Buttons for Starting and Ending Visit -->
      <div>
        <button
          v-if="!visitInProgress"
          @click="startVisit"
          class="px-4 py-2 bg-green-500 text-white rounded-lg shadow hover:bg-green-600"
        >
          Start Visit
        </button>
        <button
          v-else
          @click="endVisit"
          class="px-4 py-2 bg-red-500 text-white rounded-lg shadow hover:bg-red-600"
        >
          End Visit
        </button>
      </div>

      <!-- Display Visit Timer -->
      <div v-if="visitInProgress" class="mt-4">
        <p class="text-gray-800 font-semibold">Visit Duration: {{ timer }}</p>
      </div>

      <!-- Capture Location -->
      <div>
        <button
          @click="captureLocationAndSave"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 mt-4"
        >
          Capture Location
        </button>
      </div>

      <!-- Display location and map -->
      <div v-if="locationCaptured" class="mt-4">
        <p>Location: {{ capturedLocation }}</p>
        <p>Area: {{ capturedArea }}</p>
        <div id="map" class="h-48 w-full mt-2"></div>
      </div>
    </div>
  </div>
</div>



    <!-- Modal for Feedback -->
    <div
      v-if="showFeedbackModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeFeedbackModal"
    >
      <div
        class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md"
        @click.stop
      >
        <h2 class="text-lg font-bold mb-4">Provide Feedback</h2>
        <form @submit.prevent="submitFeedback" class="space-y-4">
          <div>
            <label for="feedback" class="block text-sm font-medium text-gray-700">Feedback:</label>
            <textarea
              id="feedback"
              v-model="feedbackText"
              required
              class="w-full mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-400"
              rows="4"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeFeedbackModal"
              class="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600"
            >
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from "vue";

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
    const showCustomerVisitModal = ref(false);
    const showFeedbackModal = ref(false);
    const currentCustomer = ref({});
    const visitInProgress = ref(false);
    const timer = ref("00:00");
    const feedbackText = ref("");
    let visitInterval = null;
    const capturedLocation = ref("");
    const locationCaptured = ref(false);

    const fetchCustomers = async (isSearch = false) => {
      try {
        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            doctype: "Customer",
            fields: ["name", "customer_name"],
            order_by: "creation desc",
            filters: searchQuery.value
              ? [["customer_name", "like", `%${searchQuery.value}%`]]
              : [],
            limit_start: limitStart.value,
            limit_page_length: limitPageLength,
          }),
        });

        const data = await response.json();
        const fetchedCustomers = data?.message?.values?.map((val) => ({
          name: val[0],
          customer_name: val[1],
        })) || [];

        if (isSearch) customers.value = fetchedCustomers;
        else customers.value = [...customers.value, ...fetchedCustomers];

        hasMore.value = fetchedCustomers.length >= limitPageLength;
        if (!isSearch) limitStart.value += limitPageLength;
      } catch (error) {
        console.error("Error fetching customers:", error);
      }
    };

    const loadMore = () => fetchCustomers();

    const handleSearch = () => {
      limitStart.value = 0;
      hasMore.value = true;
      fetchCustomers(true);
    };

    const addCustomer = async () => {
      try {
        await fetch("/api/resource/Customer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newCustomer.value),
        });
        alert("Customer created successfully");
        newCustomer.value = { name: "", customer_name: "" };
        showAddCustomerModal.value = false;
        fetchCustomers();
      } catch (error) {
        alert("Failed to create customer.");
        console.error(error);
      }
    };

    const closeModal = () => (showAddCustomerModal.value = false);

    const viewCustomerDetails = (customer) => {
      currentCustomer.value = customer;
      showCustomerVisitModal.value = true;
    };

    const closeVisitModal = () => (showCustomerVisitModal.value = false);

    const startVisit = () => {
  visitInProgress.value = true;
  timer.value = "00:00";
  let seconds = 0;

  // Start interval for timer
  visitInterval = setInterval(() => {
    seconds++;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    timer.value = `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  }, 1000);
};

const endVisit = () => {
  clearInterval(visitInterval);
  visitInProgress.value = false;
  showFeedbackModal.value = true; // Show feedback modal after ending the visit
};


    const submitFeedback = async () => {
      try {
        await fetch("/api/resource/Customer Visits", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customer: currentCustomer.value.name,
            feedback: feedbackText.value,
            duration: timer.value,
          }),
        });
        alert("Visit recorded successfully");
        visitInProgress.value = false;
        showCustomerVisitModal.value = false;
        showFeedbackModal.value = false;
      } catch (error) {
        alert("Failed to record visit.");
        console.error(error);
      }
    };

    const closeFeedbackModal = () => (showFeedbackModal.value = false);

    const capturedArea = ref("");

    const captureLocationAndSave = async () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            capturedLocation.value = `Latitude: ${lat}, Longitude: ${lng}`;
            locationCaptured.value = true;

            // Reverse geocode to get area name
            const areaName = await reverseGeocode(lat, lng);
            capturedArea.value = areaName;

            // Save to ERPNext
            await updateCustomerLocation(lat, lng, areaName);

            // Render map
            renderMap(lat, lng);
          },
          (error) => {
            console.error("Error capturing location:", error);
            alert("Failed to capture location.");
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
      }
    };

    const reverseGeocode = async (lat, lng) => {
      try {
        const response = await fetch(
          `https://api.opencagedata.com/geocode/v1/json?q=${lat}+${lng}&key=b5208eed61654e19bcb89063dab6bf3d`
        );
        const data = await response.json();
        return data.results[0]?.formatted || "Unknown Area";
      } catch (error) {
        console.error("Error during reverse geocoding:", error);
        return "Unknown Area";
      }
    };

    const updateCustomerLocation = async (lat, lng, areaName) => {
      try {
        await fetch(`/api/resource/Customer/${currentCustomer.value.name}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            custom_customer_location: `${lat}, ${lng}`,
            custom_area_name: areaName
          }),
        });
        alert("Location saved successfully.");
      } catch (error) {
        console.error("Error saving location to ERPNext:", error);
        alert("Failed to save location.");
      }
    };

    const renderMap = (lat, lng) => {
      const map = L.map("map").setView([lat, lng], 13);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);

      L.marker([lat, lng]).addTo(map).bindPopup("Customer Location").openPopup();
    };
;

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
      showCustomerVisitModal,
      currentCustomer,
      viewCustomerDetails,
      closeVisitModal,
      startVisit,
      endVisit,
      visitInProgress,
      timer,
      showFeedbackModal,
      feedbackText,
      submitFeedback,
      closeFeedbackModal,
      captureLocationAndSave,
      capturedLocation,
      locationCaptured,
      capturedArea,
    };
  },
};
</script>
