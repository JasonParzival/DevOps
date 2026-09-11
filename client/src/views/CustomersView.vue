<script setup>
import axios, { Axios } from "axios";
import { ref, onMounted, computed } from 'vue';
import Cookies from 'js-cookie';
import UserFilter from '../components/UserFilter.vue'

const filterUserId = ref('')

const loading = ref(false);
const customers = ref([]);
const customerToAdd = ref({ name: '', address: '', phone_number: '', email: '' });
const customerToEdit = ref({ id: null, name: '', address: '', phone_number: '', email: '' });
const customersPictureRef = ref();
const customersAddImageUrl = ref();

const customerStats = ref(null);

const imageModalUrl = ref("")

/*onMounted(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})*/

async function loadCustomerStats() {
  const response = await axios.get('/api/customers/stats/');
  customerStats.value = response.data;
}

async function fetchCustomers() {
  loading.value = true;
  const url = filterUserId.value 
    ? `/api/customers/?user_id=${filterUserId.value}` 
    : '/api/customers/';
  const r = await axios.get(url);
  customers.value = r.data;
  loading.value = false;
}

function onFilterChange(userId) {
  filterUserId.value = userId;
  fetchCustomers();     
  loadCustomerStats();   
}

async function customersAddPictureChange() {
  customersAddImageUrl.value = URL.createObjectURL(customersPictureRef.value.files[0])
}

