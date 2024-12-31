<template>
    <div>
      <button v-if="showButton" @click="installPWA" class="install-button">
        Install Frappe Live
      </button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        showButton: false,
        deferredPrompt: null
      };
    },
    mounted() {
      window.addEventListener("beforeinstallprompt", (e) => {
        e.preventDefault();
        this.deferredPrompt = e;
        this.showButton = true;
      });
  
      window.addEventListener("appinstalled", () => {
        console.log("PWA installed");
        this.showButton = false;
      });
    },
    methods: {
      async installPWA() {
        if (this.deferredPrompt) {
          this.deferredPrompt.prompt();
          const choiceResult = await this.deferredPrompt.userChoice;
          if (choiceResult.outcome === "accepted") {
            console.log("User accepted the install prompt");
          } else {
            console.log("User dismissed the install prompt");
          }
          this.deferredPrompt = null;
          this.showButton = false;
        }
      }
    }
  };
  </script>
  
  <style>
  .install-button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    border-radius: 5px;
    cursor: pointer;
  }
  </style>
  