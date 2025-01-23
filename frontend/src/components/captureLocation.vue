<template>
  <div class="location-container">
    <button
      @click="captureLocation"
      class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600"
    >
      Capture Location
    </button>
    <div v-if="location">
      <p>Coordinates: {{ location }}</p>
      <p>Area: {{ areaName || 'Fetching location...' }}</p>
      <div id="map" class="w-full h-64 rounded-lg mt-4"></div>
    </div>
  </div>
</template>

<script>
import L from "leaflet"; // Import Leaflet for map rendering

export default {
  name: "LocationCapture",
  data() {
    return {
      location: "", // Stores the latitude and longitude
      areaName: "", // Stores the reverse-geocoded area name
      map: null, // Reference to the Leaflet map instance
      marker: null, // Reference to the Leaflet marker
    };
  },
  methods: {
    // Load Leaflet resources dynamically
    loadLeafletResources(callback) {
      if (!window.L) {
        // Load Leaflet CSS
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css";
        document.head.appendChild(link);

        // Load Leaflet JS
        const script = document.createElement("script");
        script.src = "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js";
        script.onload = callback;
        document.head.appendChild(script);
      } else {
        callback();
      }
    },
    // Capture the current location
    captureLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            this.location = `${latitude},${longitude}`;

            // Save location to ERPNext
            this.saveLocationToERPNext(latitude, longitude);

            // Render map
            this.loadLeafletResources(() => {
              this.renderMap(latitude, longitude);
              this.reverseGeocode(latitude, longitude);
            });
          },
          (error) => {
            alert(`Unable to retrieve location: ${error.message}`);
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
      }
    },
    // Render the map
    renderMap(latitude, longitude) {
      const mapContainer = document.getElementById("map");

      // Destroy the previous map instance if it exists
      if (this.map) {
        this.map.remove();
      }

      this.map = L.map(mapContainer).setView([latitude, longitude], 13);

      // Set up the tile layer
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(this.map);

      // Add a marker to the map
      this.marker = L.marker([latitude, longitude]).addTo(this.map);
      this.marker.bindPopup("Fetching location...").openPopup();
    },
    // Perform reverse geocoding
    reverseGeocode(latitude, longitude) {
      const apiKey = "b5208eed61654e19bcb89063dab6bf3d"; // Replace with your OpenCage API key
      const url = `https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=${apiKey}&pretty=1`;

      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          if (data.results.length > 0) {
            this.areaName = data.results[0].formatted;
            if (this.marker) {
              this.marker.setPopupContent(
                `Customer Location: ${this.areaName} (${latitude}, ${longitude})`
              );
              this.marker.openPopup();
            }

            // Save area name to ERPNext
            this.saveAreaNameToERPNext(this.areaName);
          } else {
            this.areaName = `Unknown location (${latitude}, ${longitude})`;
          }
        })
        .catch((error) => {
          alert(`Error in reverse geocoding: ${error.message}`);
        });
    },
    // Save the location data to ERPNext
    async saveLocationToERPNext(latitude, longitude) {
      const locationField = `${latitude},${longitude}`;
      try {
        await fetch("/api/resource/Customer", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            custom_customer_location: locationField,
          }),
        });
      } catch (error) {
        alert(`Failed to save location to ERPNext: ${error.message}`);
      }
    },
    // Save the area name to ERPNext
    async saveAreaNameToERPNext(areaName) {
      try {
        await fetch("/api/resource/Customer", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            custom_area_name: areaName,
          }),
        });
      } catch (error) {
        alert(`Failed to save area name to ERPNext: ${error.message}`);
      }
    },
  },
};
</script>

<style>
#map {
  height: 300px;
  margin-top: 15px;
}
</style>
