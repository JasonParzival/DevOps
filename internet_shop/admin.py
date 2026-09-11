from django.contrib import admin

from internet_shop.models import Product
from internet_shop.models import Category
from internet_shop.models import Customer
from internet_shop.models import Order
from internet_shop.models import OrderDetail

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'description', 'quantity', 'category']
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'phone_number', 'email']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'date', 'status', 'customer']
    
@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity']