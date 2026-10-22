from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.TextField("Название")
    description = models.TextField("Описание")
    # Identity is owned by users-service; this is an external identifier, not a FK.
    user_id = models.PositiveBigIntegerField("ID владельца")

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.TextField("Название")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    description = models.TextField("Описание")
    quantity = models.IntegerField("Количество на складе", validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True,
                                 verbose_name="Категория")
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="products")
    user_id = models.PositiveBigIntegerField("ID владельца")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name
