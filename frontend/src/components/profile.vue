<template>
  <div class="flex justify-end items-center p-4 relative">
    <!-- Profile Icon and Dropdown -->
    <div class="relative">
      <!-- Profile Button -->
      <button
        @click="toggleDropdown"
        class="w-8 h-8 rounded-full overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <img
          :src="user.profilePicture || 'https://via.placeholder.com/40'"
          alt="Profile"
          class="w-full h-full object-cover"
        />
      </button>

      <!-- Dropdown Menu -->
      <div
        v-show="dropdownOpen"
        class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-50"
      >
        <!-- User Info -->
        <div class="p-4 border-b border-gray-200">
          <p class="font-semibold text-gray-800">{{ user.fullName }}</p>
          <p class="text-sm text-gray-600">
            Total Check-ins: {{ user.totalCheckIns }}
          </p>
        </div>
        <!-- Logout Button -->
        <button
          @click="logout"
          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { session } from "../data/session";

export default {
  data() {
    return {
      user: {
        fullName: "",
        profilePicture: "",
        totalCheckIns: 0,
      },
      dropdownOpen: true, // Always visible for your requirement
    };
  },
  methods: {
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    async fetchUserDetails() {
      try {
        if (session.user) {
          const userId = session.user;
          const response = await fetch(`/api/resource/User/${userId}`, {
            credentials: "include",
          });

          if (response.ok) {
            const userData = await response.json();
            this.user.fullName = userData.data.full_name || userId;
            this.user.profilePicture =
              userData.data.user_image || "https://via.placeholder.com/40";
            this.user.totalCheckIns = userData.data.check_ins || 0;
          } else {
            console.error("Failed to fetch user data:", response.statusText);
          }
        } else {
          console.warn("No user session found.");
        }
      } catch (error) {
        console.error("Error fetching user details:", error);
        alert("Failed to fetch user details.");
      }
    },
    async logout() {
      try {
        await fetch("/api/method/logout", {
          method: "POST",
          credentials: "include",
        });

        session.logout.submit();
        alert("Logged out successfully");
        this.$router.push({ name: "Login" });
      } catch (error) {
        console.error("Logout failed:", error);
        alert("Failed to logout. Please try again.");
      }
    },
  },
  async mounted() {
    await this.fetchUserDetails();
  },
};
</script>

<style scoped>
/* Style for the profile dropdown visibility */
</style>
