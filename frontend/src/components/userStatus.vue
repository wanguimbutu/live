<template>
    <div class="max-w-md mx-auto mt-5 bg-white rounded-lg shadow-lg overflow-hidden">
      <!-- Header Section -->
      <div class="bg-gray-100 border-b border-gray-300 p-4">
        <h3 class="text-xl font-bold text-gray-800">User Status</h3>
        <p class="text-sm text-gray-600 mt-1">
          Current Location: <br />
          <span v-if="location">
            Latitude: {{ location.latitude }}, Longitude: {{ location.longitude }}
          </span>
          <span v-else class="text-red-500">Fetching location...</span>
        </p>
      </div>
  
      <!-- Battery and Mobile Data Information -->
      <div class="p-4">
        <p class="text-base text-gray-700">
          Battery Percentage: <span class="font-bold">{{ batteryPercentage || 'Fetching...' }}%</span>
        </p>
        <p class="text-base text-gray-700">
          Mobile Data: 
          <span
            :class="{'text-green-500': mobileData, 'text-red-500': !mobileData}"
          >
            {{ mobileData ? 'On' : 'Off' }}
          </span>
        </p>
      </div>
  
      <!-- Refresh Button -->
      <div class="flex justify-center bg-gray-100 border-t border-gray-300 p-4">
        <button
          class="px-4 py-2 text-sm font-semibold text-white bg-blue-500 rounded hover:bg-blue-700 transition duration-300"
          @click="fetchStatus"
        >
          Refresh Status
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        location: null, // User's current location
        batteryPercentage: null, // Battery status
        mobileData: false, // Mobile data status
      };
    },
    methods: {
      /**
       * Fetches the user's current geolocation.
       */
      async fetchLocation() {
        return new Promise((resolve, reject) => {
          if (!navigator.geolocation) {
            reject("Geolocation is not supported by your browser.");
            return;
          }
  
          navigator.geolocation.getCurrentPosition(
            (position) => {
              const { latitude, longitude } = position.coords;
              this.location = { latitude, longitude };
              resolve(this.location);
            },
            (error) => {
              console.error("Error fetching location:", error);
              this.location = null;
              reject("Unable to retrieve location.");
            }
          );
        });
      },
  
      /**
       * Fetches the current battery status.
       */
      async fetchBatteryStatus() {
        try {
          const battery = await navigator.getBattery();
          this.batteryPercentage = Math.round(battery.level * 100);
  
          // Listen for changes in battery level
          battery.addEventListener("levelchange", () => {
            this.batteryPercentage = Math.round(battery.level * 100);
          });
        } catch (error) {
          console.error("Error getting battery status:", error);
        }
      },
  
      /**
       * Checks if mobile data is enabled.
       */
      fetchMobileDataStatus() {
        try {
          // Check if the user is online
          this.mobileData = navigator.connection?.type === "cellular" || navigator.onLine;
        } catch (error) {
          console.error("Error checking mobile data status:", error);
        }
      },
  
      /**
       * Fetches all the status information.
       */
      async fetchStatus() {
        await this.fetchLocation();
        await this.fetchBatteryStatus();
        this.fetchMobileDataStatus();
      },
    },
  
    /**
     * Lifecycle hook: Called when the component is mounted.
     */
    async mounted() {
      await this.fetchStatus();
    },
  };
  </script>
  
  <style scoped>
  .text-red-500 {
    color: #f56565;
  }
  .text-green-500 {
    color: #48bb78;
  }
  </style>
  