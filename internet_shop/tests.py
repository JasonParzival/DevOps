from django.test import TestCase
#from rest_framework import APIClient
from model_bakery import baker

from internet_shop.models import Product
from internet_shop.models import Category
from internet_shop.models import Customer
from internet_shop.models import Order
from internet_shop.models import OrderDetail

# Create your tests here.
class ProductsViewsetTestCase(TestCase):
    def test_get_list(self):
        ctg = baker.make("Category")
        
        product = baker.make("Product", category = ctg)

        r = self.client.get('/api/products/')
        data = r.json()
        print(data)
        assert product.name == data[0]['name']
        assert product.id == data[0]['id']
        assert product.category.id == data[0]['category']#['id']
        assert len(data) == 1
        
    def test_create(self):
        ctg = baker.make("Category")

        r = self.client.post("/api/products/", {
            "name": "Молоко",
            "category": ctg.id,
            "price": 10.0,
            "quantity": 5,
            "description": "yo"
        })
        print(r.json())

        new_product_id = r.json()['id']
        

        products = Product.objects.all()
        assert len(products) == 1

        new_product = Product.objects.filter(id=new_product_id).first()
        assert new_product.name == 'Молоко'
        assert new_product.category == ctg
        
    def test_delete(self):
        products = baker.make("Product", 10)
        r = self.client.get('/api/products/')
        data = r.json()
        assert len(data) == 10
        
        product_id_to_delete = products[3].id
        self.client.delete(f'/api/products/{product_id_to_delete}/')
        
        r = self.client.get('/api/products/')
        data = r.json()
        assert len(data) == 9
        
        assert product_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        products = baker.make("Product", 10)
        product: Product = products[2]
        
        ctg = baker.make("Category")
        
        r = self.client.get(f'/api/products/{product.id}/')
        data = r.json()
        assert data['name'] == product.name
        
        import json
        r = self.client.put(
            f'/api/products/{product.id}/', 
            data=json.dumps({
                "name": "Молоко",
                "category": ctg.id,
                "price": 10.0,
                "quantity": 5,
                "description": "yo"
            }), 
            content_type='application/json'
        )
        
        assert r.status_code == 200
        
        r = self.client.get(f'/api/products/{product.id}/')
        data = r.json()
        assert data['name'] == "Молоко"
        
        product.refresh_from_db()
        assert data['name'] == product.name
        
class CategoriesViewsetTestCase(TestCase):
    def test_get_list(self):
        ctg = baker.make("Category")

        r = self.client.get('/api/categories/')
        data = r.json()
        print(data)
        assert ctg.name == data[0]['name']
        assert ctg.id == data[0]['id']
        assert len(data) == 1
        
    def test_create(self):
        r = self.client.post("/api/categories/", {
            "name": "Молочное",
            "description": "yo"
        })
        print(r.json())

        new_ctg_id = r.json()['id']

        ctgs = Category.objects.all()
        assert len(ctgs) == 1

        new_ctg = Category.objects.filter(id=new_ctg_id).first()
        assert new_ctg.name == "Молочное"
        
    def test_delete(self):
        ctgs = baker.make("Category", 10)
        r = self.client.get('/api/categories/')
        data = r.json()
        assert len(data) == 10
        
        ctg_id_to_delete = ctgs[3].id
        self.client.delete(f'/api/categories/{ctg_id_to_delete}/')
        
        r = self.client.get('/api/categories/')
        data = r.json()
        assert len(data) == 9
        
        assert ctg_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        ctgs = baker.make("Category", 10)
        ctg: Category = ctgs[2]
        
        r = self.client.get(f'/api/categories/{ctg.id}/')
        data = r.json()
        assert data['name'] == ctg.name
        
        import json
        r = self.client.put(
            f'/api/categories/{ctg.id}/', 
            data=json.dumps({
                "name": "Молочное",
                "description": "yo"
            }), 
            content_type='application/json'
        )
        
        assert r.status_code == 200
        
        r = self.client.get(f'/api/categories/{ctg.id}/')
        data = r.json()
        assert data['name'] == "Молочное"
        
        ctg.refresh_from_db()
        assert data['name'] == ctg.name
        
class CustomersViewsetTestCase(TestCase):
    def test_get_list(self):
        cst = baker.make("Customer")

        r = self.client.get('/api/customers/')
        data = r.json()
        print(data)
        assert cst.name == data[0]['name']
        assert cst.id == data[0]['id']
        assert len(data) == 1
        
    def test_create(self):
        r = self.client.post("/api/customers/", {
            "name": "Sami",
            "address": "barselona",
            "phone_number": "89086661115",
            "email": "gg@gmail.com",
        })
        print(r.json())

        new_cst_id = r.json()['id']
        

        csts = Customer.objects.all()
        assert len(csts) == 1

        new_cst = Customer.objects.filter(id=new_cst_id).first()
        assert new_cst.name == 'Sami'
        
    def test_delete(self):
        csts = baker.make("Customer", 10)
        r = self.client.get('/api/customers/')
        data = r.json()
        assert len(data) == 10
        
        cst_id_to_delete = csts[3].id
        self.client.delete(f'/api/customers/{cst_id_to_delete}/')
        
        r = self.client.get('/api/customers/')
        data = r.json()
        assert len(data) == 9
        
        assert cst_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        csts = baker.make("Customer", 10)
        cst: Customer = csts[2]
        
        r = self.client.get(f'/api/customers/{cst.id}/')
        data = r.json()
        assert data['name'] == cst.name
        
        import json
        r = self.client.put(
            f'/api/customers/{cst.id}/', 
            data=json.dumps({
                "name": "Sami",
                "address": "barselona",
                "phone_number": "89086661115",
                "email": "gg@gmail.com",
            }), 
            content_type='application/json'
        )
        
        assert r.status_code == 200
        
        r = self.client.get(f'/api/customers/{cst.id}/')
        data = r.json()
        assert data['name'] == "Sami"
        
        cst.refresh_from_db()
        assert data['name'] == cst.name
        
