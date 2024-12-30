<template>
    <ion-page>
      <ion-header>
        <ion-toolbar>
          <ion-title>Create Sales Order</ion-title>
        </ion-toolbar>
      </ion-header>
  
      <ion-content>
        <ion-card>
          <ion-card-header>
            <ion-card-title>Create New Sales Order</ion-card-title>
          </ion-card-header>
  
          <ion-card-content>
            <form @submit.prevent="createSalesOrder">
              <!-- Customer Selection -->
              <frappe-ui-select
                label="Customer"
                v-model="form.customer"
                :options="customers"
                item-text="label"
                item-value="value"
                placeholder="Select Customer"
                searchable
              ></frappe-ui-select>
  
              <!-- Item Selection -->
              <frappe-ui-select
                label="Item"
                v-model="form.item"
                :options="items"
                item-text="label"
                item-value="value"
                placeholder="Select Item"
                searchable
              ></frappe-ui-select>
  
              <!-- Quantity -->
              <ion-item>
                <ion-label>Quantity</ion-label>
                <ion-input
                  type="number"
                  v-model.number="form.quantity"
                  placeholder="Enter quantity"
                ></ion-input>
              </ion-item>
  
              <!-- Submit Button -->
              <ion-button expand="block" type="submit">Create Sales Order</ion-button>
            </form>
          </ion-card-content>
        </ion-card>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
  import axiosInstance from "@/axios";
  import { Select as FrappeUiSelect } from "frappe-ui";
  
  export default {
    components: {
      "frappe-ui-select": FrappeUiSelect,
    },
    data() {
      return {
        customers: [],
        items: [],
        form: {
          customer: "",
          item: "",
          quantity: 1,
        },
      };
    },
    created() {
      this.fetchCustomers();
      this.fetchItems();
    },
    methods: {
      async fetchCustomers() {
        try {
          const response = await axiosInstance.post("/api/method/frappe.desk.reportview.get", {
            doctype: "Customer",
            fields: ["name", "customer_name"],
          });
  
          this.customers = response.data.message.values.map(([name, customer_name]) => ({
            label: customer_name, // What the user sees
            value: name,          // What is stored
          }));
        } catch (error) {
          console.error("Error fetching customers:", error);
        }
      },
  
      async fetchItems() {
        try {
          const response = await axiosInstance.post("/api/method/frappe.desk.reportview.get", {
            doctype: "Item",
            fields: ["name", "item_name"],
          });
  
          this.items = response.data.message.values.map(([name, item_name]) => ({
            label: item_name, // What the user sees
            value: name,      // What is stored
          }));
        } catch (error) {
          console.error("Error fetching items:", error);
        }
      },
  
      async createSalesOrder() {
        try {
          const payload = {
            doctype: "Sales Order",
            customer: this.form.customer,
            items: [
              {
                item_code: this.form.item,
                qty: this.form.quantity,
              },
            ],
          };
  
          const response = await axiosInstance.post("/api/resource/Sales Order", payload);
  
          console.log("Sales Order Created:", response.data);
          alert("Sales Order created successfully!");
          this.$router.push("/salesOrders");
        } catch (error) {
          console.error("Error creating Sales Order:", error);
          alert("Failed to create Sales Order. Please try again.");
        }
      },
    },
  };
  </script>
  