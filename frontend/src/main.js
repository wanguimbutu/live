import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import {IonicVue} from '@ionic/vue'

import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'

/* Core CSS required for Ionic components to work properly */
import '@ionic/vue/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/vue/css/normalize.css';
import '@ionic/vue/css/structure.css';
import '@ionic/vue/css/typography.css';

/* Optional CSS utils that can be commented out */
import '@ionic/vue/css/padding.css';
import '@ionic/vue/css/float-elements.css';
import '@ionic/vue/css/text-alignment.css';
import '@ionic/vue/css/text-transformation.css';
import '@ionic/vue/css/flex-utils.css';
import '@ionic/vue/css/display.css';


setConfig('resourceFetcher', frappeRequest)

const app = createApp(App).use(IonicVue).use(router);


app.use(resourcesPlugin)


app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)



router.isReady().then(() => {
  app.mount('#app');
});