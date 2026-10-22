from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.IntegerField(verbose_name="Дневной номер заказа")),
                ("date", models.DateField(verbose_name="Дата заказа")),
                ("status", models.TextField(choices=[("В обработке", "В обработке"), ("В сборке", "В сборке"), ("Собран", "Собран"), ("Отправлен", "Отправлен"), ("Доставлен", "Доставлен"), ("Отменен", "Отменен")], default="В обработке", verbose_name="Статус")),
                ("customer_id", models.PositiveBigIntegerField(verbose_name="ID клиента users-service")),
                ("user_id", models.PositiveBigIntegerField(verbose_name="ID владельца users-service")),
            ],
            options={"verbose_name":"Заказ", "verbose_name_plural":"Заказы"},
        ),
        migrations.CreateModel(
            name="OrderDetail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_id", models.PositiveBigIntegerField(verbose_name="ID товара catalog-service")),
                ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name="Количество")),
                ("user_id", models.PositiveBigIntegerField(verbose_name="ID владельца users-service")),
                ("product_name", models.TextField(default="", verbose_name="Название товара при добавлении")),
                ("product_price", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Цена товара при добавлении")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="details", to="orders_app.order")),
            ],
            options={"verbose_name":"Деталь заказа", "verbose_name_plural":"Детали заказов"},
        ),
    ]
