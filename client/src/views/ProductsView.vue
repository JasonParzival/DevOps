<script setup>
import axios from "axios";
import { ref, onMounted, computed } from 'vue';
import Cookies from 'js-cookie';
import UserFilter from '../components/UserFilter.vue'

const filterUserId = ref('')

const loading = ref(false);
const products = ref([]);
const categories = ref([]);
const productToAdd = ref({ name: '', price: null, description: '', quantity: null, category: null });
const productToEdit = ref({ id: null, name: '', price: null, description: '', quantity: null, category: null });
const productsPictureRef = ref();
const productsAddImageUrl = ref();

const productStats = ref(null);

const imageModalUrl = ref("")

const groupsById = computed(() => {
  const map = {};
  categories.value.forEach(cat => {
    map[cat.id] = cat;
  });
  return map;
});

/*onMounted(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})*/

async function loadProductStats() {
  const response = await axios.get('/api/products/stats/');
  productStats.value = response.data;
}

async function fetchProducts() {
  loading.value = true;
  const url = filterUserId.value 
    ? `/api/products/?user_id=${filterUserId.value}` 
    : '/api/products/';
  const r = await axios.get(url);
  console.log(r.data)
  products.value = r.data;
  loading.value = false;
}

function onFilterChange(userId) {
  filterUserId.value = userId;
  fetchProducts();     
  loadProductStats();   
}

async function fetchCategories() {
  loading.value = true;
  const r = await axios.get("/api/categories/");
  console.log(r.data)
  categories.value = r.data;
  loading.value = false;
}

async function productsAddPictureChange() {
  productsAddImageUrl.value = URL.createObjectURL(productsPictureRef.value.files[0])
}

/*async function onProductAdd() {
  const formData = new FormData();

  // вытаскиваем выбранный файл с формы через studentsPictureRef.value.files
  formData.append('picture', productsPictureRef.value.files[0]);

  // явно привязываем поля из studentToAdd
  formData.set('name', productToAdd.value.name)
  formData.set('price', productToAdd.value.price)
  formData.set('description', productToAdd.value.description)
  formData.set('quantity', productToAdd.value.quantity)
  formData.set('category', productToAdd.value.category)

  // ну и тут указываем в заголовке что отправляем данные с файлом
  await axios.post("/api/products/", formData, {
      headers: {
          'Content-Type': 'multipart/form-data'
      }
  });
  await fetchProducts();
  await fetchCategories();

  /*await axios.post("/api/products/", {
    ...productToAdd.value,
  });
  await fetchProducts();
  await fetchCategories();*//*
  // Сброс формы
  productToAdd.value = { name: '', price: null, description: '', quantity: null, category: null };
}*/

