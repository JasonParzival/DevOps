<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Cookies from 'js-cookie'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  error.value = ''
  loading.value = true
  
  try {
    const csrftoken = Cookies.get('csrftoken')
    if (csrftoken) {
      axios.defaults.headers.common['X-CSRFToken'] = csrftoken
    }
    
    const response = await axios.post('/api/login/', {
      username: username.value,
      password: password.value
    })
    
    // Сохраняем токен
    const token = response.data.token
    localStorage.setItem('authToken', token)
    
    // Устанавливаем заголовок для всех будущих запросов
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    
    // Получаем CSRF токен
    //await axios.get('/api/customers/')
    
    // Перенаправляем на страницу товаров
    router.push('/products')
  } catch (err) {
    if (err.response && err.response.data) {
      error.value = err.response.data.error || 'Ошибка входа'
    } else {
      error.value = 'Неверное имя пользователя или пароль'
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h3 class="mb-0">Вход в систему</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="username" class="form-label">Имя пользователя</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username"
                  v-model="username"
                  required
                  :disabled="loading"
                >
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password"
                  v-model="password"
                  required
                  :disabled="loading"
                >
              </div>
              
              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
            
            <hr>
            
            <p class="text-center mb-0">
              Нет аккаунта? 
              <router-link to="/register">Зарегистрироваться</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>