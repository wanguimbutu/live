<template>
  <div class="max-w-md mx-auto mt-5 bg-white rounded-lg shadow-lg overflow-hidden">
    <div class="bg-gray-100 border-b border-gray-300 p-4">
      <h3 class="text-xl font-bold text-gray-800">
        Hello, {{ currentUser || "Guest" }}
      </h3>
      <p class="text-sm text-gray-600 mt-1">
        Last Check-In:
        <span v-if="loading">Loading...</span>
        <span v-else-if="lastCheckIn">{{ formatDateTime(lastCheckIn) }}</span>
        <span v-else>No record available</span>
        <br />
        Last Check-Out:
        <span v-if="loading">Loading...</span>
        <span v-else-if="lastCheckOut">{{ formatDateTime(lastCheckOut) }}</span>
        <span v-else>No record available</span>
        <a
          href="#"
          class="text-blue-500 hover:underline"
          @click.prevent="toggleCheckInList"
        >
          View List
        </a>
      </p>
    </div>
    <div class="flex justify-center bg-gray-100 border-t border-gray-300 p-4">
      <button
        class="px-4 py-2 text-sm font-semibold text-white bg-black rounded hover:bg-gray-800 transition duration-300"
        @click="handleCheckInOut"
      >
        {{ buttonText }}
      </button>
    </div>

    <!-- Modal for Viewing Check-in List -->
    <div
      v-if="showCheckInList"
      class="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Check-In Logs</h3>
        <!-- Scrollable Visit List -->
        <div class="visit-list overflow-y-auto max-h-60">
          <table class="table-auto w-full border-collapse border border-gray-200">
            <thead>
              <tr>
                <th class="border border-gray-300 px-4 py-2 text-left">Type</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Time</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Latitude</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Longitude</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(log, index) in checkInList"
                :key="index"
                class="text-sm text-gray-700"
              >
                <td class="border border-gray-300 px-4 py-2">
                  {{ log.log_type === "IN" ? "Check-In" : "Check-Out" }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatDateTime(log.time) }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ log.latitude || "N/A" }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ log.longitude || "N/A" }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex justify-end mt-4">
          <button
            class="px-4 py-2 text-sm text-white bg-gray-800 rounded hover:bg-gray-700"
            @click="toggleCheckInList"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { session } from "@/data/session"; // Adjust the path to where session is located

export default {
  name: "CheckIn",
  data() {
    return {
      buttonText: "Check In",
      lastCheckIn: null,
      lastCheckOut: null,
      checkInList: [], // Stores all logs
      showCheckInList: false,
      loading: false, // To manage the loading state
    };
  },
  computed: {
    currentUser() {
      return session.user; // Access session.user directly in a computed property
    },
  },
  methods: {
    async handleCheckInOut() {
      const logType = this.buttonText === "Check In" ? "IN" : "OUT";
      const now = new Date();

      // Format time as YYYY-MM-DD HH:mm:ss
      const formattedTime = `${now.getFullYear()}-${String(
        now.getMonth() + 1
      ).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")} ${String(
        now.getHours()
      ).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(
        now.getSeconds()
      ).padStart(2, "0")}`;

      try {
        const { latitude, longitude } = await this.getCurrentLocation();

        const payload = {
          employee: session.user,
          time: formattedTime,
          log_type: logType,
          latitude,
          longitude,
        };

        console.log("Payload:", payload); // Debugging payload

        const response = await fetch("/api/resource/Employee Checkin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorText = await response.text(); // Detailed error response
          console.error("Server Error:", errorText);
          throw new Error("Failed to check in/out");
        }

        this.buttonText = logType === "IN" ? "Check Out" : "Check In";
        await this.fetchCheckInOutTimes();
      } catch (error) {
        console.error("Error during check-in/out:", error);
        alert("An error occurred. Please try again.");
      }
    },

    async getCurrentLocation() {
      return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject("Geolocation is not supported by your browser.");
          return;
        }

        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            resolve({ latitude, longitude });
          },
          (error) => {
            console.error("Error fetching location:", error);
            reject("Unable to retrieve location. Please enable location services.");
          }
        );
      });
    },

    async fetchCheckInOutTimes() {
  this.loading = true;
  try {
    // Fetch records with explicit fields
    const response = await fetch(
      `/api/resource/Employee Checkin?filters=[["employee","=","${session.user}"]]&fields=["log_type","time","name"]&order_by=creation desc`,
      { credentials: "include" }
    );

    if (!response.ok) throw new Error("Failed to fetch check-in/out times");

    const { data: records } = await response.json();

    console.log("Fetched Records:", records); // Log all fetched records for debugging

    // Find the latest check-in and check-out records
    const latestIn = records.find((record) => record.log_type === "IN");
    const latestOut = records.find((record) => record.log_type === "OUT");

    // Assign the time values (if found) to the respective fields
    this.lastCheckIn = latestIn ? latestIn.time : null;
    this.lastCheckOut = latestOut ? latestOut.time : null;

    console.log("Last Check-In:", this.lastCheckIn);
    console.log("Last Check-Out:", this.lastCheckOut);

    // Update the check-in list for modal display
    this.checkInList = records;
  } catch (error) {
    console.error("Error fetching check-in/out records:", error);
    alert("Failed to retrieve check-in/out records.");
  } finally {
    this.loading = false;
  }
},


    toggleCheckInList() {
      this.showCheckInList = !this.showCheckInList;
    },

    formatDateTime(dateTime) {
      if (!dateTime) return "Invalid Time";

      const parsedDate = new Date(dateTime);

      if (isNaN(parsedDate)) return "Invalid Date";

      const options = {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      };
      return parsedDate.toLocaleString("en-US", options);
    },
  },
  async mounted() {
    if (!session.isLoggedIn) {
      console.warn("User is not logged in");
      return;
    }

    await this.fetchCheckInOutTimes();
  },
};
</script>
<style>
.visit-list {
  max-height: 300px; /* Set the maximum height */
  overflow-y: auto; /* Enable vertical scrolling */
  padding: 10px; /* Optional: Add padding for aesthetics */
  border: 1px solid #ccc; /* Optional: Add a border for clarity */
  background-color: #f9f9f9; /* Optional: Set a background color */
  border-radius: 5px; /* Optional: Rounded corners */
}

</style>
