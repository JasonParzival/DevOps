# Initial catalog schema: no cross-service foreign keys.
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField(verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                ("user_id", models.PositiveBigIntegerField(verbose_name="ID владельца")),
            ],
            options={"verbose_name": "Категория товара", "verbose_name_plural": "Категории товаров"},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField(verbose_name="Название")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name="Цена")),
                ("description", models.TextField(verbose_name="Описание")),
                ("quantity", models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name="Количество на складе")),
                ("picture", models.ImageField(blank=True, null=True, upload_to="products", verbose_name="Изображение")),
                ("user_id", models.PositiveBigIntegerField(verbose_name="ID владельца")),
                ("category", models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="catalog_app.category", verbose_name="Категория")),
            ],
            options={"verbose_name": "Товар", "verbose_name_plural": "Товары"},
        ),
    ]
