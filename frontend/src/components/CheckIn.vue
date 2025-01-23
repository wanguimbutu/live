<template>
  <div class="max-w-md mx-auto mt-5 bg-white rounded-lg shadow-lg overflow-hidden">
    <div class="bg-gray-100 border-b border-gray-300 p-4">
      <h3 class="text-xl font-bold text-gray-800">
        Hello, {{ currentUser || "Guest" }}
      </h3>
      <p class="text-sm text-gray-600 mt-1">
        Last Check-In: {{ lastCheckIn || "No record available" }} <br />
        Last Check-Out: {{ lastCheckOut || "No record available" }}
        <a href="#" class="text-blue-500 hover:underline">View List</a>
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
      const formattedTime = now.toISOString().slice(0, 19).replace("T", " ");

      try {
        const { latitude, longitude } = await this.getCurrentLocation();
        const payload = {
          employee: session.user,
          time: formattedTime,
          log_type: logType,
          latitude,
          longitude,
        };

        const response = await fetch("/api/resource/Employee Checkin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to check in/out");

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
      try {
        const response = await fetch(
          `/api/resource/Employee Checkin?filters=[["employee","=","${session.user}"]]&order_by=creation desc&limit_page_length=2`,
          { credentials: "include" }
        );

        if (!response.ok) throw new Error("Failed to fetch check-in/out times");

        const { data: records } = await response.json();

        this.lastCheckIn = records.find((record) => record.log_type === "IN")?.time || null;
        this.lastCheckOut = records.find((record) => record.log_type === "OUT")?.time || null;
      } catch (error) {
        console.error("Error fetching check-in/out records:", error);
        alert("Failed to retrieve check-in/out records.");
      }
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
