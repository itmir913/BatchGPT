import {createApp} from 'vue'
import App from './App.vue'
import router from './router/router';

import 'bootstrap/dist/css/bootstrap.min.css';
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle.js';

createApp(App).use(router)
    .provide('bootstrap', bootstrap)
    .mount('#app')
