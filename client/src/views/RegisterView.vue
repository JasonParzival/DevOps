<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const formData = ref({
  username: '',
  password: '',
  password2: '',
  email: '',
  first_name: '',
  last_name: ''
})
const errors = ref({})
const loading = ref(false)

async function register() {
  errors.value = {}
  loading.value = true
  
  try {
    const response = await axios.post('/api/register/', formData.value)
    
    // Сохраняем токен
    const token = response.data.token
    localStorage.setItem('authToken', token)
    
    // Устанавливаем заголовок
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    
    // Перенаправляем на страницу товаров
    router.push('/products')
  } catch (err) {
    if (err.response && err.response.data) {
      errors.value = err.response.data
    } else {
      errors.value = { non_field_errors: ['Ошибка регистрации'] }
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-success text-white">
            <h3 class="mb-0">Регистрация</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="register">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="first_name" class="form-label">Имя</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="first_name"
                    v-model="formData.first_name"
                    required
                    :disabled="loading"
                  >
                  <div v-if="errors.first_name" class="text-danger small">
                    {{ errors.first_name[0] }}
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="last_name" class="form-label">Фамилия</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="last_name"
                    v-model="formData.last_name"
                    required
                    :disabled="loading"
                  >
                  <div v-if="errors.last_name" class="text-danger small">
                    {{ errors.last_name[0] }}
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="username" class="form-label">Имя пользователя</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username"
                  v-model="formData.username"
                  required
                  :disabled="loading"
                >
                <div v-if="errors.username" class="text-danger small">
                  {{ errors.username[0] }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email"
                  v-model="formData.email"
                  required
                  :disabled="loading"
                >
                <div v-if="errors.email" class="text-danger small">
                  {{ errors.email[0] }}
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="password" class="form-label">Пароль</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password"
                    v-model="formData.password"
                    required
                    :disabled="loading"
                  >
                  <div v-if="errors.password" class="text-danger small">
                    {{ errors.password[0] }}
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="password2" class="form-label">Подтверждение пароля</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password2"
                    v-model="formData.password2"
                    required
                    :disabled="loading"
                  >
                </div>
              </div>
              
              <div v-if="errors.non_field_errors" class="alert alert-danger">
                {{ errors.non_field_errors[0] }}
              </div>
              
              <button 
                type="submit" 
                class="btn btn-success w-100"
                :disabled="loading"
              >
                {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
              </button>
            </form>
            
            <hr>
            
            <p class="text-center mb-0">
              Уже есть аккаунт? 
              <router-link to="/login">Войти</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>