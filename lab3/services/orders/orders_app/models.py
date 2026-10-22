from django.core.validators import MinValueValidator
from django.db import models


STATUS_CHOICES = [
    ("В обработке", "В обработке"), ("В сборке", "В сборке"),
    ("Собран", "Собран"), ("Отправлен", "Отправлен"),
    ("Доставлен", "Доставлен"), ("Отменен", "Отменен"),
]

class Order(models.Model):
    order_number = models.IntegerField("Дневной номер заказа")
    date = models.DateField("Дата заказа")
    status = models.TextField("Статус", choices=STATUS_CHOICES, default="В обработке")
    customer_id = models.PositiveBigIntegerField("ID клиента users-service")
    user_id = models.PositiveBigIntegerField("ID владельца users-service")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return str(self.date)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    product_id = models.PositiveBigIntegerField("ID товара catalog-service")
    quantity = models.PositiveIntegerField("Количество", validators=[MinValueValidator(1)])
    user_id = models.PositiveBigIntegerField("ID владельца users-service")
    product_name = models.TextField("Название товара при добавлении", default="")
    product_price = models.DecimalField("Цена товара при добавлении", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Деталь заказа"
        verbose_name_plural = "Детали заказов"
