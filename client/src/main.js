import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios' 
import "bootstrap/dist/css/bootstrap.css"
//import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap"

import App from './App.vue'
import router from './router'

const token = localStorage.getItem('authToken')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Token ${token}`
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
