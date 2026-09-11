<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['filter-change'])

const users = ref([])
const selectedUserId = ref('')
const isSuperuser = ref(false)

async function loadUsers() {
  try {
    const response = await axios.get('/api/users/')

    if (response.data && response.data.length > 0) {
      users.value = response.data
      isSuperuser.value = true
    } else {
      isSuperuser.value = false
      users.value = []
    }
  } catch (error) {
    isSuperuser.value = false
    users.value = []
    console.log('Не суперюзер или нет прав')
  }
}

function applyFilter() {
  emit('filter-change', selectedUserId.value)
}

function clearFilter() {
  selectedUserId.value = ''
  applyFilter()
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div v-if="isSuperuser && users.length > 0" class="card mb-3 p-3 bg-light">
    <div class="row g-2 align-items-center">
      <div class="col-auto">
        <label class="form-label mb-0 fw-bold">Фильтр по пользователю:</label>
      </div>
      <div class="col-auto flex-grow-1">
        <select class="form-select" v-model="selectedUserId" @change="applyFilter">
          <option value="">Все пользователи</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.username }} ({{ user.first_name }} {{ user.last_name }})
          </option>
        </select>
      </div>
      <div class="col-auto">
        <button 
          class="btn btn-outline-secondary btn-sm" 
          @click="clearFilter" 
          v-if="selectedUserId"
        >
          Сбросить
        </button>
      </div>
    </div>
  </div>
</template>