async function onCustomerAdd() {
  const formData = new FormData();

  // проверяем, выбран ли файл перед добавлением
  if (customersPictureRef.value.files[0]) {
    formData.append('picture', customersPictureRef.value.files[0]);
  }

  // явно привязываем поля из customerToAdd
  formData.set('name', customerToAdd.value.name)
  formData.set('address', customerToAdd.value.address)
  formData.set('phone_number', customerToAdd.value.phone_number)
  formData.set('email', customerToAdd.value.email)

  try {
    // ну и тут указываем в заголовке что отправляем данные с файлом
    await axios.post("/api/customers/", formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    await fetchCustomers();
    
    // Сброс формы
    customerToAdd.value = { name: '', address: '', phone_number: '', email: '' };
    customersPictureRef.value.value = ''; // очищаем input file
    customersAddImageUrl.value = ''; // очищаем превью
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при добавлении клиента: ' + JSON.stringify(error.response.data));
  }
}

async function onUpdateCustomer() {
  const formData = new FormData();

  // проверяем, выбран ли файл перед добавлением
  if (customersPictureRef.value.files[0]) {
    formData.append('picture', customersPictureRef.value.files[0]);
  }

  // явно привязываем поля из customerToEdit
  formData.set('name', customerToEdit.value.name)
  formData.set('address', customerToEdit.value.address)
  formData.set('phone_number', customerToEdit.value.phone_number)
  formData.set('email', customerToEdit.value.email)

  try {
    await axios.put(`/api/customers/${customerToEdit.value.id}/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    await fetchCustomers();
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при обновлении клиента: ' + JSON.stringify(error.response.data));
  }
}

async function onRemoveClick(customer) {
  if (confirm(`Удалить клиента "${customer.name}"?`)) {
    try {
      await axios.delete(`/api/customers/${customer.id}/`);
      await fetchCustomers();
    } catch (error) {
      console.error('Error details:', error.response.data);
      alert('Ошибка при удалении клиента: ' + JSON.stringify(error.response.data));
    }
  }
}

async function onCustomerEditClick(customer) {
  customerToEdit.value = { ...customer };
}

async function onLoadClick() {
  await fetchCustomers()
  loading.value = true;
  try {
    await Promise.all([await fetchCustomers(), loadCustomerStats()]);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await onLoadClick()
})

function openImageModal(imageUrl) {
  imageModalUrl.value = imageUrl
}
</script>

<template>
  <div class="modal fade" id="imageModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">Просмотр изображения</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body text-center">
          <img :src="imageModalUrl" class="img-fluid" style="max-height:70vh" alt="" />
        </div>
      </div>
    </div>
  </div>

  <div class="container my-5">
    <UserFilter @filter-change="onFilterChange" />
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Клиенты</h1>
      <button @click="onLoadClick" class="btn btn-outline-primary">
        Обновить!
      </button>
    </div>

    <div class="container mb-5">
      <form @submit.prevent.stop="onCustomerAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="customerToAdd.name"
                required
              />
              <label for="floatingInput">ФИО</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="customerToAdd.address"
                required
              />
              <label for="floatingInput">Адрес</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <input
                type="file"
                class="form-control"
                ref="customersPictureRef"
                @change="customersAddPictureChange"
              />
            </div>
          </div>
          <div class="col-auto">
            <img :src="customersAddImageUrl" 
            style="max-height: 60px;" 
            alt=""
            >
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="customerToAdd.phone_number"
                required
              />
              <label for="floatingInput">Номер телефона</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="customerToAdd.email"
                required
              />
              <label for="floatingInput">Электронная почта</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary">
              Добавить
            </button>
          </div>
        </div>
      </form>
    </div>
    

    <div class="modal fade" id="editCustomerModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content pb-3">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Редактирование
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-3">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="customerToEdit.name"
                  />
                  <label for="floatingInput">ФИО</label>
                </div>
              </div>
              <div class="col-3">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="customerToEdit.address"
                  />
                  <label for="floatingInput">Адрес</label>
                </div>
              </div>
              <div class="col-3">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="customerToEdit.phone_number"
                  />
                  <label for="floatingInput">Номер телефона</label>
                </div>
              </div>
              <div class="col-3">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="customerToEdit.email"
                  />
                  <label for="floatingInput">Электронный адрес</label>
                </div>
              </div>
            </div>
            <div class="row" style="margin-top: 3px;">
              <div class="col-auto">
                <div class="form-floating">
                  <input
                    type="file"
                    class="form-control"
                    ref="customersPictureRef"
                    @change="customersAddPictureChange"
                  />
                </div>
              </div>
              <div class="col-auto">
                <img :src="customersAddImageUrl" 
                style="max-height: 60px;" 
                alt=""
                >
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Закрыть
            </button>
            <button
              data-bs-dismiss="modal"
              type="button"
              class="btn btn-primary"
              @click="onUpdateCustomer"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    

    <div class="container" style="display: flex; gap: 20px">
      <div class="container">
        <div v-for="item in customers" class="customer-item card mb-3 shadow-sm">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6">
                <h5 class="card-title text-primary mb-2">{{ item.name }}</h5>
              </div>
              
              <div class="col-md-2">
                <div class="product-meta">
                  <small class="text-muted d-block">Адрес: {{ item.address }}</small>
                  <small class="text-muted d-block">Номер телефона: {{ item.phone_number }}</small>
                </div>
              </div>

              <div class="col-md-2">
                <div v-show="item.picture">
                  <img :src="item.picture" 
                  data-bs-toggle="modal"
                  data-bs-target="#imageModal"
                  @click="openImageModal(item.picture)"
                  style="max-height: 60px; cursor: pointer;" 
                  alt=""
                  ></img>
                </div>
              </div>
              
              <div class="col-md-2">
                <div class="d-flex gap-2 justify-content-end">
                  <button
                    class="btn btn-outline-primary btn-lg"
                    @click="onCustomerEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editCustomerModal"
                    title="Редактировать"
                  >
                    <i class="bi bi-pen-fill"></i>
                  </button>
                  <button 
                    class="btn btn-outline-danger btn-lg"
                    @click="onRemoveClick(item)"
                    title="Удалить"
                  >
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <div v-if="item.email" class="mt-3">
              <p class="card-text text-muted small">{{ item.email }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats">
        <h3>📊 Статистика по клиентам</h3>
        <div class="stats-card">
          <p><strong>Всего клиентов:</strong> <span id="total-customers">{{ customerStats?.total_count ?? 'Загрузка...' }}</span></p>
          <p><strong>Клиентов с заказами: </strong> 
            <span id="customers-with-orders">{{ customerStats?.customers_with_orders ?? 'Загрузка...' }}</span>
          </p>
          <p><strong>Всего заказов:</strong> <span id="total-orders">{{ customerStats?.total_orders ?? 'Загрузка...' }}</span></p>
          <p><strong>Среднее заказов: </strong> 
            <span id="avg-orders-per-customer">{{ customerStats?.avg_orders_per_customer ?? 'Загрузка...' }}</span>
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.customer-item {
  transition: transform 0.2s;
}

.customer-item:hover {
  transform: translateY(-2px);
}

.btn-lg {
  padding: 0.5rem 1rem;
  font-size: 1.1rem;
}
</style>