class OrdersViewsetTestCase(TestCase):
    def test_get_list(self):
        cst = baker.make("Customer")

        order = baker.make("Order", customer = cst)

        r = self.client.get('/api/orders/')
        data = r.json()
        print(data)
        assert str(order.date) == data[0]['date']
        assert order.id == data[0]['id']
        assert order.customer.id == data[0]['customer']#['id']
        assert len(data) == 1
        
    def test_create(self):
        cst = baker.make("Customer")

        import json
        
        r = self.client.post(
            "/api/orders/",
            json.dumps({
                "date": "2025-10-10",
                "customer": cst.id,
                "status": "в процессе"
            }),
            content_type="application/json"
        )
        print(r.json())

        new_order_id = r.json()['id']
        

        orders = Order.objects.all()
        assert len(orders) == 1

        new_order = Order.objects.filter(id=new_order_id).first()
        #assert Customer.objects.filter(pk=cst.id).exists()
        assert str(new_order.date) == '2025-10-10'
        assert new_order.customer == cst
        
    def test_delete(self):
        orders = baker.make("Order", 10)
        r = self.client.get('/api/orders/')
        data = r.json()
        assert len(data) == 10
        
        order_id_to_delete = orders[3].id
        self.client.delete(f'/api/orders/{order_id_to_delete}/')
        
        r = self.client.get('/api/orders/')
        data = r.json()
        assert len(data) == 9
        
        assert order_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        orders = baker.make("Order", 10)
        order: Order = orders[2]
        
        cst = baker.make("Customer")
        
        r = self.client.get(f'/api/orders/{order.id}/')
        data = r.json()
        assert data['date'] == str(order.date)
        
        import json
        r = self.client.put(
            f'/api/orders/{order.id}/', 
            data=json.dumps({
                "date": "2025-10-10",
                "customer": cst.id,
                "status": "в процессе"
            }), 
            content_type='application/json'
        )
        
        assert r.status_code == 200
        
        r = self.client.get(f'/api/orders/{order.id}/')
        data = r.json()
        assert data['date'] == "2025-10-10"

        order.refresh_from_db()
        assert data['date'] == str(order.date)
        
class OrderDetailsViewsetTestCase(TestCase):
    def test_get_list(self):
        cst = baker.make("Customer")

        order = baker.make("Order", customer = cst)
        
        ctg = baker.make("Category")
        
        product = baker.make("Product", category = ctg)
        
        ordt = baker.make("OrderDetail", product = product, order = order)

        r = self.client.get('/api/orderDetails/')
        data = r.json()
        print(data)
        assert ordt.quantity == data[0]['quantity']
        assert ordt.id == data[0]['id']
        assert ordt.product.id == data[0]['product']#['id']
        assert ordt.order.id == data[0]['order']#['id']
        assert len(data) == 1
        
    def test_create(self):
        cst = baker.make("Customer")

        order = baker.make("Order", customer = cst)
        
        ctg = baker.make("Category")
        
        product = baker.make("Product", category = ctg)

        r = self.client.post("/api/orderDetails/", {
            "order": order.id,
            "product": product.id,
            "quantity": 5,
        })
        print(r.json())

        new_ordt_id = r.json()['id']
        

        ordts = OrderDetail.objects.all()
        assert len(ordts) == 1

        new_ordt = OrderDetail.objects.filter(id=new_ordt_id).first()
        assert new_ordt.quantity == 5
        assert new_ordt.product == product
        assert new_ordt.order == order
        
    def test_delete(self):
        ordts = baker.make("OrderDetail", 10)
        r = self.client.get('/api/orderDetails/')
        data = r.json()
        assert len(data) == 10
        
        ordt_id_to_delete = ordts[3].id
        self.client.delete(f'/api/orderDetails/{ordt_id_to_delete}/')
        
        r = self.client.get('/api/orderDetails/')
        data = r.json()
        assert len(data) == 9
        
        assert ordt_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        ordts = baker.make("OrderDetail", 10)
        ordt: OrderDetail = ordts[2]
        
        cst = baker.make("Customer")

        order = baker.make("Order", customer = cst)
        
        ctg = baker.make("Category")
        
        product = baker.make("Product", category = ctg)
        
        r = self.client.get(f'/api/orderDetails/{ordt.id}/')
        data = r.json()
        assert data['quantity'] == ordt.quantity
        
        import json
        r = self.client.put(
            f'/api/orderDetails/{ordt.id}/', 
            data=json.dumps({
                "order": order.id,
                "product": product.id,
                "quantity": 5,
            }), 
            content_type='application/json'
        )
        
        assert r.status_code == 200
        
        r = self.client.get(f'/api/orderDetails/{ordt.id}/')
        data = r.json()
        assert data['quantity'] == 5
        
        ordt.refresh_from_db()
        assert data['quantity'] == ordt.quantity