async function onProductAdd() {
  const formData = new FormData();

  if (productsPictureRef.value.files[0]) {
    formData.append('picture', productsPictureRef.value.files[0]);
  }

  formData.set('name', productToAdd.value.name)
  formData.set('price', productToAdd.value.price)
  formData.set('description', productToAdd.value.description)
  formData.set('quantity', productToAdd.value.quantity)
  formData.set('category', productToAdd.value.category)

  try {
    const response = await axios.post("/api/products/", formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    await fetchProducts();
    await fetchCategories();
    productToAdd.value = { name: '', price: null, description: '', quantity: null, category: null };
    productsPictureRef.value.value = '';
    productsAddImageUrl.value = ''; 
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при добавлении товара: ' + JSON.stringify(error.response.data));
  }
}

async function onUpdateProduct() {
  const formData = new FormData();

  if (productsPictureRef.value.files[0]) {
    formData.append('picture', productsPictureRef.value.files[0]);
  }

  formData.set('name', productToEdit.value.name)
  formData.set('price', productToEdit.value.price)
  formData.set('description', productToEdit.value.description)
  formData.set('quantity', productToEdit.value.quantity)
  formData.set('category', productToEdit.value.category)

  try {
    await axios.put(`/api/products/${productToEdit.value.id}/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    await fetchProducts();
    productsPictureRef.value.value = '';
    productsAddImageUrl.value = '';
  } catch (error) {
    console.error('Error details:', error.response.data);
    alert('Ошибка при обновлении товара: ' + JSON.stringify(error.response.data));
  }
}

async function onRemoveClick(product) {
  if (confirm(`Удалить товар "${product.name}"?`)) {
    try {
      await axios.delete(`/api/products/${product.id}/`);
      await fetchProducts();
    } catch (error) {
      console.error('Error details:', error.response.data);
      alert('Ошибка при удалении товара: ' + JSON.stringify(error.response.data));
    }
  }
}

async function onProductEditClick(product) {
  productToEdit.value = { ...product };
}

async function onLoadClick() {
  loading.value = true;
  try {
    await Promise.all([fetchProducts(), fetchCategories(), loadProductStats()]);
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
      <h1>Товары</h1>
      <button @click="onLoadClick" class="btn btn-outline-primary">
        Обновить!
      </button>
    </div>

    <div class="container mb-5">
      <form @submit.prevent.stop="onProductAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="productToAdd.name"
                required
              />
              <label for="floatingInput">Название</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="productToAdd.price"
                required
              />
              <label for="floatingInput">Цена</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <input
                type="file"
                class="form-control"
                ref="productsPictureRef"
                @change="productsAddPictureChange"
              />
            </div>
          </div>
          <div class="col-auto">
            <img :src="productsAddImageUrl" 
            style="max-height: 60px;" 
            alt=""
            >
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="productToAdd.description"
                required
              />
              <label for="floatingInput">Описание</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="productToAdd.quantity"
                required
              />
              <label for="floatingInput">Количество</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <select class="form-select" v-model="productToAdd.category" required>
                <option :value="g.id" v-for="g in categories">{{ g.name }}</option>
              </select>
              <label for="floatingInput">Категория</label>
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
    

    <div class="modal fade" id="editProductModal" tabindex="-1">
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
              <div class="col-2">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="productToEdit.name"
                  />
                  <label for="floatingInput">Название</label>
                </div>
              </div>
              <div class="col-2">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="productToEdit.price"
                  />
                  <label for="floatingInput">Цена</label>
                </div>
              </div>
              <div class="col-3">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="productToEdit.description"
                  />
                  <label for="floatingInput">Описание</label>
                </div>
              </div>

              <div class="col-2">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="productToEdit.quantity"
                  />
                  <label for="floatingInput">Количество</label>
                </div>
              </div>
              <div class="col-3">
                <div class="form-floating">
                  <select class="form-select" v-model="productToEdit.category">
                    <option :value="g.id" v-for="g in categories">
                      {{ g.name }}
                    </option>
                  </select>
                  <label for="floatingInput">Группа</label>
                </div>
              </div>
            </div>
            <div class="row" style="margin-top: 3px;">
              <div class="col-auto">
                <div class="form-floating">
                  <input
                    type="file"
                    class="form-control"
                    ref="productsPictureRef"
                    @change="productsAddPictureChange"
                  />
                </div>
              </div>
              <div class="col-auto">
                <img :src="productsAddImageUrl" 
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
              @click="onUpdateProduct"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    

    <div class="container" style="display: flex; gap: 20px">
      <div class="container">
        <div v-for="item in products" class="product-item card mb-3 shadow-sm">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6">
                <h5 class="card-title text-primary mb-2">{{ item.name }}</h5>
                <div class="d-flex align-items-center">
                  <span class="badge bg-success me-2">Категория:</span>
                  <span class="text-muted">{{ groupsById[item.category]?.name }}</span>
                </div>
              </div>

              <div class="col-md-2">
                <div class="product-meta">
                  <small class="text-muted d-block">Цена: {{ item.price }} ₽</small>
                  <small class="text-muted d-block">В наличии: {{ item.quantity }} шт.</small>
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
                    @click="onProductEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editProductModal"
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
            
            <div v-if="item.description" class="mt-3">
              <p class="card-text text-muted small">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats">
        <h3>📊 Статистика по товарам</h3>
        <div class="stats-card">
          <p><strong>Всего товаров:</strong> <span id="total-products">{{ productStats?.total_count ?? 'Загрузка...' }}</span></p>
          <p><strong>Средняя цена:</strong> <span id="avg-price">{{ productStats?.avg_price ? productStats.avg_price + ' ₽' : 'Загрузка...' }}</span></p>
          <p><strong>Общий запас:</strong> <span id="total-stock">{{ productStats?.total_stock ?? 'Загрузка...' }}</span></p>
          <p><strong>Ценовой диапазон:</strong> 
            <span id="price-range">{{ productStats?.min_price && productStats?.max_price 
               ? productStats.min_price + ' - ' + productStats.max_price + ' ₽' 
               : 'Загрузка...' }}</span>
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.product-item {
  transition: transform 0.2s;
}

.product-item:hover {
  transform: translateY(-2px);
}

.btn-lg {
  padding: 0.5rem 1rem;
  font-size: 1.1rem;
}
</style>