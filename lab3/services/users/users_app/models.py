from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    name = models.TextField("ФИО")
    address = models.TextField("Адрес")
    phone_number = models.TextField("Номер телефона")
    email = models.TextField("Электронная почта")
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="customers")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name
