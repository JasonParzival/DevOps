from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.TextField("Название")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    description = models.TextField("Описание")
    quantity = models.IntegerField("Количество на складе")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, null=True, verbose_name="Категория")
    # добавим ImageField, в upload_to указываем папку куда загружать файл
    picture = models.ImageField("Изображение", null=True, upload_to="products")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True) 
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        
    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.TextField("Название")
    description = models.TextField("Описание")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"
        
    def __str__(self) -> str:
        return self.name
         
class Customer(models.Model):
    name = models.TextField("ФИО")
    address = models.TextField("Адрес")
    phone_number = models.TextField("Номер телефона")
    email = models.TextField("Электронная почта")
    picture = models.ImageField("Изображение", null=True, upload_to="customers")
    
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        
    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    order_number = models.IntegerField("Дневной номер заказа")
    date = models.DateField("Дата заказа")
    status = models.TextField("Статус", choices=[    
        ('В обработке', 'В обработке'),
        ('В сборке', 'В сборке'), 
        ('Собран', 'Собран'),
        ('Отправлен', 'Отправлен'),
        ('Доставлен', 'Доставлен'),
        ('Отменен', 'Отменен'),
    ], 
    default='В обработке' )
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, null=True, verbose_name="Клиент")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True) 
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        
    def __str__(self) -> str:
        return str(self.date)

class OrderDetail(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, null=True, verbose_name="Заказ")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, null=True, verbose_name="Продукт")
    quantity = models.IntegerField("Количество")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True) 
    
    class Meta:
        verbose_name = "Детали заказа"
        verbose_name_plural = "Детали заказов"
    