<script setup>
import axios from "axios";
import { ref, onMounted, computed } from 'vue';
import Cookies from 'js-cookie';
import UserFilter from '../components/UserFilter.vue'

const filterUserId = ref('')

const loading = ref(false);
const orderDetails = ref([]);
const orders = ref([]);
const products = ref([]);
const orderDetailToAdd = ref({ order: null, product: null, quantity: null });
const orderDetailToEdit = ref({ id: null, order: null, product: null, quantity: null });

const orderDetailStats = ref(null);

const ordersById = computed(() => {
  const map = {};
  orders.value.forEach(cat => {
    map[cat.id] = cat;
  });
  return map;
});

const productsById = computed(() => {
  const map = {};
  products.value.forEach(cat => {
    map[cat.id] = cat;
  });
  return map;
});

async function loadOrderDetailStats() {
  const response = await axios.get('/api/orderDetails/stats/');
  orderDetailStats.value = response.data;
}

/*onMounted(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})*/

async function fetchOrderDetails() {
  loading.value = true;
  const url = filterUserId.value 
    ? `/api/orderDetails/?user_id=${filterUserId.value}` 
    : '/api/orderDetails/';
  const r = await axios.get(url);
  console.log(r.data)
  orderDetails.value = r.data;
  loading.value = false;
}

function onFilterChange(userId) {
  filterUserId.value = userId;
  fetchOrderDetails();      
  loadOrderDetailStats();   
}

async function fetchOrders() {
  loading.value = true;
  const r = await axios.get("/api/orders/");
  console.log(r.data)
  orders.value = r.data;
  loading.value = false;
}

async function fetchProducts() {
  loading.value = true;
  const r = await axios.get("/api/products/");
  console.log(r.data)
  products.value = r.data;
  loading.value = false;
}

async function onOrderDetailAdd() {
  try {
    await axios.post("/api/orderDetails/", {
      ...orderDetailToAdd.value,
    });
    await fetchOrderDetails();
    await fetchOrders();
    await fetchProducts();
    orderDetailToAdd.value = { order: null, product: null, quantity: null };
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при добавлении детали заказа: ' + JSON.stringify(error.response.data));
  }
}

async function onUpdateOrderDetail() {
  try {
    await axios.put(`/api/orderDetails/${orderDetailToEdit.value.id}/`, {
      ...orderDetailToEdit.value,
    });
    await fetchOrderDetails();
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при обновлении детали заказа: ' + JSON.stringify(error.response.data));
  }
}

async function onRemoveClick(orderDetail) {
  if (confirm(`Удалить позицию с количеством ${orderDetail.quantity}?`)) {
    try {
      await axios.delete(`/api/orderDetails/${orderDetail.id}/`);
      await fetchOrderDetails();
    } catch (error) {
      console.error('Error details:', error.response.data);
      alert('Ошибка при удалении детали заказа: ' + JSON.stringify(error.response.data));
    }
  }
}

async function onOrderDetailEditClick(orderDetail) {
  orderDetailToEdit.value = { ...orderDetail };
}

async function onLoadClick() {
  loading.value = true;
  try {
    await Promise.all([fetchOrderDetails(), fetchOrders(), fetchProducts(), loadOrderDetailStats()]);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await onLoadClick()
})
</script>

<template>
  <div class="container my-5">
    <UserFilter @filter-change="onFilterChange" />
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Детали заказа</h1>
      <button @click="onLoadClick" class="btn btn-outline-primary">
        Обновить!
      </button>
    </div>

    <div class="container mb-5">
      <form @submit.prevent.stop="onOrderDetailAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="orderDetailToAdd.quantity"
                required
              />
              <label for="floatingInput">Количество</label>
            </div>
          </div>
          <div class="col-2">
            <div class="form-floating">
              <select class="form-select" v-model="orderDetailToAdd.order" required>
                <option :value="g.id" v-for="g in orders">{{ g.date }} - №{{ g.order_number }}</option>
              </select>
              <label for="floatingInput">Заказ</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <select class="form-select" v-model="orderDetailToAdd.product" required>
                <option :value="g.id" v-for="g in products">{{ g.name }}</option>
              </select>
              <label for="floatingInput">Товар</label>
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
    

    <div class="modal fade" id="editOrderDetailModal" tabindex="-1">
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
              <div class="col-4">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="orderDetailToEdit.quantity"
                  />
                  <label for="floatingInput">Количество</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <select class="form-select" v-model="orderDetailToEdit.order">
                    <option :value="g.id" v-for="g in orders">
                      {{ g.date }} - №{{ g.order_number }}
                    </option>
                  </select>
                  <label for="floatingInput">Заказ</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <select class="form-select" v-model="orderDetailToEdit.product">
                    <option :value="g.id" v-for="g in products">
                      {{ g.name }}
                    </option>
                  </select>
                  <label for="floatingInput">Товар</label>
                </div>
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
              @click="onUpdateOrderDetail"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    

    <div class="container" style="display: flex; gap: 20px">
      <div class="container">
        <div v-for="item in orderDetails" class="orderDetail-item card mb-3 shadow-sm">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6">
                <h5 class="card-title text-primary mb-2">{{ item.quantity }}</h5>
                <div class="d-flex align-items-center">
                  <span class="badge bg-success me-2">Заказ:</span>
                  <span class="text-muted">{{ ordersById[item.order]?.date }} - №{{ ordersById[item.order]?.order_number }}</span>
                </div>
              </div>
              
              <div class="col-md-3">
                <div class="product-meta">
                  <span class="badge bg-success me-2">Товар:</span>
                  <span class="text-muted">{{ productsById[item.product]?.name }}</span>
                </div>
              </div>
              
              <div class="col-md-3">
                <div class="d-flex gap-2 justify-content-end">
                  <button
                    class="btn btn-outline-primary btn-lg"
                    @click="onOrderDetailEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editOrderDetailModal"
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
          </div>
        </div>
      </div>
      
      <div class="stats">
        <h3>📊 Статистика по деталям заказов</h3>
        <div class="stats-card">
          <p><strong>Всего позиций:</strong> <span id="total-order-details">{{ orderDetailStats?.total_count ?? 'Загрузка...' }}</span></p>
          <p><strong>Общее количество:</strong> <span id="total-quantity">{{ orderDetailStats?.total_quantity ?? 'Загрузка...' }}</span></p>
          <p><strong>Среднее количество:</strong> <span id="avg-quantity">{{ orderDetailStats?.avg_quantity ?? 'Загрузка...' }}</span></p>
          <p><strong>Минимум/Максимум: </strong> 
            <span id="quantity-range">{{ orderDetailStats?.min_quantity ?? 'Загрузка...'}} - {{ orderDetailStats?.max_quantity ?? 'Загрузка...'}}</span>
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.orderDetail-item {
  transition: transform 0.2s;
}

.orderDetail-item:hover {
  transform: translateY(-2px);
}

.btn-lg {
  padding: 0.5rem 1rem;
  font-size: 1.1rem;
}
</style>