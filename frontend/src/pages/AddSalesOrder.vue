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
          <!-- Form -->
          <form @submit.prevent>
            <!-- Customer Selection -->
            <div class="form-group">
              <frappe-ui-autocomplete
                label="Customer"
                v-model="form.customer"
                :options="customers"
                item-text="label"
                item-value="value"
                placeholder="Select Customer"
                @click.native.stop="logEvent('Customer dropdown clicked')"
                @keydown.native.stop="logEvent('Customer dropdown keydown')"
                required
              />
            </div>

            <!-- Item Selection -->
            <div class="form-group">
              <frappe-ui-autocomplete
                label="Item"
                v-model="form.item"
                :options="items"
                item-text="label"
                item-value="value"
                placeholder="Select Item"
                @click.native.stop="logEvent('Item dropdown clicked')"
                @keydown.native.stop="logEvent('Item dropdown keydown')"
                required
              />
            </div>

            <!-- Quantity -->
            <div class="form-group">
              <ion-item>
                <ion-label position="stacked">Quantity</ion-label>
                <ion-input
                  type="number"
                  v-model.number="form.quantity"
                  placeholder="Enter quantity"
                  required
                />
              </ion-item>
            </div>

            <!-- Delivery Date -->
            <div class="form-group">
              <frappe-ui-datepicker
                label="Delivery Date"
                v-model="form.deliveryDate"
                placeholder="Select delivery date"
                required
              />
            </div>
          </form>

          <!-- Submit Button -->
          <div class="form-actions">
            <ion-button
              expand="block"
              color="primary"
              @click="createSalesOrder"
            >
              Create Sales Order
            </ion-button>
          </div>
        </ion-card-content>
      </ion-card>
    </ion-content>
  </ion-page>
</template>

<script>
import {
  Autocomplete as FrappeUiAutocomplete,
  DatePicker as FrappeUiDatePicker,
} from "frappe-ui";
import {
  IonPage,
  IonContent,
  IonCard,
  IonCardContent,
  IonInput,
  IonLabel,
  IonItem,
  IonButton,
  IonCardTitle,
  IonCardHeader,
  IonToolbar,
  IonTitle,
  IonHeader,
} from "@ionic/vue";

export default {
  components: {
    "frappe-ui-autocomplete": FrappeUiAutocomplete,
    "frappe-ui-datepicker": FrappeUiDatePicker,
    IonPage,
    IonCard,
    IonCardContent,
    IonContent,
    IonInput,
    IonItem,
    IonLabel,
    IonButton,
    IonCardTitle,
    IonCardHeader,
    IonHeader,
    IonTitle,
    IonToolbar,
  },
  data() {
    return {
      customers: [],
      items: [],
      form: {
        customer: "",
        item: "",
        quantity: 1,
        deliveryDate: "",
      },
    };
  },
  created() {
    this.fetchCustomers();
    this.fetchItems();
  },
  methods: {
    logEvent(eventDescription) {
      console.log(eventDescription);
    },

    async fetchCustomers() {
      try {
        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            doctype: "Customer",
            fields: ["name", "customer_name"],
          }),
        });

        const data = await response.json();
        this.customers = data.message.values.map(([name, customer_name]) => ({
          label: customer_name,
          value: name,
        }));
      } catch (error) {
        console.error("Error fetching customers:", error);
      }
    },

    async fetchItems() {
      try {
        const response = await fetch("/api/method/frappe.desk.reportview.get", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            doctype: "Item",
            fields: ["name", "item_name"],
          }),
        });

        const data = await response.json();
        this.items = data.message.values.map(([name, item_name]) => ({
          label: item_name,
          value: name,
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
          delivery_date: this.form.deliveryDate,
        };

        const response = await fetch("/api/resource/Sales Order", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const result = await response.json();
        console.log("Sales Order Created:", result);
        alert("Sales Order created successfully!");
        this.$router.push("/salesOrderList");
      } catch (error) {
        console.error("Error creating Sales Order:", error);
        alert("Failed to create Sales Order. Please try again.");
      }
    },
  },
};
</script>
<style scoped>
.form-group {
  margin-bottom: 20px;
}

.form-actions {
  margin-top: 30px;
}

ion-card-title {
  font-size: 1.4rem;
  text-align: center;
  margin-bottom: 10px;
}
</style>