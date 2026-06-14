import { createApp } from "vue";
import App from './App.vue'
import '../node_modules/bootstrap/dist/css/bootstrap.css'  //for css and styling
import router from './router'


createApp(App).use(router).mount('#app');